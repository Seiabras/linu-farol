# Identidade de Linu Farol

Preencha ANTES de desenhar qualquer tela. É o que impede o site de ficar com cara de “feito por IA”: sem decisão,
a IA e os modelos prontos voltam para a média (fonte Inter, roxo, três cartões iguais, emoji como ícone). A pesquisa
completa está no linuarquivos, em `projetos/design-humano.md`. O Claude lê este arquivo antes de mexer em tela.
Produto da família Linu: o que é comum (o Linu, as cores, as letras, o que nunca entra) está no `IDENTIDADE-LINU.md`
do linuarquivos; aqui fica só o que é deste produto.

## O que o site é, numa frase
[Para quem, o que resolve, o que só ele tem.]

## Referências (3 a 5, de verdade)
[Sites, embalagens, lugares, livros, a fachada da loja. Para cada uma: o que exatamente queremos dela.]

## Fontes (no máximo duas famílias, licença livre, só os pesos usados)
- Título: [fonte] · por quê: [motivo ligado ao negócio]
- Texto: [fonte] · por quê: [leitura fácil no celular]

## Cores (tiradas do próprio negócio, não da moda)
- Dominante: [#…] de onde vem: [a parede da loja, o uniforme, o logo]
- Acento: [#…]
- Neutros: [fundo, texto] · contraste AA conferido no claro e no escuro

## Formas
[Arredondado, reto, carimbo, recorte de papel… Uma regra para cantos, sombras e bordas, e onde ela muda.]

## Imagens
[Fotos reais do lugar e das pessoas, desenho próprio, capturas do produto. Nada de banco de imagens nem ilustração de IA.]

## Voz
[Como o dono fala. Três palavras que ele usaria e três que nunca usaria. Exemplos de frases boas e ruins.]

## O que evitar neste site
- Emoji como ícone, em título ou em lista
- Três cartões iguais com ícone em cima, faixa de números genérica
- Títulos EM MAIÚSCULAS espaçadas
- Frases que serviriam para qualquer negócio (“simples, rápido e seguro”, “transforme”, “eleve”)
- [o que mais for específico daqui]

## Uma marca de mão
[O que este site tem que só uma pessoa faria: letra manuscrita, desenho, foto do dono, carimbo, mapa desenhado.]

## Na prática: o que a política de segurança do site não deixa (aprendido na Trupe, 23/10/2026)
- **Fontes de fora não carregam** (Google Fonts, por exemplo): baixe os `.woff2` (fontsource, licença OFL) para
  `public/fontes/`, declare com `@font-face` no CSS e só os pesos usados. Pré-carregue a do título com
  `<link rel="preload" … as="font" crossorigin>`.
- **Nada de `style="…"` no HTML nem de `<script>` dentro da página:** use classes no CSS e arquivos `.js`. Mudança de
  estilo pelo JavaScript, só pelo `elemento.style.x = …` (esse passa).
