/* The neuromorphic deployment stack figure.
   Selecting anything narrows the question rather than restarting it. Constraints
   accumulate, the surviving routes are ranked, and the best one is drawn.
   A route that cannot complete is drawn up to its snap point and then broken. */

const LAYERS = [
  { id: 'app', n: 1, name: 'Application', sub: 'the task, the sensor that feeds it, and the form the input takes', rows: [
    { label: 'Task', chips: [
      ['image-classification-static', 'Image classification'], ['object-detection', 'Object detection'],
      ['gesture-recognition', 'Gesture recognition'], ['tracking-motion', 'Tracking and motion'],
      ['keyword-spotting-audio', 'Keyword spotting'], ['biosignal-decoding', 'Biosignal decoding'],
      ['olfaction', 'Olfaction'], ['robotics-closed-loop-control', 'Robotics and control'],
      ['slam', 'SLAM'], ['optimization-constraint-satisfaction', 'Optimization and SAT'] ] },
    { label: 'Sensor', chips: [
      ['event-camera', 'Event camera (DVS)'], ['frame-camera', 'Frame camera'],
      ['silicon-cochlea', 'Silicon cochlea'], ['microphone', 'Microphone'],
      ['tactile-sensor', 'Tactile sensor'], ['chemical-sensor-array', 'Chemical sensor array'],
      ['imu-analog-sensor', 'IMU and analog sensors'], ['no-physical-sensor', 'No sensor (dataset or solver)'] ] },
    { label: 'Input representation', chips: [
      ['native-events', 'Native event stream'], ['frames-from-events', 'Frames reconstructed from events'],
      ['static-frames', 'Static frames'], ['time-series', 'Sampled time series'] ] } ] },

  { id: 'learn', n: 2, name: 'Learning path', sub: 'how the weights are obtained', rows: [
    { label: 'ANN-to-SNN', chips: [
      ['classical-conversion', 'Classical conversion'], ['low-latency-conversion', 'Low-latency conversion'],
      ['quant-aware-conversion', 'Quantization-aware conversion'], ['codesigned-conversion', 'Hardware co-designed conversion'] ] },
    { label: 'Direct and hybrid', chips: [
      ['direct-training-surrogate-gradient', 'Surrogate gradients'], ['spike-time-gradient-methods', 'Spike-time gradients'],
      ['local-learning-plasticity', 'Local learning and plasticity'], ['hand-designed-hybrid-finetuning', 'Hand-designed circuits'],
      ['hardware-in-the-loop-training', 'Hardware-in-the-loop'], ['hybrid-finetuning', 'Hybrid fine-tuning'] ] } ] },

  { id: 'code', n: 3, name: 'Representation', sub: 'what the spike train means', rows: [
    { label: 'Neural code', chips: [
      ['rate-coding', 'Rate coding'], ['ttfs', 'Time-to-first-spike (TTFS)'], ['phase-coding', 'Phase coding'],
      ['burst-coding', 'Burst coding'], ['population-coding', 'Population coding'], ['sigma-delta', 'Sigma-delta coding'],
      ['rank-order-coding', 'Rank order coding'], ['direct-input-encoding', 'Direct (constant-current) input'] ] },
    { label: 'Event payload', chips: [
      ['binary-spikes', 'Binary spikes'], ['signed-spikes', 'Signed spikes'], ['graded-spikes', 'Graded spikes'] ] } ] },

  { id: 'compute', n: 4, name: 'Computation', sub: 'the neuron and its execution contract', rows: [
    { label: 'Neuron model', chips: [
      ['if-neuron', 'Integrate-and-fire (IF)'], ['lif-neuron', 'Leaky IF (LIF)'], ['cuba-lif', 'Current-based LIF (CUBA)'],
      ['adaptive-neuron', 'Adaptive LIF (ALIF)'], ['multi-compartment', 'Multi-compartment'], ['pasc-if', 'PASC-IF'] ] },
    { label: 'Reset rule', chips: [
      ['reset-by-subtraction', 'Reset by subtraction (soft)'], ['reset-to-zero', 'Reset to zero (hard)'] ] },
    { label: 'Execution contract', chips: [
      ['sync-tick', 'Synchronous global tick'], ['async-events', 'Asynchronous event-driven'],
      ['analog-time', 'Analog continuous time'], ['single-pass', 'Single pass, T collapsed'] ] } ] },

  { id: 'sw', n: 5, name: 'Software stack', sub: 'in process order: train, export, compile, run', rows: [
    { label: 'Develop and train', chips: [
      ['spikingjelly', 'SpikingJelly'], ['snn-toolbox', 'SNN Toolbox'], ['snntorch', 'snnTorch'],
      ['norse', 'Norse'], ['sinabs', 'Sinabs'], ['rockpool', 'Rockpool'], ['lava', 'Lava'],
      ['lava-dl', 'Lava-DL'], ['hxtorch', 'hxtorch'], ['nengo', 'Nengo'], ['pynn', 'PyNN'],
      ['brian2', 'Brian2'], ['nest', 'NEST'], ['mlgenn', 'mlGeNN'], ['bidl', 'BIDL'],
      ['quantizeml', 'QuantizeML'], ['quartz', 'Quartz'] ] },
    { label: 'Export and interchange', chips: [
      ['nir', 'NIR'], ['lava-exchange', 'lava_exchange'], ['nir-exchange', 'nir_exchange'],
      ['backend-graph', 'Backend-specific graph'] ] },
    { label: 'Compile and map', chips: [
      ['nxtf', 'NxTF'], ['netx', 'NetX'], ['dynapcnn-mapper', 'DynapCNN mapper'],
      ['xylo-mapper', 'Xylo mapper'], ['spynnaker', 'sPyNNaker'], ['nengo-loihi', 'NengoLoihi'],
      ['cnn2snn', 'CNN2SNN'], ['ann2snn', 'ann2snn'] ] },
    { label: 'Run on device', chips: [
      ['nxsdk', 'NxSDK'], ['lava-runtime', 'Lava ProcessModels'], ['samna', 'samna'],
      ['spinnaker-runtime', 'SpiNNaker runtime'], ['akida-runtime', 'Akida runtime'],
      ['host-io', 'Host encoding and readout'] ] } ] },

  { id: 'hw', n: 6, name: 'Hardware', sub: 'where it actually runs', rows: [
    { label: 'Synchronous digital', chips: [
      ['loihi-1', 'Loihi 1'], ['loihi-2', 'Loihi 2'], ['spinnaker-1', 'SpiNNaker 1'],
      ['spinnaker-2', 'SpiNNaker 2'], ['truenorth', 'TrueNorth'], ['tianjic', 'Tianjic'],
      ['lynxi-ka200', 'Lynxi KA200'], ['xylo', 'Xylo'] ] },
    { label: 'Event-driven and analog', chips: [
      ['speck', 'Speck'], ['dynapcnn', 'DYNAP-CNN'], ['brainscales-1', 'BrainScaleS-1'],
      ['brainscales-2', 'BrainScaleS-2'], ['dynap-se2', 'DYNAP-SE2'],
      ['innatera-pulsar', 'Innatera Pulsar'] ] },
    { label: 'Other substrates', chips: [
      ['akida', 'Akida'], ['morphic', 'MorphIC'], ['northpole', 'NorthPole'],
      ['fpga', 'FPGA designs'], ['syncnn', 'SyncNN (FPGA)'], ['cerebron', 'Cerebron (FPGA)'],
      ['apex', 'APEX (RTL)'], ['neuroflex', 'NeuroFlex (RTL)'] ] } ] },
];

