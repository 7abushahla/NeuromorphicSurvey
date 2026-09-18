/* The neuromorphic deployment stack figure, drawn from the route view inlined ahead of it.
   assets/figure-engine.js holds the compatibility model and decides what a selection still
   reaches; this file builds the grid, paints the chip states, traces the line and writes
   the panel. Selecting anything narrows the question rather than restarting it, and a
   route that cannot complete is drawn up to its break and then snapped. */
import { createEngine } from './figure-engine.js?v=20260919a';

const view = JSON.parse(document.getElementById('nstk-data').textContent);
const E = createEngine(view);
const TC = view.toolchains;
let Q = E.blank();
let active = null;   // the toolchain id being drawn
let tipEl = null;

const $ = (s, r = document) => r.querySelector(s);
const all = (s, r = document) => Array.from(r.querySelectorAll(s));
const esc = (s) => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

/* A label names a chip, so a quick button and a typed word reach the same place. A label
   with a parenthetical also answers to its plain form, which is how the quick button
   Akida reaches the chip written Akida (event NPU). Exact labels always win. */
const BY_LABEL = new Map();
E.chips.forEach(c => BY_LABEL.set(c.label.toLowerCase(), c.id));
E.chips.forEach(c => {
  const short = c.label.replace(/\s*\(.*\)\s*$/, '').toLowerCase();
  if (short && !BY_LABEL.has(short)) BY_LABEL.set(short, c.id);
});
const keyFor = (text) => BY_LABEL.get(String(text || '').trim().toLowerCase()) || text;
/* The drawn line anchors once per ROW, not once per layer, so that the traversal inside
   the software stack (train, export, compile, run) is visible rather than collapsed. */
const rowOf = (k) => { const c = E.chips.get(k); return c ? `${c.layer}::${c.row}` : null; };
const noteText = (k) => (view.notes[k] || {}).text || (view.unreached[k] || {}).why || (view.nodes[k] || {}).summary || '';
const readOf = (k) => (view.notes[k] || {}).read || (view.unreached[k] || {}).read || '';
const SEAM_LIST = Object.values(view.seams || {}).flat();

