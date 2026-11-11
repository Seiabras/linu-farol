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
- **Falta:** o aviso no WhatsApp quando uma luz apaga. O texto do plano “Farol do site” passou de “de hora em hora”
  para “de 6 em 6 horas”, como a ronda (07/11/2026).

## O contador de visitas sem cookie (11/11/2026)

`servidor/linu-visitas/` conta as visitas do site do cliente sem cookie e sem guardar quem visitou, e o painel lê
os números sozinho. Nos planos “completo” e “avulsa”; o exemplo segue com os números inventados.

- **No site do cliente:** `<script src="https://farol.linupedia.com.br/v.js" defer></script>` no `<head>` de cada página.
  Se o site tiver CSP, acrescentar `https://farol.linupedia.com.br` ao `script-src` e ao `connect-src`. No aviso de
  privacidade do cliente: “contamos as visitas sem cookie e sem guardar dados de quem visita (Linu Farol)”.
- **Como conta:** cada página aberta manda o caminho, o nome do site de onde veio e o `utm_source`. O serviço resume
  sal do dia + site + IP + navegador num sha256 para saber se a pessoa já foi contada hoje; o sal e os resumos
  somem no dia seguinte, e o IP e o navegador nunca vão para o disco. “Pessoas” do mês é a soma das pessoas de cada
  dia (quem volta em outro dia conta de novo; o painel diz isso). Robôs, `navigator.webdriver`, Do Not Track e
  Global Privacy Control não contam.
- **Quais sites:** só os que o painel pediu nos últimos 60 dias (o painel pede a cada ronda). Cliente novo no
  `FAROL_CLIENTES` começa a contar na ronda seguinte; aviso de site desconhecido é descartado.
- **No painel:** o mês fechado sem visitas no cadastro recebe as do contador (o que for lançado à mão vale mais), o
  mês fechado que ainda não está no cadastro aparece só com as visitas, e o mês corrente vira a linha “Neste mês, até
  agora”. A leitura é `GET /api/visitas?site=<host>` com `Authorization: Bearer` e o segredo `FAROL_VISITAS_CHAVE`.
- **Ligar (uma vez, o dono roda):** `bash servidor/linu-visitas/ligar-visitas.sh` sorteia a chave, guarda no segredo
  do GitHub e no `.env` da VM, instala o `linu-visitas.service` (porta 8095, usuário `linuvisitas`, as proteções do
  `linu-pedidos`) e liga o `/api/visita` no bloco do Farol no Caddy (com cópia antes e volta atrás se o Caddy reprovar).
  Rodar de novo atualiza o código; `TROCAR_CHAVE=1` troca a chave.
- **Os sites da família (11/11/2026):** os cinco contam visitas (cópia do `v.js` em `js/farol-visitas.js` em cada um; o
  Farol usa o `v.js` direto). Os painéis deles são públicos, em `ferramentas/paineis-da-casa.json`: `/p/casa-familia/`,
  `/p/casa-sites/`, `/p/casa-digital/`, `/p/casa-seguro/` e `/p/casa-farol/`. O CSP de cada um no Caddy libera o Farol no
  `connect-src`: `bash servidor/linu-visitas/liberar-sites-da-casa.sh` (uma vez; volta atrás se o Caddy reprovar).
- **Dados:** `/opt/linu-visitas/dados/visitas.json` (só os totais, 25 meses), `hoje.json` (o sal e os resumos do dia),
  `sites.json`. Teste: `node servidor/linu-visitas/teste.mjs`.

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
| O contador de visitas | `v.js` (no site do cliente), `servidor/linu-visitas/` (na VM, porta 8095) |
| Os pedidos | `/api/pedido`, o `linu-pedidos` do linuarquivos (e-mail na hora, 12 meses guardados) |
