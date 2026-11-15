#!/usr/bin/env python3
"""Cria no Stripe um link de pagamento por tinteiro/toner, com portes fixos.

Uso:
    STRIPE_API_KEY=rk_... python3 ferramentas/criar_links_consumiveis.py
    python3 ferramentas/gerar_consumiveis.py      # volta a gerar as páginas com os links

Lê dados/artigos_para_links.csv (feito pelo gerador) e escreve
dados/links_pagamento_consumiveis.csv (artigo;preco;link).
Só cria links para artigos novos ou com o preço mudado; o link antigo é desativado.

Entrega (o cliente escolhe no pagamento):
    Levantar na loja (Porto)  0€      tarifa já existente
    Envio Portugal continental  PORTES_CONTINENTE  criada uma vez por este script
    Açores e Madeira           19,90€  tarifa já existente
O cliente pode mudar a quantidade (1 a 10).
"""
import base64
import csv
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ENTRADA = RAIZ / "dados" / "artigos_para_links.csv"
LINKS = RAIZ / "dados" / "links_pagamento_consumiveis.csv"
SITE = "https://pauloavresende-ai.github.io/pcinfor-site"

PORTES_CONTINENTE = 395  # cêntimos, IVA incluído
TARIFA_LOJA = "shr_1Ublvk34kwTMi5VOaGBEcRKa"
TARIFA_ILHAS = "shr_1Ublvl34kwTMi5VOQwHPtlWs"

CHAVE = os.environ.get("STRIPE_API_KEY") or sys.exit("Falta a variável STRIPE_API_KEY.")


def stripe(metodo, caminho, dados=None):
    corpo = urllib.parse.urlencode(dados or {}).encode() if metodo == "POST" else None
    url = "https://api.stripe.com/v1/" + caminho
    if metodo == "GET" and dados:
        url += "?" + urllib.parse.urlencode(dados)
    req = urllib.request.Request(url, data=corpo, method=metodo)
    req.add_header("Authorization", "Basic " + base64.b64encode(f"{CHAVE}:".encode()).decode())
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as erro:
        sys.exit(f"Stripe recusou {caminho}: {erro.read().decode()}")


def tarifa_continente():
    for t in stripe("GET", "shipping_rates", {"active": "true", "limit": 100})["data"]:
        if t.get("metadata", {}).get("pcinfor") == f"consumiveis-continente-{PORTES_CONTINENTE}":
            return t["id"]
    return stripe("POST", "shipping_rates", {
        "display_name": "Envio Portugal continental",
        "type": "fixed_amount",
        "fixed_amount[amount]": PORTES_CONTINENTE,
        "fixed_amount[currency]": "eur",
        "tax_behavior": "inclusive",
        "delivery_estimate[minimum][unit]": "business_day", "delivery_estimate[minimum][value]": 1,
        "delivery_estimate[maximum][unit]": "business_day", "delivery_estimate[maximum][value]": 3,
        "metadata[pcinfor]": f"consumiveis-continente-{PORTES_CONTINENTE}",
    })["id"]


def main():
    artigos = list(csv.DictReader(ENTRADA.read_text(encoding="utf-8").splitlines(), delimiter=";"))
    links = {}
    if LINKS.exists():
        links = {l["artigo"]: l for l in csv.DictReader(LINKS.read_text(encoding="utf-8").splitlines(), delimiter=";")}
    continente = tarifa_continente()
    novos = 0
    for a in artigos:
        atual = links.get(a["artigo"])
        if atual and f"{float(atual['preco']):.2f}" == a["preco"]:
            continue
        if atual and atual.get("id"):
            stripe("POST", f"payment_links/{atual['id']}", {"active": "false"})
        cents = round(float(a["preco"]) * 100)
        prod = stripe("POST", "products", {"name": a["nome"], "url": a["pagina"], "metadata[slug]": a["artigo"]})["id"]
        price = stripe("POST", "prices", {"product": prod, "currency": "eur", "unit_amount": cents, "tax_behavior": "inclusive"})["id"]
        link = stripe("POST", "payment_links", {
            "line_items[0][price]": price, "line_items[0][quantity]": 1,
            "line_items[0][adjustable_quantity][enabled]": "true",
            "line_items[0][adjustable_quantity][minimum]": 1,
            "line_items[0][adjustable_quantity][maximum]": 10,
            "billing_address_collection": "required",
            "phone_number_collection[enabled]": "true",
            "tax_id_collection[enabled]": "true",
            "shipping_address_collection[allowed_countries][0]": "PT",
            "shipping_options[0][shipping_rate]": TARIFA_LOJA,
            "shipping_options[1][shipping_rate]": continente,
            "shipping_options[2][shipping_rate]": TARIFA_ILHAS,
            "after_completion[type]": "redirect",
            "after_completion[redirect][url]": f"{SITE}/obrigado/",
            "metadata[slug]": a["artigo"],
        })
        links[a["artigo"]] = {"artigo": a["artigo"], "preco": a["preco"], "link": link["url"], "id": link["id"]}
        novos += 1
        print(a["artigo"], link["url"])
    with LINKS.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["artigo", "preco", "link", "id"], delimiter=";", extrasaction="ignore")
        w.writeheader()
        for l in links.values():
            w.writerow(l)
    print(f"{novos} links novos. Agora: python3 ferramentas/gerar_consumiveis.py")


if __name__ == "__main__":
    main()
