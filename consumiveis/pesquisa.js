// Pesquisa de tinteiros e toners: por modelo de impressora ou por referência.
(function () {
  var D = window.CONSUMIVEIS || { artigos: [], impressoras: [] };
  var POR_PAGINA = 24;
  var q = document.getElementById("q");
  var fTipo = document.getElementById("f-tipo");
  var fOrigem = document.getElementById("f-origem");
  var fMarca = document.getElementById("f-marca");
  var res = document.getElementById("resultados");
  var cont = document.getElementById("contagem");
  var sug = document.getElementById("sugestoes");
  var mais = document.getElementById("mais");
  var mostrados = POR_PAGINA;

  function chave(t) {
    return String(t || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase().replace(/[^a-z0-9]/g, "");
  }
  function esc(t) {
    return String(t).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; });
  }
  function preco(v) {
    var s = v.toFixed(2).replace(".", ",");
    return (s.slice(-3) === ",00" ? s.slice(0, -3) : s) + "€";
  }

  // Texto pesquisável de cada artigo (sem espaços nem hífenes: "hl-l2350dw" = "HL L2350DW")
  D.artigos.forEach(function (a) {
    a._ref = chave(a.r);
    a._imp = a.i.map(chave);
    a._tudo = chave([a.r, a.n, a.m, a.t, a.c, a.o].join(" ")) + "|" + a._imp.join("|");
  });
  D.impressoras.forEach(function (i) { i._k = chave(i.n); });

  function termos(texto) {
    return String(texto || "").split(/\s+/).map(chave).filter(Boolean);
  }

  function pontuar(a, ts, kq) {
    if (!ts.length) return 1;
    for (var j = 0; j < ts.length; j++) if (a._tudo.indexOf(ts[j]) < 0) return 0;
    if (a._ref === kq) return 100;
    if (a._imp.indexOf(kq) >= 0) return 80;
    if (a._ref.indexOf(kq) === 0) return 60;
    for (var k = 0; k < a._imp.length; k++) if (a._imp[k].indexOf(kq) >= 0) return 40;
    return 10;
  }

  function cartao(a) {
    var para = a.i.slice(0, 2).join(", ") + (a.i.length > 2 ? " e mais " + (a.i.length - 2) : "");
    var foto = a.f ? '<img src="' + esc(a.f) + '" alt="' + esc(a.n) + '" loading="lazy">' : a.g;
    return '<a class="item-consumivel" href="' + a.s + '/index.html">' +
      '<span class="item-foto">' + foto + "</span>" +
      '<span class="etiquetas"><span class="etiqueta forte">' + esc(a.o) + "</span>" +
      (a.e ? '<span class="etiqueta ok">Em stock</span>' : '<span class="etiqueta">Por encomenda</span>') + "</span>" +
      '<span class="item-nome">' + esc(a.n) + "</span>" +
      '<span class="item-ref">Ref. ' + esc(a.r) + "</span>" +
      '<span class="item-para">' + (a.i.length ? "Para " + esc(para) : "") + "</span>" +
      '<span class="item-preco">' + preco(a.p) + "</span></a>";
  }

  function atualizar(manterPagina) {
    if (!manterPagina) mostrados = POR_PAGINA;
    var texto = q.value.trim();
    var ts = termos(texto);
    var kq = chave(texto);
    var lista = [];
    D.artigos.forEach(function (a) {
      if (fTipo.value && a.t !== fTipo.value) return;
      if (fOrigem.value && a.o !== fOrigem.value) return;
      if (fMarca.value && a.m !== fMarca.value) return;
      var s = pontuar(a, ts, kq);
      if (s) lista.push({ a: a, s: s });
    });
    lista.sort(function (x, y) {
      return y.s - x.s || (y.a.e - x.a.e) || x.a.t.localeCompare(y.a.t) || x.a.p - y.a.p;
    });

    // Impressoras que correspondem ao que foi escrito
    var imps = [];
    if (kq.length >= 2) {
      D.impressoras.forEach(function (i) {
        for (var j = 0; j < ts.length; j++) if (i._k.indexOf(ts[j]) < 0) return;
        imps.push(i);
      });
    }
    if (imps.length) {
      sug.hidden = false;
      sug.innerHTML = '<span class="sugestoes-titulo">Impressoras:</span>' + imps.slice(0, 10).map(function (i) {
        return '<a class="chip" href="impressora/' + i.s + '/index.html">' + esc(i.n) + " <small>" + i.q + "</small></a>";
      }).join("") + (imps.length > 10 ? '<span class="chip-mais">e mais ' + (imps.length - 10) + "</span>" : "");
    } else {
      sug.hidden = true;
      sug.innerHTML = "";
    }

    cont.textContent = !D.artigos.length ? "O catálogo está a ser preparado. Fale connosco no WhatsApp." :
      lista.length === 0 ? "Não encontrámos nada com “" + texto + "”. Experimente só o número do modelo (ex.: 2720) ou pergunte-nos no WhatsApp." :
      (texto ? lista.length + (lista.length === 1 ? " artigo para “" : " artigos para “") + texto + "”" :
        lista.length + " artigos");
    res.innerHTML = lista.slice(0, mostrados).map(function (x) { return cartao(x.a); }).join("");
    mais.hidden = lista.length <= mostrados;

    var url = new URL(location.href);
    if (texto) url.searchParams.set("q", texto); else url.searchParams.delete("q");
    history.replaceState(null, "", url);
  }

  var t;
  q.addEventListener("input", function () { clearTimeout(t); t = setTimeout(function () { atualizar(); }, 120); });
  q.form.addEventListener("submit", function (ev) { ev.preventDefault(); atualizar(); q.blur(); });
  [fTipo, fOrigem, fMarca].forEach(function (s) { s.addEventListener("change", function () { atualizar(); }); });
  mais.addEventListener("click", function () { mostrados += POR_PAGINA; atualizar(true); });

  var inicial = new URLSearchParams(location.search).get("q");
  if (inicial) q.value = inicial;
  atualizar();
})();
