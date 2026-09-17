#!/usr/bin/env python3
"""Renumber survey sections from the site manifest.

The manifest's section records, in file order, define the new numbers (1, 2, ... in
order of appearance). The inserted record carries the number it wants in its id prefix
(section-NN-) and its display_number; the records after it still carry their old
numbers, so the first repeated prefix number marks the insertion and the earlier record
with that prefix is the new one. Rewrites, from one mapping: manifest display numbers
and section-NN- id prefixes, fragment filenames (git mv, highest first), figure-manifest
destination_section slugs, heading numbers in <h2>/<h3>/<h4>, "Section N",
"Section N.M", "Sections N and M" tokens in the manifest's fragments, site/figures/*.html
and assets/figure.js, and the "| N. Title |" rows of research/rewrite/section-map.md.
The new fragment, written by hand with its own numbers, is never rewritten; with
--new-fragment PATH it is moved into the manifest's path for the new record after the
renames. Dry run by default; --apply writes.
"""
import json, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DRY = '--apply' not in sys.argv
NEW_FRAGMENT = ROOT / sys.argv[sys.argv.index('--new-fragment') + 1] if '--new-fragment' in sys.argv else None
manifest_path = ROOT / 'data/site-manifest.json'
sm = json.loads(manifest_path.read_text())
sections = [f for f in sm['fragments'] if f.get('kind') == 'section']

prefix = lambda rec: int(re.match(r'section-(\d+)-', rec['id']).group(1))
seen = set(); new_record = None
for rec in sections:
    n = prefix(rec)
    if n in seen and new_record is None:
        new_record = next(r for r in sections if prefix(r) == n)
    seen.add(n)
if new_record is None:
    sys.exit('no inserted section found (every section-NN- prefix is unique); nothing to do')
mapping = {}; new_number = 1
for rec in sections:
    if rec is new_record:
        new_number += 1; continue
    mapping[prefix(rec)] = new_number; new_number += 1
print('mapping (old -> new):', {k: v for k, v in mapping.items() if k != v})

def map_num(n): return mapping.get(n, n)
def map_token(tok):  # "12" or "12.3"
    head, _, tail = tok.partition('.')
    return str(map_num(int(head))) + (('.' + tail) if tail else '')

NUM = r'\d+(?:\.\d+)?'
TAGWS = r'(?:<[^>]+>|\s)*'
# A "Sections A ... B" list may wrap across a line break in the source prose, or split
# each number into its own <a> deep link ("Sections 12</a> through <a ...>13</a>"),
# leaving the second (and later) numbers with no adjacent "Section" word of their own.
# The connector tolerates embedded tags and any whitespace, not just a literal space,
# so every number in the list is captured for substitution regardless of markup.
PLURAL = re.compile(rf'\bSections(?:<[^>]+>|\s)+{NUM}(?:{TAGWS}(?:,|\band\b|\bto\b|\bthrough\b){TAGWS}(?:Sections?{TAGWS})?{NUM})+', re.S)

def sub_tokens(text):
    text = re.sub(r'\bSection (\d+(?:\.\d+)?)(?!\d)', lambda m: 'Section ' + map_token(m.group(1)), text)
    text = PLURAL.sub(lambda m: re.sub(NUM, lambda n: map_token(n.group(0)), m.group(0)), text)
    text = re.sub(r'section-(\d+)-', lambda m: f'section-{map_num(int(m.group(1))):02d}-', text)
    return text

def sub_headings(text):
    return re.sub(r'(<h[2-4]\b[^>]*>)\s*(\d+)((?:\.\d+)*)\.?\s+', lambda m: f'{m.group(1)}{map_num(int(m.group(2)))}{m.group(3)} ', text)

new_fragment_target = ROOT / new_record['fragment']
targets = [ROOT / f['fragment'] for f in sm['fragments'] if (ROOT / f['fragment']).exists() and (ROOT / f['fragment']) != NEW_FRAGMENT]
targets += sorted((ROOT / 'site/figures').glob('*.html')) + [ROOT / 'assets/figure.js', ROOT / 'research/rewrite/section-map.md']
changes = {}
for path in targets:
    if not path.exists(): continue
    t = path.read_text(); u = sub_tokens(t)
    if path.suffix == '.html' and path.parent == ROOT / 'site':
        u = sub_headings(u)
    if path.name == 'section-map.md':
        u = re.sub(r'^\| (\d+)\. ', lambda m: f'| {map_num(int(m.group(1)))}. ', u, flags=re.M)
    if u != t: changes[path] = u

renames = []
for rec in sections:
    if rec is new_record: continue
    old = prefix(rec); new = mapping[old]
    if new != old:
        renames.append((ROOT / f'site/sec-{old:02d}.html', ROOT / f'site/sec-{new:02d}.html'))
        rec['fragment'] = f'site/sec-{new:02d}.html'
    rec['display_number'] = new
    rec['id'] = re.sub(r'^section-\d+-', f'section-{new:02d}-', rec['id'])
new_record['display_number'] = prefix(new_record)

fm_path = ROOT / 'data/figure-manifest.json'
fm_text = fm_path.read_text(); fm_new = sub_tokens(fm_text)

if DRY:
    for p in changes: print('would rewrite', p.relative_to(ROOT))
    for a, b in renames: print('would rename', a.name, '->', b.name)
    if NEW_FRAGMENT: print('would move', NEW_FRAGMENT.relative_to(ROOT), '->', new_fragment_target.relative_to(ROOT))
    if fm_new != fm_text: print('would rewrite data/figure-manifest.json')
    print('would rewrite data/site-manifest.json'); sys.exit(0)

for a, b in sorted(renames, key=lambda r: -int(re.search(r'(\d+)', r[0].name).group(1))):
    content = changes.pop(a, a.read_text())
    subprocess.run(['git', 'mv', str(a), str(b)], cwd=ROOT, check=True)
    b.write_text(content)
for p, u in changes.items(): p.write_text(u)
if NEW_FRAGMENT:
    subprocess.run(['git', 'mv', str(NEW_FRAGMENT), str(new_fragment_target)], cwd=ROOT, check=True)
fm_path.write_text(fm_new)
manifest_path.write_text(json.dumps(sm, indent=2, ensure_ascii=False) + '\n')
print('applied')
