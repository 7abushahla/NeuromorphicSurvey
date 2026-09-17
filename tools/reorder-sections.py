#!/usr/bin/env python3
"""Reorder survey sections from data/section-reorder.json.

Reads every section fragment named by data/site-manifest.json, splits it into its intro
(the content between <h2> and the first <h3>) and one block per <h3>, and rebuilds the
fragments named by the plan: each plan section becomes site/sec-NN.html holding its <h2>,
its intro(s), and its subsections in plan order. A folded old heading keeps its id as an
inline <span id> at the top of its content. Every "Section N", "Section N.M" and
"Sections A ... B" token in the fragments, site/figures/*.html, site/shell-figure.html,
assets/figure.js and data/evidence-stack.json is rewritten from the old-to-new map; every
href="#anchor" whose anchor stopped being a heading is retargeted, a folded <h3> to the <h3>
that now holds it and a folded <h2> to the new section's <h2> (a bare "Section N" token is a
section-level reference, so it names the whole new section rather than the subsection its
intro landed in); the words of every anchored "Section N, Words,</a>" token become the new title;
the site manifest (ids, numbers, titles, fragments, map position) and the figure manifest's
destination_section slugs are rewritten. Plural "Sections A ... B" tokens and chains of
singular "Section N and Section M" tokens whose numbers collapse (two old sections now one)
are reported, not rewritten. Dry run by default; --apply writes.
"""
import json, re, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
DRY = '--apply' not in sys.argv
plan = json.loads((ROOT / 'data/section-reorder.json').read_text())
sm_path = ROOT / 'data/site-manifest.json'; sm = json.loads(sm_path.read_text())
old_sections = [f for f in sm['fragments'] if f.get('kind') == 'section']

H2 = re.compile(r'<h2\b[^>]*\bid="([^"]+)"[^>]*>\s*(\d+)\s+(.*?)\s*</h2>', re.S)
H3 = re.compile(r'<h3\b[^>]*\bid="([^"]+)"[^>]*>\s*(\d+)\.(\d+)\s+(.*?)\s*</h3>', re.S)
blocks, intro, old_num, old_h2_num = {}, {}, {}, {}
for rec in old_sections:
    text = (ROOT / rec['fragment']).read_text()
    m2 = H2.search(text); sec = m2.group(1); old_h2_num[sec] = int(m2.group(2))
    if text[:m2.start()].strip(): sys.exit(f"{rec['fragment']}: content before the <h2> would be dropped")
    parts = re.split(r'(?=<h3\b)', text[m2.end():])
    intro[sec] = parts[0].strip('\n')
    for part in parts[1:]:
        m3 = H3.match(part); a = m3.group(1)
        blocks[a] = part[m3.end():].strip('\n'); old_num[a] = f'{m3.group(2)}.{m3.group(3)}'

def slug(title):
    return re.sub(r'-+', '-', re.sub(r'[^a-z0-9]+', '-', title.lower())).strip('-')

new_text, anchor_num, retarget, new_title, new_id = {}, {}, {}, {}, {}
used_blocks, used_intros = set(), set()
for sec in plan['sections']:
    n = sec['number']; sid = f"section-{n:02d}-{slug(sec['title'])}"; new_id[sec['anchor']] = sid
    out = [f'<h2 id="{sec["anchor"]}">{n} {sec["title"]}</h2>', '']
    new_title[sec['anchor']] = sec['title']; anchor_num[sec['anchor']] = str(n)
    for src in sec.get('intro_from', []):
        body = intro[src]; used_intros.add(src)
        if src != sec['anchor']:
            body = f'<span id="{src}"></span>\n' + body; retarget[src] = sec['anchor']; anchor_num[src] = str(n)
        if body.strip(): out += [body, '']
    for i, sub in enumerate(sec['subsections'], start=1):
        a = sub['from'][0]; anchor_num[a] = f'{n}.{i}'; new_title[a] = sub['title']
        out += [f'<h3 id="{a}">{n}.{i} {sub["title"]}</h3>', '']
        for src in sub.get('intro_from', []):  # an old section's intro opening this subsection
            used_intros.add(src); retarget[src] = sec['anchor']; anchor_num[src] = str(n)  # its tokens name the new section
            out += [f'<span id="{src}"></span>', intro[src], '']
        for j, src in enumerate(sub['from']):
            body = blocks[src]; used_blocks.add(src)
            if j: body = f'<span id="{src}"></span>\n' + body; retarget[src] = a; anchor_num[src] = f'{n}.{i}'
            out += [body, '']
    new_text[f'site/sec-{n:02d}.html'] = '\n'.join(out).rstrip('\n') + '\n'
unused = (set(blocks) - used_blocks) | {s for s in intro if s not in used_intros and intro[s].strip()}
if unused: sys.exit(f'old content not placed by the plan: {sorted(unused)}')

sec_map = {old_h2_num[a]: int(anchor_num[a].split('.')[0]) for a in old_h2_num}
sub_map = {old_num[a]: anchor_num[a] for a in old_num}
num_to_new_id = {s['number']: new_id[s['anchor']] for s in plan['sections']}
id_map = {}  # old manifest id -> the new id of the section that now holds the old section's intro
for rec in old_sections:
    old_anchor = next(a for a in old_h2_num if old_h2_num[a] == rec['display_number'])
    id_map[rec['id']] = num_to_new_id[int(anchor_num[old_anchor].split('.')[0])]
