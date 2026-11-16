#!/usr/bin/env python3
"""Gera a secção de tinteiros e toners do site PCinfor a partir de uma lista.

Uso:
    python3 ferramentas/gerar_consumiveis.py [lista.csv|lista.xlsx]

Por omissão lê dados/consumiveis.csv. Gera:
    consumiveis/index.html                    catálogo com pesquisa
    consumiveis/dados.js                      dados para a pesquisa
    consumiveis/<artigo>/index.html           uma página por artigo
    consumiveis/impressora/<modelo>/index.html uma página por impressora

Colunas reconhecidas (o nome pode variar, ver ALIASES): referencia, descricao,
marca, tipo, cor, origem, impressoras, preco, stock, rendimento, foto.
Colunas de fornecedor ou de preço de compra são sempre ignoradas.

Os links de pagamento vêm de dados/links_pagamento_consumiveis.csv
(artigo;preco;link), criado por ferramentas/criar_links_consumiveis.py.
"""
import csv
import html
import json
import re
import shutil
import sys
import unicodedata
import urllib.parse
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DADOS = RAIZ / "dados"
SAIDA = RAIZ / "consumiveis"
IMG = RAIZ / "img" / "consumiveis"
LINKS = DADOS / "links_pagamento_consumiveis.csv"
WHATS = "351963401241"
SITE = "https://www.pcinfor.pt"

ALIASES = {
    "referencia": ["referencia", "ref", "referencia original", "codigo", "cod", "sku", "modelo consumivel"],
    "descricao": ["descricao", "nome", "designacao", "artigo", "produto"],
    "marca": ["marca", "fabricante", "marca impressora"],
    "tipo": ["tipo", "categoria", "familia"],
    "cor": ["cor", "cores", "colour", "color"],
    "origem": ["origem", "original compativel", "original/compativel", "original ou compativel", "compativel", "original"],
    "impressoras": ["impressoras", "impressoras compativeis", "compatibilidade", "compativel com", "modelos compativeis", "equipamentos"],
    "preco": ["preco", "preco com iva", "pvp", "preco venda", "preco iva incluido", "pvp com iva"],
    "stock": ["stock", "quantidade", "qtd", "existencias", "disponivel"],
    "rendimento": ["rendimento", "paginas", "capacidade", "rendimento paginas"],
    "foto": ["foto", "imagem", "link foto", "url foto", "fotografia", "image"],
}
# Nunca chegam ao site.
PROIBIDAS = ["fornecedor", "custo", "compra", "preco compra", "preco custo", "margem", "distribuidor", "pvf", "preco sem iva"]

MARCAS_IMPRESSORA = ["hp", "canon", "epson", "brother", "samsung", "lexmark", "xerox", "kyocera", "ricoh",
                     "oki", "dell", "konica", "minolta", "sharp", "pantum", "olivetti", "utax", "triumph"]

CORES = {
    "preto": ["#2B2724"], "black": ["#2B2724"], "bk": ["#2B2724"],
    "ciano": ["#0098D8"], "azul": ["#0098D8"], "cyan": ["#0098D8"],
    "magenta": ["#D1077B"],
    "amarelo": ["#F6C400"], "yellow": ["#F6C400"],
    "cinzento": ["#8C8580"], "cinza": ["#8C8580"],
    "tricolor": ["#0098D8", "#D1077B", "#F6C400"], "cores": ["#0098D8", "#D1077B", "#F6C400"], "cor": ["#0098D8", "#D1077B", "#F6C400"],
    "pack": ["#2B2724", "#0098D8", "#D1077B", "#F6C400"], "multipack": ["#2B2724", "#0098D8", "#D1077B", "#F6C400"],
}


# ---------------------------------------------------------------- utilidades
def sem_acentos(t):
    return "".join(c for c in unicodedata.normalize("NFD", t) if unicodedata.category(c) != "Mn")


def chave(t):
    """Texto compacto para comparar: minúsculas, sem acentos, só letras e números."""
    return re.sub(r"[^a-z0-9]", "", sem_acentos(str(t)).lower())


def slug(t):
    t = re.sub(r"[^a-z0-9]+", "-", sem_acentos(str(t)).lower()).strip("-")
    return re.sub(r"-{2,}", "-", t)


def e(t):
    return html.escape(str(t), quote=True)