/* Routes. `line` lists the chips on the path. `breakAt` names the chip where the chain
   snaps, and everything below it is unreachable by this route. `implied` chips are fixed
   by the route rather than chosen. */
const ROUTES = [
  { id: 'snntoolbox-loihi1', name: 'SNN Toolbox to Loihi 1', ev: 'E1', pc: '#2A8A7A', rec: true,
    story: 'A rate-coded converted MobileNet measured on physical Loihi 1 silicon at CIFAR-10 scale. It reached 8.52% error across 1,753 cores on 14 chips.',
    note: 'Historical. SNN Toolbox last released March 2021 and last patched August 2022. NxTF is Keras-native and its host repository carries a discontinuation notice. Loihi 1 is superseded.',
    line: ['image-classification-static','frame-camera','static-frames','classical-conversion','rate-coding','binary-spikes','if-neuron','reset-by-subtraction','sync-tick','snn-toolbox','backend-graph','nxtf','nxsdk','loihi-1'] },

  { id: 'snntoolbox-spinnaker', name: 'SNN Toolbox to SpiNNaker 1', ev: 'E1', pc: '#42647B',
    story: 'A converted Keras LeNet on a physical 48-chip machine. 98.20% on MNIST, roughly 0.4 s per inference.',
    note: 'Nothing at CIFAR-10 scale or above was found on physical SpiNNaker silicon. A timestep here is a timer interrupt, conventionally 1 ms, pinned to biological real time.',
    line: ['image-classification-static','frame-camera','static-frames','classical-conversion','rate-coding','binary-spikes','if-neuron','reset-by-subtraction','sync-tick','snn-toolbox','backend-graph','spynnaker','spinnaker-runtime','spinnaker-1'] },

  { id: 'sinabs-speck', name: 'Sinabs to Speck', ev: 'E1', pc: '#237985', rec: true, live: true,
    story: 'The one live route that preserves reset by subtraction end to end, on hardware anyone can buy. Measured 3.36 us across nine layers.',
    note: 'Sinabs from_model() defaults to MembraneSubtract(). Speck supports subtractive reset natively via return_to_zero=False. A Demo Kit presold at $199 with no approval gate. Speck has no global clock, so T exists only at the raster-to-events boundary. Sinabs has no built-in BatchNorm folding.',
    line: ['gesture-recognition','event-camera','native-events','classical-conversion','rate-coding','binary-spikes','if-neuron','reset-by-subtraction','async-events','sinabs','backend-graph','dynapcnn-mapper','samna','speck'] },

  { id: 'rockpool-xylo', name: 'Rockpool to Xylo', ev: 'E1', pc: '#3F5FBF',
    story: 'On-chip accuracy and per-channel power measured. Audio and low-dimensional signals rather than vision.',
    note: 'Xylo documents a synchronous time-stepped architecture with a global dt, so T here is a genuine hardware tick. Same vendor as Speck, opposite time model.',
    line: ['keyword-spotting-audio','microphone','time-series','direct-training-surrogate-gradient','rate-coding','binary-spikes','lif-neuron','reset-to-zero','sync-tick','rockpool','backend-graph','xylo-mapper','samna','xylo'] },

  { id: 'spikingjelly-lava', name: 'SpikingJelly to Lava to Loihi 2', ev: 'BLOCKED', pc: '#C0392B',
    story: 'The obvious modern route, and it does not complete.',
    note: 'Two independent blockers. lava_exchange raises ValueError("lava only supports for v_reset == 0!") at five call sites, rejecting the soft-reset neurons that SpikingJelly ann2snn produces by default. It also dispatches only Linear, Conv2d, AvgPool2d and Flatten, so a VGG MaxPool or a ResNet skip connection fails immediately. Intel archived all Lava repositories on 13 May 2026.',
    breakAt: 'lava-exchange',
    breakWhy: 'Soft reset is rejected at export. The conversion produced a network the framework’s own exporter will not accept.',
    line: ['image-classification-static','frame-camera','static-frames','quant-aware-conversion','rate-coding','binary-spikes','if-neuron','reset-by-subtraction','sync-tick','spikingjelly','lava-exchange','netx','lava-runtime','loihi-2'] },

  { id: 'spikingjelly-nxtf', name: 'SpikingJelly to NxTF to Loihi 1', ev: 'BLOCKED', pc: '#C0392B',
    story: 'Substituting the maintained framework into the route that actually reached silicon. It does not connect.',
    note: 'NxTF inherits from the Keras Model and Layer interface. No PyTorch bridge exists, and the only bridge ever built was specific to SNN Toolbox. The host repository carries a discontinuation notice, and INRC has redirected users to Lava since 2022. NxTF on Loihi 2 was not found.',
    breakAt: 'nxtf',
    breakWhy: 'NxTF is Keras-native and SpikingJelly is PyTorch. The framework boundary was only ever crossed by an SNN-Toolbox-specific bridge that no longer has a maintained counterpart.',
    line: ['image-classification-static','frame-camera','static-frames','quant-aware-conversion','rate-coding','binary-spikes','if-neuron','reset-by-subtraction','sync-tick','spikingjelly','backend-graph','nxtf','nxsdk','loihi-1'] },

  { id: 'spikingjelly-nir', name: 'SpikingJelly to NIR', ev: 'BLOCKED', pc: '#C0392B',
    story: 'The portability route, blocked in the specification rather than the implementation.',
    note: 'NIR defines six primitives. All three spiking ones (IF, LIF, CubaLIF) document reset as v = v_reset when a spike fires. No NIR primitive expresses reset by subtraction. SpikingJelly nir_exchange raising NotImplementedError("NIR does not distinguish soft reset.") is correct behavior given the target format.',
    breakAt: 'nir',
    breakWhy: 'The broadest interchange format in the ecosystem cannot represent reset by subtraction at all.',
    line: ['image-classification-static','frame-camera','static-frames','quant-aware-conversion','rate-coding','binary-spikes','if-neuron','reset-by-subtraction','sync-tick','spikingjelly','nir','netx','lava-runtime','loihi-2'] },

  { id: 'quantizeml-akida', name: 'QuantizeML to CNN2SNN to Akida', ev: 'E1', pc: '#6D4C9F',
    story: 'A shipping commercial processor. The conversion folds to a static threshold and the temporal dimension disappears.',
    note: 'CNN2SNN computes y = x / act_step with a static threshold absorbing BatchNorm scale and shift, folded once at conversion time. No membrane potential carries across timesteps and no T is exposed. Two independent papers describe it as squashing the rate-code approximation of ReLU into one time step. The rank-order-coding heritage is genuine, but no source shows order sensitivity operating in converted hidden layers.',
    line: ['image-classification-static','frame-camera','static-frames','quant-aware-conversion','rank-order-coding','binary-spikes','if-neuron','reset-to-zero','single-pass','quantizeml','backend-graph','cnn2snn','akida-runtime','akida'] },

  { id: 'quartz-loihi', name: 'Quartz to Loihi 1', ev: 'E1', pc: '#A97818',
    story: 'A new method that reached silicon, by abandoning rate coding for TTFS.',
    note: 'Measured static, dynamic and total power, latency and energy per inference on a physical Nahuku 32 board, head to head against a rate-coded baseline on the same chip. The authors’ released implementation uses NxSDK 0.9.8 directly.',
    line: ['image-classification-static','frame-camera','static-frames','codesigned-conversion','ttfs','binary-spikes','if-neuron','reset-to-zero','sync-tick','quartz','backend-graph','nxsdk','loihi-1'] },

  { id: 'slayer-loihi2', name: 'Lava-DL SLAYER to Loihi 2', ev: 'E1', pc: '#98622C',
    story: 'Direct training with a vendor toolchain, reaching silicon where conversion did not.',
    note: 'Physical Loihi 2 results exist for directly trained sigma-delta and LIF networks. Intel moved Loihi 2 toward graded sigma-delta payloads, stating that rate-coded converted models suffer long latencies and inter-chip congestion.',
    line: ['robotics-closed-loop-control','imu-analog-sensor','time-series','direct-training-surrogate-gradient','sigma-delta','graded-spikes','cuba-lif','reset-to-zero','sync-tick','lava-dl','backend-graph','netx','lava-runtime','loihi-2'] },

];

