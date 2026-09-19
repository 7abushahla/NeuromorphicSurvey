/* Hovering an in-text equation reference (MathJax's own \eqref links, tagged via
   tex.tags: 'ams' in site/shell-head.html) shows the numbered equation itself,
   the same idea as a citation's own hover card. MathJax puts the tag id on the
   small label cell in its own side table, not on the equation, so the id is
   only a hook to find the enclosing mjx-container, the whole equation block,
   which is what gets cloned into the card. */
(function () {
  var card, closeTimer;

  function cancelClose() { clearTimeout(closeTimer); }
  function scheduleClose() { closeTimer = setTimeout(hide, 250); }

  function ensureCard() {
    if (card) return card;
    card = document.createElement('div');
    card.className = 'eq-hover-card';
    card.setAttribute('aria-hidden', 'true');
    card.addEventListener('mouseenter', cancelClose);
    card.addEventListener('mouseleave', scheduleClose);
    document.body.appendChild(card);
    return card;
  }

  function targetFor(link) {
    var href = link.getAttribute('href') || '';
    if (href.charAt(0) !== '#') return null;
    var id;
    try { id = decodeURIComponent(href.slice(1)); } catch (e) { return null; }
    var label = document.getElementById(id);
    return label ? label.closest('mjx-container') : null;
  }

  function stripIds(root) {
    if (root.id) root.removeAttribute('id');
    root.querySelectorAll('[id]').forEach(function (n) { n.removeAttribute('id'); });
  }

  function show(link, eqEl) {
    var c = ensureCard();
    c.innerHTML = '';
    var clone = eqEl.cloneNode(true);
    stripIds(clone);
    c.appendChild(clone);
    c.style.opacity = '0';
    c.style.display = 'block';
    requestAnimationFrame(function () {
      var r = link.getBoundingClientRect();
      var cw = c.offsetWidth, ch = c.offsetHeight;
      var left = Math.min(Math.max(8, r.left), window.innerWidth - cw - 8);
      var top = r.bottom + 10;
      if (top + ch > window.innerHeight - 8) top = r.top - ch - 10;
      c.style.left = Math.round(left) + 'px';
      c.style.top = Math.round(Math.max(8, top)) + 'px';
      c.style.opacity = '1';
    });
  }

  function hide() {
    if (card) card.style.opacity = '0';
  }

  function wire(link) {
    if (link.dataset.eqWired) return;
    link.dataset.eqWired = '1';
    var eqEl = targetFor(link);
    if (!eqEl) return;
    var open = function () { cancelClose(); show(link, eqEl); };
    link.addEventListener('mouseenter', open);
    link.addEventListener('mouseleave', scheduleClose);
    link.addEventListener('focus', open);
    link.addEventListener('blur', hide);
  }

  function run() {
    document.querySelectorAll('d-article a[href^="#mjx-eqn"]').forEach(wire);
  }

  if (window.MathJax && window.MathJax.startup && window.MathJax.startup.promise) {
    window.MathJax.startup.promise.then(run);
  }
  window.addEventListener('load', run);
  // MathJax's own typesetting can finish after load on a slow connection.
  setTimeout(run, 2000);
})();
