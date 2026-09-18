/* The route map's engine, pure. A compatibility model after the QuantizationSurvey's
   Figure 17. Each toolchain declares what it can carry in every slot, what it fixes, and
   which parts it reaches; a task ranks and never restricts; anything still reachable is
   a branch. No DOM here; assets/figure.js draws what this decides. */
export function createEngine(view) {
  const slots = view.slots;
  const TC = view.toolchains;
  const TIDS = Object.keys(TC);
  const chips = new Map();
  view.layers.forEach(L => L.rows.forEach(row => row.chips.forEach(c =>
    chips.set(c.id, { id: c.id, label: c.label, slot: row.slot, layer: L.id, row: row.label, bucket: row.bucket || null }))));
  const slotOf = id => (chips.get(id) || {}).slot || null;
  const labelOf = id => (chips.get(id) || {}).label || id;
  const idx = k => slots.indexOf(slotOf(k));
  /* A step is one chip or an ordered run of them, so PyNN comes before NEST and
     nir_exchange before NIR. Everything that reads a step reads it as a list. */
  const stepChips = (T, slot) => [].concat(T.steps[slot] || []);

  const blank = () => ({ task: null, sel: {}, base: {}, pick: null, paper: null, dead: null, text: '' });
  const clone = Q => ({ task: Q.task, sel: { ...Q.sel }, base: { ...Q.base }, pick: Q.pick, paper: Q.paper, dead: Q.dead, text: Q.text });

  const carries = (T, slot, k) => slot === 'hw' ? T.targets.includes(k)
    : (T.can[slot] || []).includes(k) || (T.implies || []).includes(k);

  function fits(tid, Q) {
    const T = TC[tid];
    for (const [slot, k] of Object.entries(Q.sel)) {
      if (!k) continue;
      if (!carries(T, slot, k)) return false;
      // A broken toolchain fits only selections that lie before its break.
      if (T.breakAt && idx(k) > idx(T.breakAt)) return false;
      if (T.breakAt && slot === 'hw') return false;
    }
    return true;
  }
  function order(Q) {
    const pref = (Q.task && view.applications[Q.task] && view.applications[Q.task].prefer) || [];
    const hw = Q.sel.hw;
    return (a, b) => {
      const A = TC[a], B = TC[b];
      if (!!A.breakAt !== !!B.breakAt) return A.breakAt ? 1 : -1;
      if (hw) {
        const va = (A.vendorFor || []).includes(hw), vb = (B.vendorFor || []).includes(hw);
        if (va !== vb) return va ? -1 : 1;
      }
      const ia = pref.indexOf(a), ib = pref.indexOf(b);
      if (ia !== -1 || ib !== -1) { if (ia === -1) return 1; if (ib === -1) return -1; if (ia !== ib) return ia - ib; }
      if (!!A.live !== !!B.live) return A.live ? -1 : 1;
      return (A.rank || 99) - (B.rank || 99);
    };
  }
  const viable = Q => Q.dead ? [] : TIDS.filter(t => fits(t, Q)).sort(order(Q));
  function recommended(Q) {
    const vp = viable(Q);
    return vp.find(t => !TC[t].caveat && !TC[t].breakAt) || vp[0] || null;
  }
  function picked(Q) {
    const vp = viable(Q);
    if (Q.pick && vp.includes(Q.pick)) return Q.pick;
    return recommended(Q);
  }
  function reachable(k, Q) {
    const slot = slotOf(k);
    if (!slot || slot === 'task') return false;
    const probe = clone(Q); probe.dead = null; probe.sel[slot] = k;
    return TIDS.some(t => fits(t, probe));
  }
  function via(Q) {
    // The pinned paper's steps override the task's steps.
    const out = { ...Q.base };
    if (Q.paper) {
      const P = Object.values(TC).flatMap(T => T.papers || []).find(p => p.id === Q.paper);
      if (P) Object.assign(out, P.via || {});
    }
    return out;
  }
  function lineOf(tid, Q) {
    const T = TC[tid], base = via(Q), out = [];
    for (const slot of slots) {
      if (slot === 'hw') {
        const h = Q.sel.hw && T.targets.includes(Q.sel.hw) ? Q.sel.hw
          : base.hw && T.targets.includes(base.hw) ? base.hw : T.targets[0];
        if (!T.breakAt) out.push(h);
        continue;
      }
      if (slot === 'task') { if (Q.task) out.push(Q.task); continue; }
      /* Choosing one chip of an ordered step keeps the whole step, so picking NIR still
         draws nir_exchange before it. Choosing a chip outside the step draws it alone. */
      const ks = Q.sel[slot] && carries(T, slot, Q.sel[slot])
        ? (stepChips(T, slot).includes(Q.sel[slot]) ? stepChips(T, slot) : [Q.sel[slot]])
        : base[slot] && carries(T, slot, base[slot])
          ? (stepChips(T, slot).includes(base[slot]) ? stepChips(T, slot) : [base[slot]])
          : stepChips(T, slot);
      const group = [...ks, ...(T.implies || []).filter(im => slotOf(im) === slot)].filter(Boolean);
      group.forEach(g => { if (!out.includes(g)) out.push(g); });
      if (T.breakAt && group.includes(T.breakAt)) break;
    }
    return out;
  }
  const cutOf = tid => TC[tid].breakAt ? lineOf(tid, blank()).indexOf(TC[tid].breakAt) : -1;

  function routeSources(tid, Q) {
    const line = lineOf(tid, Q), ids = new Set(line), T = TC[tid];
    const last = line[line.length - 1];
    const edges = view.edges.filter(e => ids.has(e.from) && ids.has(e.to) &&
      (['dev', 'export', 'compile', 'run'].includes(slotOf(e.from)) || slotOf(e.to) === 'hw' || e.to === T.breakAt));
    edges.sort((a, b) => (b.to === last) - (a.to === last));
    const seen = new Set(), out = [];
    edges.forEach(e => (e.sources || []).forEach(s => { if (!seen.has(s.id)) { seen.add(s.id); out.push(s); } }));
    return out;
  }
  function paperFits(p, Q) {
    const v = p.via || {};
    if (Q.task && v.task && v.task !== Q.task) return false;
    return Object.entries(Q.sel).every(([slot, k]) => !k || !v[slot] || v[slot] === k);
  }
  const routePapers = (tid, Q) => (TC[tid].papers || []).filter(p => paperFits(p, Q))
    .map(p => ({ ...(view.papers[p.id] || { id: p.id, title: p.id }), via: p.via || {}, note: p.note || null }));

  function applyQuery(Q0, k) {
    const Q = clone(Q0); Q.dead = null; Q.paper = null;
    const slot = slotOf(k);
    if (!slot) return Q;
    if (slot === 'task') {
      if (Q.task === k) { Q.task = null; Q.base = {}; return Q; }
      Q.task = k; Q.base = { ...((view.applications[k] || {}).via || {}) }; return Q;
    }
    if (Q.sel[slot] === k) { delete Q.sel[slot]; return Q; }
    if (reachable(k, Q)) Q.sel[slot] = k; else Q.dead = k;
    return Q;
  }
  function search(Q, text) {
    const q = (text || '').trim().toLowerCase();
    if (!q) return TIDS.slice();
    return TIDS.filter(t => TC[t].name.toLowerCase().includes(q) || TC[t].story.toLowerCase().includes(q) ||
      lineOf(t, Q).some(k => labelOf(k).toLowerCase().includes(q)));
  }
  return { slots, chips, slotOf, labelOf, blank, fits, viable, recommended, picked, reachable, lineOf, cutOf,
           routeSources, routePapers, paperFits, applyQuery, search };
}