def preco_txt(v):
    s = f"{v:,.2f}".replace(",", " ").replace(".", ",").replace(" ", ".")
    return (s[:-3] if s.endswith(",00") else s) + "€"


def ler_preco(t):
    t = str(t or "").replace("€", "").replace("EUR", "").strip()
    if not t:
        return None
    if "," in t and "." in t:
        t = t.replace(".", "").replace(",", ".") if t.rfind(",") > t.rfind(".") else t.replace(",", "")
    else:
        t = t.replace(",", ".")
    try:
        return round(float(t), 2)
    except ValueError:
        return None


def ler_inteiro(t):
    m = re.search(r"-?\d+", str(t or "").replace(".", "").replace(" ", ""))
    return int(m.group()) if m else None


def wa(texto):
    return f"https://wa.me/{WHATS}?text=" + urllib.parse.quote(texto, safe="")


# ---------------------------------------------------------------- leitura
def ler_linhas(caminho):
    caminho = Path(caminho)
    if caminho.suffix.lower() in (".xlsx", ".xlsm"):
        import openpyxl
        ws = openpyxl.load_workbook(caminho, read_only=True, data_only=True).active
        linhas = [["" if c is None else str(c) for c in r] for r in ws.iter_rows(values_only=True)]
        cab, corpo = linhas[0], linhas[1:]
        return [dict(zip(cab, r)) for r in corpo]
    texto = caminho.read_bytes()
    for cod in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            texto = texto.decode(cod)
            break
        except UnicodeDecodeError:
            continue
    dialeto = csv.Sniffer().sniff(texto.splitlines()[0], delimiters=";,\t")
    return list(csv.DictReader(texto.splitlines(), dialect=dialeto))


def mapear_colunas(cabecalho):
    mapa, ignoradas = {}, []
    for col in cabecalho:
        k = re.sub(r"\s+", " ", sem_acentos(col or "").lower().replace("_", " ")).strip()
        if any(p in k for p in PROIBIDAS):
            ignoradas.append(col)
            continue
        for campo, nomes in ALIASES.items():
            if campo not in mapa and k in nomes:
                mapa[campo] = col
                break
    return mapa, ignoradas


def normalizar_tipo(t, descricao):
    k = chave(f"{t} {descricao}")
    if "toner" in k:
        return "Toner"
    if "tambor" in k or "drum" in k or "unidadedeimagem" in k:
        return "Tambor"
    if "fita" in k or "ribbon" in k:
        return "Fita"
    if "tinteiro" in k or "cartucho" in k or "tinta" in k or "ink" in k:
        return "Tinteiro"
    return (t or "Consumível").strip().capitalize()


def normalizar_origem(t, descricao):
    k = chave(f"{t} {descricao}")
    if "compat" in k or "reciclad" in k or "remanufat" in k:
        return "Compatível"
    if "original" in k or k in ("sim", "s", "o"):
        return "Original"
    return "Compatível"


def dividir_impressoras(t, marca):
    """Separa a lista de impressoras (grupos com | ou ; e modelos com vírgula).
    "PIXMA MG2450, MG2550" passa a "PIXMA MG2450" e "PIXMA MG2550"; "DeskJet 2710, 2720" igual."""
    nomes, vistos = [], set()
    for grupo in re.split(r"[|\n;]+", str(t or "")):
        serie = ""
        for parte in grupo.split(","):
            p = re.sub(r"\s+", " ", parte).strip(" .")
            if not p:
                continue
            if " " not in p and serie and chave(p) not in MARCAS_IMPRESSORA:
                p = f"{serie} {p}"
            elif " " in p:
                serie = p.rsplit(" ", 1)[0]
            if marca and chave(p.split(" ")[0]) not in MARCAS_IMPRESSORA:
                p = f"{marca} {p}"
            if chave(p) not in vistos:
                vistos.add(chave(p))
                nomes.append(p)
    return nomes


