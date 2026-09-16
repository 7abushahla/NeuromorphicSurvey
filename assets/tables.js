/* Table toolbars: filter chips, search, sort, row count, reset.

   Declarative. A wrapper opts in with data-table-toolbar. Any <th data-chip="Label">
   becomes a filter chip that keeps only the rows with coverage in that column. Any
   <th data-sort="text|num"> becomes sortable. Nothing else needs wiring. */

(function () {
  'use strict';

  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  function covered(td) {
    if (!td) return false;
    if (td.classList.contains('cov-full') || td.classList.contains('cov-part')) return true;
    if (td.classList.contains('cov-ment')) return true;
    // A badge cell counts as covered when it actually carries a badge.
    if (td.classList.contains('hwcell')) return !!td.querySelector('.hw');
    return false;
  }

  function build(wrap) {
    var table = $('table.ptable', wrap);
    if (!table) return;
    var ths = $$('thead th', table);
    var rows = $$('tbody tr', table);
    var total = rows.length;

    var bar = document.createElement('div');
    bar.className = 'tbl-toolbar';

    var chipDefs = [{ label: 'All', col: -1 }];
    ths.forEach(function (th, i) {
      var l = th.getAttribute('data-chip');
      if (l) chipDefs.push({ label: l, col: i });
    });

    var state = { col: -1, q: '' };

    var chipEls = chipDefs.map(function (d) {
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'chip' + (d.col === -1 ? ' active' : '');
      b.textContent = d.label;
      b.addEventListener('click', function () { state.col = (state.col === d.col ? -1 : d.col); apply(); });
      bar.appendChild(b);
      return { el: b, col: d.col };
    });

    var input = document.createElement('input');
    input.type = 'search';
    input.placeholder = 'Search this table…';
    input.setAttribute('aria-label', 'Search this table');
    input.addEventListener('input', function () { state.q = input.value.trim().toLowerCase(); apply(); });
    bar.appendChild(input);

    var reset = document.createElement('button');
    reset.type = 'button';
    reset.className = 'treset';
    reset.innerHTML = '↺ reset';
    reset.addEventListener('click', function () {
      state.col = -1; state.q = ''; input.value = '';
      if (sortState.th) { sortState.th = null; restore(); }
      apply();
    });
    bar.appendChild(reset);

    var count = document.createElement('span');
    count.className = 'tcount';
    bar.appendChild(count);

    wrap.insertBefore(bar, wrap.firstChild);

    function apply() {
      var shown = 0;
      rows.forEach(function (tr) {
        var okCol = state.col === -1 || covered(tr.cells[state.col]);
        var okQ = !state.q || tr.textContent.toLowerCase().indexOf(state.q) !== -1;
        var vis = okCol && okQ;
        tr.hidden = !vis;
        if (vis) shown++;
      });
      chipEls.forEach(function (c) { c.el.classList.toggle('active', c.col === state.col); });
      count.textContent = shown + ' / ' + total + ' rows';
    }

    /* ---- sorting ---- */
    var original = rows.slice();
    var tbody = $('tbody', table);
    var sortState = { th: null, dir: 1 };

    function restore() {
      original.forEach(function (tr) { tbody.appendChild(tr); });
      ths.forEach(function (t) { t.classList.remove('sorted'); });
    }

    ths.forEach(function (th, i) {
      var mode = th.getAttribute('data-sort');
      if (!mode) return;
      var btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'th-sort';
      btn.innerHTML = th.innerHTML + ' <span class="sort-ind">⇅</span>';
      th.textContent = '';
      th.appendChild(btn);
      btn.addEventListener('click', function () {
        sortState.dir = (sortState.th === th) ? -sortState.dir : 1;
        sortState.th = th;
        ths.forEach(function (t) { t.classList.remove('sorted'); });
        th.classList.add('sorted');
        var sorted = rows.slice().sort(function (a, b) {
          var x = (a.cells[i] ? a.cells[i].textContent : '').trim();
          var y = (b.cells[i] ? b.cells[i].textContent : '').trim();
          if (mode === 'num') {
            var nx = parseFloat(x.replace(/[^0-9.\-]/g, '')), ny = parseFloat(y.replace(/[^0-9.\-]/g, ''));
            if (isNaN(nx)) nx = -Infinity;
            if (isNaN(ny)) ny = -Infinity;
            return (nx - ny) * sortState.dir;
          }
          return x.localeCompare(y) * sortState.dir;
        });
        // The "Ours" row is the comparison anchor, so it stays last whatever the sort.
        var ours = sorted.filter(function (t) { return t.classList.contains('ours'); });
        sorted = sorted.filter(function (t) { return !t.classList.contains('ours'); }).concat(ours);
        sorted.forEach(function (tr) { tbody.appendChild(tr); });
      });
    });

    apply();
  }

  function init() { $$('.ptable-wrap[data-table-toolbar]').forEach(build); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();

/* ---------- back to top ----------
   The template ships the #toTop button; upstream its wiring lives in supplements.js,
   which is otherwise specific to that survey's tables. Only this block carries over. */
(function () {
  var toTop = document.getElementById("toTop");
  if (!toTop) return;
  document.addEventListener("scroll", function () {
    toTop.classList.toggle("show", window.scrollY > 900);
  }, { passive: true });
  toTop.addEventListener("click", function () {
    window.scrollTo({ top: 0, behavior: "smooth" });
  });
})();

/* ---------- citation affordances ----------
   Two gaps in distill's citation component, both only visible inside tables.

   1. Position. The hover card is absolutely positioned and takes its `top` from the
      citation's offsetTop. In prose both resolve against d-article and agree. Inside
      a table the browser makes the <td> the offsetParent while the card, having no
      positioned ancestor, still resolves against the document, so the two disagree
      and the card lands thousands of pixels from the pointer. d-article carries
      `contain: layout`, so it is the containing block for the card in both cases;
      measuring the citation against d-article gives the number distill's own
      arithmetic produces in prose. Prose citations are left alone, so they keep
      rendering exactly as the template renders them.

   2. Clicking. The citation shows `cursor: pointer` but has no click behaviour, here
      or upstream. A citation number should take you to the entry it names. */
(function () {
  function entryFor(cite) {
    var key = (cite.getAttribute('key') || cite.getAttribute('bibtex-key') || '')
                .split(',')[0].trim();
    if (!key) return null;
    var list = document.querySelector('d-citation-list ol.references');
    return list ? list.querySelector('[id="' + key.replace(/"/g, '\\"') + '"]') : null;
  }

  function wire(cite) {
    if (cite.dataset.wired) return;
    cite.dataset.wired = '1';

    var box = cite.shadowRoot && cite.shadowRoot.querySelector('d-hover-box');
    var article = cite.closest('d-article');
    if (box && article && cite.closest('table')) {
      cite.addEventListener('mouseover', function () {
        // After distill has set its own top, not before.
        requestAnimationFrame(function () {
          var c = cite.getBoundingClientRect(), a = article.getBoundingClientRect();
          box.style.top = Math.round(c.bottom - a.top + article.scrollTop + 10) + 'px';
        });
      });
    }

    cite.setAttribute('tabindex', '0');
    cite.setAttribute('role', 'link');
    var go = function (e) {
      var li = entryFor(cite);
      if (!li) return;
      if (e) e.preventDefault();
      li.scrollIntoView({ behavior: 'smooth', block: 'center' });
      li.classList.add('ref-flash');
      setTimeout(function () { li.classList.remove('ref-flash'); }, 1600);
    };
    cite.addEventListener('click', go);
    cite.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') go(e);
    });
  }

  /* A table's width strategy is chosen at build time from its column count, which is
     only a proxy for how wide it actually renders. Any wrapper whose content still
     overflows is switched to scrolling, so nothing is silently clipped by d-article. */
  function fixOverflow() {
    document.querySelectorAll('.ptable-wrap').forEach(function (w) {
      var over = w.scrollWidth > w.clientWidth + 2;
      w.classList.toggle('t-scroll', over);
      w.classList.toggle('t1-wide', w.classList.contains('t1-wide') && !over);
    });
  }

  function run() {
    document.querySelectorAll('d-cite').forEach(wire);
    fixOverflow();
  }

  if (document.readyState === 'complete') run();
  else window.addEventListener('load', run);
  // The bibliography is fetched asynchronously; catch anything upgraded after load.
  setTimeout(run, 2000);
  var t; window.addEventListener('resize', function () {
    clearTimeout(t); t = setTimeout(fixOverflow, 150);
  }, { passive: true });
})();