/* Seams sit between layers and name what is lost crossing them. */
const SEAMS = {
  code:    [['8.3', 'Input encoding and readout', 'Nearly all modern low-T conversion feeds the real-valued image as constant current, which makes layer one effectively an ANN layer. Readout cost and the decision window are rarely inside the reported measurement.']],
  compute: [['8.4', 'Time model', 'T means a different thing under a synchronous tick, an asynchronous event stream, and analog continuous time. Software timesteps do not map one to one onto hardware steps.'],
            ['8.5', 'Per-layer horizons', 'No framework expresses a per-layer timestep horizon in one forward pass. TrueNorth, Loihi, Loihi 2 and Tianjic all advance through a single global barrier.']],
  sw:      [['8.1', 'Operator coverage', 'lava_exchange dispatches only Linear, Conv2d, AvgPool2d and Flatten. Sinabs has no built-in BatchNorm folding. Akida caps Dense input at 57,334 features and requires bounded ReLU.'],
            ['8.2', 'Reset semantics', 'The sharpest seam. Conversion requires reset by subtraction, worth roughly twenty accuracy points. NIR cannot express it. SpikingJelly rejects it at both export paths. Loihi needs a two-compartment workaround that doubles neuron count.']],
};

const RAIL_L = [
  ['Accuracy', 'What every reduction below trades against, and the reason the conversion literature exists.'],
  ['Latency', 'Set by the time model, the horizon T, and how much spike traffic the fabric carries per inference.'],
  ['Energy', 'Static and leakage power dominate measured energy on synchronous chips, so cutting T does not cut energy proportionally.'],
  ['Availability', 'A chip you cannot obtain is a different answer from a chip that does not suit. Access gates and dormant toolchains belong on this axis.'],
];