def ler_artigos(caminho):
    linhas = ler_linhas(caminho)
    if not linhas:
        sys.exit("A lista está vazia.")
    mapa, ignoradas = mapear_colunas(linhas[0].keys())
    if ignoradas:
        print("Colunas ignoradas (fornecedor/compra, nunca vão para o site):", ", ".join(ignoradas))
    for obrig in ("referencia", "preco", "impressoras"):
        if obrig not in mapa:
            sys.exit(f"Falta a coluna '{obrig}'. Colunas encontradas: {', '.join(linhas[0].keys())}")
    artigos, slugs, avisos = [], set(), []
    for n, l in enumerate(linhas, start=2):
        g = lambda c: str(l.get(mapa.get(c, ""), "") or "").strip()
        ref = g("referencia")
        if not ref:
            continue
        preco = ler_preco(g("preco"))
        if preco is None or preco <= 0:
            avisos.append(f"linha {n} ({ref}): sem preço, não publicado")
            continue
        marca = g("marca")
        descricao = g("descricao")
        tipo = normalizar_tipo(g("tipo"), descricao)
        origem = normalizar_origem(g("origem"), descricao)
        cor = g("cor").capitalize()
        impressoras = dividir_impressoras(g("impressoras"), marca)
        if not impressoras:
            avisos.append(f"linha {n} ({ref}): sem impressoras compatíveis")
        nome = descricao or " ".join(x for x in [tipo, marca, ref, cor] if x)
        base = slug(nome if chave(origem)[:6] in chave(nome) else f"{nome} {origem}")[:80].strip("-")
        s, i = base, 2
        while s in slugs:
            s, i = f"{base}-{i}", i + 1
        slugs.add(s)
        stock = ler_inteiro(g("stock"))
        artigos.append({
            "slug": s, "ref": ref, "nome": nome, "marca": marca, "tipo": tipo, "cor": cor,
            "origem": origem, "impressoras": impressoras, "preco": preco,
            "em_stock": stock is None or stock > 0, "rendimento": g("rendimento"), "foto_origem": g("foto"),
        })
    for a in avisos:
        print("Aviso:", a)
    return artigos


def ler_links():
    links = {}
    if LINKS.exists():
        for l in csv.DictReader(LINKS.read_text(encoding="utf-8").splitlines(), delimiter=";"):
            links[l["artigo"]] = {"preco": ler_preco(l["preco"]), "link": l["link"]}
    return links


# ---------------------------------------------------------------- fotos
def preparar_foto(a):
    """Copia ou descarrega a foto para img/consumiveis (o endereço do fornecedor nunca fica no site)."""
    f = a["foto_origem"]
    existente = next(IMG.glob(a["slug"] + ".*"), None) if IMG.exists() else None
    if existente:
        return existente.name
    if not f:
        return ""
    IMG.mkdir(parents=True, exist_ok=True)
    ext = (Path(urllib.parse.urlparse(f).path).suffix.lower() or ".jpg")[:5]
    if ext not in (".jpg", ".jpeg", ".png", ".webp"):
        ext = ".jpg"
    destino = IMG / (a["slug"] + ext)
    try:
        if re.match(r"https?://", f):
            req = urllib.request.Request(f, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=20) as r:
                destino.write_bytes(r.read())
        else:
            origem = Path(f) if Path(f).is_absolute() else DADOS / "fotos" / f
            shutil.copyfile(origem, destino)
        return destino.name
    except Exception as erro:  # foto em falta não impede o resto
        print(f"Aviso: foto de {a['ref']} não descarregada ({erro})")
        return ""


def cores_de(cor, tipo):
    k = chave(cor)
    for nome, lista in CORES.items():
        if nome in k:
            return lista
    return ["#2B2724"] if tipo in ("Toner", "Tambor") else ["#2B2724"]


def ilustracao(a):
    """Desenho simples quando não há foto: tinteiro ou toner com a cor."""
    cs = cores_de(a["cor"], a["tipo"])
    if a["tipo"] in ("Toner", "Tambor"):
        faixas = "".join(
            f'<rect x="{40 + i * (120 / len(cs))}" y="92" width="{120 / len(cs)}" height="16" fill="{c}"/>' for i, c in enumerate(cs))
        corpo = (f'<rect x="20" y="70" width="160" height="60" rx="10" fill="#FFFFFF" stroke="#E6DAD1" stroke-width="3"/>'
                 f'<rect x="20" y="70" width="34" height="60" rx="10" fill="#F4ECE6"/>{faixas}')
    else:
        faixas = "".join(
            f'<rect x="62" y="{86 + i * (52 / len(cs))}" width="76" height="{52 / len(cs)}" fill="{c}"/>' for i, c in enumerate(cs))
        corpo = (f'<rect x="50" y="40" width="100" height="120" rx="14" fill="#FFFFFF" stroke="#E6DAD1" stroke-width="3"/>'
                 f'<rect x="80" y="150" width="40" height="18" rx="4" fill="#E6DAD1"/>'
                 f'<rect x="62" y="54" width="76" height="20" rx="4" fill="#F4ECE6"/>{faixas}')
    return (f'<svg class="ilustracao" viewBox="0 0 200 200" role="img" aria-label="{e(a["tipo"])} {e(a["cor"])}">'
            f'<circle cx="100" cy="100" r="92" fill="#FCE3D6"/>{corpo}</svg>')


