#!/usr/bin/env node
// Tests of assets/figure-engine.js against the built view. From the repository root,
// run `node tools/verify-figure-engine.mjs`.
import { readFileSync } from 'node:fs';
import assert from 'node:assert/strict';
import { createEngine } from '../assets/figure-engine.js';

const view = JSON.parse(readFileSync(new URL('../data/generated/figure-guide-view.json', import.meta.url), 'utf8'));
const E = createEngine(view);
const tests = [];
const test = (name, fn) => tests.push([name, fn]);

test('every chip has a slot and every slot is known', () => {
  for (const c of E.chips.values()) assert.ok(E.slots.includes(c.slot), c.id);
});
test('a blank query has every toolchain viable, completing first', () => {
  const vp = E.viable(E.blank());
  assert.equal(vp.length, Object.keys(view.toolchains).length);
  const firstBroken = vp.findIndex(t => view.toolchains[t].breakAt);
  const lastWhole = vp.map(t => !view.toolchains[t].breakAt).lastIndexOf(true);
  assert.ok(firstBroken === -1 || firstBroken > lastWhole, 'broken toolchains rank last');
});
test('selecting a hardware chip keeps only toolchains that target it', () => {
  const Q = E.applyQuery(E.blank(), 'speck');
  assert.deepEqual(E.viable(Q).every(t => view.toolchains[t].targets.includes('speck')), true);
  assert.equal(E.picked(Q), 'sinabs-speck');
});
test('a live route outranks a plain one and vendorFor leads on its own part', () => {
  const Q = E.applyQuery(E.blank(), 'speck');
  assert.equal(E.recommended(Q), 'sinabs-speck');
});
test('a task ranks and never restricts', () => {
  const task = Object.keys(view.applications)[0];
  if (!task) return;
  const Q = E.applyQuery(E.blank(), task);
  assert.equal(E.viable(Q).length, Object.keys(view.toolchains).length);
  assert.equal(E.viable(Q)[0], view.applications[task].prefer[0]);
});
test('an unreachable combination is dead with a subject', () => {
  let Q = E.applyQuery(E.blank(), 'speck');
  Q = E.applyQuery(Q, 'loihi-2');            // same slot: replaces, still alive
  assert.equal(Q.sel.hw, 'loihi-2'); assert.equal(Q.dead, null);
  Q = E.applyQuery(E.blank(), 'quantizeml');
  Q = E.applyQuery(Q, 'speck');
  assert.equal(Q.dead, 'speck');
});
test('lineOf walks the slots in order and ends on a target', () => {
  const Q = E.applyQuery(E.blank(), 'speck');
  const line = E.lineOf('sinabs-speck', Q);
  const order = line.map(k => E.slots.indexOf(E.slotOf(k)));
  assert.deepEqual(order, [...order].sort((a, b) => a - b));
  assert.equal(line[line.length - 1], 'speck');
});
test('a broken toolchain stops at breakAt', () => {
  const Q = E.applyQuery(E.blank(), 'spikingjelly');
  const tid = E.viable(Q).find(t => view.toolchains[t].breakAt === 'nir');
  assert.ok(tid);
  const line = E.lineOf(tid, Q);
  assert.equal(line[line.length - 1], 'nir');
  assert.equal(E.cutOf(tid), line.length - 1);
});
test('routeSources resolves every edge source on the line', () => {
  const Q = E.applyQuery(E.blank(), 'cortex-m-mcu');
  const tid = E.picked(Q);
  const srcs = E.routeSources(tid, Q);
  assert.ok(srcs.length >= 1, 'the Cortex-M4 route lists its sources');
  assert.ok(srcs.every(s => s.url && s.title));
});
test('routePapers lists only papers whose via agrees with the selection', () => {
  const tid = Object.keys(view.toolchains).find(t => (view.toolchains[t].papers || []).length);
  if (!tid) return;
  const Q = E.blank();
  assert.equal(E.routePapers(tid, Q).length, view.toolchains[tid].papers.length);
});
test('reachable is false for a chip no toolchain can carry with the selection', () => {
  const Q = E.applyQuery(E.blank(), 'quantizeml');
  assert.equal(E.reachable('speck', Q), false);
  assert.equal(E.reachable('akida', Q), true);
});
test('every chip either reaches a route or is listed as unreached', () => {
  for (const c of E.chips.values()) {
    if (c.slot === 'task') continue;
    const ok = E.reachable(c.id, E.blank()) || !!view.unreached[c.id];
    assert.ok(ok, c.id);
  }
});
// A step may name an ordered pair of chips. The line draws both, in the order given,
// and a broken toolchain stops at its break with the rest of the chain kept in after.
test('an ordered step draws both chips and the break ends the line', () => {
  const T = view.toolchains['spikingjelly-nir'];
  const line = E.lineOf('spikingjelly-nir', E.blank());
  assert.equal(line.indexOf('nir-exchange'), line.indexOf('nir') - 1, 'nir_exchange sits immediately before NIR');
  assert.equal(line[line.length - 1], 'nir', 'the line ends at the break');
  assert.equal(E.cutOf('spikingjelly-nir'), line.length - 1);
  assert.deepEqual(T.after, ['lava-dl', 'netx', 'lava-runtime'], 'the chain past the break is kept in after');
  assert.ok(T.after.every(k => !line.includes(k)), 'nothing past the break is on the line');
});
test('an ordered development step keeps its given order', () => {
  const line = E.lineOf('nest-cpu', E.blank());
  assert.equal(line.indexOf('pynn'), line.indexOf('nest') - 1, 'PyNN sits immediately before NEST');
});

let failed = 0;
for (const [name, fn] of tests) {
  try { fn(); console.log('ok   ', name); } catch (e) { failed++; console.log('FAIL ', name, '\n     ', e.message); }
}
console.log(`${tests.length - failed} of ${tests.length} engine tests passed`);
process.exit(failed ? 1 : 0);