const RAIL_R = [
  ['8.6', 'Measurement', 'A SynOps figure is an operation-count ratio under an unstated hardware model, not joules. Boundary choices alone produce 14x swings for the identical chip and network.'],
  ['8.7', 'Toolchain decay', 'SNN Toolbox last released March 2021. Intel archived all Lava repositories on 13 May 2026 with no maintenance and no patches accepted. The only toolchain that reached silicon is dormant.'],
  ['8.8', 'Portability', 'NIR reaches nine simulators and five hardware platforms, turning m x n integrations into m + n. Its primitive set still omits the one semantics this literature depends on.'],
  ['8.9', 'Two populations', 'The division of labor that no survey states. Algorithm papers advance accuracy at low T and do not deploy. Of 39 algorithm-population papers, zero reach physical silicon. Every confirmed instance of a new method reaching silicon abandons rate coding.'],
];

/* ---------- state ---------- */
const sel = new Set();
let active = null;
let tipEl = null;
let evidence = null;

const $ = (s, r = document) => r.querySelector(s);
const all = (s, r = document) => Array.from(r.querySelectorAll(s));
const esc = (s) => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

/* ---------- build ---------- */
function build() {
  const layers = $('#nstk-layers');
  layers.innerHTML = LAYERS.map(L => {
    const rows = L.rows.map(r => `
      <div class="nstk-row${L.rows.length === 1 ? ' nstk-row-plain' : ''}">
        ${L.rows.length > 1 ? `<span class="nstk-rowlabel" data-row="${esc(r.label)}">${esc(r.label)}</span>` : ''}
        <span class="nstk-rowchips">${r.chips.map(([id, t]) =>
          `<span class="nstk-chip" data-k="${id}" tabindex="0" role="button">${esc(t)}</span>`).join('')}</span>
      </div>`).join('');
    const seam = (SEAMS[L.id] || []).map(([n, t, d]) =>
      `<span class="nstk-pin" data-pin="${n}" data-tip="<b>${n} ${esc(t)}.</b> ${esc(d)}" tabindex="0" role="button">${n}</span>`).join('');
    return `<div class="nstk-layer" data-layer="${L.id}">
      <div class="nstk-label" data-layer-label="${L.id}" tabindex="0" role="button">
        <span class="nstk-step">${L.n}</span><span class="nstk-name">${esc(L.name)}</span><span class="nstk-sub">${esc(L.sub)}</span>
      </div>
      <div class="nstk-chips">${rows}</div>
      ${seam ? `<div class="nstk-seam">${seam}</div>` : ''}
    </div>`;
  }).join('');

  $('#nstk-rail-l').innerHTML = RAIL_L.map(([t, d]) =>
    `<span class="nstk-rail-cell" data-tip="<b>${esc(t)}.</b> ${esc(d)}">${esc(t)}</span>`).join('');
  $('#nstk-rail-r').innerHTML = RAIL_R.map(([n, t, d]) =>
    `<span class="nstk-rail-cell" data-tip="<b>${n} ${esc(t)}.</b> ${esc(d)}" tabindex="0" role="button">${n} ${esc(t)}</span>`).join('');

  const quick = ['Image classification', 'Gesture recognition', 'Keyword spotting', 'Robotics and control',
                 'Event camera (DVS)', 'Frame camera', 'Rate coding', 'Reset by subtraction (soft)',
                 'SpikingJelly', 'Loihi 2', 'Speck', 'Akida'];
  $('#nstk-quick').innerHTML = quick.map(q => `<button type="button" class="nstk-quick" data-q="${esc(q)}">${esc(q)}</button>`).join('');

  tipEl = document.createElement('div');
  tipEl.className = 'nstk-tip';
  document.body.appendChild(tipEl);
}