# ---------------------------------------------------------------- moldes
ICONE_WHATS = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 11.5a8.5 8.5 0 0 1-12.6 7.4L3 20l1.2-4.2A8.5 8.5 0 1 1 20 11.5z"/></svg>'


def cabeca(p, titulo, descricao, extra=""):
    return f"""<!doctype html>
<html lang="pt-PT">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(titulo)}</title>
<meta name="description" content="{e(descricao)}">
<meta property="og:title" content="{e(titulo)}">
<meta property="og:description" content="{e(descricao)}">
<link rel="icon" href="{p}img/logo-pcinfor.png">
<link rel="stylesheet" href="{p}style.css">
{extra}</head>
<body class="com-barra">

<header class="topo">
  <div class="wrap">
    <a class="logo" href="{p}index.html"><img src="{p}img/logo-pcinfor.png" alt="PCinfor, informática para todos" width="220" height="76"></a>
    <nav class="menu" aria-label="Principal">
      <a class="link-sec" href="{p}index.html#equipamentos">Equipamentos</a>
      <a class="link-sec" href="{p}consumiveis/index.html">Tinteiros e toners</a>
      <a class="link-sec" href="{p}index.html#contactos">Contactos</a>
      <a class="pill-tel" href="https://wa.me/{WHATS}" target="_blank" rel="noopener">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 11.5a8.5 8.5 0 0 1-12.6 7.4L3 20l1.2-4.2A8.5 8.5 0 1 1 20 11.5z"/></svg>963 401 241 <span class="ast">**</span></a>
    </nav>
  </div>
</header>

<main>
"""


def rodape(p, barra):
    return f"""
</main>

<footer class="rodape">
  <div class="wrap">
    <div class="rodape-topo">
      <img src="{p}img/logo-pcinfor.png" alt="PCinfor" width="160" height="56">
      <nav class="rodape-links" aria-label="Rodapé">
        <a href="{p}index.html#equipamentos">Equipamentos</a>
        <a href="{p}consumiveis/index.html">Tinteiros e toners</a>
        <a href="{p}index.html#servicos">Serviços</a>
        <a href="{p}index.html#contactos">Contactos</a>
        <a href="{p}condicoes/index.html">Condições de venda</a>
        <a href="{p}privacidade/index.html">Privacidade</a>
        <a href="https://www.facebook.com/Pcinfor.pt/" target="_blank" rel="noopener">Facebook</a>
        <a href="https://www.instagram.com/pcinforinformticaparatodos/" target="_blank" rel="noopener">Instagram</a>
      </nav>
    </div>
    <div class="rodape-legal">
      <a class="livro" href="https://www.livroreclamacoes.pt/Inicio/" target="_blank" rel="noopener">
        <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 4h11a3 3 0 0 1 3 3v13H7a3 3 0 0 1-3-3z"/><path d="M4 17a3 3 0 0 1 3-3h11"/></svg>
        <span><strong>Livro de Reclamações Eletrónico</strong><small>www.livroreclamacoes.pt</small></span>
      </a>
      <p>Em caso de litígio, o consumidor pode recorrer ao <strong>CICAP – Centro de Informação de Consumo e Arbitragem do Porto</strong> (<a href="https://www.cicap.pt" target="_blank" rel="noopener">www.cicap.pt</a>). Mais informação no Portal do Consumidor (<a href="https://www.consumidor.gov.pt" target="_blank" rel="noopener">www.consumidor.gov.pt</a>).</p>
      <div class="contactos-legais">
        <p>Rua da Alegria 1035, 4000-048 Porto</p>
        <p>Telefone: (+351) 22 201 24 25 <span class="ast">*</span></p>
        <p>Telefone/WhatsApp: (+351) 963 401 241 <span class="ast">**</span></p>
        <p>geral@pcinfor.pt</p>
        <p class="nota-chamadas">* Chamada para a rede fixa nacional<br>** Chamada para a rede móvel nacional</p>
      </div>
    </div>
    <div class="legal">
      <span>PCinfor® é uma marca de PL Resende – Tecnologias de Informação, Lda. · Sede: Rua da Alegria 1035, 4000-048 Porto · Capital social: 5.000€ · Matriculada na Conservatória do Registo Comercial do Porto sob o número único de matrícula e de pessoa coletiva 508239052</span>
      <span>Loja: Rua da Alegria 1035, 4000-048 Porto · Dias úteis 09:00–13:00 · 14:00–18:00</span>
    </div>
  </div>
</footer>

{barra}
</body>
</html>
"""


