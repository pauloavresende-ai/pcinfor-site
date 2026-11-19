#!/usr/bin/env python3
"""Gera as imagens combinadas computador + monitor dos packs.

Uso (na raiz do site):  python3 tools/gerar_imagens_packs.py [--monitor slug-monitor] [slug-computador ...]
Saída: img/packs/pack-<computador>-<monitor>.jpg (1200x900, fundo branco, caixa do pack)
       img/packs/mini/pack-<computador>-<monitor>.jpg (240x180, lista de Packs da página inicial).

Para um computador ou monitor novo, acrescentar uma linha em COMPUTADORES ou
MONITORES (foto limpa em img/, sem placa gráfica solta nem selos, e a medida
real em cm) e voltar a correr o script.
"""
import os, sys
from PIL import Image, ImageDraw, ImageFilter

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(RAIZ, "img")
SAIDA = os.path.join(IMG, "packs")
W, H, MARGEM = 1200, 900, 50

# monitor: (foto, altura real com o pé em cm; a altura não engana nas fotos de lado)
MONITORES = {
    "dell-c3422we-34": ("monitor-c3422we-lado.jpg", 53),
    "hp-elitedisplay-e23-g4": ("hp-e23-g4-angulo.jpg", 46),
    "hp-elitedisplay-e243m": ("hp-e243m-frente.jpg", 50),
    "hp-elitedisplay-e243d": ("hp-e243d-angulo.jpg", 50),
    "hp-elitedisplay-e27q-g4": ("hp-e27q-g4-angulo.jpg", 54),
    "hp-elitedisplay-e27d-g4": ("hp-e27d-g4-angulo.jpg", 56),
    "lg-32up550-w": ("lg-32up550-angulo.jpg", 52),
    "lenovo-thinkvision-t32p-20": ("lenovo-t32p-20-angulo.jpg", 55),
}
# computador: (foto, medida real em cm, "altura" ou "largura" a que a medida se refere, recorte opcional (x0,y0,x1,y1) em fração)
COMPUTADORES = {
    "lenovo-thinkcentre-m700-tiny": ("lenovo-m700-tiny-frente.jpg", 18, "altura", None),
    "dell-optiplex-3070-micro": ("minipc-optiplex-3070.jpg", 18, "altura", (0, 0, 0.56, 1)),
    "hp-prodesk-400-g4-mini": ("hp-prodesk-400-g4-mini-direita.jpg", 20, "largura", None),
    "hp-prodesk-400-g4-sff": ("hp-prodesk-400-g4-sff.jpg", 30, "largura", None),
    "hp-prodesk-400-g6-mini": ("hp-prodesk-400-g6-mini-direita.jpg", 20, "largura", None),
    "hp-prodesk-400-g6-mini-16gb": ("hp-prodesk-400-g6-mini-direita.jpg", 20, "largura", None),
    "hp-z2-g5-sff": ("hp-z2-g5-direita.jpg", 36, "largura", None),
    "hp-prodesk-600-g6-tower": ("hp-prodesk-600-g6-direita.jpg", 34, "altura", None),
    "hp-z2-g5-tower-m4000": ("hp-z2-g5-tower-angulo.jpg", 38, "altura", None),
    "hp-z2-g5-tower-rtx2070": ("hp-z2-g5-tower-rtx2070-angulo.jpg", 38, "altura", None),
    "hp-z4-g4-rtx4000": ("hp-z4-g4-angulo-direita.jpg", 42, "altura", None),
    "hp-z4-g4-i9-rtx4000": ("hp-z4-g4-angulo-direita.jpg", 42, "altura", None),
    "lenovo-thinkstation-p520": ("lenovo-p520-direita.jpg", 42, "altura", None),
    "lenovo-thinkstation-p520-gtx1080": ("lenovo-p520-direita.jpg", 42, "altura", None),
    "hp-z2-mini-g5-i9-t1000": ("hp-z2-mini-g5-frente.jpg", 22, "largura", None),
    "lenovo-thinkstation-p620": ("lenovo-p620-angulo.jpg", 44, "altura", None),
}


