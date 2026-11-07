# Identidade do Linu Farol

Lido antes de mexer em qualquer tela, junto com o `DIRETRIZES-UX.md`. O que é comum à família (o Linu, as cores, o que
nunca entra) está no `IDENTIDADE-LINU.md` do linuarquivos; aqui fica só o que é deste site. Primeira versão de
07/11/2026.

## O que o site é, numa frase
O painel do mês para pequenos negócios: se o site está no ar, com o cadeado em dia, rápido e trancado, e, com o acesso
do dono, as visitas, o Google e o Instagram do mês, com o rumo do mês seguinte. Da família Linu; o conserto fica com o
irmão certo (o site com o Linu Sites, a segurança com o Linu Seguro, as redes com o Digital Linu).

## O objeto: o farol, visto do mar
A LinuPedia é o caderno de expedição; o Linu Sites, a estação; o Digital Linu, a ilha de edição; o Linu Seguro, o iglu.
O Linu Farol é **o farol**: quem olha de fora, de longe, e avisa.
- **De dia, a torre branca de faixas vermelhas;** à noite (modo escuro), a lanterna acesa e o facho. A faixa vermelha
  e branca é a borda de cima das seções alternadas.
- **O painel é a “lista de faróis”** (o registro técnico de cada farol que a Marinha publica): uma entrada por site,
  com quatro luzes (Luz, Cadeado, Rapidez, Trancas), cada uma acesa, fraca ou apagada, sempre com a palavra ao lado
  da cor. A lista da página é real: os sites da família, conferidos de 6 em 6 horas (`ferramentas/ronda.py`).
- **A abertura:** o céu e o mar, o farol em pixel art (`img/farol.png`, 110 × 221, gerado pela API e levado à grade) e
  o Linu faroleiro com a luneta (`img/linu-luneta.png`, 124 × 198). À noite, `farol-noite.png`, `farol-luz.png` e
  `farol-feixe.png` (`ferramentas/farol-luz.py`). Ao trocar o tema, a lanterna acende piscando uma vez e firma, e o
  Linu dá um pulinho; só ao toque, nunca em loop; com “reduzir movimento”, sem animar.

## Três versões, cada uma com a sua composição
- **Celular (até 699 px):** coluna única; o farol e o Linu lado a lado em 1×; cada site da lista é um cartão com as
  luzes num 2 × 2; o plano completo vem primeiro; a barra de pedir fica presa embaixo e some no contato. Desde
  07/11/2026, a lista de faróis, as quatro luzes e os planos correm de lado, um cartão por vez (`scroll-snap`), com
  “Arraste para o lado” em cima, em vez de três telas de cartões empilhados.
- **Tablet (700 a 1099 px):** a abertura em panorama (o texto em cima, o farol em 2× com o facho atravessando a tela);
  a lista em duas colunas; o plano completo ocupa a linha de cima e os outros dois embaixo.
- **Computador (1100 px ou mais):** o texto ao lado do farol (o facho cortado do lado do texto); a lista vira a tabela
  do registro, uma linha por site e uma coluna por luz; as etapas numa linha, ligadas por uma rota tracejada.

## Formas e letras
- Cartões de canto quase reto (4 px), borda fina e sombra baixa; botões em pílula (a forma da lanterna). A luz é um
  círculo: cheio (acesa), meio (fraca), só o contorno (apagada).
- **Big Shoulders Display** 700 a 800 nos títulos (as placas e os números pintados no mar), **Public Sans** no texto,
  **IBM Plex Mono** nos números e nas anotações do registro. Servidas pelo site em `fontes/`, licença OFL ao lado.

## Cores
- **Dia:** fundo `#F4F7FA`, papel `#FFFFFF`, texto `#0F1E33` e `#44546A`; o **vermelho do farol** `#C81E1E` nos botões
  e destaques (5,9:1 com o branco); céu `#CFE6F5` a `#EEF6FB`; mar `#2E6E9E`.
- **Noite (modo escuro):** fundo `#06101F`, papel `#0E2038`, texto `#E8EEF6` e `#A7B6C8`; a **lanterna** `#FBBF24`
  nos botões (texto `#1A1200`) e destaques.
- **As luzes:** acesa `#15803D` (noite `#4ADE80`), fraca `#B45309` (`#FBBF24`), apagada `#B91C1C` (`#F87171`).

## Ícones
Traço 2, pontas redondas, um por luz e por número do painel (`<symbol>` do começo do `<body>`); o `i-farol` é a marca.
