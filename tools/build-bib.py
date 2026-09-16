#!/usr/bin/env python3
"""Turn the section fragments' inline reference lists into a BibTeX file.

The quantization survey cites with distill's own <d-cite key="...">, backed by
assets/bibliography/references.bib. That is what gives a citation its hover card and
its entry in <d-citation-list>. This script produces the same input from the
free-text <li data-ref="..."> entries the section fragments carry, so the two sites
use one identical citation mechanism.

Also emits data/refmap.json: duplicate id -> canonical id, since the fragments were
written independently and catalogue the same work under several keys.
"""
import re, json, html
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REF_LI = re.compile(r'<li[^>]*\bdata-ref="([^"]+)"[^>]*>(.*?)</li>', re.S)
TITLE_Q = re.compile(r'[“"‘]([^”"’]{12,})[”"’]')
INITIALS = re.compile(r'^(?:[A-Z]\.\s*){1,4}$')
NAME_FIRST = re.compile(r'^[A-Z]\.\s*[A-Z]?\.?\s*[A-ZÀ-ž]')


def detag(s):
    s = re.sub(r'<span class="src-type">.*?</span>', '', s, flags=re.S)
    s = re.sub(r'<[^>]+>', '', s)
    s = html.unescape(s).replace('\u00a0', ' ').strip()
    # Some fragments repeat the key as a leading marker inside the entry itself.
    return re.sub(r'^\[[^\]]{2,60}\]\s*', '', s).strip()


def srctype(body):
    m = re.search(r'<span class="src-type">(.*?)</span>', body, re.S)
    return re.sub(r'\s+', ' ', detag(m.group(1))).strip(' .') if m else ''


def emph(body):
    m = re.search(r'<em>(.*?)</em>', body, re.S)
    return re.sub(r'\s+', ' ', detag(m.group(1))).strip(' .,') if m else ''


def org(tok):
    """Brace-wrap a name that has no given/family split, e.g. a company or a project.

    The template renders `{{Name}}` literally instead of turning it into `Name, N.`,
    so this is how an organizational author is spelled.
    """
    return tok if re.search(r'[A-Z]\.', tok) else '{{' + tok + '}}'


def split_authors(raw):
    """Normalize an author run into BibTeX's `A and B and C` form.

    Two conventions appear in the fragments: `Last, F. M., Last, F. M.` and
    `F. M. Last, F. M. Last`. Both are comma-separated, so the format is detected
    from the first token rather than assumed.
    """
    raw = raw.strip().strip(',').strip()
    if not raw:
        return ''
    raw = re.sub(r'\bet\s+al\.?', 'ETAL', raw)
    toks = [t.strip() for t in re.split(r',\s*|\s+and\s+|\s*&\s*', raw) if t.strip()]
    if not toks:
        return ''
    out = []
    # A token that is nothing but initials means the list pairs surname with initials.
    if not any(INITIALS.match(t) for t in toks):
        # "F. M. Last" per token, or bare surnames.
        for t in toks:
            t = t.strip()
            if t == 'ETAL':
                out.append('{{et al.}}')
            elif t.endswith('ETAL'):
                head = t[:-4].strip()
                if head:
                    out.append(org(head))
                out.append('{{et al.}}')
            else:
                out.append(org(t))
    else:
        i = 0
        while i < len(toks):
            t = toks[i]
            if t == 'ETAL':
                out.append('{{et al.}}'); i += 1; continue
            if t.endswith('ETAL'):
                head = t[:-4].strip(' .,')
                if head:
                    out.append(head)
                out.append('{{et al.}}'); i += 1; continue
            if i + 1 < len(toks) and INITIALS.match(toks[i + 1]):
                out.append(f'{t}, {toks[i + 1]}'); i += 2
            else:
                out.append(org(t)); i += 1
    return ' and '.join(out)