/* ---------- ranking ---------- */
function matching() {
  let rs = ROUTES.filter(r => Array.from(sel).every(k => r.line.includes(k)));
  const q = ($('#nstk-q').value || '').trim().toLowerCase();
  if (q) {
    rs = rs.filter(r => {
      if (r.name.toLowerCase().includes(q) || r.story.toLowerCase().includes(q)) return true;
      return r.line.some(k => (label(k) || '').toLowerCase().includes(q));
    });
  }
  // A completing route outranks a broken one, and a recommended route outranks the rest.
  return rs.sort((a, b) => (!!a.breakAt - !!b.breakAt) || (!!b.rec - !!a.rec) || (!!b.live - !!a.live));
}

function label(k) {
  for (const L of LAYERS) for (const r of L.rows) for (const [id, t] of r.chips) if (id === k) return t;
  return null;
}
function layerOf(k) {
  for (const L of LAYERS) for (const r of L.rows) for (const [id] of r.chips) if (id === k) return L.id;
  return null;
}
/* The drawn line anchors once per ROW, not once per layer, so that the traversal inside
   the software stack (train, export, compile, run) is visible rather than collapsed. */
function rowOf(k) {
  for (const L of LAYERS) for (const r of L.rows) for (const [id] of r.chips) if (id === k) return `${L.id}::${r.label}`;
  return null;
}

