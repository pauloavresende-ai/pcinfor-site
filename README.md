# Site PCinfor · www.pcinfor.pt

Loja online da PCinfor (PL Resende – Tecnologias de Informação, Lda.), Rua da Alegria 1035, Porto. Vende equipamentos profissionais seminovos (portáteis, computadores, All-in-One, monitores e packs computador + monitor) com pagamento online no Stripe, e mostra os serviços da loja (assistência técnica, tinteiros e toners, venda e consultoria).

Este ficheiro é o contexto do site: como foi feito, como está organizado e tudo o que já faz. As regras de trabalho para o Claude estão em [`CLAUDE.md`](CLAUDE.md).

## Índice

1. [Como foi desenvolvido](#1-como-foi-desenvolvido)
2. [Arquitetura e publicação](#2-arquitetura-e-publicação)
3. [Estrutura de pastas](#3-estrutura-de-pastas)
4. [Páginas do site](#4-páginas-do-site)
5. [Funcionalidades](#5-funcionalidades)
6. [Preços](#6-preços)
7. [Pagamentos e encomendas (Stripe e Make)](#7-pagamentos-e-encomendas-stripe-e-make)
8. [Packs computador + monitor](#8-packs-computador--monitor)
9. [Ferramentas (`tools/`)](#9-ferramentas-tools)
10. [Como lançar um equipamento](#10-como-lançar-um-equipamento)
11. [Equipamentos e endereços fixos](#11-equipamentos-e-endereços-fixos)
12. [Fora do repositório](#12-fora-do-repositório)
13. [Pontos em aberto](#13-pontos-em-aberto)

---

## 1. Como foi desenvolvido

O site foi feito de raiz com o Claude, em conversas e PRs, para substituir a loja PrestaShop antiga em pcinfor.pt. É HTML e CSS escritos à mão, sem base de dados, sem plugins e sem passo de compilação. Cada alteração é feita num ramo `claude/...`, entra por PR em `main` e o GitHub Pages publica em poucos minutos.

Cronologia (do histórico git):

| Data | O que entrou |
|---|---|
| 14/11/2026 | Primeira versão: página inicial e 4 equipamentos (Pack Dell, HP EliteBook 840 G7, 840 G7 i7, 650 G9). Informação legal (preço das chamadas, Livro de Reclamações, CICAP, condições de venda, privacidade), rodapé com sede, capital social e matrícula. Saiu o aluguer de impressoras. Página `/obrigado/` depois do pagamento e botões Comprar ligados aos links Stripe. Faixa e banner "Black Friday todos os dias". Portes grátis para o continente até 31 de dezembro. |
| 15 a 17/11 | Ficheiro `CNAME` (`www.pcinfor.pt`). Pagamento sempre online antes do levantamento ou envio; WhatsApp só para dúvidas, a compra é sempre pelo site. |
| 18/11 | Lenovo ThinkCentre M700 Tiny (primeiro equipamento lançado com PR, #2). |
| 19/11 | Dia principal (cerca de 170 commits, PRs #4 a #58): divisão em categorias (Portáteis, Computadores, Monitores, depois Packs e All-in-One); dezenas de equipamentos lançados; 8 monitores com um pack para cada computador; imagens combinadas dos packs; nova margem por escalões (14 equipamentos e 78 packs repreçados, links Stripe novos); barra de categorias fixa no cabeçalho de todas as páginas; PVP de referência riscado, oferta de teclado e rato nos packs e botão "Leve em conjunto"; banner Black Friday em vídeo; packs todos no mesmo formato resumido; ordenação por preço e destaque "Packs desde"; botão "Pack c/ monitor desde X€" nos cartões; selo "Últimas unidades"; assinatura de email PCinfor alojada no site (#58). |

## 2. Arquitetura e publicação

- **Site estático** no **GitHub Pages**, repositório `pauloavresende-ai/pcinfor-site`, ramo `main`, raiz do repositório.
- `CNAME` com `www.pcinfor.pt`. No DNS: `www` em CNAME para `pauloavresende-ai.github.io` e o domínio sem `www` com os 4 registos A do GitHub Pages (185.199.108.153, .109.153, .110.153, .111.153).
- `.nojekyll` (vazio): o Pages serve os ficheiros tal como estão, sem passar pelo Jekyll.
- Sem JavaScript de terceiros nem fontes externas: a letra Poppins (300 a 700) está em `fonts/` e é carregada por `@font-face` no `style.css`. O JavaScript é só nosso: o do botão Comprar das páginas de produto, o que mantém o vídeo do banner a rodar e a pesquisa de artigos (`pesquisa.js`).
- Todas as páginas partilham o mesmo `style.css` (imagem PCinfor: Poppins, laranja `#E4521F`, fundos pêssego, cores em variáveis no topo).
- Os links internos usam caminhos relativos para `index.html` (ex.: `../../index.html#packs`), por isso o site funciona também aberto a partir dos ficheiros.
- O PrestaShop antigo deixou de estar em pcinfor.pt; os links antigos deixaram de funcionar. Os QR da montra apontam para `www.pcinfor.pt` e para endereços fixos de equipamentos, que não mudam.

## 3. Estrutura de pastas

```
index.html              página inicial (todas as categorias e cartões)
style.css               estilos de todo o site
pesquisa.js             pesquisa de artigos do cabeçalho (todas as páginas)
CNAME, .nojekyll        GitHub Pages
equipamentos/<slug>/    uma página por equipamento (endereço fixo, usado em QR)
equipamentos/pack-dell-34/   endereço antigo do Pack Dell, redireciona para dell-optiplex-3070-micro/#pack
portateis/ computadores/ all-in-one/ monitores/ packs/
                        endereços curtos que redirecionam para a categoria em index.html
condicoes/              condições de venda
privacidade/            política de privacidade
obrigado/               página para onde o Stripe manda o cliente depois de pagar (noindex)
assinatura/             assinatura de email PCinfor e as suas imagens (noindex,nofollow)
img/                    logótipo e fotos dos equipamentos
img/packs/              imagens combinadas dos packs (1200×900) e img/packs/mini/ (240×180)
video/                  vídeo e imagem de capa do banner Black Friday
fonts/                  Poppins em woff2
tools/                  scripts Python de manutenção (packs)
card-*.png, pag-*.png   capturas de ecrã de verificação (cartão e página, computador e telemóvel)
```

## 4. Páginas do site

### Página inicial (`index.html`)

Por ordem:

1. **Faixa Black Friday** (`.bf`) no topo: "Black Friday todos os dias · Portes grátis no continente · Portáteis desde 379€ · Ver preços".
2. **Cabeçalho** (`header.topo`): logótipo, links Serviços e Contactos, WhatsApp 963 401 241, e a **barra de categorias** `nav.cat-topo` (Portáteis, Computadores, All-in-One, Monitores, Packs), fixa no topo.
3. **Hero dos packs** (`.hero-packs`): "Packs completos desde 228€", selo "Teclado e rato de oferta em todos os packs", foto do pack mais barato (Lenovo M700 Tiny + HP E23 G4) e botões "Ver todos os packs" e WhatsApp.
4. **Banner Black Friday** (`.banner-bf`): "Não esperamos por novembro. Os nossos preços já são de Black Friday.", envio grátis até 31 de dezembro, atalhos para as categorias e o **vídeo** `video/black-friday-destaques.mp4` (sem som, em loop; um pequeno script volta a pô-lo a tocar se parar ou se a página voltar a ficar visível).
5. **Equipamentos** (`#equipamentos`): botões de categoria com contadores (`nav.categorias`) e um bloco por categoria (`<div class="categoria" id="...">`) com título, "N disponíveis", frase e a lista de cartões.
6. **Serviços** (`#servicos`): Assistência técnica, Tinteiros e toners, Venda e consultoria, cada um com link para o WhatsApp com mensagem pré-preenchida.
7. **Como comprar**: 3 passos (ver o equipamento no site, na montra pelo QR ou nos anúncios; pagar online ou perguntar no WhatsApp; levantar na loja ou receber em casa).
8. **Contactos** (`#contactos`): morada, horário (dias úteis 09:00–13:00 e 14:00–18:00), telefone 22 201 24 25, WhatsApp, geral@pcinfor.pt e Google Maps.
9. **Rodapé**: links das categorias, serviços, contactos, condições, privacidade, Facebook e Instagram; Livro de Reclamações Eletrónico; CICAP e Portal do Consumidor; dados legais da PL Resende (sede, capital social 5.000€, NIPC 508239052) e as notas do preço das chamadas (`*` rede fixa, `**` rede móvel).

### Página de equipamento (`equipamentos/<slug>/index.html`)

Todas seguem o mesmo molde (copiado de um equipamento parecido):

- `<body class="com-barra">`, a mesma faixa Black Friday, o cabeçalho com menu da página (Destaques, Especificações, Encomendar) e a barra `cat-topo` com a categoria do equipamento marcada (`class="atual" aria-current="true"`).
- **Hero**: etiquetas ("Seminovo · Grade A", "Testado e com garantia" e, se for o caso, "Últimas unidades"), título, descrição curta, cartão de preço (Preço Black Friday, PVP de referência riscado, IVA incluído), botões Comprar e "Dúvidas? WhatsApp", botão **"Leve em conjunto com monitor desde X€"** (`.btn-conjunto`, salta para o pack mais barato) e nota sobre pagamento e envio.
- Secções de argumentos (3 cartões numerados), "No dia a dia", **ficha técnica** (`#especificacoes`, tabela `.specs` com garantia, referência, condição e preço) e nota de upgrades sob consulta.
- **Caixas de pack** (só computadores): uma por monitor, entre comentários `<!-- PACK-...:INICIO -->` e `<!-- PACK-...:FIM -->` (ver secção 8).
- **Encomendar** (`#encomendar`): chamada final com Comprar e WhatsApp.
- **Barra fixa no telemóvel** (`.barra-movel`, até 700 px): Comprar e Dúvidas sempre à vista, a pensar em quem chega pelo QR da montra.
- Script no fim: `LINK_PAGAMENTO` com o link Stripe. Os botões `.js-comprar` passam a abrir esse link. Se estiver vazio, o clique mostra o aviso `.js-aviso` ("pagamento online temporariamente indisponível", com WhatsApp).

Nas páginas dos **monitores**, o botão diz "Leve em conjunto com computador desde X€" e salta para a lista de packs desse monitor.

### Outras páginas

- `condicoes/`: quem vende; preços com IVA; encomenda pelo botão Comprar; pagamento sempre online no Stripe (MB WAY, Multibanco, cartão, Apple Pay, Google Pay), sem pagamento no levantamento; fatura do programa certificado por email ou WhatsApp; levantamento grátis ou envio (grátis no continente até 31/12/2026, Açores e Madeira 19,90€; envio em 1 a 2 dias úteis); livre resolução de 14 dias com formulário modelo; garantia de 18 meses nos seminovos e 3 anos nos novos (DL 84/2021); reclamações e CICAP; lei aplicável.
- `privacidade/`: responsável, o que o site recolhe, dados de quem contacta ou compra, finalidades, partilha, prazos, segurança e direitos.
- `obrigado/`: "Obrigado pela sua compra!", explica o recibo por email, o Multibanco, o contacto para levantamento ou envio e a fatura.
- `assinatura/`: página para copiar a assinatura de email PCinfor (botão "Copiar assinatura"); as imagens ficam alojadas aqui para aparecerem nos emails.
- `portateis/`, `computadores/`, `all-in-one/`, `monitores/`, `packs/`: endereços curtos (`https://www.pcinfor.pt/packs/`) que redirecionam para a âncora da categoria.

## 5. Funcionalidades

- **Categorias**: Portáteis, Computadores (mini PC e secretária), All-in-One (computador e ecrã numa peça, sem packs com monitor), Monitores e Packs. Cada uma com bloco próprio na página inicial, contador no botão e "N disponíveis", e endereço curto.
- **Pesquisa de artigos** (`form.pesquisa` em `header.topo`, todas as páginas, com `pesquisa.js`): caixa "Pesquisar artigo, marca ou modelo" ao lado do logótipo no computador e numa linha própria por baixo do logótipo no telemóvel. Ao escrever mostra até 6 sugestões (foto, nome, categoria e preço) e Enter abre a página inicial só com os artigos encontrados (`index.html?q=...#equipamentos`), com "Ver todos os artigos" e, se não houver nada, "Perguntar no WhatsApp". Lê os cartões de `index.html` (nas outras páginas vai buscá-lo quando o cliente toca na caixa), por isso **não há índice para manter**: um cartão novo fica logo pesquisável. Aceita sem acentos (`portatil`), números como palavra inteira (`24` encontra os 24″ e não 249€) e `16gb` ou `16 gb`. Os packs só aparecem quando se escreve "pack" ou quando não há artigo com aquele nome. Sem JavaScript, o formulário leva à página inicial.
- **Barra de categorias em todas as páginas** (`nav.cat-topo` dentro de `header.topo`), com a categoria atual marcada. Testada sem scroll horizontal entre 320 e 480 px (regras próprias a 480 e 370 px no CSS).
- **Cartões de produto** (`article.produto-destaque`): foto, etiquetas, 3 pontos, PVP de referência riscado e Preço Black Friday, botões **Comprar XXX€** (link Stripe direto) e **Dúvidas** (WhatsApp com o nome do equipamento na mensagem), e "Ver fotos e características completas".
- **Ordenação por preço**: dentro de cada categoria os cartões estão do mais barato para o mais caro; os packs também, dentro de cada monitor.
- **Botão "Pack c/ monitor desde X€"** (`.btn-pack`) nos cartões de computadores, gerado por `tools/botao_pack_cartoes.py`.
- **Botão "Leve em conjunto"** (`.btn-conjunto`) junto ao preço nas páginas de computadores e monitores.
- **Preços Black Friday**: preço de venda com "Preço Black Friday" e o "PVP de referência" riscado ao lado, em todos os artigos e packs (regra na secção 6).
- **Destaque dos packs**: hero "Packs completos desde 228€" na página inicial, selo "Teclado e rato de oferta" (`.oferta-pack`) em todas as caixas e listas de packs.
- **Selo "Últimas unidades"** (`span.etiqueta.ultimas-unidades`) quando o stock do fornecedor é de 10 unidades ou menos, no cartão e na página.
- **Banner e faixa Black Friday** em todas as páginas; vídeo dos destaques no banner da página inicial.
- **Portes grátis** para Portugal continental até 31 de dezembro, em destaque na faixa, no banner, nas páginas e nas condições.
- **Compra sempre online** (Stripe); o WhatsApp é só para dúvidas.
- **Endereços fixos por equipamento** para os QR codes da montra e dos vídeos; endereços antigos redirecionam (ex.: `pack-dell-34`).
- **Variantes ligadas entre si**: o mesmo modelo com outra configuração tem slug próprio (ex.: `lenovo-thinkstation-p520` e `lenovo-thinkstation-p520-gtx1080`).
- **Informação legal completa**: Livro de Reclamações, CICAP, dados da empresa, preço das chamadas, condições e privacidade.
- **Assinatura de email** alojada em `/assinatura/`, usada no Outlook e nos emails automáticos.
- **Acessibilidade e desempenho**: `lang="pt-PT"`, `aria-label` nos botões e navegações, imagens com `width`/`height` e `loading="lazy"`, fontes locais com `font-display: swap`, respeito por `prefers-reduced-motion`.

## 6. Preços

Todos os custos indicados pelo Paulo são **sem IVA**. Preço Black Friday = (custo + ganho) × 1,23, com ganho = o maior entre a percentagem do escalão e o ganho mínimo, **arredondado para baixo** para um valor terminado em 9 ou 5.

| Custo (sem IVA) | Margem | Ganho mínimo | PVP de referência |
|---|---|---|---|
| até 100 € | 50% | 40 € | 60% |
| mais de 100 € até 250 € | 40% | 50 € | 50% |
| mais de 250 € até 500 € | 30% | 100 € | 40% |
| acima de 500 € | 25% | 150 € | 35% |

- **PVP de referência** (`<div class="preco-antes">`): a mesma regra com +10 pontos percentuais e os mesmos mínimos. Se der igual ao preço (porque manda o ganho mínimo), usa-se o ganho mínimo + 10 € (ex.: E23 G4 129 €, E243m 139 €, M700 109 €), para haver sempre preço riscado. Nunca escrever "preço anterior" nem "antes".
- **Pack**: preço = soma exata do computador e do monitor; referência = soma das duas referências (`<s class="pack-ref">` nas listas).
- Upgrades e opcionais: custo × 1,30 × 1,23, arredondado para baixo, pedidos por WhatsApp ("sob consulta").
- Exceção: o Lenovo M700 Tiny tem preço fixo (109 €).
- O cálculo está em `/mnt/project-files/precos-referencia/calcular_referencia.py` (fora do repositório).

## 7. Pagamentos e encomendas (Stripe e Make)

O site não tem servidor nem carrinho: cada artigo e cada pack tem o seu **Payment Link** do Stripe.

- Produto + preço em EUR com `tax_behavior=inclusive` (IVA incluído).
- O link pede morada de faturação, telefone e NIF, envio só para Portugal com 3 tarifas (levantar na loja, continente grátis, Açores e Madeira), limite de vendas igual ao stock (`restrictions[completed_sessions][limit]`), `metadata[slug]` e redireciona para `https://www.pcinfor.pt/obrigado/`.
- Monitores com cabo à escolha: campo obrigatório "Cabo de imagem incluído" (DisplayPort, HDMI ou VGA).
- Meios de pagamento: cartão, MB WAY, Multibanco, Apple Pay e Google Pay.
- A fatura legal sai do programa de faturação certificado (não do Stripe), e segue por email ou WhatsApp.
- O link está em dois sítios: `LINK_PAGAMENTO` na página do produto e o botão "Comprar XXX€" do cartão na página inicial. As caixas de pack têm o link do pack no botão "Comprar o pack".

**Emails automáticos (Make)**, a partir de geral@pcinfor.pt por SMTP do cPanel:

1. *Cenário 1*: Stripe "Watch Events" (`checkout.session.completed` e `checkout.session.async_payment_succeeded`), filtro "Só pagos" (`payment_status = paid`, para o Multibanco só disparar quando pago), chamada à API para obter os artigos (`/v1/checkout/sessions/{id}/line_items`) e envio do email 1 "recebemos a sua encomenda" (nome, equipamento, valor e assinatura). Testado a 19/11/2026 com cartão.
2. *Cenário 2* (modelo): uma folha Google de encomendas com coluna Estado; ao mudar para `Pronta` ou `Enviada`, o Make envia o email 2a (pronta para levantamento) ou 2b (enviada, com transportadora e seguimento).

Os textos dos emails e os passos do Make estão em `/mnt/project-files/emails-encomendas/` e no guia `/mnt/project-files/modelo-loja-online/GUIA-LOJA-ONLINE.md`.

## 8. Packs computador + monitor

- Regra: quando entra um **monitor** novo, cria-se um pack com cada computador à venda; quando entra um **computador** (não portátil, não All-in-One), cria-se um pack com cada monitor à venda. Teclado e rato de oferta, slug Stripe `pack-<computador>-<monitor>` (o pack Dell 34″ usa `pack-<computador>`). Limite do link = o menor stock dos dois. Quando um monitor esgota, saem os packs dele.
- Na página de cada computador há uma caixa por monitor, entre comentários marcadores:

| Monitor | Âncora | Marcador |
|---|---|---|
| Dell C3422WE 34″ curvo | `#pack` | `PACK-MONITOR` |
| HP EliteDisplay E23 G4 23″ | `#pack-e23` | `PACK-E23` |
| HP EliteDisplay E243m 24″ | `#pack-e243m` | `PACK-E243M` |
| HP EliteDisplay E243d 24″ (dock USB-C) | `#pack-e243d` | `PACK-E243D` |
| HP EliteDisplay E27q G4 27″ | `#pack-e27q` | `PACK-E27Q` |
| HP E27d G4 27″ (dock USB-C) | `#pack-e27d` | `PACK-E27D` |
| LG 32UP550-W 32″ 4K | `#pack-lg32` | `PACK-LG32` |
| Lenovo ThinkVision T32p-20 32″ 4K (dock USB-C) | `#pack-t32p` | `PACK-T32P` |

- Todas as caixas têm o mesmo formato resumido: imagem combinada, selo "Teclado e rato de oferta", resumo `pack-resumo` (Computador / Monitor / Oferta, a partir das descrições curtas das duas páginas), PVP de referência + Preço Black Friday e botão "Comprar o pack".
- Na página inicial, a categoria Packs tem uma lista por monitor (`.pack-lista`, entre os mesmos marcadores) com linhas `.pack-linha`: miniatura, nome do computador, "preço + monitor preço", referência riscada e preço do pack.
- Cada pack tem uma imagem combinada (monitor atrás, computador à frente, fundo branco) em `img/packs/pack-<computador>-<monitor>.jpg` (1200×900) e miniatura em `img/packs/mini/` (240×180).

## 9. Ferramentas (`tools/`)

Correr na raiz do site (precisam de Python 3 e, o primeiro, de Pillow):

- `python3 tools/gerar_imagens_packs.py [--monitor slug] [slug-computador ...]`: gera as imagens combinadas e as miniaturas dos packs à escala real (usa a altura de cada monitor e a medida de cada computador). Para um equipamento novo, acrescentar a foto limpa e a medida em `COMPUTADORES` ou `MONITORES`.
- `python3 tools/ligar_imagens_packs.py`: põe essas imagens nas caixas de pack de cada computador e na lista de Packs. Para um monitor novo, acrescentar o marcador, a âncora e o nome em `MONITORES`. Pode correr-se várias vezes.
- `python3 tools/botao_pack_cartoes.py`: põe ou atualiza o botão "Pack c/ monitor desde X€" nos cartões de computadores, lendo o preço e a âncora do `.btn-conjunto` de cada página. Correr de novo quando muda um preço de pack ou entra um computador.

## 10. Como lançar um equipamento

O processo completo está na skill `lancar-equipamento-pcinfor`. Em resumo:

1. **Preço** pela regra de escalões (secção 6), com as contas na resposta.
2. **Página** em `equipamentos/<slug>/index.html`, copiada de um equipamento parecido (ex.: `lenovo-thinkcentre-m700-tiny` para mini PC, `hp-elitebook-*` para portáteis, `hp-eliteone-840-g9` para All-in-One), com a barra `cat-topo` e a categoria marcada.
3. **Fotos** verificadas e limpas em `img/` (fundo branco, recortadas, 1200 px no lado maior, menos de ~150 KB).
4. **Link Stripe** criado com a API (secção 7) e colado na página e no cartão; a linha `<slug> <link>` vai para `stripe/links_reais.txt` (na cópia em project-files).
5. **Cartão** na categoria certa da página inicial, por ordem de preço, contadores atualizados (botão e "N disponíveis"), e o selo "Últimas unidades" se o stock for até 10.
6. **Packs** com cada monitor (ou cada computador, se for monitor), imagens com os scripts de `tools/`, e `botao_pack_cartoes.py`.
7. **README**: acrescentar o endereço à lista da secção 11.
8. **Verificar** com capturas em computador e telemóvel, sem scroll horizontal.
9. **PR** para `main` (depois de juntar o `main` mais recente e manter todos os cartões), merge e confirmar que a página abre em `https://www.pcinfor.pt/equipamentos/<slug>/`. Copiar os ficheiros alterados para `/mnt/project-files/website-pcinfor/`.

## 11. Equipamentos e endereços fixos

Cada equipamento é uma pasta em `equipamentos/<slug>/`. O endereço fica fixo, por isso o QR da montra pode ser impresso e gravado no vídeo sem medo de mudar:

- Pack Dell: `https://www.pcinfor.pt/equipamentos/pack-dell-34/` (redireciona para `dell-optiplex-3070-micro/#pack`)
- HP EliteBook 840 G7: `https://www.pcinfor.pt/equipamentos/hp-elitebook-840-g7/`
- HP EliteBook 840 G7 i7: `https://www.pcinfor.pt/equipamentos/hp-elitebook-840-g7-i7/`
- HP EliteBook 650 G9: `https://www.pcinfor.pt/equipamentos/hp-elitebook-650-g9/`
- HP EliteBook 640 G11: `https://www.pcinfor.pt/equipamentos/hp-elitebook-640-g11/`
- HP EliteBook 1040 G8 x360: `https://www.pcinfor.pt/equipamentos/hp-elitebook-1040-g8-x360/`
- HP ZBook Fury 16 G9: `https://www.pcinfor.pt/equipamentos/hp-zbook-fury-16-g9/`
- Lenovo V15 G5: `https://www.pcinfor.pt/equipamentos/lenovo-v15-g5/`
- HP ProBook 640 G8: `https://www.pcinfor.pt/equipamentos/hp-probook-640-g8/`
- HP ProBook 640 G8 i7 Touch: `https://www.pcinfor.pt/equipamentos/hp-probook-640-g8-i7-touch/`
- Dell Latitude 7430 Touch: `https://www.pcinfor.pt/equipamentos/dell-latitude-7430-touch/`
- Lenovo ThinkPad L14 Gen 3: `https://www.pcinfor.pt/equipamentos/lenovo-thinkpad-l14-g3/`
- Lenovo ThinkPad T14s Gen 2 Touch: `https://www.pcinfor.pt/equipamentos/lenovo-thinkpad-t14s-g2-touch/`
- Dynabook Satellite Pro A50-J: `https://www.pcinfor.pt/equipamentos/dynabook-satellite-pro-a50-j/`
- Dell Latitude 5440: `https://www.pcinfor.pt/equipamentos/dell-latitude-5440/`
- HP EliteOne 840 G9 All-in-One: `https://www.pcinfor.pt/equipamentos/hp-eliteone-840-g9/`
- Bundle All-in-One HP Z2 Mini G9 + Monitor HP Z32 4K: `https://www.pcinfor.pt/equipamentos/hp-z2-mini-g9-z32-bundle/`
- Lenovo ThinkCentre M700 Tiny: `https://www.pcinfor.pt/equipamentos/lenovo-thinkcentre-m700-tiny/`
- Lenovo ThinkCentre M720q Tiny: `https://www.pcinfor.pt/equipamentos/lenovo-thinkcentre-m720q-tiny/`
- Dell OptiPlex 3070 Micro (só o computador do pack): `https://www.pcinfor.pt/equipamentos/dell-optiplex-3070-micro/`
- Dell OptiPlex 3060 Micro: `https://www.pcinfor.pt/equipamentos/dell-optiplex-3060-micro/`
- HP ProDesk 400 G4 SFF: `https://www.pcinfor.pt/equipamentos/hp-prodesk-400-g4-sff/`
- HP ProDesk 400 G4 Mini: `https://www.pcinfor.pt/equipamentos/hp-prodesk-400-g4-mini/`
- HP EliteDesk 800 G4 SFF: `https://www.pcinfor.pt/equipamentos/hp-elitedesk-800-g4-sff/`
- HP Z2 G5 SFF: `https://www.pcinfor.pt/equipamentos/hp-z2-g5-sff/`
- Monitor Dell C3422WE 34″ (só o monitor do pack): `https://www.pcinfor.pt/equipamentos/dell-c3422we-34/`
- HP ProDesk 600 G6 Tower: `https://www.pcinfor.pt/equipamentos/hp-prodesk-600-g6-tower/`
- Lenovo ThinkStation P520: `https://www.pcinfor.pt/equipamentos/lenovo-thinkstation-p520/`
- Lenovo ThinkStation P520 GTX 1080: `https://www.pcinfor.pt/equipamentos/lenovo-thinkstation-p520-gtx1080/`
- Lenovo ThinkStation P620 Threadripper PRO RTX 5070: `https://www.pcinfor.pt/equipamentos/lenovo-thinkstation-p620/`
- HP Z2 G5 Tower Quadro M4000: `https://www.pcinfor.pt/equipamentos/hp-z2-g5-tower-m4000/`
- HP Z2 G5 Tower RTX 2070: `https://www.pcinfor.pt/equipamentos/hp-z2-g5-tower-rtx2070/`
- HP Z4 G4 Quadro RTX 4000: `https://www.pcinfor.pt/equipamentos/hp-z4-g4-rtx4000/`
- HP Z4 G4 i9 Quadro RTX 4000: `https://www.pcinfor.pt/equipamentos/hp-z4-g4-i9-rtx4000/`
- HP Z2 Mini G5 i9 NVIDIA T1000: `https://www.pcinfor.pt/equipamentos/hp-z2-mini-g5-i9-t1000/`
- HP ProDesk 400 G6 Mini: `https://www.pcinfor.pt/equipamentos/hp-prodesk-400-g6-mini/`
- HP ProDesk 400 G6 Mini 16GB: `https://www.pcinfor.pt/equipamentos/hp-prodesk-400-g6-mini-16gb/`
- Monitor HP EliteDisplay E23 G4 23″: `https://www.pcinfor.pt/equipamentos/hp-elitedisplay-e23-g4/`
- Monitor HP EliteDisplay E243m 24″: `https://www.pcinfor.pt/equipamentos/hp-elitedisplay-e243m/`
- Monitor HP EliteDisplay E243d 24″ (dock USB-C): `https://www.pcinfor.pt/equipamentos/hp-elitedisplay-e243d/`
- Monitor HP EliteDisplay E27q G4 27″: `https://www.pcinfor.pt/equipamentos/hp-elitedisplay-e27q-g4/`
- Monitor HP E27d G4 27″ (dock USB-C): `https://www.pcinfor.pt/equipamentos/hp-elitedisplay-e27d-g4/`
- Monitor LG 32UP550-W 32″ 4K (USB-C): `https://www.pcinfor.pt/equipamentos/lg-32up550-w/`
- Monitor Lenovo ThinkVision T32p-20 32″ 4K (dock USB-C): `https://www.pcinfor.pt/equipamentos/lenovo-thinkvision-t32p-20/`

## 12. Fora do repositório

Material ligado ao site que vive na pasta do projeto (`/mnt/project-files/`), não no repositório:

- `website-pcinfor/`: cópia do site e a pasta `stripe/` (`criar_links_pagamento.sh`, `links_reais.txt` com os links de todos os artigos e packs, `links_teste.txt`, `plano_stripe.md`).
- `emails-encomendas/`: textos e HTML dos emails 1, 2a e 2b e os passos do cenário Make.
- `assinatura-email-pcinfor/`: modelo da assinatura de email.
- `precos-referencia/calcular_referencia.py`: cálculo do Preço Black Friday e do PVP de referência.
- `montra-black-friday/`, `montra-pack-dell/`, `videos-equipamentos/`, etc.: vídeos da montra da loja (16:9, com QR para o site) e reels para as redes sociais (9:16). O vídeo do banner do site (`video/black-friday-destaques.mp4`, 1280×720, sem QR) sai de `montra-black-friday/`.
- `modelo-loja-online/GUIA-LOJA-ONLINE.md`: guia para montar uma loja igual para outro cliente.

## 13. Pontos em aberto

- O texto do hero da página inicial ainda diz "São 136 combinações", mas a categoria Packs já tem 152.
- O PrestaShop antigo: se for para manter, passa para um subdomínio (ex.: `loja.pcinfor.pt`) ou fica em modo de manutenção.
- Confirmar com o contabilista se os seminovos estão no regime da margem (afeta o IVA, não o site).
- Os portes grátis e a campanha Black Friday estão escritos até 31 de dezembro de 2026: em janeiro é preciso rever a faixa, o banner, as páginas e as condições.