ID_RE = re.compile('|'.join(re.escape(k) for k in sorted(id_map, key=len, reverse=True)))

def map_token(tok):
    if '.' in tok: return sub_map.get(tok, tok)
    return str(sec_map.get(int(tok), tok))
NUM = r'\d+(?:\.\d+)?'; TAGWS = r'(?:<[^>]+>|\s)*'
PLURAL = re.compile(rf'\bSections(?:<[^>]+>|\s)+{NUM}(?:{TAGWS}(?:,|\band\b|\bto\b|\bthrough\b){TAGWS}(?:Sections?{TAGWS})?{NUM})+', re.S)
SINGULAR = re.compile(rf'\bSection\s+{NUM}(?:{TAGWS}(?:,|\band\b|\bto\b|\bthrough\b){TAGWS}Section\s+{NUM})+', re.S)
collapsed = []
def sub_tokens(text, where):
    protected = {}
    def singular(m):
        # A chain of repeated singular "Section N and Section M" tokens must be collapse-checked
        # and frozen BEFORE the bare-singular substitutions below run, or each number in a
        # colliding pair would be independently (and silently) renumbered to the same target.
        nums = re.findall(NUM, m.group(0)); mapped = [map_token(x) for x in nums]
        if len(set(n.split('.')[0] for n in mapped)) < len(set(n.split('.')[0] for n in nums)):
            collapsed.append(f'{where}: {re.sub("<[^>]+>", "", m.group(0))[:80]}')
            key = f'\x00SINGULAR{len(protected)}\x00'; protected[key] = m.group(0); return key
        return m.group(0)  # no collapse: leave untouched, the bare-singular substitutions below handle it
    text = SINGULAR.sub(singular, text)
    text = re.sub(r'\bSection (\d+\.\d+)(?!\.?\d)', lambda m: 'Section ' + map_token(m.group(1)), text)
    text = re.sub(r'\bSection (\d+)(?!\.?\d)', lambda m: 'Section ' + map_token(m.group(1)), text)
    def plural(m):
        nums = re.findall(NUM, m.group(0)); mapped = [map_token(x) for x in nums]
        if len(set(n.split('.')[0] for n in mapped)) < len(set(n.split('.')[0] for n in nums)):
            collapsed.append(f'{where}: {re.sub("<[^>]+>", "", m.group(0))[:80]}'); return m.group(0)
        return re.sub(NUM, lambda x: map_token(x.group(0)), m.group(0))
    text = PLURAL.sub(plural, text)
    text = re.sub(r'href="#([^"]+)"', lambda m: f'href="#{retarget.get(m.group(1), m.group(1))}"', text)
    def words(m):
        title = new_title.get(m.group(1))
        return m.group(0) if title is None else f'<a href="#{m.group(1)}">Section {m.group(2)}, {title},</a>'
    text = re.sub(r'<a href="#([^"]+)">\s*Section (\d+(?:\.\d+)?),\s*[^<]*?,?</a>', words, text)
    text = ID_RE.sub(lambda m: id_map[m.group(0)], text)
    for key, val in protected.items(): text = text.replace(key, val)
    return text

changes = {}
for rel, t in new_text.items(): changes[ROOT / rel] = sub_tokens(t, rel)
for p in sorted((ROOT / 'site/figures').glob('*.html')) + [ROOT / 'site/shell-figure.html', ROOT / 'assets/figure.js', ROOT / 'data/evidence-stack.json']:
    t = p.read_text(); u = sub_tokens(t, p.name)
    if u != t: changes[p] = u
fm_path = ROOT / 'data/figure-manifest.json'; fm_text = fm_path.read_text(); fm_new = sub_tokens(fm_text, 'figure-manifest.json')
fm_changed = fm_new != fm_text
removals = [ROOT / rec['fragment'] for rec in old_sections if rec['fragment'] not in new_text]

frags = [f for f in sm['fragments'] if f.get('kind') != 'section']
head, tail = frags[0], frags[-1]; interactive = next(f for f in frags if f.get('kind') == 'interactive')
new_frags = [head]
for sec in plan['sections']:
    new_frags.append({'id': new_id[sec['anchor']], 'kind': 'section', 'display_number': sec['number'], 'title': sec['title'], 'fragment': f"site/sec-{sec['number']:02d}.html"})
    if sec['anchor'] == plan['map_after']: new_frags.append(interactive)
new_frags.append(tail); sm['fragments'] = new_frags

print('sections (old -> new):', {k: v for k, v in sec_map.items() if k != v})
print('subsections (old -> new):', {k: v for k, v in sub_map.items() if k != v})
print('retargeted anchors:', len(retarget))
for c in collapsed: print('COLLAPSED plural token, fix by hand:', c)
if DRY:
    for p in changes: print('would write', p.relative_to(ROOT))
    for p in removals: print('would git rm', p.relative_to(ROOT))
    msg = 'would rewrite data/site-manifest.json'
    if fm_changed: msg += ' and data/figure-manifest.json'
    print(msg); sys.exit(0)
for p in removals: subprocess.run(['git', 'rm', '-q', str(p)], cwd=ROOT, check=True)
for p, u in changes.items(): p.write_text(u)
if fm_changed: fm_path.write_text(fm_new)
sm_path.write_text(json.dumps(sm, indent=2, ensure_ascii=False) + '\n')
print('applied')
