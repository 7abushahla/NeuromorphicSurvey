#!/usr/bin/env python3
"""Generate Table 1, the scope comparison of prior surveys.

Reads the 37-survey scoring from research/raw/a15-prior-surveys.md and writes the
coverage heat-map into site/sec-01.html. Re-runnable, so a score can be corrected in
one place and the table regenerated.

The twelve research axes are merged into eight table columns. Merging takes the
stronger of the pair, because a survey that covers neuron models fully and encodings
partially has still covered that territory.
"""
import re, html
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# a15 row order, 1 to 37, mapped to the reference ids already in sec-01.html.
IDS = """pedersen-2024-nir kudithipudi-2025 deng-2025-edgesnn yik-2025-neurobench davies-2021-loihi
huynh-2022 roy-2019 schuman-2017 schuman-2022 eshraghian-2023 rathi-2023 yamazaki-2022 ivanov-2022
basu-2022 nunes-2022 khan-2025 zheng-2022 anon-edge-survey xie-2024 ferreira-2025 manna-2023
gallego-2022 gebregiorgis-2025 bouvier-2019 shrestha-2022 chips-2026 epjb-2024
spiking-transformers-2024 mdpi-tutorial-2025 alabdulwahid-2024 tayarani-2021 cimarelli-2025
npl-2026 luu-2026 caviglia-2026 edge-bench-2026 farsa-2026""".split()

COLS = [
    ('Codes &amp; neurons',        'Codes',      ['A', 'B']),
    ('Training &amp; conversion',  'Conversion', ['C', 'D']),
    ('Software frameworks',        'Software',   ['E']),
    ('Compilers &amp; interchange','Compilers',  ['F', 'G']),
    ('Hardware platforms',         'Hardware',   ['H']),
    ('Boundary semantics',         'Boundaries', ['I']),
    ('Evidence types',             'Evidence',   ['J']),
    ('Traced chip routes',         'Routes',     ['L']),
]
AXES = 'ABCDEFGHIJKL'

# Corrections to a15's scoring, applied openly rather than silently. Each carries the
# reason, which is surfaced as a tooltip on the corrected cell.
OVERRIDES = {
    ('davies-2021-loihi', 'H'): ('P', 'Covers one platform family in depth. On an axis '
                                      'measuring breadth of platform coverage that is partial, '
                                      'not full. a15 annotated this survey as single-chip on the '
                                      'evidence and route axes but not here.'),
}

RANK = {'F': 3, 'P': 2, 'M': 1}

# A short categorical tag per survey, the same treatment the hardware landscape gets in
# the quantization survey. Hand-set where the survey has a clear identity, otherwise
# derived from its strongest axes.
TAGS = {
    'pedersen-2024-nir':   ('Interchange',  'tag-software'),
    'kudithipudi-2025':    ('Ecosystem',    'tag-overview'),
    'deng-2025-edgesnn':   ('Edge systems', 'tag-overview'),
    'yik-2025-neurobench': ('Benchmark',    'tag-evaluation'),
    'davies-2021-loihi':   ('Hardware',     'tag-hardware'),
    'huynh-2022':          ('Toolchains',   'tag-software'),
    'manna-2023':          ('Frameworks',   'tag-software'),
    'gallego-2022':        ('Sensing',      'tag-hardware'),
    'edge-bench-2026':     ('Benchmark',    'tag-evaluation'),
    'basu-2022':           ('Circuits',     'tag-hardware'),
}


def tag_for(rid, ax):
    """Fall back to the survey's strongest axis when no tag is hand-set."""
    if rid in TAGS:
        return TAGS[rid]
    g = lambda k: RANK.get(re.match(r'\s*([FPM])', ax[k].replace('*', '').replace('†', '')).group(1), 0) \
        if re.match(r'\s*([FPM])', ax[k].replace('*', '').replace('†', '')) else 0
    if g('G') >= 2: return ('Interchange', 'tag-software')
    if g('J') >= 2: return ('Evaluation',  'tag-evaluation')
    if g('F') >= 2: return ('Toolchains',  'tag-software')
    if g('E') >= 2: return ('Frameworks',  'tag-software')
    if g('D') >= 2: return ('Conversion',  'tag-methods')
    if g('C') >= 2: return ('Training',    'tag-methods')
    if g('H') >= 2: return ('Hardware',    'tag-hardware')
    return ('Overview', 'tag-overview')


# Author lists resolved from the primary source where a15 left the entry unattributed.
NAMES = {
    'anon-edge-survey':          ('Rashed &amp; Dias', '2025'),
    'chips-2026':                ('Chen et al.', None),
    'epjb-2024':                 ('Zolfagharinejad et al.', None),
    'spiking-transformers-2024': ('Hu et al.', None),
    'mdpi-tutorial-2025':        ('Ayasi et al.', None),
    'npl-2026':                  ('He &amp; Gao', None),
    'edge-bench-2026':           ('Du et al.', None),
}