def parse(rid, body):
    plain = detag(body)
    m = TITLE_Q.search(plain)
    if m:
        title = re.sub(r'\s+', ' ', m.group(1)).strip().rstrip('.,')
        author_raw = plain[:m.start()]
        rest = plain[m.end():]
    else:
        author_raw, body_txt = '', plain
        am = re.match(r'^((?:[A-Z][\w\'\u2019\-\u00c0-\u017e]+,\s*(?:[A-Z]\.\s*){1,4},?\s*)+)', plain)
        if am:
            author_raw, body_txt = am.group(1), plain[am.end():]
        else:
            om = re.match(r'^([A-Z][\w&/.\- ]{2,34}?)\.\s+(?=[A-Z])', plain)
            if om and not re.match(r'^[A-Z]\.', om.group(1)):
                author_raw, body_txt = om.group(1), plain[om.end():]
        tm = re.search(r'\.\s+(?=[A-Z0-9])|\s+https?://|\s+arXiv:', body_txt)
        title = (body_txt[:tm.start()] if tm else body_txt)[:220]
        title = re.sub(r'\s+', ' ', title).strip(' .,;:')
        rest = body_txt[tm.end():] if tm else ''

    doi = ''
    d = re.search(r'(?:doi\.org/|DOI:\s*|doi:\s*)(10\.[^\s,;)\]]+)', plain, re.I)
    if d:
        doi = d.group(1).rstrip('.')

    url = ''
    u = re.search(r'https?://[^\s,;)\]<]+', plain)
    if u:
        url = u.group(0).rstrip('.')
    ax = re.search(r'arXiv:\s*([0-9]{4}\.[0-9]{4,5})', plain)
    if not url and ax:
        url = f'https://arxiv.org/abs/{ax.group(1)}'

    yrs = re.findall(r'\b(1[89]\d\d|20[0-3]\d)\b', rest) or re.findall(r'\b(1[89]\d\d|20[0-3]\d)\b', plain)
    year = yrs[-1] if yrs else ''
    ym = re.search(r'\((1[89]\d\d|20[0-3]\d)\)', plain)
    if ym:
        year = ym.group(1)

    venue = emph(body)
    if not venue:
        v = rest.strip(' .,;')
        v = re.split(r'https?://|arXiv:|\bDOI\b|\bdoi\b', v)[0]
        v = re.sub(r'\(\s*(1[89]|20)\d\d\s*\)', '', v)
        v = re.sub(r'\b(1[89]|20)\d\d\b', '', v)
        v = re.sub(r'\s+', ' ', v).strip(' .,;:-')
        venue = v[:180]

    if venue and (venue.lower().startswith(title.lower()[:40])
                  or title.lower().startswith(venue.lower()[:40])):
        venue = ''

    conf = bool(re.search(r'\b(NeurIPS|ICLR|ICML|AAAI|CVPR|ICCV|ECCV|IJCAI|ISCAS|DATE|DAC|'
                          r'Proceedings|Conference|Workshop|Symposium|NICE|IJCNN|ISSCC)\b',
                          venue + ' ' + srctype(body), re.I))
    return dict(key=rid, title=title, author=split_authors(author_raw), year=year,
                venue=venue, doi=doi, url=url, note=srctype(body), conf=conf)


def esc(s):
    # Braces delimit a BibTeX value, a backslash starts a control sequence, and a
    # percent sign starts a comment. None survive unescaped inside a field.
    return (s.replace('{', '(').replace('}', ')')
             .replace('\\', '/').replace('%', '\\%'))


def main():
    seen = {}
    for f in sorted((ROOT / 'site').glob('*.html')):
        for rid, body in REF_LI.findall(f.read_text()):
            body = body.strip()
            if len(body) > len(seen.get(rid, '')):
                seen[rid] = body

    ents = {rid: parse(rid, b) for rid, b in seen.items()}

    # Merge ids that describe the same work, keeping the fullest entry.
    groups = {}
    for rid, e in ents.items():
        t = re.sub(r'[^a-z0-9 ]+', ' ', e['title'].lower())
        t = re.sub(r'\s+', ' ', t).strip()
        if t:
            groups.setdefault(t, []).append(rid)
    alias = {}
    for ids in groups.values():
        if len(ids) < 2:
            continue
        canon = sorted(ids, key=lambda r: (-len(seen[r]), r))[0]
        for rid in ids:
            if rid != canon:
                alias[rid] = canon
    for dup in alias:
        ents.pop(dup, None)

    lines = ['% Generated by tools/build-bib.py from the section fragments.',
             '% Do not edit by hand; edit the <li data-ref="..."> entry instead.', '']
    for rid in sorted(ents):
        e = ents[rid]
        typ = 'inproceedings' if e['conf'] else 'article'
        vf = 'booktitle' if e['conf'] else 'journal'
        lines.append(f'@{typ}{{{rid},')
        lines.append(f'  title = {{{esc(e["title"])}}},')
        if e['author']:
            lines.append(f'  author = {{{esc(e["author"]).replace("((", "{{").replace("))", "}}")}}},')
        if e['venue']:
            lines.append(f'  {vf} = {{{esc(e["venue"])}}},')
        lines.append(f'  year = {{{e["year"] or "n.d."}}},')
        if e['doi']:
            lines.append(f'  doi = {{{esc(e["doi"])}}},')
        if e['url']:
            lines.append(f'  url = {{{esc(e["url"])}}},')
        if e['note']:
            lines.append(f'  note = {{{esc(e["note"])}}},')
        lines.append('}')
        lines.append('')

    out = ROOT / 'assets/bibliography/references.bib'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text('\n'.join(lines))
    (ROOT / 'data/refmap.json').write_text(json.dumps(alias, indent=1, sort_keys=True))

    noauth = [r for r, e in ents.items() if not e['author']]
    noyear = [r for r, e in ents.items() if not e['year']]
    print(f'entries    : {len(ents)}  ({len(alias)} duplicate ids merged)')
    print(f'no author  : {len(noauth)}' + (f'  e.g. {noauth[:5]}' if noauth else ''))
    print(f'no year    : {len(noyear)}' + (f'  e.g. {noyear[:5]}' if noyear else ''))
    print(f'wrote      : {out}')


if __name__ == '__main__':
    main()