/* ---------- render ---------- */
function render() {
  const rs = matching();
  const route = rs[0] || null;
  active = route;
  const fig = $('#nstk-fig');
  const grid = $('#nstk-grid');

  all('.nstk-chip').forEach(c => c.classList.remove('nstk-line', 'nstk-branch', 'nstk-implied', 'nstk-break'));
  all('.nstk-rowlabel').forEach(l => l.classList.remove('nstk-on'));
  all('.nstk-layer').forEach(l => l.classList.remove('nstk-bridge'));

  // Show a documented example on first load, so the figure explains a route
  // before the reader interacts with it. The clear control still reflects only
  // user-entered constraints.
  const constrained = sel.size > 0 || !!($('#nstk-q').value || '').trim();
  const tracing = !!route;
  fig.classList.toggle('nstk-tracing', tracing);
  $('#nstk-clear').hidden = !constrained;
  all('.nstk-quick').forEach(b => b.classList.toggle('nstk-active', sel.has(keyFor(b.dataset.q))));

  if (tracing) {
    grid.style.setProperty('--pc', route.pc);
    const cut = route.breakAt ? route.line.indexOf(route.breakAt) : route.line.length - 1;
    route.line.forEach((k, i) => {
      const el = $(`.nstk-chip[data-k="${k}"]`);
      if (!el) return;
      if (route.breakAt && i > cut) el.classList.add('nstk-implied');
      else if (route.breakAt && i === cut) el.classList.add('nstk-break');
      else el.classList.add('nstk-line');
      const lab = el.closest('.nstk-row')?.querySelector('.nstk-rowlabel');
      if (lab) lab.classList.add('nstk-on');
    });
    // Alternatives reachable from the current constraints read as branches.
    const alt = new Set();
    rs.slice(1).forEach(r => r.line.forEach(k => { if (!route.line.includes(k)) alt.add(k); }));
    alt.forEach(k => {
      const el = $(`.nstk-chip[data-k="${k}"]`);
      if (el && !el.classList.contains('nstk-line') && !el.classList.contains('nstk-break') && !el.classList.contains('nstk-implied')) el.classList.add('nstk-branch');
    });
  }

  // Highlighting route chips changes their font weight and can reflow rows.
  // Measure the settled layout before drawing the SVG path.
  requestAnimationFrame(() => drawPath(active));
  panel(rs, tracing);
}

