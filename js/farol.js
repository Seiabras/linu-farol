/* Linu Farol (07/11/2026): o tema com a lanterna, o menu do celular, a barra de pedir do celular e o formulário que
   escreve a mensagem. Sem biblioteca; sem JavaScript, a página inteira continua lá (a lista de faróis vem pronta
   no HTML, escrita pela ronda). */
(function () {
  "use strict";
  var raiz = document.documentElement;
  var menosMovimento = window.matchMedia("(prefers-reduced-motion: reduce)");
  function guardar(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  function ler(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }

  /* 1. Tema: sem escolha, segue o sistema. Ao escurecer, a lanterna acende (pisca uma vez e firma) e o Linu dá um
        pulinho; ao clarear, apaga. Só ao toque, nunca sozinho. */
  var botaoTema = document.querySelector("[data-tema]");
  var sistemaEscuro = window.matchMedia("(prefers-color-scheme: dark)");
  var cena = document.querySelector("[data-cena]");
  var legenda = document.querySelector("[data-cena-legenda]");
  function escuroAgora() { return raiz.dataset.theme ? raiz.dataset.theme === "dark" : sistemaEscuro.matches; }
  function rotular() {
    var escuro = escuroAgora();
    botaoTema.setAttribute("aria-label", escuro ? "Mudar para o modo claro" : "Mudar para o modo escuro");
    botaoTema.title = escuro ? "Modo claro" : "Modo escuro";
  }
  botaoTema.addEventListener("click", function () {
    raiz.dataset.theme = escuroAgora() ? "light" : "dark";
    guardar("tema", raiz.dataset.theme);
    rotular();
    var escuro = raiz.dataset.theme === "dark";
    legenda.textContent = escuro ? "Anoiteceu: o Linu acendeu a lanterna do farol." : "Amanheceu: o Linu apagou a lanterna.";
    if (menosMovimento.matches) return;
    cena.classList.remove("acendeu", "apagou");
    void cena.offsetWidth;
    cena.classList.add(escuro ? "acendeu" : "apagou");
  });
  sistemaEscuro.addEventListener("change", rotular);
  rotular();

  /* 2. Menu do celular e do tablet */
  var menuBotao = document.querySelector("[data-menu]");
  var menuLinks = document.getElementById("menu-links");
  function fecharMenu() { menuLinks.classList.remove("aberto"); menuBotao.setAttribute("aria-expanded", "false"); }
  menuBotao.addEventListener("click", function () {
    var abrir = !menuLinks.classList.contains("aberto");
    menuLinks.classList.toggle("aberto", abrir);
    menuBotao.setAttribute("aria-expanded", String(abrir));
  });
  menuLinks.addEventListener("click", function (e) { if (e.target.closest("a")) fecharMenu(); });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") fecharMenu(); });

  /* 3. A barra de pedir (celular): some quando o contato já está na tela */
  var barra = document.querySelector("[data-barra]");
  var contato = document.getElementById("contato");
  if (barra && "IntersectionObserver" in window) {
    new IntersectionObserver(function (itens) {
      barra.classList.toggle("escondida", itens[0].isIntersecting);
    }, { rootMargin: "0px 0px -20% 0px" }).observe(contato);
  }

  /* 4. Formulário: validação na hora e a mensagem pronta para o WhatsApp e o e-mail */
  var form = document.querySelector("[data-formulario]");
  function campo(k) { return document.getElementById(k); }
  var campos = { nome: campo("nome"), negocio: campo("negocio") };
  var avisos = { nome: "Escreva o seu nome.", negocio: "Conte o tipo de negócio e a cidade." };
  var whats = form.querySelector('[data-enviar="whatsapp"]');
  var email = form.querySelector('[data-enviar="email"]');
  function plano() { var r = form.querySelector('[name="plano"]:checked'); return r ? r.value : ""; }
  ["nome", "negocio", "endereco", "mensagem"].forEach(function (k) {
    var v = ler("farol-" + k);
    if (v) campo(k).value = v;
    campo(k).addEventListener("input", function () { guardar("farol-" + k, campo(k).value); escrever(); });
  });
  form.querySelectorAll('[name="plano"]').forEach(function (r) { r.addEventListener("change", escrever); });
  document.querySelectorAll("[data-escolher]").forEach(function (a) {
    a.addEventListener("click", function () {
      var r = form.querySelector('[name="plano"][value="' + a.dataset.escolher + '"]');
      if (r) { r.checked = true; escrever(); }
    });
  });
  function conferir(k, mostrar) {
    var ok = campos[k].value.trim().length >= 2;
    if (mostrar || ok) {
      document.getElementById(k + "-erro").textContent = ok ? "" : avisos[k];
      campos[k].setAttribute("aria-invalid", String(!ok));
    }
    return ok;
  }
  Object.keys(campos).forEach(function (k) {
    campos[k].addEventListener("blur", function () { if (campos[k].value) conferir(k, true); });
    campos[k].addEventListener("input", function () { conferir(k, false); });
  });
  function texto() {
    var p = ["Olá, Linu Farol! Quero o painel do mês."];
    if (campo("nome").value.trim()) p.push("Nome: " + campo("nome").value.trim());
    if (campo("negocio").value.trim()) p.push("Negócio: " + campo("negocio").value.trim());
    if (campo("endereco").value.trim()) p.push("Site: " + campo("endereco").value.trim());
    if (plano()) p.push("Plano: " + plano());
    if (campo("mensagem").value.trim()) p.push(campo("mensagem").value.trim());
    return p.join("\n");
  }
  function escrever() {
    var t = encodeURIComponent(texto());
    whats.href = "https://wa.me/5561996672610?text=" + t;
    email.href = "mailto:contato@linupedia.com.br?subject=" + encodeURIComponent("Linu Farol") + "&body=" + t;
  }
  // o pedido também fica registrado (linuarquivos/servidor/linu-pedidos); se falhar, a conversa segue igual
  function registrar(canal) {
    try {
      var robo = form.querySelector('[name="site_extra"]');
      var dados = {
        nome: campo("nome").value.trim(), negocio: campo("negocio").value.trim(),
        pacote: [plano(), campo("endereco").value.trim()].filter(Boolean).join(" · "),
        estimativa: "", mensagem: campo("mensagem").value.trim(), canal: canal, site_extra: robo ? robo.value : ""
      };
      if (navigator.sendBeacon) navigator.sendBeacon("/api/pedido", new Blob([JSON.stringify(dados)], { type: "application/json" }));
    } catch (e) {}
  }
  [whats, email].forEach(function (a) {
    a.addEventListener("click", function (e) {
      if (!(conferir("nome", true) & conferir("negocio", true))) {
        e.preventDefault();
        form.querySelector('[aria-invalid="true"]').focus();
        return;
      }
      registrar(a === email ? "email" : "whatsapp");
      a.classList.add("enviado");
      setTimeout(function () { a.classList.remove("enviado"); }, 1600);
    });
  });
  escrever();

  /* 5. Voltar ao topo, sem deixar o # no endereço */
  document.querySelector("[data-voltar]").addEventListener("click", function (e) {
    e.preventDefault();
    window.scrollTo({ top: 0, behavior: menosMovimento.matches ? "auto" : "smooth" });
  });
})();
