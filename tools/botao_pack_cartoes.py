"""Põe o botão "Pack c/ monitor desde X€" nos cartões de computadores da página inicial.

Lê o preço mais baixo e a âncora do pack no botão .btn-conjunto da página de cada
computador (equipamentos/<slug>/index.html). Corre de novo sempre que um preço de
pack mudar ou entrar um computador novo: substitui os botões já existentes.
"""
import re, pathlib, sys

raiz = pathlib.Path(__file__).resolve().parent.parent
idx = raiz / "index.html"
html = idx.read_text(encoding="utf-8")

ini = html.index('<div class="categoria" id="computadores">')
fim = html.index('<div class="categoria"', ini + 10)
bloco = html[ini:fim]

ICONE = ('<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
         'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2" y="3" width="20" height="13" rx="2"/>'
         '<path d="M8 21h8M12 16v5"/></svg>')

def trata(m):
    art = m.group(0)
    art = re.sub(r'\n\s*<a class="btn btn-pack[^\n]*', '', art)
    nome = re.search(r"<h3[^>]*>(.*?)</h3>", art).group(1)
    slug = re.search(r'href="equipamentos/([^/]+)/index.html"', art).group(1)
    pag = (raiz / "equipamentos" / slug / "index.html").read_text(encoding="utf-8")
    c = re.search(r'<a class="btn-conjunto" href="(#pack[^"]*)".*?desde (\d+)\s*€', pag)
    if not c or "com monitor" not in pag[c.start():c.end()]:
        print("sem packs:", slug); return art
    ancora, preco = c.group(1), c.group(2)
    botao = (f'\n          <a class="btn btn-pack btn-pequeno" href="equipamentos/{slug}/index.html{ancora}" '
             f'aria-label="Ver os packs do {nome} com monitor, desde {preco}€">{ICONE}Pack c/ monitor desde {preco}€</a>')
    art = re.sub(r'(<a class="btn btn-whats btn-pequeno"[^\n]*)', lambda w: w.group(1) + botao, art, count=1)
    print(f"{slug}: desde {preco}€ -> {ancora}")
    return art

novo = re.sub(r'<article class="produto-destaque">.*?</article>', trata, bloco, flags=re.S)
idx.write_text(html[:ini] + novo + html[fim:], encoding="utf-8")