function keyFor(text) {
  for (const L of LAYERS) for (const r of L.rows) for (const [id, t] of r.chips) if (t === text) return id;
  return text;
}

/* ---------- overlay ---------- */
function drawPath(route) {
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

  const d = pts.map((p, i) => (i ? `L ${p[0].toFixed(1)} ${p[1].toFixed(1)}` : `M ${p[0].toFixed(1)} ${p[1].toFixed(1)}`)).join(' ');
  svg.insertAdjacentHTML('beforeend', `<path class="nstk-path-halo" d="${d}"/>`);
  svg.insertAdjacentHTML('beforeend', `<path class="nstk-path" style="stroke:${route.pc}" d="${d}"/>`);

  if (route.breakAt) {
    const [x, y] = pts[pts.length - 1];
    svg.insertAdjacentHTML('beforeend', `<path class="nstk-path-broken" d="M ${x.toFixed(1)} ${y.toFixed(1)} L ${x.toFixed(1)} ${(y + 42).toFixed(1)}"/>`);
    const cx = x, cy = y + 52;
    svg.insertAdjacentHTML('beforeend',
      `<path class="nstk-breakmark" d="M ${(cx - 7).toFixed(1)} ${(cy - 7).toFixed(1)} L ${(cx + 7).toFixed(1)} ${(cy + 7).toFixed(1)} M ${(cx + 7).toFixed(1)} ${(cy - 7).toFixed(1)} L ${(cx - 7).toFixed(1)} ${(cy + 7).toFixed(1)}"/>`);
  }
}

function routeSources(route) {
  if (!evidence) return '';
  const ids = new Set(route.line);
  const sources = new Map(evidence.sources.map(s => [s.id, s]));
  const ordered = [];
  const seen = new Set();
  const edges = evidence.edges.filter(e =>
    ids.has(e.from) && ids.has(e.to) &&
    (layerOf(e.from) === 'sw' || layerOf(e.to) === 'hw' || e.to === route.breakAt));
  // Put the chip-facing edge first, then the software handoffs. Every displayed
  // link is attached to an edge that the highlighted route actually traverses.
  edges.sort((a, b) =>
    (b.to === route.line[route.line.length - 1]) - (a.to === route.line[route.line.length - 1]));
  edges.forEach(e => (e.sources || []).forEach(id => {
    const src = sources.get(id);
    if (src && src.url && !seen.has(id)) { seen.add(id); ordered.push(src); }
  }));
  if (!ordered.length) return '';
  return `<details class="nstk-sources"><summary>Sources for the highlighted route (${ordered.length})</summary>
    <ul>${ordered.map(s => `<li><a href="${esc(s.url)}" target="_blank" rel="noopener noreferrer">${esc(s.title)}</a> <span>${esc(s.type || 'source')}</span></li>`).join('')}</ul>
  </details>`;
}

