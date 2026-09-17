#!/usr/bin/env python3
"""Every graded evidence marker carries the target chip of the claim beside it.

Rules: an E1, E2, E3 or E4 span must be followed by a chip span; an E5 span may be bare
only when the nearest cited paper (the closest <d-cite key> in the same table row, list
item or paragraph) has target_kind "none"; a chip word must be in data/target-kinds.json;
where the enclosing row, item or paragraph cites exactly one evidence paper, the chip must
equal that paper's target_kind. Exit 1 on any failure, listing file, line and reason.
A marker that names a class rather than grades a claim carries the extra class ev-name and
is skipped. Citation keys are canonicalized through data/source-registry.json's aliases and
data/refmap.json before matching a paper's own source keys. A first pass scans every
(tr|li|p) block; a second pass scans <div class="caveat"> blocks (which hold a marker with
no enclosing tr/li/p, e.g. the caveat in site/sec-09.html), skipping any marker whose
absolute position the first pass already checked, so no marker is double-scanned.
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KINDS = {k['word']: k for k in json.loads((ROOT / 'data/target-kinds.json').read_text())['kinds']}
papers = json.loads((ROOT / 'data/evidence-papers.json').read_text())['papers']

canon = {}
for source in json.loads((ROOT / 'data/source-registry.json').read_text())['sources']:
    for alias in source.get('aliases', []) or []:
        canon[alias] = source['id']
canon.update(json.loads((ROOT / 'data/refmap.json').read_text()))

def canonical(key):
    return canon.get(key, key)

by_source = {}
for p in papers:
    for key in p.get('sources', []):
        by_source.setdefault(canonical(key), set()).add(p['target_kind'])
MARK = re.compile(r'<span class="ev ev-e([1-5])( ev-name)?">E\1</span>(\s*<span class="tk tk-([a-z-]+)"( data-second-target="1")?>([^<]+)</span>)?')
BLOCK = re.compile(r'<(tr|li|p)\b.*?</\1>', re.S)
CAVEAT = re.compile(r'<div class="caveat">.*?</div>', re.S)
errors = []
for path in sorted((ROOT / 'site').glob('sec-*.html')):
    text = path.read_text()
    checked_positions = set()

    def scan_block(body, base_offset, line):
        keys = re.findall(r'<d-cite key="([^"]+)"', body)
        cited_kinds = set()
        for key_list in keys:
            for key in key_list.split(','):
                cited_kinds |= by_source.get(canonical(key.strip()), set())
        for m in MARK.finditer(body):
            abs_pos = base_offset + m.start()
            if abs_pos in checked_positions:
                continue
            checked_positions.add(abs_pos)
            level, is_name, chip_css, second_target, chip_word = m.group(1), m.group(2), m.group(4), m.group(5), m.group(6)
            where = f'{path.relative_to(ROOT)}:{line}'
            if is_name:
                continue
            if chip_word is None:
                if level != '5':
                    errors.append(f'{where}: E{level} marker without a target chip')
                elif cited_kinds and 'none' not in cited_kinds:
                    errors.append(f'{where}: bare E5 marker but the cited paper has target {sorted(cited_kinds)}')
                continue
            if chip_word not in KINDS or KINDS[chip_word]['css'] != 'tk-' + chip_css:
                errors.append(f'{where}: chip "{chip_word}" (tk-{chip_css}) is not in data/target-kinds.json')
                continue
            if second_target:
                continue
            if len(cited_kinds) == 1 and chip_word not in cited_kinds:
                errors.append(f'{where}: chip "{chip_word}" disagrees with the cited paper\'s target {sorted(cited_kinds)}')

    for block in BLOCK.finditer(text):
        line = text.count('\n', 0, block.start()) + 1
        scan_block(block.group(0), block.start(), line)
    for block in CAVEAT.finditer(text):
        line = text.count('\n', 0, block.start()) + 1
        scan_block(block.group(0), block.start(), line)
if errors:
    print('\n'.join(errors)); sys.exit(1)
print('check-evidence-markers: every graded marker carries a valid target chip')
