#!/usr/bin/env python3
"""Renumber survey tables in reading order across the fragments named by the site manifest.

Reading order = manifest fragment order, and inside a fragment the order of
<caption><b>Table N:</b> labels. Rewrites, from one mapping, every "<b>Table N:</b>"
label, every "Table N" and "Tables N and M" token in site/*.html, site/figures/*.html
and assets/figure.js, and every href="#table-N" numeric anchor. Slug anchors are untouched.
Dry run by default; --apply writes.
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DRY = '--apply' not in sys.argv
sm = json.loads((ROOT / 'data/site-manifest.json').read_text())
order = []
for frag in sm['fragments']:
    text = (ROOT / frag['fragment']).read_text()
    for m in re.finditer(r'<b>\s*Table\s+(\d+)\s*:\s*</b>', text):
        n = int(m.group(1))
        if n in order:
            sys.exit(f'Table {n} is labeled twice; fix the duplicate before renumbering')
        order.append(n)
mapping = {old: new for new, old in enumerate(order, start=1)}
print('mapping (old -> new):', {k: v for k, v in mapping.items() if k != v})

def sub(text):
    # one pass over "Table N" covers the <b>Table N:</b> labels too; a second label-only pass would chain
    text = re.sub(r'\bTable (\d+)(?!\d)', lambda m: f'Table {mapping.get(int(m.group(1)), int(m.group(1)))}', text)
    def plural(m):
        return 'Tables ' + re.sub(r'\d+', lambda n: str(mapping.get(int(n.group(0)), int(n.group(0)))), m.group(1))
    text = re.sub(r'\bTables (\d+(?:(?:, | and | to | through |, and )\d+)*)', plural, text)
    text = re.sub(r'#table-(\d+)(?!\d)', lambda m: f'#table-{mapping.get(int(m.group(1)), int(m.group(1)))}', text)
    text = re.sub(r'id="table-(\d+)"', lambda m: f'id="table-{mapping.get(int(m.group(1)), int(m.group(1)))}"', text)
    return text

changes = {}
for path in sorted((ROOT / 'site').glob('*.html')) + sorted((ROOT / 'site/figures').glob('*.html')) + [ROOT / 'assets/figure.js']:
    if not path.exists(): continue
    t = path.read_text(); u = sub(t)
    if u != t: changes[path] = u
if DRY:
    for p in changes: print('would rewrite', p.relative_to(ROOT))
    sys.exit(0)
for p, u in changes.items(): p.write_text(u)
print('applied')