/* ---------- panel ---------- */
function panel(rs, tracing) {
  const p = $('#nstk-panel');
  if (!tracing) {
    p.innerHTML = `<div class="nstk-guide">No documented route carries that combination. Clear a constraint to widen the question.</div>`;
    return;
  }
  const r = rs[0];
  if (!r) return;

  const cut = r.breakAt ? r.line.indexOf(r.breakAt) : r.line.length - 1;
  const chain = r.line.map((k, i) => {
    const t = label(k) || k;
    const cls = (r.breakAt && i === cut) ? 'nstk-step-chip nstk-step-break' : 'nstk-step-chip';
    const arr = i < r.line.length - 1 ? `<span class="nstk-arr${(r.breakAt && i === cut) ? ' nstk-arr-break' : ''}">${(r.breakAt && i === cut) ? '×' : '→'}</span>` : '';
    return `<span class="${cls}">${esc(t)}</span>${arr}`;
  }).join('');

  const others = rs.slice(1).map(o =>
    `<li class="nstk-route" data-route="${o.id}" style="--pc:${o.pc}" tabindex="0" role="button">
       <span class="nstk-rhead"><b>${esc(o.name)}</b><span class="nstk-evid${o.breakAt ? ' nstk-evid-blocked' : ''}" style="--pc:${o.pc}">${o.ev}</span></span>
       <span class="nstk-rstory">${esc(o.story)}</span></li>`).join('');

  p.innerHTML = `
    <div class="nstk-ph" style="--pc:${r.pc}">
      <span class="nstk-dot" style="--pc:${r.pc}"></span><b>${esc(r.name)}</b>
      <span class="nstk-evid${r.breakAt ? ' nstk-evid-blocked' : ''}" style="--pc:${r.pc}">${r.ev}</span>
      ${r.live ? '<span class="nstk-evid" style="--pc:#237985">live route</span>' : ''}
    </div>
    <div class="nstk-pbody" style="--pc:${r.pc}">
      <div class="nstk-steps">${chain}</div>
      <p class="nstk-note">${esc(r.story)}</p>
      ${r.breakAt ? `<p class="nstk-break-note"><b>Breaks at ${esc(label(r.breakAt) || r.breakAt)}.</b> ${esc(r.breakWhy)}</p>` : ''}
      <p class="nstk-note">${esc(r.note)}</p>
      ${routeSources(r)}
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
function wire() {
  document.addEventListener('click', e => {
    const chip = e.target.closest('.nstk-chip');
    if (chip && !chip.classList.contains('nstk-implied')) {
      const k = chip.dataset.k;
      sel.has(k) ? sel.delete(k) : sel.add(k);
      render(); return;
    }
    const q = e.target.closest('.nstk-quick');
    if (q) { const k = keyFor(q.dataset.q); sel.has(k) ? sel.delete(k) : sel.add(k); render(); return; }
    const ro = e.target.closest('.nstk-route');
    if (ro) { const r = ROUTES.find(x => x.id === ro.dataset.route); if (r) { sel.clear(); r.line.forEach(k => sel.add(k)); render(); } return; }
    if (e.target.closest('#nstk-clear')) { sel.clear(); $('#nstk-q').value = ''; render(); return; }
  });

  $('#nstk-q').addEventListener('input', render);

  document.addEventListener('mouseover', e => { const t = e.target.closest('[data-tip]'); if (t) tipOn(t); });
  document.addEventListener('mouseout', e => { if (e.target.closest('[data-tip]')) tipOff(); });
  document.addEventListener('focusin', e => { const t = e.target.closest('[data-tip]'); if (t) tipOn(t); });
  document.addEventListener('focusout', tipOff);
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') { sel.clear(); $('#nstk-q').value = ''; render(); }
    if ((e.key === 'Enter' || e.key === ' ') && e.target.classList?.contains('nstk-chip')) { e.preventDefault(); e.target.click(); }
  });
  window.addEventListener('resize', () => drawPath(active && $('#nstk-fig').classList.contains('nstk-tracing') ? active : null));
}

build(); wire(); render();
window.addEventListener('load', () => drawPath(active));
fetch('data/evidence-stack.json')
  .then(response => { if (!response.ok) throw new Error('evidence registry unavailable'); return response.json(); })
  .then(data => { evidence = data; render(); })
  .catch(() => { /* The figure still works when opened without the local server. */ });
