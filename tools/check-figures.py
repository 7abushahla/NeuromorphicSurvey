#!/usr/bin/env python3
"""Check the section 2 figures against the constraints in site/figures/BRIEF.md.

Five figures were drawn in parallel by five authors who could not see each
other's work, and they all land in one HTML document. The failure that matters
is therefore collision rather than individual error: a duplicate marker id
silently retargets another figure's arrowheads, and nothing about the page looks
broken when it happens. Everything here is a whole-document check for that
reason.
"""
import re, sys
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
FIGS = ROOT / 'site/figures'
NUMS = range(2, 7)

# Coordinates live in different attributes per element, so containment is checked
# against the ones that are always plain user-space numbers.
XA = ('x', 'x1', 'x2', 'cx')
YA = ('y', 'y1', 'y2', 'cy')

bad = []


def fail(n, msg):
    bad.append(f'figure-{n}: {msg}')


def main():
    ids, files = {}, {}
    for n in NUMS:
        f = FIGS / f'figure-{n}.html'
        if not f.exists():
            fail(n, 'missing')
            continue
        files[n] = s = f.read_text()

        # Identity and structure.
        if f'id="figure-{n}"' not in s:
            fail(n, 'lost its figure id')
        if s.count('<figure') != 1 or s.count('</figure>') != 1:
            fail(n, 'must hold exactly one <figure> element')
        if not re.search(r'<figcaption>\s*<b>Figure %d:</b>' % n, s):
            fail(n, 'figcaption must open with <b>Figure N:</b>')

        # House style.
        if '<svg' not in s:
            fail(n, 'no inline svg')
        if re.search(r'<svg[^>]*\s(width|height)=', s):
            fail(n, 'svg carries width/height; it must scale by viewBox alone')
        if not re.search(r'<svg[^>]*viewBox=', s):
            fail(n, 'svg has no viewBox')
        # url(#id) is how SVG references its own markers and gradients, so only an
        # external target counts as a violation here.
        if re.search(r'<img\b|<script\b|url\(\s*["\']?(?:https?:|/|\.)', s):
            fail(n, 'references an external asset or script')
        if 'prefers-color-scheme' in s:
            fail(n, 'dark mode rules do not belong here')

        # Publishable caption. The placeholders were drawing instructions naming
        # source files, which is exactly what must not survive into the page.
        cap = re.search(r'<figcaption>(.*?)</figcaption>', s, re.S)
        cap = re.sub(r'<[^>]+>', '', cap.group(1)) if cap else ''
        for leak in ('FIGURE TO DRAW', 'Redraw', '.pdf', 'vault', 'Chapter', 'thesis'):
            if leak.lower() in cap.lower():
                fail(n, f'caption still says {leak!r}')
        if '—' in cap or '&#8212;' in s:
            fail(n, 'em dash in figure text')

        # Id collisions across the five, which is the whole point of this script.
        for i in re.findall(r'\bid="([^"]+)"', s):
            if i == f'figure-{n}':
                continue
            if not i.startswith(f'f{n}'):
                fail(n, f'id {i!r} is not prefixed f{n}')
            ids.setdefault(i, []).append(n)

        # Every url(#x) must resolve inside its own figure.
        own = set(re.findall(r'\bid="([^"]+)"', s))
        for r in set(re.findall(r'url\(#([^)]+)\)', s)):
            if r not in own:
                fail(n, f'url(#{r}) has no definition in this figure')

        # Geometry containment.
        try:
            svg = ET.fromstring(re.search(r'<svg.*</svg>', s, re.S).group(0))
        except Exception as e:
            fail(n, f'svg is not well formed: {e}')
            continue
        _, _, vw, vh = [float(v) for v in svg.get('viewBox').split()]
        for el in svg.iter():
            for a in XA:
                v = el.get(a)
                if v and re.fullmatch(r'-?[\d.]+', v) and not -1 <= float(v) <= vw + 1:
                    fail(n, f'{el.tag.split("}")[-1]} {a}={v} outside viewBox width {vw:g}')
            for a in YA:
                v = el.get(a)
                if v and re.fullmatch(r'-?[\d.]+', v) and not -1 <= float(v) <= vh + 1:
                    fail(n, f'{el.tag.split("}")[-1]} {a}={v} outside viewBox height {vh:g}')

    for i, ns in ids.items():
        if len(ns) > 1:
            bad.append(f'DUPLICATE id {i!r} in figures {ns}')

    # Scoped css only, so one figure cannot restyle another.
    for n in NUMS:
        c = FIGS / f'figure-{n}.css'
        if not c.exists():
            continue
        for rule in re.findall(r'([^{}]+)\{', c.read_text()):
            for sel in rule.split(','):
                sel = sel.strip()
                if sel and not sel.startswith('@') and f'#figure-{n}' not in sel:
                    fail(n, f'css selector {sel!r} is not scoped to #figure-{n}')

    for n in sorted(files):
        m = re.search(r'viewBox="([^"]+)"', files[n])
        cls = re.search(r'<figure class="([^"]+)"', files[n])
        print(f'figure-{n}: viewBox {m.group(1) if m else "?"}  [{cls.group(1) if cls else "?"}]')
    print()
    if bad:
        print(f'{len(bad)} problem(s):')
        for b in bad:
            print('  -', b)
        sys.exit(1)
    print('all checks passed')


if __name__ == '__main__':
    main()
