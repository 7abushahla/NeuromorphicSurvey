#!/usr/bin/env python3
"""Every chip and every drawn route on the stack map exists in the route data.

The map (assets/figure.js) is hand-written; the route data (data/generated/route-index.json)
is built from data/evidence-stack.json. This checker holds the map to the data:

  1. every chip on the map is a node, and every id on a route's `line` is a node and a chip;
  2. every hardware chip sits in the bucket row that data/target-kinds.json assigns to the
     target kind its node records;
  3. every software-to-hardware step a route draws is an edge in the data. The one step
     into a route's `breakAt` chip is the documented refusal, so there the data must record
     either no edge at all or an edge not recorded as exercised on silicon (route_state
     physical, or E1/E2 evidence on a legacy edge without a route_state);
  4. every route names its target's chip word (`tk`), which equals the target kind of the
     hardware node its line ends on;
  5. the bucket names and meanings in figure.js, and the bucket colors in figure.css, are
     those of data/target-kinds.json.
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
js = (ROOT / 'assets/figure.js').read_text()
css = (ROOT / 'assets/figure.css').read_text()
index = json.loads((ROOT / 'data/generated/route-index.json').read_text())
kinds = json.loads((ROOT / 'data/target-kinds.json').read_text())
node_ids = {n['id'] for n in index['nodes']}
node_type = {n['id']: n.get('type') for n in index['nodes']}
node_kind = {n['id']: (n.get('attributes') or {}).get('target_kind') for n in index['nodes']}
# The software layer holds framework, exchange, compiler, runtime and method nodes; the
# hardware layer holds hardware nodes. Application, learning-path, code and neuron chips
# are selections, not steps the data chains.
STACK_TYPES = {'framework', 'exchange', 'compiler', 'runtime', 'method', 'hardware'}
edge_state = {(e['from'], e['to']): e.get('route_state') for e in index['routes']}
edge_evidence = {(e['from'], e['to']): e.get('evidence_class') or e.get('evidence') for e in index['routes']}
edge_pairs = set(edge_state)
# An edge the data records as exercised on silicon: route_state physical, or E1/E2 evidence
# on the legacy edges that carry no route_state.
physical = lambda pair: edge_state.get(pair) == 'physical' or edge_evidence.get(pair) in {'E1', 'E2'}
bucket_of_kind = {k['word']: k['bucket'] for k in kinds['kinds']}
buckets = {b['name']: b for b in kinds['buckets']}
words = set(bucket_of_kind)

layers_src = js[js.index('const LAYERS'):js.index('const ROUTES')]
chip_ids = set(re.findall(r"\['([a-z0-9-]+)', '", layers_src))
routes_src = js[js.index('const ROUTES'):js.index('];', js.index('const ROUTES')) + 2]
errors = []

# 1. Chips are nodes.
for chip in sorted(chip_ids):
    if chip not in node_ids:
        errors.append(f'map chip {chip!r} is not a node in route-index.json')

# 2. Hardware rows carry a bucket, and each chip's node belongs to that bucket.
hw_src = layers_src[layers_src.index("id: 'hw'"):]
hw_rows = re.findall(r"\{ label: '([^']+)',(?: bucket: '([a-z]+)',)? chips: \[(.*?)\] \}", hw_src, re.S)
if not hw_rows:
    errors.append('no hardware rows found in figure.js')
gathered = sum(len(re.findall(r"\['([a-z0-9-]+)', '", chips)) for _, _, chips in hw_rows)
in_source = len(re.findall(r"\['([a-z0-9-]+)', '", hw_src))
if gathered != in_source:
    errors.append(f'hardware rows gathered {gathered} chips but the hardware layer source holds {in_source} chip tuples; a row the parser did not match')
for label, bucket, chips in hw_rows:
    if bucket not in buckets:
        errors.append(f'hardware row {label!r} has no bucket from data/target-kinds.json (found {bucket!r})')
    for chip in re.findall(r"\['([a-z0-9-]+)', '", chips):
        if chip not in node_ids:
            errors.append(f'hardware chip {chip!r} is not a node in route-index.json')
            continue
        if node_type.get(chip) != 'hardware':
            errors.append(f'hardware chip {chip!r} is a {node_type.get(chip)!r} node, not a hardware node')
        kind = node_kind.get(chip)
        if bucket_of_kind.get(kind) != bucket:
            errors.append(f'hardware chip {chip!r} sits in the {bucket!r} row but its node records target_kind {kind!r} ({bucket_of_kind.get(kind)!r})')

# 3 and 4. Routes: every line id is a chip, the software-to-hardware steps are edges, the
# break step is a recorded refusal or absence, and `tk` is the terminal node's target kind.
route_count = 0
for m in re.finditer(r"\{ id: '([a-z0-9-]+)'(.*?)line: \[(.*?)\]", routes_src, re.S):
    route_count += 1
    rid, head, line = m.group(1), m.group(2), re.findall(r"'([a-z0-9-]+)'", m.group(3))
    break_at = (re.search(r"breakAt: '([a-z0-9-]+)'", head) or [None, None])[1]
    tk = (re.search(r"tk: '([^']+)'", head) or [None, None])[1]
    for k in line:
        if k not in node_ids:
            errors.append(f'route {rid}: line id {k!r} is not a node in route-index.json')
        if k not in chip_ids:
            errors.append(f'route {rid}: line id {k!r} is not a chip on the map')
    if break_at and break_at not in line:
        errors.append(f'route {rid}: breakAt {break_at!r} is not on its line')
    sw_and_hw = [c for c in line if node_type.get(c) in STACK_TYPES]
    for a, b in zip(sw_and_hw, sw_and_hw[1:]):
        if (a, b) in edge_pairs:
            if b == break_at and physical((a, b)):
                errors.append(f'route {rid}: drawn as breaking at {b!r}, but the data records {a} -> {b} as exercised on silicon')
        elif b != break_at:
            errors.append(f'route {rid}: no edge {a} -> {b} in route-index.json')
    last = line[-1] if line else None
    if node_type.get(last) != 'hardware':
        errors.append(f'route {rid}: line does not end on a hardware node (ends on {last!r})')
    elif tk is None:
        errors.append(f'route {rid}: no tk (chip word) for its target {last!r}')
    elif tk not in words:
        errors.append(f'route {rid}: tk {tk!r} is not a word in data/target-kinds.json')
    elif tk != node_kind.get(last):
        errors.append(f'route {rid}: tk {tk!r} but its target {last!r} records target_kind {node_kind.get(last)!r}')
if route_count == 0:
    errors.append('no routes found in figure.js')

# 5. Bucket names, meanings and colors follow data/target-kinds.json.
bucket_src = js[js.index('const BUCKETS'):js.index('];', js.index('const BUCKETS'))]
js_buckets = {n: mn.replace("\\'", "'") for n, mn in re.findall(r"\['([a-z]+)', '((?:[^'\\]|\\.)*)'\]", bucket_src)}
if set(js_buckets) != set(buckets):
    errors.append(f'figure.js BUCKETS names {sorted(js_buckets)} differ from data/target-kinds.json {sorted(buckets)}')
for name, meaning in js_buckets.items():
    if name in buckets and meaning != buckets[name]['meaning']:
        errors.append(f'figure.js BUCKETS meaning for {name!r} differs from data/target-kinds.json')
for name, b in buckets.items():
    rules = ''.join(body for sel, body in re.findall(r'([^{}]+)\{([^{}]*)\}', css) if f'[data-bucket="{name}"]' in sel)
    if not rules:
        errors.append(f'figure.css has no rule for [data-bucket="{name}"]')
        continue
    for key in ('line', 'fill', 'ink'):
        if b[key].lower() not in rules.lower():
            errors.append(f'figure.css rule for [data-bucket="{name}"] lacks the bucket {key} color {b[key]}')

if errors:
    print('\n'.join(errors)); sys.exit(1)
print(f'check-figure-map: {len(chip_ids)} chips and {route_count} routes on the map agree with the route data; '
      'every hardware chip sits in its bucket, every drawn software-to-hardware step is an edge, and every route names its target kind')