def foto_html(a, p, classe=""):
    if a.get("foto"):
        return f'<img{classe} src="{p}img/consumiveis/{e(a["foto"])}" alt="{e(a["nome"])}" loading="lazy">'
    return ilustracao(a)


def etiquetas(a):
    origem = '<span class="etiqueta forte">Original</span>' if a["origem"] == "Original" else '<span class="etiqueta forte">Compatível</span>'
    disp = '<span class="etiqueta ok">Em stock</span>' if a["em_stock"] else '<span class="etiqueta">Por encomenda</span>'
    return origem + disp


def cartao(a, p):
    imp = a["impressoras"]
    para = ", ".join(imp[:2]) + (f" e mais {len(imp) - 2}" if len(imp) > 2 else "")
    return f"""<a class="item-consumivel" href="{p}consumiveis/{a['slug']}/index.html">
  <span class="item-foto">{foto_html(a, p)}</span>
  <span class="etiquetas">{etiquetas(a)}</span>
  <span class="item-nome">{e(a['nome'])}</span>
  <span class="item-ref">Ref. {e(a['ref'])}</span>
  <span class="item-para">{('Para ' + e(para)) if imp else ''}</span>
  <span class="item-preco">{preco_txt(a['preco'])}</span>
</a>"""


def pesquisa_form(p, valor=""):
    return f"""<form class="pesquisa" action="{p}consumiveis/index.html" method="get" role="search">
  <label for="q" class="sr">Impressora ou referência</label>
  <input id="q" name="q" type="search" value="{e(valor)}" placeholder="Ex.: HP DeskJet 2720, Brother HL-L2350 ou 305XL" autocomplete="off" enterkeyhint="search">
  <button class="btn btn-comprar" type="submit">Procurar</button>
</form>"""


