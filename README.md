# Website PCinfor (protótipo)

Site estático, sem base de dados nem plugins, pronto para o GitHub Pages.

## Estrutura

- `index.html`: página inicial (Black Friday, equipamentos, serviços, como comprar, contactos)
- `equipamentos/pack-dell-34/index.html`: endereço antigo do Pack Dell (QR da montra); redireciona para a caixa do pack em `dell-optiplex-3070-micro/#pack`
- `style.css`: imagem PCinfor (Poppins, laranja #E4521F, fundos pêssego)
- `img/`: logótipo e fotos

## Categorias

A lista de equipamentos da página inicial está dividida em três categorias, cada uma com o seu bloco em `index.html`:

- Portáteis: `<div class="categoria" id="portateis">` (endereço curto `https://www.pcinfor.pt/portateis/`)
- Computadores (mini PC e secretária): `id="computadores"` (`https://www.pcinfor.pt/computadores/`)
- Monitores (só monitores): `id="monitores"` (`https://www.pcinfor.pt/monitores/`)
- Packs (computador + monitor juntos): `id="packs"` (`https://www.pcinfor.pt/packs/`)

Um equipamento novo entra como `<article class="produto-destaque">` dentro do `<div class="lista-produtos">` da sua categoria. Ao acrescentar ou retirar, atualizar o número no botão da categoria (`<nav class="categorias">`) e o texto "N disponíveis" do bloco.

Cada equipamento novo é uma pasta em `equipamentos/<nome-curto>/`. O endereço fica fixo, por isso o QR da montra pode ser impresso e gravado no vídeo sem medo de mudar:

- Pack Dell: `https://www.pcinfor.pt/equipamentos/pack-dell-34/` (redireciona para `dell-optiplex-3070-micro/#pack`)
- HP EliteBook 840 G7: `https://www.pcinfor.pt/equipamentos/hp-elitebook-840-g7/`
- HP EliteBook 840 G7 i7: `https://www.pcinfor.pt/equipamentos/hp-elitebook-840-g7-i7/`
- HP EliteBook 650 G9: `https://www.pcinfor.pt/equipamentos/hp-elitebook-650-g9/`
- Lenovo ThinkCentre M700 Tiny: `https://www.pcinfor.pt/equipamentos/lenovo-thinkcentre-m700-tiny/`
- Dell OptiPlex 3070 Micro (só o computador do pack): `https://www.pcinfor.pt/equipamentos/dell-optiplex-3070-micro/`
- HP ProDesk 400 G4 SFF: `https://www.pcinfor.pt/equipamentos/hp-prodesk-400-g4-sff/`
- HP ProDesk 400 G4 Mini: `https://www.pcinfor.pt/equipamentos/hp-prodesk-400-g4-mini/`
- HP Z2 G5 SFF: `https://www.pcinfor.pt/equipamentos/hp-z2-g5-sff/`
- Monitor Dell C3422WE 34″ (só o monitor do pack): `https://www.pcinfor.pt/equipamentos/dell-c3422we-34/`
- HP ProDesk 600 G6 Tower: `https://www.pcinfor.pt/equipamentos/hp-prodesk-600-g6-tower/`
- Lenovo ThinkStation P520: `https://www.pcinfor.pt/equipamentos/lenovo-thinkstation-p520/`
- Lenovo ThinkStation P520 GTX 1080: `https://www.pcinfor.pt/equipamentos/lenovo-thinkstation-p520-gtx1080/`
- HP Z2 G5 Tower Quadro M4000: `https://www.pcinfor.pt/equipamentos/hp-z2-g5-tower-m4000/`
- HP Z4 G4 Quadro RTX 4000: `https://www.pcinfor.pt/equipamentos/hp-z4-g4-rtx4000/`
- HP Z4 G4 i9 Quadro RTX 4000: `https://www.pcinfor.pt/equipamentos/hp-z4-g4-i9-rtx4000/`
- HP ProDesk 400 G6 Mini: `https://www.pcinfor.pt/equipamentos/hp-prodesk-400-g6-mini/`
- HP ProDesk 400 G6 Mini 16GB: `https://www.pcinfor.pt/equipamentos/hp-prodesk-400-g6-mini-16gb/`
- Monitor HP EliteDisplay E23 G4 23″: `https://www.pcinfor.pt/equipamentos/hp-elitedisplay-e23-g4/`
- Monitor HP EliteDisplay E243m 24″: `https://www.pcinfor.pt/equipamentos/hp-elitedisplay-e243m/`
- Monitor HP EliteDisplay E243d 24″ (dock USB-C): `https://www.pcinfor.pt/equipamentos/hp-elitedisplay-e243d/`
- Monitor HP EliteDisplay E27q G4 27″: `https://www.pcinfor.pt/equipamentos/hp-elitedisplay-e27q-g4/`
- Monitor HP E27d G4 27″ (dock USB-C): `https://www.pcinfor.pt/equipamentos/hp-elitedisplay-e27d-g4/`
- Monitor LG 32UP550-W 32″ 4K (USB-C): `https://www.pcinfor.pt/equipamentos/lg-32up550-w/`
- Monitor Lenovo ThinkVision T32p-20 32″ 4K (dock USB-C): `https://www.pcinfor.pt/equipamentos/lenovo-thinkvision-t32p-20/`

## Packs com monitor

Cada computador tem na sua página uma caixa por monitor (`#pack` para o Dell C3422WE 34″, `#pack-e23` para o HP E23 G4 23″, `#pack-e243m` para o HP E243m 24″, `#pack-e243d` para o HP E243d 24″ com dock USB-C, `#pack-e27q` para o HP E27q G4 27″, `#pack-e27d` para o HP E27d G4 27″ com dock USB-C, `#pack-lg32` para o LG 32UP550-W 32″ 4K, `#pack-t32p` para o Lenovo ThinkVision T32p-20 32″ 4K com dock USB-C), entre os comentários `PACK-MONITOR`, `PACK-E23`, `PACK-E243M`, `PACK-E243D`, `PACK-E27Q`, `PACK-E27D`, `PACK-LG32` e `PACK-T32P`. Na página inicial, a categoria Packs tem uma lista por monitor. Regra: quando entra um monitor novo, cria-se um pack com cada computador à venda (preço = computador + monitor, teclado e rato de oferta, slug Stripe `pack-<computador>-<monitor>`).

Cada pack tem uma imagem combinada (monitor atrás, computador à frente, fundo branco) em `img/packs/pack-<computador>-<monitor>.jpg` (1200×900, caixa do pack) e uma miniatura em `img/packs/mini/` (240×180, listas de packs). Quando entra um computador ou monitor novo: acrescentar a foto e a medida em `tools/gerar_imagens_packs.py` (e o marcador em `tools/ligar_imagens_packs.py`, se for monitor), e correr na raiz do site `python3 tools/gerar_imagens_packs.py` seguido de `python3 tools/ligar_imagens_packs.py`.

## Em falta

- Link de pagamento: na página do produto, colar o link em `LINK_PAGAMENTO` (no fim do ficheiro). Até lá, o botão Comprar mostra um aviso e manda para o WhatsApp.
- Fotos do EliteBook: recortadas e colocadas.
- Regras: "Seminovo · Grade A"; nos destaques só "Testado e com garantia"; os 18 meses de garantia só na ficha técnica.
- Fotos do pack Dell: as imagens oficiais da apresentação do pack.

## Publicar em pcinfor.pt (plano)

1. Criar o repositório `pcinfor-site` na conta pauloavresende-ai e ativar o GitHub Pages.
2. Ficheiro `CNAME` com `www.pcinfor.pt`.
3. No DNS do domínio: `www` em CNAME para `pauloavresende-ai.github.io`, e o domínio sem `www` com os registos A do GitHub Pages.
4. O PrestaShop antigo deixa de estar em pcinfor.pt. Se for para manter, passa para um subdomínio (ex.: `loja.pcinfor.pt`) ou fica em modo de manutenção.
5. Os links antigos do PrestaShop deixam de funcionar: o QR dos vídeos da montra aponta para www.pcinfor.pt, que continua a funcionar.

## Black Friday: preço de referência e packs

- O preço de venda é o "Preço Black Friday". Ao lado aparece riscado o "PVP de referência" (`<div class="preco-antes">`): mesma regra de escalões com +10 pontos percentuais (60%, 50%, 40%, 35%; mesmos mínimos), × 1,23, arredondado para baixo para 9 ou 5. Se der igual ao preço (por causa do mínimo), não se mostra riscado. Pack: soma das duas referências (`<s class="pack-ref">` nas listas). Nunca escrever "preço anterior" ou "antes".
- Todos os packs têm o mesmo formato resumido: caixa na página do computador com selo "Teclado e rato de oferta" (`oferta-pack`), resumo `pack-resumo` (Computador / Monitor / Oferta, a partir das descrições curtas das duas páginas), preço de referência + preço Black Friday e botão.
- Em cada página de computador, junto ao preço, o botão `btn-conjunto` "Leve em conjunto com monitor desde X€" (pack mais barato) salta para essa caixa.