/* ---------- build ---------- */
function build() {
  const layers = $('#nstk-layers');
  const rowHtml = (L, r) => `
      <div class="nstk-row${L.rows.length === 1 ? ' nstk-row-plain' : ''}"${r.bucket ? ` data-bucket="${r.bucket}"` : ''}>
        ${L.rows.length > 1 ? `<span class="nstk-rowlabel" data-row="${esc(r.label)}">${esc(r.label)}</span>` : ''}
        <span class="nstk-rowchips">${r.chips.map(c =>
          `<span class="nstk-chip" data-k="${esc(c.id)}" tabindex="0" role="button">${esc(c.label)}</span>`).join('')}</span>
      </div>`;
  // Rows that share a bucket sit inside one band, so the hardware layer reads as three
  // groups rather than five rows.
  const groupRows = (L) => {
    const out = [];
    L.rows.forEach(r => {
      const last = out[out.length - 1];
      if (r.bucket && last && last.bucket === r.bucket) last.rows.push(r);
      else out.push({ bucket: r.bucket || null, rows: [r] });
    });
    return out.map(g => g.bucket
      ? `<div class="nstk-bucket" data-bucket="${esc(g.bucket)}">${g.rows.map(r => rowHtml(L, r)).join('')}</div>`
      : g.rows.map(r => rowHtml(L, r)).join('')).join('');
  };
  layers.innerHTML = view.layers.map(L => {
    const rows = groupRows(L);
    const seam = ((view.seams || {})[L.id] || []).map(s =>
      `<span class="nstk-pin" data-pin="${esc(s.pin)}" data-tip="<b>${esc(s.pin)} ${esc(s.title)}.</b> ${esc(s.text)}" tabindex="0" role="button">${esc(s.pin)}</span>`).join('');
    const legend = L.id === 'hw' ? `<div class="nstk-legend" aria-label="How the hardware layer is grouped">
        <span class="nstk-legend-lead">What a run there can claim</span>
        ${view.buckets.map(b =>
          `<span class="tk nstk-bkey" data-bucket="${esc(b.name)}" data-tip="<b>${esc(b.name)}.</b> ${esc(b.meaning)}" tabindex="0">${esc(b.name)}</span>`).join('')}
      </div>` : '';
    return `<div class="nstk-layer" data-layer="${esc(L.id)}">
      <div class="nstk-label" data-layer-label="${esc(L.id)}" tabindex="0" role="button">
        <span class="nstk-step">${L.n}</span><span class="nstk-name">${esc(L.name)}</span><span class="nstk-sub">${esc(L.sub)}</span>
      </div>
      <div class="nstk-chips">${rows}</div>
      ${seam ? `<div class="nstk-seam">${seam}</div>` : ''}
    </div>${legend}`;
  }).join('');

  $('#nstk-rail-l').innerHTML = view.rails.left.map(r =>
    `<span class="nstk-rail-cell" data-tip="<b>${esc(r.title)}.</b> ${esc(r.text)}">${esc(r.title)}</span>`).join('');
  $('#nstk-rail-r').innerHTML = view.rails.right.map(r =>
    `<span class="nstk-rail-cell" data-tip="<b>${esc(r.pin)} ${esc(r.title)}.</b> ${esc(r.text)}" tabindex="0" role="button">${esc(r.pin)} ${esc(r.title)}</span>`).join('');

  $('#nstk-quick').innerHTML = view.quick.map(q =>
    `<button type="button" class="nstk-quick" data-q="${esc(q)}">${esc(q)}</button>`).join('');

  tipEl = document.createElement('div');
  tipEl.className = 'nstk-tip';
  document.body.appendChild(tipEl);
}

/* ---------- render ---------- */
const routeShape = (tid) => tid ? { line: E.lineOf(tid, Q), breakAt: TC[tid].breakAt || null, pc: TC[tid].color } : null;

/* The seam a refusal names, when a documented break sits in the slot the reader just
   asked for. It lights the pin and adds its sentence to the dead note. */
function deadSeam(k) {
  if (!k) return null;
  const alive = { ...Q, sel: { ...Q.sel }, base: { ...Q.base }, dead: null };
  const tid = E.viable(alive).find(t => TC[t].seam && TC[t].breakAt &&
    (TC[t].breakAt === k || E.slotOf(TC[t].breakAt) === E.slotOf(k)));
  return tid ? (SEAM_LIST.find(s => s.pin === TC[tid].seam) || null) : null;
}

