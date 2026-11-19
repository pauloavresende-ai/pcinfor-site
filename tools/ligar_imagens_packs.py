#!/usr/bin/env python3
"""Põe as imagens combinadas (img/packs/) nas caixas de pack de cada computador
e na lista de Packs da página inicial. Pode correr-se várias vezes."""
import os, re
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# marcador na página do computador, âncora usada na lista, monitor, nome curto
MONITORES = [
    ("PACK-MONITOR", "pack", "dell-c3422we-34", "monitor Dell C3422WE curvo de 34″"),
    ("PACK-E23", "pack-e23", "hp-elitedisplay-e23-g4", "monitor HP EliteDisplay E23 G4 de 23″"),
    ("PACK-E243M", "pack-e243m", "hp-elitedisplay-e243m", "monitor HP EliteDisplay E243m de 24″"),
    ("PACK-E243D", "pack-e243d", "hp-elitedisplay-e243d", "monitor HP EliteDisplay E243d de 24″"),
    ("PACK-E27Q", "pack-e27q", "hp-elitedisplay-e27q-g4", "monitor HP EliteDisplay E27q G4 de 27″"),
    ("PACK-E27D", "pack-e27d", "hp-elitedisplay-e27d-g4", "monitor HP EliteDisplay E27d G4 de 27″"),
    ("PACK-LG32", "pack-lg32", "lg-32up550-w", "monitor LG 32UP550-W de 32″"),
    ("PACK-T32P", "pack-t32p", "lenovo-thinkvision-t32p-20", "monitor Lenovo ThinkVision T32p-20 de 32″"),
]
POR_ANCORA = {a: (mon, nome) for _, a, mon, nome in MONITORES}


def nome_computador(slug):
    t = open(os.path.join(RAIZ, "equipamentos", slug, "index.html"), encoding="utf-8").read()
    return re.search(r"<title>([^·|<]+)", t).group(1).strip()


def paginas():
    n = 0
    for slug in sorted(os.listdir(os.path.join(RAIZ, "equipamentos"))):
        p = os.path.join(RAIZ, "equipamentos", slug, "index.html")
        if not os.path.exists(os.path.join(RAIZ, "img", "packs", f"pack-{slug}-dell-c3422we-34.jpg")):
            continue
        t = open(p, encoding="utf-8").read()
        comp = nome_computador(slug)
        for marca, _, mon, nome in MONITORES:
            ini, fim = f"<!-- {marca}:INICIO -->", f"<!-- {marca}:FIM -->"
            if ini not in t:
                continue
            a, b = t.index(ini), t.index(fim)
            bloco = t[a:b]
            img = (f'<img src="../../img/packs/pack-{slug}-{mon}.jpg" alt="{comp} com o {nome}" '
                   f'width="1200" height="900" loading="lazy">')
            bloco2 = re.sub(r'<img [^>]*>', img, bloco, count=1)
            t = t[:a] + bloco2 + t[b:]
            n += bloco2 != bloco
        open(p, "w", encoding="utf-8").write(t)
    return n


def listas():
    """Lista de Packs da página inicial e listas de packs nas páginas dos monitores."""
    alvos = [("index.html", "equipamentos/", "img/")]
    for slug in sorted(os.listdir(os.path.join(RAIZ, "equipamentos"))):
        alvos.append((f"equipamentos/{slug}/index.html", "../", "../../img/"))
    n = 0
    for rel, pref, img in alvos:
        p = os.path.join(RAIZ, rel)
        t = open(p, encoding="utf-8").read()
        padrao = re.compile(r'<a class="pack-linha" href="' + re.escape(pref) +
                            r'([^/]+)/index.html#([\w-]+)">(?:<img [^>]*>)?')

        def troca(m):
            slug, ancora = m.group(1), m.group(2)
            mon, _ = POR_ANCORA[ancora]
            return (f'{m.group(0).split(">")[0]}><img class="pack-foto" src="{img}packs/mini/pack-{slug}-{mon}.jpg" '
                    f'alt="" width="240" height="180" loading="lazy">')
        t, k = padrao.subn(troca, t)
        n += k
        open(p, "w", encoding="utf-8").write(t)
    return n


if __name__ == "__main__":
    print("caixas:", paginas(), "| linhas da lista:", listas())
