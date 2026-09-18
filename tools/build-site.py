#!/usr/bin/env python3
"""Assemble the survey site from section fragments.

Citations use distill's own <d-cite key="...">, resolved against
assets/bibliography/references.bib, exactly as the quantization survey does. That is
what produces the numbered marker, the hover card, and the entry in <d-citation-list>.
The section fragments were written with plain <a class="cite" data-ref="..."> markers
and their own per-section reference lists; both are converted here, so no fragment
needs to know the global ordering or the canonical key for a work.
"""
import re, sys, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / 'site'

# Reading order comes from data/site-manifest.json's fragments list, in file order.
# The interactive route map (shell-figure.html, the deployment-stack-map figure) sits
# directly after Section 13, the prose synthesis of the routes it draws, as the
# manifest's "interactive-deployment-map must follow Section 13 directly" check requires.
SITE_MANIFEST = json.loads((ROOT / 'data/site-manifest.json').read_text())
ORDER = [Path(f['fragment']).name for f in SITE_MANIFEST['fragments']]

REF_UL = re.compile(r'<ul class="refs"[^>]*>.*?</ul>', re.S)
CITE = re.compile(r'<a class="cite" data-ref="([^"]+)"[^>]*>\[[^\]]*\]</a>')
# Each section emits its own "References" heading above its list. The lists are
# replaced by <d-citation-list>, so the headings would otherwise be left orphaned, and
# the ones carrying id="references" would collide with the appendix's own ids.
REF_HEAD = re.compile(r'<h[23][^>]*>\s*[Rr]eferences?\s*(?:list)?\s*</h[23]>\s*', re.I)
# Adjacent markers such as [a], [b] are one citation in distill's markup.
CITE_RUN = re.compile(r'(?:<d-cite key="[^"]+"></d-cite>)(?:\s*,?\s*(?:and\s+)?'
                      r'<d-cite key="[^"]+"></d-cite>)+')
HEADING = re.compile(r'(<h([2-4])\b[^>]*>)\s*(\d+(?:\.\d+)*)\.?\s+(?=\S)')

FIG_WIDE = re.compile(r'(<figure\b[^>]*\bclass="[^"]*?)\bl-(?:page-outset|page|screen-inset|screen|'
                      r'middle-outset|middle|body-outset|gutter)\b((?:[^"]*")[^>]*>)', re.S)
WRAP_OPEN = re.compile(r'<div class="([^"]*\bptable-wrap\b[^"]*)"')


def normalize_tables(text):
    """Apply the house table classes and choose a width strategy per table.

    Only the wrapper's opening tag is rewritten. An earlier version matched the whole
    wrapper with a non-greedy `(.*?)</div>`, which terminated at the nested legend div
    instead of the wrapper's own close, leaving the markup unbalanced and letting the
    prose after a table inherit the table's page width.
    """
    text = re.sub(r'<table(?![^>]*\bclass=)', '<table class="ptable"', text)
    text = re.sub(r'<table class="(?!.*\bptable\b)([^"]*)"', r'<table class="ptable \1"', text)

    def fix(m):
        cls = m.group(1)
        # Column count comes from the first header row after this wrapper opens.
        tail = text[m.end():m.end() + 20000]
        head = re.search(r'<thead.*?</thead>', tail, re.S)
        if head:
            ncol = len(re.findall(r'<th\b', head.group(0).split('</tr>')[0]))
        else:
            first_row = tail.split('</tr>')[0]
            ncol = len(re.findall(r'<t[hd]\b', first_row))
        cls = ' '.join(c for c in cls.split()
                       if c not in ('l-page', 'l-screen-inset', 't1-wide', 't-scroll'))
        if ncol >= 11:
            cls += ' l-screen-inset t-scroll'      # too wide to fit, scrolls in place
        elif ncol >= 6:
            cls += ' l-page t1-wide'               # widen to the page, wrap the headers
        # 5 columns or fewer stays in the text column at its natural width
        return f'<div class="{cls.strip()}"'

    return WRAP_OPEN.sub(fix, text)

TOC_H = re.compile(r'<h([23])\b[^>]*\bid="([^"]+)"[^>]*>(.*?)</h\1>', re.S)
TOC_FIG = re.compile(r'<figcaption[^>]*\bid="(figure-\d+)"[^>]*>\s*<b>Figure (\d+):</b>')
TAGS = re.compile(r'<[^>]+>')
NAV = re.compile(r'(<h3>Contents</h3>\s*)(.*?)(\s*</nav>)', re.S)


def toc_entries(parts):
    manifest = json.loads((ROOT / 'data/figure-manifest.json').read_text())
    concept = {f['fragment'].split('/')[-1]: f['concept'] for f in manifest['figures']}
    out = ['<div><a href="#abstract">Abstract</a></div>']
    for f, text in parts:
        if f.startswith('sec-'):
            for level, hid, title in TOC_H.findall(text):
                title = ' '.join(TAGS.sub('', title).split())
                cls = ' class="toc-sub"' if level == '3' else ''
                out.append(f'<div{cls}><a href="#{hid}">{title}</a></div>')
        elif f.startswith('shell-figure'):
            m = TOC_FIG.search(text)
            if m:
                out.append(f'<div><a href="#{m.group(1)}">Figure {m.group(2)}&ensp;'
                           f'{concept.get(f, "Interactive figure")}</a></div>')
    return out


