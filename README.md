# Linu Farol

Da família Linu: **https://farol.linupedia.com.br**, o painel do mês para pequenos negócios. Site estático com
publicação própria: a cada push na `main` e de 6 em 6 horas, o GitHub Actions faz a ronda, confere as páginas, os
preços e o visual e entrega na VM (`deploy/ORACLE.md`). O `/identidade` leva para
https://familia.linupedia.com.br/identidade.

## A ronda e a lista de faróis
`ferramentas/ronda.py` confere as quatro luzes de cada site da família (Luz, Cadeado, Rapidez, Trancas) e escreve
`dados/ronda.json` e a lista no `index.html` (entre `<!-- ronda:inicio -->` e `<!-- ronda:fim -->`). O histórico vem
da lista publicada (`--anterior`), até 120 rondas por site. Para pôr um site na lista: a linha dele no `SITES`.

## Onde está cada coisa
| O quê | Onde |
|---|---|
| A página | `index.html`, `css/estilo.css`, `js/farol.js` |
| A identidade (o farol, as três versões, as cores) | `IDENTIDADE.md` |
| Os preços (“a partir de”) | `precos.json` → `python3 ferramentas/precos-servicos.py` |
| O farol à noite | `ferramentas/farol-luz.py` (a partir de `img/farol.png`) |
| As artes da API | `arte/` (o pedido, as tentativas e a aprovada) |
| O Linu vivo e o movimento | `js/linu-vivo.js`, `js/movimento.js`, `css/movimento.css` (cópias do kit do linuarquivos) |
| A versão de cada arquivo | `ferramentas/versao-arquivos.py` (no Actions, antes de entregar) |
| Os pedidos | `/api/pedido`, o `linu-pedidos` do linuarquivos (e-mail na hora, 12 meses guardados) |
