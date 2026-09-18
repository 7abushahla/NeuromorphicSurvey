#!/usr/bin/env python3
"""Every chip, toolchain, paper and application of the route map exists in the data.

The map's data is data/figure-guide.json (hand-maintained); the route data is
data/generated/route-index.json (built from data/evidence-stack.json); the surveyed runs
are data/evidence-papers.json. Rules, numbered as in the design spec of 2026-09-19:
  1. every chip is a node; every hardware chip sits in its bucket row; bucket colors
     in assets/figure.css equal data/target-kinds.json;
  2. targets are hardware chips whose target_kind equals the toolchain's tk; tk is a
     known word; vendorFor is a subset of targets;
  3. every chip named in steps, can, implies, via and unreached exists in the slot it is
     named under; steps[slot] is in can[slot];
  4. consecutive software steps on the default line, and the step from the last
     software chip to each target, are edges; the step into breakAt is not exercised on
     silicon; seam names a pin;
  5. papers are E1 or E2 records with the toolchain's target kind; via chips are
     carriable; 5b (with --require-all-papers) every E1/E2 record is placed;
  6. applications key task chips, prefer toolchains, via existing chips;
  7. every non-task chip is reachable or listed under unreached, never both;
  8. every read anchor is an id in site/*.html;
  9. no em dash, en dash or prose colon in any string.

steps[slot] may be a single chip id or an ordered list of chip ids, when a route passes
through two chips of the same row (see step_chips below).
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
guide = json.loads((ROOT / 'data/figure-guide.json').read_text())
index = json.loads((ROOT / 'data/generated/route-index.json').read_text())
papers = json.loads((ROOT / 'data/evidence-papers.json').read_text())['papers']
kinds = json.loads((ROOT / 'data/target-kinds.json').read_text())
css = (ROOT / 'assets/figure.css').read_text()
require_all = '--require-all-papers' in sys.argv

node_type = {n['id']: n.get('type') for n in index['nodes']}
node_kind = {n['id']: (n.get('attributes') or {}).get('target_kind') for n in index['nodes']}
edge_state = {(e['from'], e['to']): e.get('route_state') for e in index['routes']}
edge_evidence = {(e['from'], e['to']): e.get('evidence_class') or e.get('evidence') for e in index['routes']}
physical = lambda p: edge_state.get(p) == 'physical' or edge_evidence.get(p) in {'E1', 'E2'}
bucket_of_kind = {k['word']: k['bucket'] for k in kinds['kinds']}
buckets = {b['name']: b for b in kinds['buckets']}
paper_by_id = {p['id']: p for p in papers}
deploying = {p['id'] for p in papers if p.get('evidence') in {'E1', 'E2'}}
pins = {s['pin'] for group in guide['seams'].values() for s in group}
anchors = set()
for f in (ROOT / 'site').glob('*.html'):
    anchors.update(re.findall(r'\sid="([^"]+)"', f.read_text()))

slots = guide['slots']
slot_of, label_of, bucket_row = {}, {}, {}
for L in guide['layers']:
    for row in L['rows']:
        for c in row['chips']:
            slot_of[c['id']] = row['slot']; label_of[c['id']] = c['label']
            if row.get('bucket'): bucket_row[c['id']] = row['bucket']
errors = []
err = errors.append


def step_chips(t, slots_wanted=None):
    """The chips a toolchain draws, in slot order; steps[slot] may be one id or an ordered list."""
    out = []
    for slot in (slots_wanted or [s for s in t['steps']]):
        v = t['steps'].get(slot)
        if v is None: continue
        out.extend(v if isinstance(v, list) else [v])
    return out


# 1
for chip, slot in slot_of.items():
    if chip not in node_type:
        err(f"rule 1: chip {chip!r} is not a node in route-index.json"); continue
    if slot == 'hw':
        if node_type[chip] != 'hardware':
            err(f"rule 1: hardware chip {chip!r} is a {node_type[chip]!r} node, not a hardware node")
        b = bucket_row.get(chip)
        if b not in buckets:
            err(f"rule 1: hardware chip {chip!r} sits in a row with no bucket from data/target-kinds.json ({b!r})")
        elif bucket_of_kind.get(node_kind.get(chip)) != b:
            err(f"rule 1: hardware chip {chip!r} sits in the {b!r} row but its node records target_kind {node_kind.get(chip)!r} ({bucket_of_kind.get(node_kind.get(chip))!r})")
if {b['name'] for b in guide['buckets']} != set(buckets):
    err(f"rule 1: guide buckets {sorted(b['name'] for b in guide['buckets'])} differ from data/target-kinds.json {sorted(buckets)}")
for b in guide['buckets']:
    if b['name'] in buckets and b['meaning'] != buckets[b['name']]['meaning']:
        err(f"rule 1: guide bucket meaning for {b['name']!r} differs from data/target-kinds.json")
for name, b in buckets.items():
    rules = ''.join(body for sel, body in re.findall(r'([^{}]+)\{([^{}]*)\}', css) if f'[data-bucket="{name}"]' in sel)
    if not rules:
        err(f'rule 1: figure.css has no rule for [data-bucket="{name}"]'); continue
    for key in ('line', 'fill', 'ink'):
        if b[key].lower() not in rules.lower():
            err(f'rule 1: figure.css rule for [data-bucket="{name}"] lacks the bucket {key} color {b[key]}')

def chip_in_slot(owner, chip, slot, where):
    if chip not in slot_of:
        err(f"rule 3: {owner} names {chip!r} under {where} but it is not a chip on the map"); return False
    if slot_of[chip] != slot:
        err(f"rule 3: {owner} names {chip!r} under slot {slot} but it sits in slot {slot_of[chip]}"); return False
    return True

reached = {}
for tid, t in guide['toolchains'].items():
    owner = f"toolchain {tid!r}"
    # 2
    if t['tk'] not in bucket_of_kind:
        err(f"rule 2: {owner} has tk {t['tk']!r} which is not a word in data/target-kinds.json")
    if not t.get('targets'):
        err(f"rule 2: {owner} has no targets")
    for h in t.get('targets', []):
        if slot_of.get(h) != 'hw':
            err(f"rule 2: {owner} target {h!r} is not a hardware chip"); continue
        if node_kind.get(h) != t['tk']:
            err(f"rule 2: {owner} has tk {t['tk']!r} but its target {h!r} records target_kind {node_kind.get(h)!r}")
        reached.setdefault(h, tid)
    for h in t.get('vendorFor', []):
        if h not in t.get('targets', []):
            err(f"rule 2: {owner} names vendorFor {h!r} outside its targets")
    # 3
    for slot, v in t['steps'].items():
        if slot not in slots or slot == 'hw':
            err(f"rule 3: {owner} steps names {slot!r} which is not a non-hardware slot")
        if v is None: continue
        for chip in (v if isinstance(v, list) else [v]):
            if chip_in_slot(owner, chip, slot, f"steps.{slot}") and chip not in t['can'].get(slot, []):
                err(f"rule 3: {owner} step {slot} {chip!r} is not in can.{slot}")
    for slot, chips in t['can'].items():
        if slot not in slots or slot in ('task', 'hw'):
            err(f"rule 3: {owner} can names {slot!r} which is not a restricting slot")
        for chip in chips:
            if chip_in_slot(owner, chip, slot, f"can.{slot}"): reached.setdefault(chip, tid)
    for chip in t.get('implies', []):
        if chip not in slot_of:
            err(f"rule 3: {owner} implies {chip!r} which is not a chip on the map")
        elif slot_of[chip] in ('task', 'hw'):
            err(f"rule 3: {owner} implies {chip!r} which sits in slot {slot_of[chip]}")
        else:
            reached.setdefault(chip, tid)
    for chip in t.get('after', []):
        if chip not in slot_of:
            err(f"rule 3: {owner} after names {chip!r} which is not a chip on the map")
        elif slot_of[chip] in ('task', 'hw'):
            err(f"rule 3: {owner} after names {chip!r} which sits in slot {slot_of[chip]}")
    # 4
    sw = step_chips(t, ('dev', 'export', 'compile', 'run'))
    break_at = t.get('breakAt')
    pairs = list(zip(sw, sw[1:]))
    if sw:
        pairs += [(sw[-1], h) for h in t.get('targets', [])]
    for a, b in pairs:
        if b == break_at:
            if (a, b) in edge_state and physical((a, b)):
                err(f"rule 4: {owner} breaks at {b!r} but the data records {a} -> {b} as exercised on silicon")
            break
        if (a, b) not in edge_state:
            err(f"rule 4: {owner} draws {a} -> {b} but no edge records it")
    if break_at:
        if break_at not in step_chips(t) + t.get('targets', []):
            err(f"rule 4: {owner} breakAt {break_at!r} is not on its line")
        if not t.get('breakWhy'):
            err(f"rule 4: {owner} breaks without a breakWhy")
        if t.get('seam') and t['seam'] not in pins:
            err(f"rule 4: {owner} names seam {t['seam']!r} which is not a pin")
    # 5
    for p in t.get('papers', []):
        pid = p.get('id')
        if pid not in deploying:
            err(f"rule 5: {owner} lists paper {pid!r} which is not an E1 or E2 record"); continue
        if paper_by_id[pid].get('target_kind') != t['tk']:
            err(f"rule 5: {owner} lists paper {pid!r} of target kind {paper_by_id[pid].get('target_kind')!r} under tk {t['tk']!r}")
        for slot, chip in (p.get('via') or {}).items():
            if slot not in slots:
                err(f"rule 5: {owner} paper {pid!r} via names slot {slot!r}"); continue
            if slot == 'task':
                if slot_of.get(chip) != 'task': err(f"rule 5: {owner} paper {pid!r} via task {chip!r} is not a task chip")
            elif slot == 'hw':
                if chip not in t.get('targets', []): err(f"rule 5: {owner} paper {pid!r} via hw {chip!r} is not a target")
            elif chip not in t['can'].get(slot, []) and chip not in t.get('implies', []):
                err(f"rule 5: {owner} paper {pid!r} via {slot} {chip!r} is not in can.{slot} or implies")
placed = {p['id'] for t in guide['toolchains'].values() for p in t.get('papers', [])}
if require_all:
    for pid in sorted(deploying - placed):
        err(f"rule 5b: {paper_by_id[pid]['evidence']} record {pid!r} appears under no toolchain")
# 6
for task, a in guide['applications'].items():
    if slot_of.get(task) != 'task':
        err(f"rule 6: application {task!r} is not a task chip")
    for tid in a.get('prefer', []):
        if tid not in guide['toolchains']:
            err(f"rule 6: application {task!r} prefers {tid!r} which is not a toolchain")
    for slot, chip in (a.get('via') or {}).items():
        if chip not in slot_of or slot_of[chip] != slot:
            err(f"rule 6: application {task!r} via {slot} {chip!r} is not a chip in that slot")
# 7
for chip, slot in slot_of.items():
    if slot == 'task': continue
    if chip in reached and chip in guide['unreached']:
        err(f"rule 7: chip {chip!r} is listed under unreached but toolchain {reached[chip]!r} reaches it")
    if chip not in reached and chip not in guide['unreached']:
        err(f"rule 7: chip {chip!r} is reached by no toolchain and is not listed under unreached")
for chip in guide['unreached']:
    if chip not in slot_of:
        err(f"rule 3: unreached names {chip!r} which is not a chip on the map")
# 8
for group, entries in (('notes', guide['notes']), ('unreached', guide['unreached'])):
    for chip, e in entries.items():
        read = e.get('read')
        if read and read.lstrip('#') not in anchors:
            err(f"rule 8: read anchor {read!r} ({group} {chip}) is not an id in site/*.html")
# 9
PROSE_COLON = re.compile(r'(?<![A-Za-z0-9_=]):(?![A-Za-z0-9_=/])|: ')
def walk(value, path):
    if isinstance(value, dict):
        for k, v in value.items(): walk(v, f"{path}.{k}" if path else k)
    elif isinstance(value, list):
        for i, v in enumerate(value): walk(v, f"{path}[{i}]")
    elif isinstance(value, str):
        if '—' in value: err(f"rule 9: {path} contains an em dash")
        if '–' in value: err(f"rule 9: {path} contains an en dash")
        if not path.endswith('.read') and not path.endswith('.color') and PROSE_COLON.search(value):
            err(f"rule 9: {path} contains a prose colon")
walk({k: v for k, v in guide.items() if k in ('toolchains', 'applications', 'notes', 'unreached', 'seams', 'rails', 'buckets', 'layers')}, '')

if errors:
    print('\n'.join(errors)); sys.exit(1)
print(f"check-figure-map: {len(slot_of)} chips, {len(guide['toolchains'])} toolchains, {len(placed)} placed papers and "
      f"{len(guide['unreached'])} unreached chips agree with the route data" + (" (every E1 and E2 record placed)" if require_all else ""))