function render() {
  const hits = E.search(Q, Q.text);
  const vp = E.viable(Q).filter(t => hits.includes(t));
  let tid = E.picked(Q);
  if (tid && !vp.includes(tid)) tid = vp[0] || null;
  const constrained = !!Q.task || Object.keys(Q.sel).length > 0 || !!Q.dead || !!Q.text;
  const tracing = constrained && !!tid && !Q.dead;
  active = tracing ? tid : null;
  const fig = $('#nstk-fig'), grid = $('#nstk-grid');
  all('.nstk-chip').forEach(c => c.classList.remove('nstk-line', 'nstk-branch', 'nstk-implied', 'nstk-break', 'nstk-dead'));
  all('.nstk-rowlabel').forEach(l => l.classList.remove('nstk-on'));
  all('.nstk-pin').forEach(p => p.classList.remove('nstk-pin-on', 'nstk-pulse'));
  fig.classList.toggle('nstk-tracing', tracing || !!Q.dead);
  $('#nstk-clear').hidden = !constrained;
  all('.nstk-quick').forEach(b => {
    const k = keyFor(b.dataset.q);
    b.classList.toggle('nstk-active', Q.task === k || Object.values(Q.sel).includes(k));
  });
  if (tracing) {
    const T = TC[tid];
    grid.style.setProperty('--pc', T.color);
    const line = E.lineOf(tid, Q);
    line.forEach(k => {
      const el = $(`.nstk-chip[data-k="${k}"]`); if (!el) return;
      el.classList.add(T.breakAt && k === T.breakAt ? 'nstk-break' : 'nstk-line');
      const lab = el.closest('.nstk-row')?.querySelector('.nstk-rowlabel'); if (lab) lab.classList.add('nstk-on');
    });
    /* A route fixes some chips rather than offering them, and past a break the rest of
       the chain is where it would have gone. Both read as implied, never as a branch. */
    const implied = new Set([...(T.implies || []), ...(T.breakAt ? (T.after || []).concat(T.targets) : [])]);
    all('.nstk-chip').forEach(c => {
      const k = c.dataset.k;
      if (line.includes(k) || E.slotOf(k) === 'task') return;
      if (implied.has(k)) c.classList.add('nstk-implied');
      else if (E.reachable(k, Q)) c.classList.add('nstk-branch');
    });
    if (T.breakAt && T.seam) $(`.nstk-pin[data-pin="${T.seam}"]`)?.classList.add('nstk-pin-on');
  }
  if (Q.dead) {
    $(`.nstk-chip[data-k="${Q.dead}"]`)?.classList.add('nstk-dead');
    const seam = deadSeam(Q.dead);
    if (seam) {
      const pin = $(`.nstk-pin[data-pin="${seam.pin}"]`);
      if (pin) { pin.classList.add('nstk-pin-on'); if (!reducedMotion) pin.classList.add('nstk-pulse'); }
    }
  }
  // Highlighting route chips changes their font weight and can reflow rows.
  // Measure the settled layout before drawing the SVG path.
  requestAnimationFrame(() => drawPath(routeShape(active), true));
  panel(vp, tid, constrained);
}

/* ---------- overlay ---------- */
const reducedMotion = !!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);
const svgEl = (tag, attrs) => {
  const e = document.createElementNS('http://www.w3.org/2000/svg', tag);
  for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v);
  return e;
};
/* The route is traced from the first chip downward when the reader chooses
   something, the way the QuantizationSurvey's map traces its route. A redraw
   after a resize repaints the finished line without replaying the trace. */
function drawPath(route, animate) {
  const svg = $('#nstk-overlay');
  svg.innerHTML = '';
  if (!route) return;
  const gb = $('#nstk-grid').getBoundingClientRect();
  const cut = route.breakAt ? route.line.indexOf(route.breakAt) : route.line.length - 1;

  const pts = [];
  const seen = new Set();
  route.line.forEach((k, i) => {
    if (i > cut) return;
    const el = $(`.nstk-chip[data-k="${k}"]`);
    if (!el) return;
    const row = rowOf(k);
    if (seen.has(row)) return;      // one anchor per row keeps the line readable
    seen.add(row);
    const b = el.getBoundingClientRect();
    pts.push([b.left - gb.left + b.width / 2, b.top - gb.top + b.height / 2]);
  });
  if (pts.length < 2) return;

  // An S-curve between rows keeps the line vertical where it leaves and enters a chip.
  const f = n => n.toFixed(1);
  const d = pts.map((p, i) => {
    if (!i) return `M ${f(p[0])} ${f(p[1])}`;
    const [ax, ay] = pts[i - 1];
    const my = f((ay + p[1]) / 2);
    return `C ${f(ax)} ${my} ${f(p[0])} ${my} ${f(p[0])} ${f(p[1])}`;
  }).join(' ');
  const halo = svgEl('path', { class: 'nstk-path-halo', d });
  const path = svgEl('path', { class: 'nstk-path', style: `stroke:${route.pc}`, d });
  svg.appendChild(halo); svg.appendChild(path);

  const tail = [];
  if (route.breakAt) {
    const [x, y] = pts[pts.length - 1];
    tail.push(svgEl('path', { class: 'nstk-path-broken', d: `M ${f(x)} ${f(y)} L ${f(x)} ${f(y + 42)}` }));
    const cx = x, cy = y + 52;
    tail.push(svgEl('path', { class: 'nstk-breakmark',
      d: `M ${f(cx - 7)} ${f(cy - 7)} L ${f(cx + 7)} ${f(cy + 7)} M ${f(cx + 7)} ${f(cy - 7)} L ${f(cx - 7)} ${f(cy + 7)}` }));
    tail.forEach(e => svg.appendChild(e));
  }

  if (animate && !reducedMotion) {
    const len = path.getTotalLength();
    const dur = Math.min(1.5, 0.35 + len / 1100);
    [halo, path].forEach(e => { e.style.transition = 'none'; e.style.strokeDasharray = len; e.style.strokeDashoffset = len; });
    tail.forEach(e => { e.style.transition = 'none'; e.style.opacity = '0'; });
    // The nodes were inserted this tick; their start state settles on the next
    // frame, and setting the target before then makes the value snap.
    requestAnimationFrame(() => {
      [halo, path].forEach(e => { e.style.transition = `stroke-dashoffset ${dur}s ease-out`; e.style.strokeDashoffset = '0'; });
      tail.forEach(e => { e.style.transition = `opacity 0.25s ease-out ${(dur * 0.7).toFixed(2)}s`; e.style.opacity = '1'; });
    });
  }
}

