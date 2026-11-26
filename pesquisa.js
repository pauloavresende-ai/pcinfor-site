/* Pesquisa de artigos · PCinfor
   Sem dependências. Lê os cartões da página inicial (index.html):
   - na página inicial, usa a própria página;
   - nas outras páginas, vai buscar o index.html quando o cliente toca na caixa.
   Ao escrever, mostra sugestões; ao carregar em Enter, abre a página inicial
   só com os artigos encontrados (index.html?q=...). Sem JavaScript, o formulário
   continua a levar o cliente à página inicial. */
(function () {
  'use strict';
  var forms = document.querySelectorAll('form.pesquisa');
  if (!forms.length || !window.URL || !document.querySelector) return;

  var NA_INICIAL = !!document.getElementById('equipamentos') && !!document.querySelector('.categoria');
  var SINONIMOS = {
    'portateis': 'portatil portateis laptop notebook',
    'computadores': 'computador computadores pc desktop torre secretaria mini',
    'all-in-one': 'all in one allinone tudo em um',
    'apple': 'apple mac imac macbook macos',
    'monitores': 'monitor monitores ecra ecras',
    'packs': 'pack packs conjunto monitor'
  };

  function norm(s) {
    return (s || '').toLowerCase()
      .normalize('NFD').replace(/[̀-ͯ]/g, '')
      .replace(/[^a-z0-9.,+]+/g, ' ')
      .replace(/\s+/g, ' ').trim();
  }
  function palavras(q) {
    return norm(q).split(' ').filter(function (p) { return p && p !== 'de' && p !== 'e' && p !== 'com'; });
  }
  function querPacks(ps) {
    return ps.some(function (p) { return p === 'pack' || p === 'packs' || p === 'conjunto'; });
  }

  /* ---------- Ler os artigos de um documento ---------- */
  function lerArtigos(doc, base) {
    var lista = [];
    function abs(u) { try { return new URL(u, base).href; } catch (e) { return u; } }
    doc.querySelectorAll('.categoria').forEach(function (cat) {
      var id = cat.id || '';
      var catNome = (cat.querySelector('.categoria-titulo h3') || {}).textContent || '';
      cat.querySelectorAll('article.produto-destaque').forEach(function (art) {
        if (art.closest('.categoria') !== cat) return;
        var h3 = art.querySelector('h3');
        var link = art.querySelector('a.link-detalhes') || art.querySelector('a.foto');
        var img = art.querySelector('.foto img');
        var preco = art.querySelector('.preco');
        var href = link ? link.getAttribute('href') : '';
        var nome = h3 ? h3.textContent.trim() : '';
        lista.push({
          el: art, pack: false, cat: id, catNome: catNome.trim(),
          nome: nome, href: abs(href), img: img ? abs(img.getAttribute('src')) : '',
          preco: preco ? preco.textContent.trim() : '',
          nNome: norm(nome),
          texto: norm(art.textContent + ' ' + href.replace(/[\/-]/g, ' ') + ' ' + (SINONIMOS[id] || ''))
        });
      });
      cat.querySelectorAll('.pack-lista').forEach(function (bloco) {
        if (bloco.closest('.categoria') !== cat) return;
        var h4 = bloco.querySelector('h4');
        var monitor = h4 ? h4.textContent.replace(/^.*?\+\s*/, '').trim() : 'monitor';
        bloco.querySelectorAll('a.pack-linha').forEach(function (a) {
          var nomeEl = a.querySelector('.pack-nome');
          var comp = nomeEl && nomeEl.firstChild ? nomeEl.firstChild.textContent.trim() : '';
          var img = a.querySelector('.pack-foto');
          var preco = a.querySelector('.pack-precos b');
          var href = a.getAttribute('href') || '';
          var nome = 'Pack ' + comp + ' + ' + monitor;
          lista.push({
            el: a, bloco: bloco, pack: true, cat: id, catNome: catNome.trim(),
            nome: nome, href: abs(href), img: img ? abs(img.getAttribute('src')) : '',
            preco: preco ? preco.textContent.trim() : '',
            nNome: norm(nome),
            texto: norm(nome + ' ' + a.textContent + ' ' + (h4 ? h4.textContent : '') + ' ' + href.replace(/[\/#-]/g, ' ') + ' ' + SINONIMOS.packs)
          });
        });
      });
    });
    lista.forEach(function (it) { it.textoJunto = it.texto.replace(/ /g, ''); });
    return lista;
  }

  function procurar(lista, q) {
    var ps = palavras(q);
    if (!ps.length) return { ps: ps, artigos: [], packs: [] };
    var artigos = [], packs = [];
    lista.forEach(function (it, i) {
      var ok = ps.every(function (p) {
        /* números sozinhos (24, 16, 840) contam só como palavra inteira: 24 encontra 24″ e não 249€ */
        if (/^[0-9]+$/.test(p)) return new RegExp('(^| )' + p + '($| |[a-z])').test(it.texto);
        return it.texto.indexOf(p) > -1 || it.textoJunto.indexOf(p) > -1;
      });
      if (!ok) return;
      var noNome = ps.filter(function (p) { return it.nNome.indexOf(p) > -1 || (' ' + (SINONIMOS[it.cat] || '') + ' ').indexOf(' ' + p + ' ') > -1; }).length;
      (it.pack ? packs : artigos).push({ it: it, pontos: noNome * 1000 - i });
    });
    function ord(a, b) { return b.pontos - a.pontos; }
    return {
      ps: ps,
      artigos: artigos.sort(ord).map(function (x) { return x.it; }),
      packs: packs.sort(ord).map(function (x) { return x.it; })
    };
  }

  /* Por omissão mostra os artigos; os packs só quando se pede "pack"
     ou quando não há nenhum artigo com aquele nome. */
  function resultados(lista, q) {
    var r = procurar(lista, q);
    var mostrar = querPacks(r.ps) ? r.packs.concat(r.artigos) : (r.artigos.length ? r.artigos : r.packs);
    return { r: r, mostrar: mostrar };
  }

  /* ---------- Artigos disponíveis ---------- */
  var artigosPromessa = null;
  function obterArtigos(form) {
    if (artigosPromessa) return artigosPromessa;
    if (NA_INICIAL) {
      artigosPromessa = Promise.resolve(lerArtigos(document, location.href));
      return artigosPromessa;
    }
    var url = new URL(form.getAttribute('action') || 'index.html', location.href);
    url.hash = ''; url.search = '';
    if (!window.fetch || !window.DOMParser || url.protocol === 'file:') {
      artigosPromessa = Promise.resolve([]);
      return artigosPromessa;
    }
    artigosPromessa = fetch(url.href, { credentials: 'same-origin' })
      .then(function (res) { if (!res.ok) throw new Error(res.status); return res.text(); })
      .then(function (html) { return lerArtigos(new DOMParser().parseFromString(html, 'text/html'), url.href); })
      .catch(function () { return []; });
    return artigosPromessa;
  }

  function urlResultados(form, q) {
    var url = new URL(form.getAttribute('action') || 'index.html', location.href);
    url.search = '?q=' + encodeURIComponent(q);
    url.hash = '#equipamentos';
    return url.href;
  }

  /* ---------- Sugestões por baixo da caixa ---------- */
  var MAX_SUGESTOES = 6;
  var contador = 0;

  function ligar(form) {
    var input = form.querySelector('input[name="q"]');
    if (!input) return;
    contador += 1;
    var idLista = 'pesquisa-sugestoes-' + contador;
    var caixa = document.createElement('div');
    caixa.className = 'pesquisa-sugestoes';
    caixa.id = idLista;
    caixa.setAttribute('role', 'listbox');
    caixa.setAttribute('aria-label', 'Sugestões');
    caixa.hidden = true;
    form.appendChild(caixa);
    input.setAttribute('role', 'combobox');
    input.setAttribute('aria-autocomplete', 'list');
    input.setAttribute('aria-expanded', 'false');
    input.setAttribute('aria-controls', idLista);

    var ativo = -1, opcoes = [], pedido = 0;

    function fechar() {
      caixa.hidden = true; ativo = -1;
      input.setAttribute('aria-expanded', 'false');
      input.removeAttribute('aria-activedescendant');
    }
    function marcar(i) {
      opcoes.forEach(function (o, j) { o.classList.toggle('ativo', j === i); o.setAttribute('aria-selected', j === i ? 'true' : 'false'); });
      ativo = i;
      if (i > -1 && opcoes[i]) { input.setAttribute('aria-activedescendant', opcoes[i].id); opcoes[i].scrollIntoView({ block: 'nearest' }); }
      else input.removeAttribute('aria-activedescendant');
    }
    function linha(cls, html, href) {
      var a = document.createElement('a');
      a.className = cls; a.href = href; a.innerHTML = html;
      a.setAttribute('role', 'option');
      a.id = idLista + '-' + caixa.children.length;
      a.tabIndex = -1;
      caixa.appendChild(a);
      return a;
    }
    function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }

    function mostrar() {
      var q = input.value.trim();
      var este = ++pedido;
      if (q.length < 2) { fechar(); return; }
      obterArtigos(form).then(function (lista) {
        if (este !== pedido) return;
        caixa.innerHTML = '';
        if (!lista.length) { fechar(); return; }
        var res = resultados(lista, q).mostrar;
        if (!res.length) {
          var vazio = document.createElement('p');
          vazio.className = 'sug-vazio';
          vazio.innerHTML = 'Não encontrámos «' + esc(q) + '». <a href="https://wa.me/351963401241?text=' +
            encodeURIComponent('Olá! Procuro: ' + q + '. Têm disponível?') + '" target="_blank" rel="noopener">Pergunte no WhatsApp</a>';
          caixa.appendChild(vazio);
        }
        res.slice(0, MAX_SUGESTOES).forEach(function (it) {
          linha('sug', (it.img ? '<img src="' + esc(it.img) + '" alt="" width="56" height="42" loading="lazy">' : '<span></span>') +
            '<span class="sug-nome">' + esc(it.nome) + '<small>' + esc(it.pack ? 'Pack computador + monitor' : it.catNome) + '</small></span>' +
            '<b class="sug-preco">' + esc(it.preco) + '</b>', it.href);
        });
        if (res.length) {
          linha('sug-todos', res.length > MAX_SUGESTOES ? 'Ver os ' + res.length + ' resultados →' : 'Ver resultados na página →', urlResultados(form, q));
        }
        opcoes = Array.prototype.slice.call(caixa.querySelectorAll('[role="option"]'));
        caixa.hidden = false; ativo = -1;
        input.setAttribute('aria-expanded', 'true');
      });
    }

    var espera;
    input.addEventListener('input', function () { clearTimeout(espera); espera = setTimeout(mostrar, 120); });
    input.addEventListener('focus', function () { obterArtigos(form); if (input.value.trim().length > 1) mostrar(); });
    input.addEventListener('keydown', function (e) {
      if (caixa.hidden) return;
      if (e.key === 'ArrowDown') { e.preventDefault(); marcar(Math.min(ativo + 1, opcoes.length - 1)); }
      else if (e.key === 'ArrowUp') { e.preventDefault(); marcar(Math.max(ativo - 1, -1)); }
      else if (e.key === 'Escape') { fechar(); }
      else if (e.key === 'Enter' && ativo > -1 && opcoes[ativo]) { e.preventDefault(); opcoes[ativo].click(); }
    });
    caixa.addEventListener('mousedown', function (e) { e.preventDefault(); });
    caixa.addEventListener('click', function (e) {
      var a = e.target.closest('a.sug-todos');
      if (a && NA_INICIAL) { e.preventDefault(); filtrarPagina(input.value, true); fechar(); input.blur(); }
    });
    document.addEventListener('click', function (e) { if (!form.contains(e.target)) fechar(); });
    input.addEventListener('blur', function () { setTimeout(function () { if (!form.contains(document.activeElement)) fechar(); }, 150); });

    form.addEventListener('submit', function (e) {
      var q = input.value.trim();
      if (!q) { e.preventDefault(); input.focus(); return; }
      if (NA_INICIAL) { e.preventDefault(); fechar(); input.blur(); filtrarPagina(q, true); }
    });
  }

  /* ---------- Página inicial: mostrar só os artigos encontrados ---------- */
  var aviso = null;
  function filtrarPagina(q, rolar) {
    q = (q || '').trim();
    var lista = lerArtigosPagina();
    var equip = document.getElementById('equipamentos');
    var navCats = equip && equip.querySelector('nav.categorias');
    forms.forEach(function (f) { var i = f.querySelector('input[name="q"]'); if (i) i.value = q; });

    try {
      var u = new URL(location.href);
      if (q) u.searchParams.set('q', q); else u.searchParams.delete('q');
      history.replaceState(null, '', u.pathname + u.search + u.hash);
    } catch (e) { /* sem histórico, segue */ }

    if (!q) {
      document.body.classList.remove('a-pesquisar');
      lista.forEach(function (it) { it.el.hidden = false; if (it.bloco) it.bloco.hidden = false; });
      document.querySelectorAll('#equipamentos .categoria').forEach(function (c) { c.hidden = false; c.classList.remove('sem-proprios'); });
      if (navCats) navCats.hidden = false;
      if (aviso) aviso.hidden = true;
      return;
    }

    var res = resultados(lista, q).mostrar;
    var mostrar = new Set(res.map(function (it) { return it.el; }));
    lista.forEach(function (it) { it.el.hidden = !mostrar.has(it.el); });
    document.querySelectorAll('#equipamentos .pack-lista').forEach(function (b) {
      b.hidden = !b.querySelector('a.pack-linha:not([hidden])');
    });
    document.querySelectorAll('#equipamentos .categoria').forEach(function (c) {
      var visiveis = Array.prototype.slice.call(c.querySelectorAll('article.produto-destaque:not([hidden]), a.pack-linha:not([hidden])'));
      c.hidden = !visiveis.length;
      /* uma categoria pode ter outra dentro: se só a de dentro tem resultados, esconde o título da de fora */
      c.classList.toggle('sem-proprios', !visiveis.some(function (el) { return el.closest('.categoria') === c; }));
    });
    if (navCats) navCats.hidden = true;
    document.body.classList.add('a-pesquisar');

    if (!aviso) {
      aviso = document.createElement('div');
      aviso.className = 'pesquisa-resultado';
      aviso.setAttribute('role', 'status');
      var primeira = equip.querySelector('.categoria');
      primeira.parentNode.insertBefore(aviso, primeira);
      aviso.addEventListener('click', function (e) {
        if (e.target.closest('.js-limpar')) { e.preventDefault(); filtrarPagina('', false); equip.scrollIntoView(); }
      });
    }
    var n = res.length;
    var wa = 'https://wa.me/351963401241?text=' + encodeURIComponent('Olá! Procuro: ' + q + '. Têm disponível?');
    var t = document.createElement('span'); t.textContent = q; var qs = t.innerHTML;
    aviso.innerHTML = n
      ? '<p><strong>' + n + (n === 1 ? ' artigo encontrado' : ' artigos encontrados') + '</strong> para «' + qs + '».</p>' +
        '<a class="btn btn-whats btn-pequeno js-limpar" href="#equipamentos">Ver todos os artigos</a>'
      : '<p><strong>Não encontrámos «' + qs + '».</strong> Experimente outra palavra (marca, modelo, i5, 16GB, 24″) ou pergunte-nos: podemos ter ou encomendar.</p>' +
        '<span class="pesquisa-resultado-botoes"><a class="btn btn-whats btn-pequeno" href="' + wa + '" target="_blank" rel="noopener">Perguntar no WhatsApp</a>' +
        '<a class="btn btn-whats btn-pequeno js-limpar" href="#equipamentos">Ver todos os artigos</a></span>';
    aviso.hidden = false;
    if (rolar) aviso.scrollIntoView();
  }

  var artigosPagina = null;
  function lerArtigosPagina() {
    if (!artigosPagina) artigosPagina = lerArtigos(document, location.href);
    return artigosPagina;
  }

  forms.forEach(ligar);

  /* Se o cliente escolher uma categoria durante a pesquisa, volta a mostrar tudo */
  if (NA_INICIAL) {
    window.addEventListener('hashchange', function () {
      if (!document.body.classList.contains('a-pesquisar')) return;
      var alvo = document.getElementById(location.hash.slice(1));
      if (alvo && (alvo.closest('#equipamentos') || alvo.id === 'equipamentos')) {
        filtrarPagina('', false);
        alvo.scrollIntoView();
      }
    });
  }

  if (NA_INICIAL) {
    var q0 = '';
    try { q0 = new URL(location.href).searchParams.get('q') || ''; } catch (e) { /* nada */ }
    if (q0.trim()) {
      filtrarPagina(q0, false);
      var rolar = function () { if (aviso) aviso.scrollIntoView(); };
      rolar();
      window.addEventListener('load', rolar);
    }
  }
})();
