#!/usr/bin/env python3
"""Renumber survey figures in article order, driven by the figure manifest.

Article order = build order of fragments (site-manifest), and inside each fragment the
order of <figure id="figure-N"> elements (or the figcaption id for the interactive map).
Implemented static fragments are renamed to their semantic id. Every hard-coded number
(figure DOM ids, caption labels, "Figure N" text tokens, SVG id prefixes fN..., CSS scopes)
is rewritten from one mapping so no chain collisions occur.
"""
import json, re, sys, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DRY = '--apply' not in sys.argv

fm = json.loads((ROOT / 'data/figure-manifest.json').read_text())
sm = json.loads((ROOT / 'data/site-manifest.json').read_text())
records = {r['display_number']: r for r in fm['figures']}

# 1. article order
order = []
for frag in sm['fragments']:
    text = (ROOT / frag['fragment']).read_text()
    for m in re.finditer(r'<(?:figure|figcaption)\b[^>]*\bid="figure-(\d+)"', text):
        n = int(m.group(1))
        if n in records and n not in order:
            order.append(n)
missing = sorted(set(records) - set(order))
if missing:
    sys.exit(f'figures without a placeholder in any fragment: {missing}')
mapping = {old: new for new, old in enumerate(order, start=1)}
print('mapping (old -> new):', {k: v for k, v in mapping.items() if k != v})

# 2. rewrite section and shell fragments: figure-N ids/anchors and "Figure N" tokens
def sub_numbers(text):
    text = re.sub(r'figure-(\d+)(?!\d)', lambda m: f'figure-{mapping.get(int(m.group(1)), int(m.group(1)))}', text)
    text = re.sub(r'\bFigure (\d+)(?!\d)', lambda m: f'Figure {mapping.get(int(m.group(1)), int(m.group(1)))}', text)
    # plural lists such as "Figures 11 and 12", "Figures 1 to 26", "Figures 3, 4, and 5"
    def plural(m):
        return 'Figures ' + re.sub(r'\d+', lambda n: str(mapping.get(int(n.group(0)), int(n.group(0)))), m.group(1))
    text = re.sub(r'\bFigures (\d+(?:(?:, | and | through | to |, and )\d+)*)', plural, text)
    return text

changed = {}
for frag in sm['fragments']:
    if frag.get('kind') not in ('section', 'interactive'):
        continue
    p = ROOT / frag['fragment']
    t = p.read_text(); u = sub_numbers(t)
    if u != t:
        changed[p] = u

# 3. rewrite figure fragments and css, rename to semantic id
renames = []
for old, rec in records.items():
    new = mapping[old]
    frag = ROOT / rec['fragment']; css = ROOT / rec['css']
    if rec['status'] == 'implemented' and not rec['interactive']:
        t = frag.read_text()
        t = sub_numbers(t)  # own id, caption label, and any cross-reference to another figure, from the one mapping
        t = re.sub(rf'<b>\s*Figure\s+{new}\s*\.\s*</b>', f'<b>Figure {new}:</b>', t)
        t = re.sub(rf'(?<![A-Za-z0-9_])f{old}(?=[A-Za-z_-])', f'f{new}', t)  # SVG id prefixes fNname
        c = css.read_text() if css.exists() else ''
        c2 = re.sub(rf'figure-{old}(?!\d)', f'figure-{new}', c)
        c2 = re.sub(rf'(?<![A-Za-z0-9_])f{old}(?=[A-Za-z_-])', f'f{new}', c2)
        new_frag = ROOT / 'site/figures' / f"{rec['id']}.html"
        new_css = ROOT / 'site/figures' / f"{rec['id']}.css"
        renames.append((frag, new_frag, t, css, new_css, c2))
        rec['fragment'] = str(new_frag.relative_to(ROOT)); rec['css'] = str(new_css.relative_to(ROOT))
    rec['display_number'] = new
fm['figures'].sort(key=lambda r: r['display_number'])

if DRY:
    for p in changed: print('would rewrite', p.relative_to(ROOT))
    for a, b, *_ in renames: print('would rename', a.name, '->', b.name)
    sys.exit(0)

for p, u in changed.items(): p.write_text(u)
for frag, new_frag, t, css, new_css, c2 in renames:
    if frag != new_frag:
        subprocess.run(['git', 'mv', str(frag), str(new_frag)], cwd=ROOT, check=True)
        if css.exists(): subprocess.run(['git', 'mv', str(css), str(new_css)], cwd=ROOT, check=True)
    new_frag.write_text(t); new_css.write_text(c2)
lines = ['{', f'  "schema_version": {json.dumps(fm["schema_version"])},', '  "figures": [']
lines += [('    ' + json.dumps(r, separators=(',', ':'), ensure_ascii=False) + (',' if i < len(fm['figures']) - 1 else '')) for i, r in enumerate(fm['figures'])]
lines += ['  ]', '}']
(ROOT / 'data/figure-manifest.json').write_text('\n'.join(lines) + '\n')
print('applied')
