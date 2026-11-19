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
- Lenovo ThinkCentre M700 Tiny: `https://www.pcinfor.pt/equipamentos/lenovo-thinkcentre-m700-tiny/`
- HP Z2 G5 SFF: `https://www.pcinfor.pt/equipamentos/hp-z2-g5-sff/`

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