/* ---------- panel ---------- */
/* The target's chip word, one vocabulary with the prose and Table 1 (data/target-kinds.json). */
function tkChip(T) {
  if (!T.tk) return '';
  const css = T.tk.toLowerCase().replace(/ /g, '-');
  return `<span class="tk tk-${css}" title="target kind">${esc(T.tk)}</span>`;
}
function subjectBlock(key) {
  // The chip the reader last clicked, explained by its note or node summary, with a read link.
  const k = key === undefined ? (Q.dead || Object.values(Q.sel).slice(-1)[0] || Q.task) : key;
  if (!k) return '';
  const text = noteText(k), read = readOf(k);
  if (!text) return '';
  return `<div class="nstk-subject"><b>${esc(E.labelOf(k))}.</b> ${esc(text)}${read ? ` <a class="nstk-read" href="${esc(read)}">Read the section</a>` : ''}</div>`;
}
function chainBlock(tid) {
  const T = TC[tid], line = E.lineOf(tid, Q);
  const arrow = '<span class="nstk-arr">→</span>';
  const drawn = line.map((k, i) => {
    const brk = T.breakAt && k === T.breakAt;
    return `<span class="nstk-step-chip${brk ? ' nstk-step-break' : ''}">${esc(E.labelOf(k))}</span>` +
      (i < line.length - 1 ? arrow : '');
  }).join('');
  if (!T.breakAt) return `<div class="nstk-steps">${drawn}</div>`;
  // Past the break, where the chain would have gone.
  const rest = (T.after || []).concat(T.targets.length ? [T.targets[0]] : [])
    .map(k => `<span class="nstk-step-chip nstk-step-implied">${esc(E.labelOf(k))}</span>`).join(arrow);
  return `<div class="nstk-steps">${drawn}<span class="nstk-arr nstk-arr-break">×</span>${rest}</div>`;
}
function sourcesBlock(tid) {
  const srcs = E.routeSources(tid, Q);
  if (!srcs.length) return '';
  return `<details class="nstk-sources"><summary>Documentation and sources on the route (${srcs.length})</summary><ul>${
    srcs.map(s => `<li><a href="${esc(s.url)}" target="_blank" rel="noopener noreferrer">${esc(s.title)}</a> <span>${esc(s.type)}</span></li>`).join('')}</ul></details>`;
}
function papersBlock(tid) {
  const ps = E.routePapers(tid, Q);
  if (!ps.length) return '';
  return `<details class="nstk-papers" open><summary>Surveyed papers that demonstrate this route (${ps.length})</summary><ul>${
    ps.map(p => `<li class="nstk-paper${Q.paper === p.id ? ' nstk-paper-on' : ''}" data-paper="${esc(p.id)}" tabindex="0" role="button">
      <a href="${esc(p.url || '#')}" target="_blank" rel="noopener noreferrer">${esc(p.title)}</a>
      <span class="nstk-pmeta">${esc(p.authors || '')}${p.year ? `, ${p.year}` : ''}${p.venue ? `, ${esc(p.venue)}` : ''}</span>
      <span class="nstk-evid" style="--pc:${TC[tid].color}">${esc(p.evidence || '')}</span>
      <span class="nstk-ptarget">${esc(p.target_hardware || '')}</span>
      <span class="nstk-ppin">${Q.paper === p.id ? 'showing this run' : 'show this run'}</span></li>`).join('')}</ul></details>`;
}
const countText = (n) => n ? `${n} ${n === 1 ? 'route' : 'routes'}, best first` : 'no route in this stack';

