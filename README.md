# Linu Farol

Da família Linu: **https://farol.linupedia.com.br**, o painel do mês para pequenos negócios. Site estático com
publicação própria: a cada push na `main` e de 6 em 6 horas, o GitHub Actions faz a ronda, confere as páginas, os
preços e o visual e entrega na VM (`deploy/ORACLE.md`). O `/identidade` leva para
https://familia.linupedia.com.br/identidade.

## A ronda e a lista de faróis
`ferramentas/ronda.py` confere as quatro luzes de cada site da família (Luz, Cadeado, Rapidez, Trancas) e escreve
`dados/ronda.json` e a lista no `index.html` (entre `<!-- ronda:inicio -->` e `<!-- ronda:fim -->`). O histórico vem
da lista publicada (`--anterior`), até 120 rondas por site. Para pôr um site na lista: a linha dele no `SITES`.

## O painel de cada cliente (07/11/2026)

Cada cliente tem uma página só dele em `https://farol.linupedia.com.br/p/<código>/`, refeita a cada ronda (de 6 em 6
horas) pelo `ferramentas/painel.py`: as quatro luzes agora, a faixa dos últimos 30 dias (uma marca por ronda, com as
vezes em que não estava tudo certo), o mês fechado (visitas, Google e Maps, Instagram, com a comparação com o mês
anterior) e o rumo, e o “Salvar em PDF” (a impressão do navegador, em papel branco). Três versões: no celular, uma
coluna com o resumo e o PDF presos embaixo; no tablet, o resumo deitado em cima e os cartões em 2; no computador, o
resumo parado à esquerda, com o Linu de luneta (`css/painel.css`, `js/painel.js`).

- **Exemplo público:** `/p/exemplo/`, o Café Aurora (o site de demonstração do Linu Sites), com luzes de verdade e números
  do mês inventados (`ferramentas/painel-exemplo.json`); a página de planos aponta para ele.
- **Os clientes não ficam no git** (o repositório é público). A lista é o segredo `FAROL_CLIENTES` do GitHub, no mesmo
  formato do `painel-exemplo.json`; no computador, `dados/clientes.json` (ignorado pelo git). Os painéis (`p/`) só existem
  no Actions e na VM. O log do Actions mostra só as 4 primeiras letras do código.
- **Cliente novo:** `python3 ferramentas/painel.py --novo-codigo` sorteia o código; pôr o cliente no arquivo (código,
  nome, site, um trecho do título do site, plano `site`, `completo` ou `avulsa`, `desde` como `2026-11`) e subir o
  segredo: `gh secret set FAROL_CLIENTES < dados/clientes.json`. O painel aparece na próxima publicação.
- **Todo mês (até o dia 5):** acrescentar em `meses` o mês fechado (`visitas`, `google`, `instagram` e o `rumo`, de 1 a
  3 frases) e subir o segredo de novo. Os números do Google e do Instagram vêm dos painéis deles, pelo acesso de
  leitura que o cliente dá.
- **Privacidade:** o endereço não é adivinhável (16 letras sorteadas), não entra no sitemap, o `robots.txt` fecha `/p/` e
  a página pede `noindex` e não manda o endereço para os sites de fora (`no-referrer`). Quem tiver o link vê o painel,
  e o rodapé diz isso; trocar o endereço é trocar o código.
- **Falta:** o contador de visitas sem cookie (um serviço na VM, como o `linu-pedidos`, e um script no site do
  cliente); até lá, as visitas são lançadas à mão como o resto do mês. O aviso no WhatsApp quando uma luz apaga também
  não existe, (o texto do plano “Farol do site” passou de “de hora em hora” para “de 6 em 6 horas”, como a ronda, em 07/11/2026).

## Onde está cada coisa
| O quê | Onde |
|---|---|
| A página | `index.html`, `css/estilo.css`, `js/farol.js` |
| O painel de cada cliente | `ferramentas/painel.py`, `ferramentas/painel-exemplo.json`, `css/painel.css`, `js/painel.js` (gerados em `p/`, fora do git) |
| A identidade (o farol, as três versões, as cores) | `IDENTIDADE.md` |
| Os preços (“a partir de”) | `precos.json` → `python3 ferramentas/precos-servicos.py` |
| O farol à noite | `ferramentas/farol-luz.py` (a partir de `img/farol.png`) |
| As artes da API | `arte/` (o pedido, as tentativas e a aprovada) |
| O Linu vivo e o movimento | `js/linu-vivo.js`, `js/movimento.js`, `css/movimento.css` (cópias do kit do linuarquivos) |
| A versão de cada arquivo | `ferramentas/versao-arquivos.py` (no Actions, antes de entregar) |
| Os pedidos | `/api/pedido`, o `linu-pedidos` do linuarquivos (e-mail na hora, 12 meses guardados) |