def insert_toc(doc, parts):
    entries = '\n            '.join(toc_entries(parts))
    doc, n = NAV.subn(lambda m: f'{m.group(1)}{entries}{m.group(3)}', doc, count=1)
    if n != 1:
        sys.exit('table of contents frame (<h3>Contents</h3> ... </nav>) not found')
    return doc


def main():
    missing = [f for f in ORDER if not (SITE / f).exists()]
    if missing:
        sys.exit('missing fragments: ' + ', '.join(missing))
    bib = ROOT / 'assets/bibliography/references.bib'
    if not bib.exists():
        sys.exit('run tools/build-bib.py first')
    keys = set(re.findall(r'^@\w+\{([^,]+),', bib.read_text(), re.M))
    alias = json.loads((ROOT / 'data/refmap.json').read_text())

    parts = [(f, (SITE / f).read_text()) for f in ORDER]

    # 1. The per-section reference lists and their headings are replaced by the
    #    appendix's <d-citation-list>, which distill renders from the .bib file.
    parts = [(f, REF_HEAD.sub('', REF_UL.sub('', text))) for f, text in parts]

    # 2. Normalize table markup. Section fragments were emitted without the house
    #    classes, so none of the table styling applied. Give every table `ptable`, and
    #    pick a width strategy from its column count: a narrow table sits in the text
    #    column, a medium one widens to the page with wrapping headers, and only a
    #    genuinely wide one scrolls, inside its own container so the page never does.
    parts = [(f, normalize_tables(text)) for f, text in parts]
    #    Figures never leave the text column: any distill width class wider than l-body
    #    on a figure is replaced, so a figure fragment installed with l-page or l-screen
    #    still renders in line with the prose. Tables keep their own width strategy.
    #    The interactive route map (shell-figure.html) is exempt and keeps its page width.
    parts = [(f, text if f == 'shell-figure.html' else FIG_WIDE.sub(r'\1l-body\2', text))
             for f, text in parts]

    # 3. Section numbers are separated from their titles by an en space, matching the
    #    template, and the stray full stop some fragments carry is dropped.
    parts = [(f, HEADING.sub(lambda m: f'{m.group(1)}{m.group(3)}&ensp;', text))
             for f, text in parts]

    # 4. Convert the fragments' plain markers to distill citations, resolving duplicate
    #    ids onto the canonical key first.
    unknown = set()

    def sub_cite(m):
        rid = alias.get(m.group(1), m.group(1))
        if rid not in keys:
            unknown.add(rid)
        return f'<d-cite key="{rid}"></d-cite>'

    def join_run(m):
        ks = re.findall(r'key="([^"]+)"', m.group(0))
        seen, out = set(), []
        for k in ks:
            if k not in seen:
                seen.add(k); out.append(k)
        return f'<d-cite key="{",".join(out)}"></d-cite>'

    def realias(m):
        ks, out, seen = m.group(1).split(','), [], set()
        for k in ks:
            k = alias.get(k.strip(), k.strip())
            if k not in keys:
                unknown.add(k)
            if k not in seen:
                seen.add(k); out.append(k)
        return f'<d-cite key="{",".join(out)}"></d-cite>'

    # Table 1 is generated with d-cite already, so the alias map is applied to existing
    # tags as well as to the markers converted above.
    parts = [(f, re.sub(r'<d-cite key="([^"]+)"></d-cite>', realias,
                        CITE_RUN.sub(join_run, CITE.sub(sub_cite, text))))
             for f, text in parts]

    # 5. The table of contents is generated from the live headings, in build order, so
    #    it never lags the fragments. The shell keeps only the nav's frame and the
    #    Abstract entry; every h2 and h3 of a section fragment becomes an entry, and the
    #    interactive figure fragment contributes its own line at its position.
    parts = [(f, text) for f, text in parts]
    doc = '\n'.join(text for _, text in parts)

    # The route map reads its data from an inline JSON block, so the figure works from a
    # local file and on GitHub Pages alike and never fetches. The block is the generated
    # view of data/figure-guide.json (tools/build-figure-guide.py).
    view_path = ROOT / 'data/generated/figure-guide-view.json'
    if not view_path.exists():
        sys.exit('data/generated/figure-guide-view.json is missing; run tools/build-figure-guide.py first')
    view_json = view_path.read_text().replace('</', '<\\/')
    marker = '<figure class="pfig stack-fig'
    if doc.count(marker) != 1:
        sys.exit('the interactive route map figure was not found exactly once')
    doc = doc.replace(marker, f'<script type="application/json" id="nstk-data">{view_json}</script>\n{marker}', 1)

    doc = insert_toc(doc, parts)
    (ROOT / 'index.html').write_text(doc)

    cited = {k for c in re.findall(r'<d-cite key="([^"]+)"></d-cite>', doc) for k in c.split(',')}
    print(f'sections    : {len(ORDER) - 3} content fragments')
    print(f'bib entries : {len(keys)}')
    print(f'cited       : {len(cited)} distinct keys in {doc.count("<d-cite")} d-cite tags')
    print(f'aliased     : {len(alias)} duplicate ids resolved')
    if unknown:
        print(f'UNKNOWN KEYS ({len(unknown)}): ' + ', '.join(sorted(unknown)[:20]))
    uncited = keys - cited
    if uncited:
        print(f'defined but not cited: {len(uncited)}')
    print(f'wrote       : {ROOT / "index.html"} '
          f'({(ROOT / "index.html").stat().st_size // 1024} KB)')


if __name__ == '__main__':
    main()
