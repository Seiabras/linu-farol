/* Movimento de página (07/11/2026): as entradas de texto e de imagem ao rolar, por atributo, sem biblioteca e sem
   CSS. Guia, catálogo e regras: README.md desta pasta. O original mora em linuarquivos/modelos/ferramentas/movimento/;
   cada site tem uma cópia em js/ (sincronizar-familia.py).

   No HTML:
     data-mov="sobe"      sobe 24 px e aparece (o padrão: parágrafo, cartão, botão)
     data-mov="aparece"   só aparece
     data-mov="lado"      vem da esquerda (lista de itens, endereço)
     data-mov="palavras"  título que sobe palavra por palavra, por baixo de uma máscara
     data-mov="cortina"   imagem que abre de cima para baixo (clip-path); serve para pixel art (sem escala)
     data-mov="foto"      foto que abre e assenta (escala 1,12 → 1); NÃO usar em pixel art
     data-mov="traco"     linha ou régua que se desenha da esquerda (scaleX)
     data-mov-grupo       no pai: cada filho entra em cascata (80 ms entre um e outro, no máximo 6 passos);
                          o valor diz o efeito dos filhos (data-mov-grupo="sobe"); vazio = "sobe"
     data-mov-atraso="200"  espera extra em ms

   Regras que o script cumpre sozinho:
   - cada elemento anima uma vez, quando entra na tela (um observer só);
   - o que já está na tela ao carregar não some para reaparecer;
   - sem JavaScript, com "menos movimento" ou com ?static=1 na URL, tudo aparece pronto, sem animar;
   - só opacity, transform e clip-path, pela API de animação do navegador (a CSP dos sites bloqueia estilo embutido;
     a API não é estilo embutido). */
(function () {
  "use strict";
  if (!("animate" in Element.prototype) || !("IntersectionObserver" in window)) return;
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  if (/[?&]static=1\b/.test(location.search)) return;

  var SAIDA = "cubic-bezier(.2, .8, .2, 1)";   // desacelera forte, sem quicar
  var EFEITOS = {
    sobe: { q: [{ opacity: 0, transform: "translateY(24px)" }, { opacity: 1, transform: "none" }], d: 700 },
    aparece: { q: [{ opacity: 0 }, { opacity: 1 }], d: 600 },
    lado: { q: [{ opacity: 0, transform: "translateX(-20px)" }, { opacity: 1, transform: "none" }], d: 650 },
    cortina: { q: [{ clipPath: "inset(0 0 100% 0)" }, { clipPath: "inset(0 0 0% 0)" }], d: 1100, e: "cubic-bezier(.7, 0, .2, 1)" },
    foto: { q: [{ clipPath: "inset(0 0 100% 0)", transform: "scale(1.12)" }, { clipPath: "inset(0 0 0% 0)", transform: "scale(1)" }], d: 1300, e: "cubic-bezier(.7, 0, .2, 1)" },
    traco: { q: [{ transform: "scaleX(0)", transformOrigin: "left center" }, { transform: "scaleX(1)", transformOrigin: "left center" }], d: 800 },
    palavra: { q: [{ transform: "translateY(110%)" }, { transform: "none" }], d: 800 }
  };

  var pendentes = [];   // [elemento, animação]
  var obs = new IntersectionObserver(function (itens) {
    itens.forEach(function (item) {
      if (!item.isIntersecting) return;
      obs.unobserve(item.target);
      (item.target.__mov || []).forEach(function (a) { a.play(); });
    });
  }, { rootMargin: "0px 0px -8% 0px" });

  // a animação nasce pausada no primeiro quadro (fill: backwards) e toca quando o gatilho entra na tela
  function preparar(gatilho, el, nome, atraso) {
    var ef = EFEITOS[nome] || EFEITOS.sobe;
    var a = el.animate(ef.q, { duration: ef.d, easing: ef.e || SAIDA, delay: atraso || 0, fill: "backwards" });
    a.pause();
    (gatilho.__mov = gatilho.__mov || []).push(a);
  }

  // título palavra por palavra: cada palavra vira <span class="mov-mascara"><span>palavra</span></span>; os espaços
  // continuam texto, então o leitor de tela lê a frase inteira. A máscara (overflow: clip) é a única regra de CSS
  // que o kit pede: ver o README.
  function palavras(el, atraso) {
    var andando = el.ownerDocument.createTreeWalker(el, NodeFilter.SHOW_TEXT);
    var textos = [];
    while (andando.nextNode()) textos.push(andando.currentNode);
    var i = 0;
    textos.forEach(function (t) {
      var partes = t.nodeValue.split(/(\s+)/);
      var frag = document.createDocumentFragment();
      partes.forEach(function (p) {
        if (!p) return;
        if (/^\s+$/.test(p)) { frag.appendChild(document.createTextNode(p)); return; }
        var fora = document.createElement("span"); fora.className = "mov-mascara";
        var dentro = document.createElement("span"); dentro.textContent = p;
        fora.appendChild(dentro); frag.appendChild(fora);
        preparar(el, dentro, "palavra", (atraso || 0) + Math.min(i++, 12) * 70);
      });
      t.parentNode.replaceChild(frag, t);
    });
  }

  function ligar(el, nome, atraso, gatilho) {
    if (nome === "palavras") palavras(el, atraso);   // o próprio título é o gatilho
    else preparar(gatilho || el, el, nome, atraso);
  }

  var altura = window.innerHeight;
  function naTela(el) { return el.getBoundingClientRect().top < altura; }
  var largura = document.documentElement.clientWidth;
  function foraDeLado(el) { var r = el.getBoundingClientRect(); return r.left >= largura || r.right <= 0; }

  document.querySelectorAll("[data-mov]").forEach(function (el) {
    if (el.closest("[data-mov-grupo]") && el.parentElement.hasAttribute("data-mov-grupo")) return; // o grupo cuida
    if (naTela(el)) return;
    var gatilho = el;
    while (gatilho.parentElement && foraDeLado(gatilho)) gatilho = gatilho.parentElement;
    ligar(el, el.getAttribute("data-mov"), +el.getAttribute("data-mov-atraso") || 0, gatilho);
    obs.observe(gatilho);
  });

  document.querySelectorAll("[data-mov-grupo]").forEach(function (pai) {
    var padrao = pai.getAttribute("data-mov-grupo") || "sobe";
    var base = +pai.getAttribute("data-mov-atraso") || 0;
    Array.prototype.forEach.call(pai.children, function (filho, i) {
      if (naTela(filho)) return;
      // numa fileira que rola de lado (celular), o que está fora da tela à direita entra junto com o primeiro
      // pai visível, e não só quando alguém arrastar até ele
      var gatilho = filho;
      while (gatilho.parentElement && foraDeLado(gatilho)) gatilho = gatilho.parentElement;
      ligar(filho, filho.getAttribute("data-mov") || padrao, base + (i % 6) * 80, gatilho);
      obs.observe(gatilho);
    });
  });
})();
