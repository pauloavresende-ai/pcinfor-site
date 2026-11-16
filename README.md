# Website PCinfor (protótipo)

Site estático, sem base de dados nem plugins, pronto para o GitHub Pages.

## Estrutura

- `index.html`: página inicial (Black Friday, equipamentos, serviços, como comprar, contactos)
- `equipamentos/pack-dell-34/index.html`: página do Pack Dell OptiPlex 3070 + monitor 34″
- `style.css`: imagem PCinfor (Poppins, laranja #E4521F, fundos pêssego)
- `img/`: logótipo e fotos

Cada equipamento novo é uma pasta em `equipamentos/<nome-curto>/`. O endereço fica fixo, por isso o QR da montra pode ser impresso e gravado no vídeo sem medo de mudar:

- Pack Dell: `https://www.pcinfor.pt/equipamentos/pack-dell-34/`
- HP EliteBook 840 G7: `https://www.pcinfor.pt/equipamentos/hp-elitebook-840-g7/`
- HP EliteBook 840 G7 i7: `https://www.pcinfor.pt/equipamentos/hp-elitebook-840-g7-i7/`
- HP EliteBook 650 G9: `https://www.pcinfor.pt/equipamentos/hp-elitebook-650-g9/`

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

## Tinteiros e toners (`consumiveis/`)

Gerado a partir de uma lista. Não editar as páginas à mão.

1. Pôr a lista em `dados/consumiveis.csv` (ou passar um .xlsx): colunas `referencia;descricao;marca;tipo;cor;origem;impressoras;preco;stock;rendimento;foto`. Na coluna `impressoras`, modelos separados por vírgula e famílias por `|` (ex.: `DeskJet 2710, 2720 | ENVY 6020`).
2. `python3 ferramentas/gerar_consumiveis.py [lista]` cria o catálogo com pesquisa (`consumiveis/index.html`), uma página por artigo e uma página por impressora.
3. Colunas de fornecedor, custo ou preço de compra são sempre ignoradas. As fotos são copiadas para `img/consumiveis/`, para o endereço do fornecedor nunca aparecer no site.
4. Links de pagamento: `STRIPE_API_KEY=... python3 ferramentas/criar_links_consumiveis.py` cria um link por artigo (quantidade 1 a 10; loja grátis, Grande Porto 4,95€, continente 3,95€, Açores e Madeira 19,90€) em `dados/links_pagamento_consumiveis.csv`, e depois volta-se a correr o gerador. Sem link (ou com o preço mudado), a página mostra "Encomendar no WhatsApp".