def recortar(nome, frac=None):
    """Abre a foto, tira o fundo branco (só o ligado às margens) e corta ao conteúdo."""
    im = Image.open(os.path.join(IMG, nome)).convert("RGB")
    if frac:
        w, h = im.size
        im = im.crop((int(frac[0] * w), int(frac[1] * h), int(frac[2] * w), int(frac[3] * h)))
    w, h = im.size
    # máscara: pixels quase brancos ligados às margens = fundo
    marca = im.copy()
    for x, y in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)] + \
                [(x, 0) for x in range(0, w, 8)] + [(x, h - 1) for x in range(0, w, 8)] + \
                [(0, y) for y in range(0, h, 8)] + [(w - 1, y) for y in range(0, h, 8)]:
        if min(marca.getpixel((x, y))) >= 235 and marca.getpixel((x, y)) != (255, 0, 255):
            ImageDraw.floodfill(marca, (x, y), (255, 0, 255), thresh=22)
    alpha = Image.new("L", (w, h), 255)
    px, pa = marca.load(), alpha.load()
    for y in range(h):
        for x in range(w):
            if px[x, y] == (255, 0, 255):
                pa[x, y] = 0
    alpha = alpha.filter(ImageFilter.GaussianBlur(0.8))
    rgba = im.convert("RGBA")
    rgba.putalpha(alpha)
    caixa = alpha.point(lambda v: 255 if v > 40 else 0).getbbox()
    return rgba.crop(caixa)


def compor(comp, mon):
    fm, alt_m = MONITORES[mon]
    fc, medida, eixo, frac = COMPUTADORES[comp]
    m = recortar(fm)
    c = recortar(fc, frac)
    escala = 10.0  # px por cm, provisório; tudo é reescalado no fim
    m = m.resize((round(m.width * alt_m * escala / m.height), round(alt_m * escala)), Image.LANCZOS)
    # o monitor manda na imagem: torres um pouco reduzidas, minis um pouco aumentadas para se verem bem
    presenca = 0.78 if (eixo == "altura" and medida >= 30) else 1.35
    f = medida * escala * presenca / (c.height if eixo == "altura" else c.width)
    c = c.resize((max(1, round(c.width * f)), max(1, round(c.height * f))), Image.LANCZOS)

    deitado = c.width > c.height
    base_m = m.height
    base_c = base_m + round(m.height * 0.05)  # um pouco mais à frente que o monitor
    if deitado:  # mini/SFF deitado à frente, no canto direito do monitor
        cx = m.width - round(c.width * 0.75)
    else:  # torre ou mini de pé ao lado direito, a sobrepor um pouco o monitor
        cx = m.width - round(c.width * 0.35)
    cy = base_c - c.height
    x0, y0 = min(0, cx), min(0, cy)
    x1, y1 = max(m.width, cx + c.width), max(base_m, base_c)
    cena = Image.new("RGBA", (x1 - x0, y1 - y0 + 20), (255, 255, 255, 0))
    cena.alpha_composite(m, (-x0, -y0))
    # sombra suave no chão por baixo do computador
    sombra = Image.new("L", cena.size, 0)
    ImageDraw.Draw(sombra).ellipse((cx - x0 + c.width * 0.02, base_c - y0 - 8, cx - x0 + c.width * 0.98, base_c - y0 + 10), fill=90)
    sombra = sombra.filter(ImageFilter.GaussianBlur(7))
    cena.alpha_composite(Image.merge("RGBA", (Image.new("L", cena.size, 0),) * 3 + (sombra,)))
    cena.alpha_composite(c, (cx - x0, cy - y0))

    k = min((W - 2 * MARGEM) / cena.width, (H - 2 * MARGEM) / cena.height)
    cena = cena.resize((round(cena.width * k), round(cena.height * k)), Image.LANCZOS)
    tela = Image.new("RGBA", (W, H), (255, 255, 255, 255))
    tela.alpha_composite(cena, ((W - cena.width) // 2, (H - cena.height) // 2))
    return tela.convert("RGB")


def main():
    os.makedirs(os.path.join(SAIDA, "mini"), exist_ok=True)
    args = sys.argv[1:]
    mons = list(MONITORES)
    if args[:1] == ["--monitor"]:
        mons, args = [args[1]], args[2:]
    comps = args or list(COMPUTADORES)
    for comp in comps:
        for mon in mons:
            destino = os.path.join(SAIDA, f"pack-{comp}-{mon}.jpg")
            img = compor(comp, mon)
            img.save(destino, "JPEG", quality=82, optimize=True, progressive=True)
            img.resize((240, 180), Image.LANCZOS).save(
                os.path.join(SAIDA, "mini", f"pack-{comp}-{mon}.jpg"), "JPEG", quality=80, optimize=True)
            print(destino, os.path.getsize(destino) // 1024, "KB")


if __name__ == "__main__":
    main()