# ---------------------------------------------------------------- páginas
def pagina_artigo(a, artigos, por_impressora, links):
    p = "../../"
    preco = preco_txt(a["preco"])
    link = links.get(a["slug"], {})
    link_ok = link.get("link") if link.get("preco") == a["preco"] else ""
    msg = wa(f"Olá! Quero o {a['nome']} (ref. {a['ref']}) por {preco}. Está disponível?")
    if link_ok and a["em_stock"]:
        botoes = (f'<a class="btn btn-comprar" href="{e(link_ok)}" target="_blank" rel="noopener">Comprar</a>'
                  f'<a class="btn btn-whats" href="{msg}" target="_blank" rel="noopener">{ICONE_WHATS}Falar no WhatsApp</a>')
        barra = (f'<div class="barra-movel"><a class="btn btn-comprar" href="{e(link_ok)}" target="_blank" rel="noopener">Comprar {preco}</a>'
                 f'<a class="btn btn-whats" href="{msg}" target="_blank" rel="noopener">WhatsApp</a></div>')
        nota = "Pagamento por MB WAY, Multibanco ou cartão. Levantamento grátis na loja, entrega rápida no Grande Porto por 4,95€, ou envio para Portugal continental por 3,95€ (Açores e Madeira 19,90€)."
    else:
        botoes = f'<a class="btn btn-comprar" href="{msg}" target="_blank" rel="noopener">{ICONE_WHATS}Encomendar no WhatsApp</a>'
        barra = f'<div class="barra-movel"><a class="btn btn-comprar" href="{msg}" target="_blank" rel="noopener">Encomendar · {preco}</a></div>'
        nota = ("Diga-nos no WhatsApp e confirmamos a disponibilidade e o prazo." if not a["em_stock"]
                else "Encomende pelo WhatsApp. Levantamento na loja do Porto ou envio combinado.")
    imp_links = "".join(
        f'<li><a href="{p}consumiveis/impressora/{slug(i)}/index.html">{e(i)}</a></li>' for i in a["impressoras"])
    linhas = [("Referência", a["ref"]), ("Marca", a["marca"]), ("Tipo", a["tipo"]), ("Cor", a["cor"]),
              ("Rendimento", a["rendimento"]),
              ("Origem", "Original da marca" if a["origem"] == "Original" else "Compatível (não original)"),
              ("Disponibilidade", "Em stock" if a["em_stock"] else "Por encomenda"),
              ("Preço", f"<strong>{preco}</strong> · IVA incluído")]
    ficha = "".join(f'<tr><th scope="row">{k}</th><td>{v if k == "Preço" else e(v)}</td></tr>' for k, v in linhas if v)
    # Outros consumíveis para as mesmas impressoras
    rel, vistos = [], {a["slug"]}
    for i in a["impressoras"]:
        for o in por_impressora.get(chave(i), {}).get("artigos", []):
            if o["slug"] not in vistos:
                vistos.add(o["slug"])
                rel.append(o)
    rel = rel[:8]
    rel_html = ""
    if rel:
        rel_html = f"""
<section class="seccao" style="padding-top:0">
  <div class="wrap">
    <div class="seccao-titulo"><div class="kicker">Para a mesma impressora</div><h2>Também lhe pode interessar.</h2></div>
    <div class="grelha-consumiveis">{''.join(cartao(o, p) for o in rel)}</div>
  </div>
</section>"""
    aviso_marca = ""
    if a["origem"] != "Original" and a["marca"]:
        aviso_marca = (f'<p class="nota-marca">Consumível compatível, não fabricado pela {e(a["marca"])}. '
                       f'O nome da marca e dos modelos serve só para indicar com que impressoras funciona.</p>')
    para = a["impressoras"][:3]
    sub = ("Para " + ", ".join(para) + (" e outras" if len(a["impressoras"]) > 3 else "")) if para else ""
    desc = f"{a['nome']} por {preco}, IVA incluído. {sub}. PCinfor, Rua da Alegria 1035, Porto."
    corpo = f"""
<section class="hero">
  <div class="wrap">
    <div class="hero-texto">
      <a class="link-detalhes" href="{p}consumiveis/index.html">← Todos os tinteiros e toners</a>
      <div class="etiquetas">{etiquetas(a)}<span class="etiqueta">{e(a['tipo'])}</span></div>
      <h1 class="h1-artigo">{e(a['nome'])}</h1>
      <div class="sub-artigo">Ref. {e(a['ref'])}{(' · ' + e(a['rendimento'])) if a['rendimento'] else ''}</div>
      <p class="lead">{e(sub) + '.' if sub else ''}</p>
      <div class="cartao-preco">
        <div>
          <div class="preco-rotulo">IVA incluído</div>
          <div class="preco">{preco}</div>
        </div>
        <div class="botoes">{botoes}</div>
      </div>
      <p class="nota-pagamento">{nota}</p>
    </div>
    <figure class="hero-foto foto-consumivel">{foto_html(a, p)}</figure>
  </div>
</section>

<section class="seccao">
  <div class="wrap duas-colunas">
    <div>
      <div class="seccao-titulo"><div class="kicker">Impressoras compatíveis</div><h2>Funciona nestas impressoras.</h2></div>
      <ul class="lista-impressoras">{imp_links}</ul>
      <p class="nota-pagamento" style="margin-top:16px">Não vê a sua impressora? <a href="{wa(f'Olá! Tenho a impressora ... Serve o {a["nome"]} (ref. {a["ref"]})?')}" target="_blank" rel="noopener">Pergunte-nos no WhatsApp</a> e confirmamos.</p>
    </div>
    <div>
      <div class="seccao-titulo"><div class="kicker">Ficha</div><h2>Características</h2></div>
      <div class="specs-caixa"><table class="specs"><tbody>{ficha}</tbody></table></div>
      {aviso_marca}
    </div>
  </div>
</section>
{rel_html}
"""
    return cabeca(p, f"{a['nome']} | PCinfor", desc) + corpo + rodape(p, barra)