function panel(vp, tid, constrained) {
  const p = $('#nstk-panel');
  if (!constrained) { p.innerHTML = ''; return; }
  if (Q.dead) {
    const k = Q.dead, seam = deadSeam(k), read = readOf(k);
    const seamText = seam ? ` ${esc(seam.pin)} ${esc(seam.title)}. ${esc(seam.text)}` : '';
    p.innerHTML = `<div class="nstk-dead-note"><b>No route in this stack carries ${esc(E.labelOf(k))} together with the current selection.</b> ${esc(noteText(k))}${seamText}${
      read ? ` <a class="nstk-read" href="${esc(read)}">Read the section</a>` : ''} <span class="nstk-crumb" data-drop="dead">dismiss</span></div>${
      subjectBlock(Object.values(Q.sel).slice(-1)[0] || Q.task || null)}`;
    return;
  }
  if (!tid) {
    p.innerHTML = `<div class="nstk-guide">No documented route carries that combination. Clear a constraint to widen the question.</div>${subjectBlock()}`;
    return;
  }
  const T = TC[tid], rec = E.recommended(Q);
  const pinned = Q.paper ? E.routePapers(tid, Q).find(x => x.id === Q.paper) : null;
  const others = vp.filter(t => t !== tid).map(o => {
    const O = TC[o];
    return `<li class="nstk-route" data-route="${esc(o)}" style="--pc:${O.color}" tabindex="0" role="button">
       <span class="nstk-rhead"><b>${esc(O.name)}</b><span class="nstk-evid${O.breakAt ? ' nstk-evid-blocked' : ''}" style="--pc:${O.color}">${esc(O.ev)}</span>${tkChip(O)}</span>
       <span class="nstk-rstory">${esc(O.story)}</span></li>`;
  }).join('');

  p.innerHTML = `
    <div class="nstk-ph" style="--pc:${T.color}">
      <span class="nstk-dot" style="--pc:${T.color}"></span><b>${esc(T.name)}</b>
      <span class="nstk-evid${T.breakAt ? ' nstk-evid-blocked' : ''}" style="--pc:${T.color}">${esc(T.ev)}</span>${tkChip(T)}
      ${T.live ? '<span class="nstk-evid" style="--pc:#237985">live route</span>' : ''}
      <span class="nstk-evid" style="--pc:#4a5560">${tid === rec ? 'recommended' : 'selected'}</span>
      <span class="nstk-count">${countText(vp.length)}</span>
    </div>
    <div class="nstk-pbody" style="--pc:${T.color}">
      ${subjectBlock()}
      ${chainBlock(tid)}
      <p class="nstk-note">${esc(T.story)}</p>
      ${T.breakAt ? `<p class="nstk-break-note"><b>Breaks at ${esc(E.labelOf(T.breakAt))}.</b> ${esc(T.breakWhy || '')}</p>` : ''}
      <p class="nstk-note">${esc(T.note || '')}</p>
      ${pinned ? `<div class="nstk-pinned">Showing the run reported by ${esc(pinned.authors || pinned.title)}${pinned.year ? `, ${pinned.year}` : ''}. <span class="nstk-crumb" data-drop="paper">drop</span></div>` : ''}
      ${sourcesBlock(tid)}
      ${papersBlock(tid)}
      ${others ? `<ul class="nstk-routes">${others}</ul>` : ''}
      <p class="nstk-legendnote">
        <span class="nstk-key nstk-line"></span> on the route &nbsp;
        <span class="nstk-key nstk-branch"></span> a branch still open &nbsp;
        <span class="nstk-key nstk-implied"></span> fixed by the route, or unreachable past a break &nbsp;
        <span class="nstk-key nstk-break"></span> where the chain snaps
      </p>
    </div>`;
}