def short_name(raw):
    """Author-only label, matching the Paper column in the quantization survey."""
    n = raw.split('—')[0].split('·')[0].strip().rstrip(',')
    n = re.sub(r'\s*\([^)]*\)\s*$', '', n).strip()
    if n.startswith('"'):                      # untitled or unattributed work
        return n.split('"')[1].strip()
    if 'et al' in n:
        first = re.split(r'[/,&]', n)[0].strip()
        return first.split()[0] + ' et al.'
    parts = re.split(r'[/,&]|\band\b', n)
    if len(parts) > 1:
        return parts[0].strip().split()[0] + ' et al.'
    return n
CLS = {3: ('cov-full', 'Full'), 2: ('cov-part', 'Partial'),
       1: ('cov-ment', 'Mentioned'), 0: ('cov-none', '')}


def score(cell):
    c = cell.replace('*', '').strip()
    dag = '†' in c
    m = re.match(r'\s*([FPM])', c.replace('†', ''))
    return (RANK.get(m.group(1), 0) if m else 0), dag


def end_of_div(s, start):
    """Index just past the </div> that closes the div opening at `start`.

    Counting is necessary because the table wrapper contains a nested legend div.
    Taking the first </div> after the legend closes the legend, not the wrapper, and
    leaves a stray </div> behind on every regeneration.
    """
    depth, i = 0, start
    for m in re.finditer(r'<div\b|</div>', s[start:]):
        depth += 1 if m.group(0) != '</div>' else -1
        if depth == 0:
            return start + m.end()
    raise ValueError('unbalanced div')


def main():
    src = (ROOT / 'research/raw/a15-prior-surveys.md').read_text().splitlines()
    rows = [l for l in src if re.match(r'^\|\s*\d+\s*\|', l)]
    assert len(rows) == len(IDS) == 37, (len(rows), len(IDS))

    applied = []
    out = []
    for line, rid in zip(rows, IDS):
        p = [c.strip() for c in line.strip().strip('|').split('|')]
        name, yr, cells = p[1], p[2], p[3:15]
        by_axis = dict(zip(AXES, cells))

        tds = []
        for _, _, axes in COLS:
            best, dag = 0, False
            for ax in axes:
                key = (rid, ax)
                if key in OVERRIDES:
                    letter, why = OVERRIDES[key]
                    v, d = RANK.get(letter, 0), False
                    applied.append(f'{rid} {ax} -> {letter}')
                else:
                    why = None
                    v, d = score(by_axis[ax])
                if v > best:
                    best, note = v, why
                elif best == 0:
                    note = why
                dag = dag or d
            cls, label = CLS[best]
            title = f' title="{html.escape(note)}"' if best and note else ''
            span = f'<span>{label}{"†" if dag else ""}</span>' if best else ''
            tds.append(f'<td class="{cls}"{title}>{span}</td>')

        nm, yr_fix = NAMES.get(rid, (None, None))
        if yr_fix:
            yr = yr_fix
        disp = nm if nm else html.escape(short_name(name))
        y = re.match(r'(\d{4})', yr)
        label, tcls = tag_for(rid, by_axis)
        out.append((int(y.group(1)) if y else 9999,
                    f'<tr><td>{disp} '
                    f'<d-cite key="{rid}"></d-cite>'
                    f'<br><span class="survey-tag {tcls}">{label}</span></td>'
                    f'<td class="ctr yr">{html.escape(yr)}</td>{"".join(tds)}</tr>'))

    out.sort(key=lambda t: t[0])
    ours = ('<tr class="ours"><td><strong>Ours</strong></td><td class="ctr yr">2026</td>'
            + '<td class="cov-full"><span>Full</span></td>' * len(COLS) + '</tr>')
    heads = '\n'.join(f'<th class="ctr" data-chip="{chip}">{title}</th>' for title, chip, _ in COLS)

    table = f'''<div class="ptable-wrap l-page t1-wide cov-table" id="table-1" data-table-toolbar>
<table class="ptable">
<caption><b>Table 1:</b> Scope comparison of surveys on spiking neural networks, neuromorphic hardware, and ANN-to-SNN deployment. All 37 screened works are listed, ordered by year.</caption>
<thead><tr>
<th>Survey</th>
<th class="ctr yr" data-sort="num">Year</th>
{heads}
</tr></thead>
<tbody>
{chr(10).join(r for _, r in out)}
{ours}
</tbody>
</table>
<div class="t1-legend"><span><i class="sw sw-full"></i>surveyed</span><span><i class="sw sw-part"></i>partially surveyed</span><span><i class="sw sw-ment"></i>mentioned only</span><span><i class="sw sw-none"></i>not covered</span><span class="t1-legend-note">† scored from an abstract or a vault note rather than confirmed full text. Hover a cell carrying a correction for its reason.</span></div>
</div>'''

    p = ROOT / 'site/sec-01.html'
    s = p.read_text()
    a = s.index('<div class="ptable-wrap')
    b = end_of_div(s, a)
    p.write_text(s[:a] + table + s[b:])
    print(f'{len(out)} surveys, {out[0][0]}-{out[-1][0]}, plus Ours')
    print(f'overrides applied: {applied or "none"}')


if __name__ == '__main__':
    main()