def pagina_impressora(nome, arts):
    p = "../../../"
    arts = sorted(arts, key=lambda a: (a["tipo"], a["origem"] != "Compatível", a["preco"]))
    desc = f"Tinteiros e toners para a {nome}, originais e compatíveis, com preço e stock. PCinfor, Porto."
    msg = wa(f"Olá! Preciso de consumíveis para a impressora {nome}.")
    corpo = f"""
<section class="hero hero-curto">
  <div class="wrap">
    <div class="hero-texto">
      <a class="link-detalhes" href="{p}consumiveis/index.html">← Todos os tinteiros e toners</a>
      <div class="kicker">Consumíveis para a sua impressora</div>
      <h1 class="h1-artigo">{e(nome)}</h1>
      <p class="lead">{len(arts)} {'artigo serve' if len(arts) == 1 else 'artigos servem'} nesta impressora. Escolha o seu e compre online ou fale connosco.</p>
    </div>
  </div>
</section>
<section class="seccao">
  <div class="wrap">
    <div class="grelha-consumiveis">{''.join(cartao(a, p) for a in arts)}</div>
    <div class="em-breve">
      <span>Dúvidas sobre qual escolher? Dizemos-lhe qual serve e quanto rende.</span>
      <a href="{msg}" target="_blank" rel="noopener" style="font-weight:600">Perguntar no WhatsApp</a>
    </div>
  </div>
</section>
"""
    barra = f'<div class="barra-movel"><a class="btn btn-whats" href="{msg}" target="_blank" rel="noopener">{ICONE_WHATS}Perguntar no WhatsApp</a></div>'
    return cabeca(p, f"Tinteiros e toners para {nome} | PCinfor", desc) + corpo + rodape(p, barra)


def pagina_catalogo(artigos, impressoras):
    p = "../"
    marcas = sorted({a["marca"] for a in artigos if a["marca"]})
    opc_marcas = "".join(f'<option value="{e(m)}">{e(m)}</option>' for m in marcas)
    msg = wa("Olá! Procuro um tinteiro/toner para a minha impressora: ...")
    corpo = f"""
<section class="hero hero-curto">
  <div class="wrap">
    <div class="hero-texto" style="flex-basis:100%">
      <div class="kicker">Tinteiros e toners</div>
      <h1>Encontre o consumível certo <span class="laranja">para a sua impressora.</span></h1>
      <p class="lead" style="max-width:44rem">Escreva o modelo da impressora ou a referência do tinteiro ou toner. Temos originais e compatíveis, e compatíveis custam bastante menos.</p>
      {pesquisa_form(p)}
      <div class="filtros" role="group" aria-label="Filtros">
        <select id="f-tipo" aria-label="Tipo"><option value="">Tinteiros e toners</option><option value="Tinteiro">Só tinteiros</option><option value="Toner">Só toners</option></select>
        <select id="f-origem" aria-label="Original ou compatível"><option value="">Originais e compatíveis</option><option value="Original">Só originais</option><option value="Compatível">Só compatíveis</option></select>
        <select id="f-marca" aria-label="Marca"><option value="">Todas as marcas</option>{opc_marcas}</select>
      </div>
    </div>
  </div>
</section>

<section class="seccao" style="padding-top:40px">
  <div class="wrap">
    <div id="sugestoes" class="sugestoes" hidden></div>
    <p id="contagem" class="contagem" aria-live="polite"></p>
    <div id="resultados" class="grelha-consumiveis"></div>
    <div class="botoes" style="justify-content:center;margin-top:24px"><button id="mais" class="btn btn-whats" type="button" hidden>Mostrar mais</button></div>
    <noscript><p>Para pesquisar, ative o JavaScript ou <a href="{msg}">fale connosco no WhatsApp</a>.</p></noscript>
    <div class="em-breve">
      <span>Não encontra a sua impressora ou o seu consumível? Arranjamos quase tudo.</span>
      <a href="{msg}" target="_blank" rel="noopener" style="font-weight:600">Pergunte-nos no WhatsApp</a>
    </div>
  </div>
</section>

<section class="seccao" style="padding-top:0">
  <div class="wrap">
    <div class="seccao-titulo"><div class="kicker">Como comprar</div><h2>Simples, como deve ser.</h2></div>
    <div class="passos">
      <div class="passo"><span class="n">1</span><div><h3>Procure a impressora</h3><p>O modelo está numa etiqueta à frente ou por cima da impressora.</p></div></div>
      <div class="passo"><span class="n">2</span><div><h3>Pague ou pergunte</h3><p>Pague por link com MB WAY, Multibanco ou cartão, ou fale connosco no WhatsApp.</p></div></div>
      <div class="passo"><span class="n">3</span><div><h3>Levante ou receba</h3><p>Levante na loja da Rua da Alegria ou combine o envio.</p></div></div>
    </div>
  </div>
</section>
<script src="dados.js"></script>
<script src="pesquisa.js"></script>
"""
    barra = f'<div class="barra-movel"><a class="btn btn-whats" href="{msg}" target="_blank" rel="noopener">{ICONE_WHATS}Perguntar no WhatsApp</a></div>'
    desc = "Tinteiros e toners originais e compatíveis para HP, Canon, Epson, Brother e outras marcas. Pesquise pelo modelo da impressora. PCinfor, Porto."
    return cabeca(p, "Tinteiros e toners | PCinfor", desc) + corpo + rodape(p, barra)


