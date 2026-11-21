# CLAUDE.md · site pcinfor.pt

Contexto completo do site (como foi feito, estrutura, funcionalidades, preços, Stripe, packs, ferramentas): ler o [`README.md`](README.md) antes de mexer em qualquer coisa.

## Essencial

- Site estático em HTML e CSS escritos à mão, publicado pelo GitHub Pages a partir de `main` (domínio `www.pcinfor.pt` no `CNAME`, `.nojekyll`). Sem compilação, sem dependências, sem JavaScript de terceiros.
- Falar e escrever sempre em **português de Portugal**. Frases simples, sem jargão.
- Trabalhar num ramo, abrir PR para `main`. Antes do merge, juntar o `main` mais recente (há muitos lançamentos em paralelo) e resolver conflitos **mantendo todos os cartões** e acertando os contadores das categorias.
- Para lançar um equipamento, seguir a skill `lancar-equipamento-pcinfor` (resumo na secção 10 do README).
- Depois de alterar o site, copiar os ficheiros alterados para `/mnt/project-files/website-pcinfor/`.

## Regras de texto e de preço

- "Seminovo · Grade A" (nunca "recondicionado"); nos destaques só "Testado e com garantia"; a garantia (18 meses, bateria 3 meses nos portáteis) só na ficha técnica. Sem nome nem preço do fornecedor. Upgrades "sob consulta".
- Valores do Paulo são sempre sem IVA. Preço = (custo + ganho do escalão ou mínimo) × 1,23, arredondado para baixo para 9 ou 5. PVP de referência com +10 p.p. Nunca escrever "preço anterior" ou "antes".
- A compra é sempre online pelo Stripe; o WhatsApp (963 401 241) é só para dúvidas.

## Ao mexer nas páginas

- Toda a página nova leva a barra `nav.cat-topo` dentro de `header.topo`, com a categoria atual marcada (`class="atual" aria-current="true"`), e o mesmo rodapé legal.
- Categoria nova: acrescentar à `cat-topo` e ao rodapé de **todas** as páginas, criar o endereço curto que redireciona e verificar a 320–480 px sem scroll horizontal.
- Cartões por ordem de preço dentro de cada categoria. Ao pôr ou tirar um cartão, atualizar o número em `nav.categorias` e o "N disponíveis" do bloco.
- Os endereços `equipamentos/<slug>/` estão em QR codes impressos: nunca mudar nem apagar um endereço; se for preciso, deixar uma página que redireciona (como `pack-dell-34`).
- Packs: blocos entre `<!-- PACK-...:INICIO -->` e `<!-- PACK-...:FIM -->`; depois de mexer, correr `tools/gerar_imagens_packs.py`, `tools/ligar_imagens_packs.py` e `tools/botao_pack_cartoes.py`.
- Verificar sempre com capturas em computador e telemóvel antes do merge.
- Ao lançar ou retirar equipamentos, atualizar a lista de endereços no README.

## Manter a documentação em dia (obrigatório)

Sempre que um PR acrescenta, altera ou retira uma funcionalidade, o mesmo PR atualiza a documentação. Um PR assim não está pronto sem isto:

- `README.md`: descrever a funcionalidade na secção certa (páginas, funcionalidades, preços, Stripe, packs, ferramentas, lançamento) e acrescentar uma linha à cronologia da secção 1 com a data e o que entrou. Se algo deixou de existir, tirá-lo do README em vez de o deixar desatualizado.
- `CLAUDE.md`: acrescentar ou mudar a regra quando a alteração cria uma regra nova de trabalho (ex.: uma classe, um marcador ou um passo que todas as páginas têm de ter).
- "Pontos em aberto": tirar o que ficou resolvido e acrescentar o que ficou por fazer.
- Na descrição do PR, dizer que secções da documentação foram atualizadas.

## Segurança

- Nunca pôr chaves do Stripe (ou outras) no repositório nem no chat. A chave está na variável `STRIPE_API_KEY` do ambiente, quando existe.
