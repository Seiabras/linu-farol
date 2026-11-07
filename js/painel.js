/* O painel de cada cliente (07/11/2026): o tema (como na página do farol, sem a cena) e o “Salvar em PDF”, que abre a
   impressão do navegador (o css/painel.css deixa a página em papel branco). Sem JavaScript, o painel está todo lá. */
(function () {
  "use strict";
  var raiz = document.documentElement;
  var sistemaEscuro = window.matchMedia("(prefers-color-scheme: dark)");
  var botao = document.querySelector("[data-tema]");
  function escuro() { return raiz.dataset.theme ? raiz.dataset.theme === "dark" : sistemaEscuro.matches; }
  function rotular() {
    botao.setAttribute("aria-label", escuro() ? "Mudar para o modo claro" : "Mudar para o modo escuro");
    botao.title = escuro() ? "Modo claro" : "Modo escuro";
  }
  if (botao) {
    rotular();
    botao.addEventListener("click", function () {
      raiz.dataset.theme = escuro() ? "light" : "dark";
      try { localStorage.setItem("tema", raiz.dataset.theme); } catch (e) {}
      rotular();
    });
  }
  Array.prototype.forEach.call(document.querySelectorAll("[data-pdf]"), function (b) {
    b.addEventListener("click", function () { window.print(); });
  });
})();