# ---------------------------------------------------------------- principal
def main():
    origem = Path(sys.argv[1]) if len(sys.argv) > 1 else DADOS / "consumiveis.csv"
    artigos = ler_artigos(origem)
    links = ler_links()
    for a in artigos:
        a["foto"] = preparar_foto(a)

    por_impressora = {}
    for a in artigos:
        for i in a["impressoras"]:
            ent = por_impressora.setdefault(chave(i), {"nome": i, "artigos": []})
            ent["artigos"].append(a)
    # Um só nome por impressora (a primeira grafia encontrada)
    for a in artigos:
        a["impressoras"] = list(dict.fromkeys(por_impressora[chave(i)]["nome"] for i in a["impressoras"]))

    # Limpa as páginas geradas antes (mantém pesquisa.js)
    if SAIDA.exists():
        for d in SAIDA.iterdir():
            if d.is_dir():
                shutil.rmtree(d)
    SAIDA.mkdir(exist_ok=True)

    for a in artigos:
        d = SAIDA / a["slug"]
        d.mkdir(parents=True)
        (d / "index.html").write_text(pagina_artigo(a, artigos, por_impressora, links), encoding="utf-8")

    slugs_imp = set()
    for ent in por_impressora.values():
        s = slug(ent["nome"])
        if s in slugs_imp:
            continue
        slugs_imp.add(s)
        d = SAIDA / "impressora" / s
        d.mkdir(parents=True)
        (d / "index.html").write_text(pagina_impressora(ent["nome"], ent["artigos"]), encoding="utf-8")

    dados = {
        "artigos": [{
            "s": a["slug"], "r": a["ref"], "n": a["nome"], "m": a["marca"], "t": a["tipo"], "c": a["cor"],
            "o": a["origem"], "i": a["impressoras"], "p": a["preco"], "e": a["em_stock"],
            "f": ("../img/consumiveis/" + a["foto"]) if a["foto"] else "", "g": "" if a["foto"] else ilustracao(a),
        } for a in artigos],
        "impressoras": sorted(({"n": v["nome"], "s": slug(v["nome"]), "q": len(v["artigos"])} for v in por_impressora.values()),
                              key=lambda x: x["n"].lower()),
    }
    (SAIDA / "dados.js").write_text("window.CONSUMIVEIS = " + json.dumps(dados, ensure_ascii=False, separators=(",", ":")) + ";\n",
                                    encoding="utf-8")
    (SAIDA / "index.html").write_text(pagina_catalogo(artigos, por_impressora), encoding="utf-8")

    # Lista para o script dos links de pagamento
    with (DADOS / "artigos_para_links.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["artigo", "nome", "preco", "pagina"])
        for a in artigos:
            w.writerow([a["slug"], a["nome"], f"{a['preco']:.2f}", f"{SITE}/consumiveis/{a['slug']}/"])

    sem_link = [a for a in artigos if links.get(a["slug"], {}).get("preco") != a["preco"]]
    print(f"{len(artigos)} artigos, {len(slugs_imp)} impressoras. Sem link de pagamento (ou preço mudou): {len(sem_link)}.")


if __name__ == "__main__":
    main()