/* ---------- tooltip ---------- */
function tipOn(el) {
  const t = el.dataset.tip; if (!t) return;
  tipEl.innerHTML = t; tipEl.classList.add('nstk-tip-on');
  const b = el.getBoundingClientRect();
  const w = Math.min(300, window.innerWidth - 24);
  tipEl.style.left = Math.max(12, Math.min(b.left, window.innerWidth - w - 12)) + 'px';
  tipEl.style.top = (b.bottom + 8) + 'px';
}
const tipOff = () => tipEl.classList.remove('nstk-tip-on');

/* ---------- events ---------- */
const toolchainOfPaper = (id) => Object.keys(TC).find(t => (TC[t].papers || []).some(p => p.id === id)) || null;
function clearAll() { Q = E.blank(); $('#nstk-q').value = ''; render(); }

function wire() {
  document.addEventListener('click', e => {
    const chip = e.target.closest('.nstk-chip');
    if (chip) { Q = E.applyQuery(Q, chip.dataset.k); render(); return; }
    const q = e.target.closest('.nstk-quick');
    if (q) { Q = E.applyQuery(Q, keyFor(q.dataset.q)); render(); return; }
    const paper = e.target.closest('.nstk-paper');
    if (paper) {
      if (e.target.closest('a')) return;              // the title link opens the record
      const id = paper.dataset.paper, owner = toolchainOfPaper(id);
      if (owner) Q.pick = owner;
      Q.paper = Q.paper === id ? null : id;
      render(); return;
    }
    const ro = e.target.closest('.nstk-route');
    if (ro) { Q.pick = ro.dataset.route; Q.paper = null; render(); return; }
    const drop = e.target.closest('[data-drop]');
    if (drop) {
      if (drop.dataset.drop === 'dead') Q.dead = null;
      if (drop.dataset.drop === 'paper') Q.paper = null;
      render(); return;
    }
    if (e.target.closest('#nstk-clear')) { clearAll(); return; }
  });

  const box = $('#nstk-q');
  box.addEventListener('input', () => { Q.text = box.value; render(); });
  // A typed chip label is a choice of that chip rather than a filter over the routes.
  box.addEventListener('change', () => {
    const k = keyFor(box.value);
    if (E.chips.has(k)) { box.value = ''; Q.text = ''; Q = E.applyQuery(Q, k); }
    render();
  });

  document.addEventListener('mouseover', e => { const t = e.target.closest('[data-tip]'); if (t) tipOn(t); });
  document.addEventListener('mouseout', e => { if (e.target.closest('[data-tip]')) tipOff(); });
  document.addEventListener('focusin', e => { const t = e.target.closest('[data-tip]'); if (t) tipOn(t); });
  document.addEventListener('focusout', tipOff);
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') { clearAll(); return; }
    if (e.key !== 'Enter' && e.key !== ' ') return;
    const el = e.target.closest?.('.nstk-chip, .nstk-route, .nstk-paper');
    if (el) { e.preventDefault(); el.click(); }
  });
  window.addEventListener('resize', () => drawPath(routeShape(active), false));
}

$('#nstk-q').value = '';
build(); wire(); render();
window.addEventListener('load', () => drawPath(routeShape(active), false));
