#!/usr/bin/env python3
"""Every Section, Table and Figure token in the built page must resolve.

Anchored "Section N[.M]" tokens must match the heading number of the anchor they link to.
Bare "Section N[.M]" tokens must exist as a heading. "Table N" and "Figure N" tokens must
have a matching <b>Table N:</b> label or figure-N id. Exit 1 on any failure.
"""
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
page = (ROOT / 'index.html').read_text()
headings, titles = {}, {}
# The built page separates a heading's number from its title with the entity &ensp;
# (see build-site.py's HEADING substitution), not a literal space, so the separator
# here must accept either.
for m in re.finditer(r'<h([2-4])\b[^>]*\bid="([^"]+)"[^>]*>\s*(\d+(?:\.\d+)*)(?:\s|&ensp;)+(.*?)</h\1>', page, re.S):
    headings[m.group(2)] = m.group(3)
    titles[m.group(2)] = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', m.group(4))).strip()
numbers = set(headings.values())
tables = set(re.findall(r'<b>\s*Table\s+(\d+)\s*:\s*</b>', page))
figures = set(re.findall(r'id="figure-(\d+)"', page))
errors = []
for m in re.finditer(r'<a href="#([^"]+)">\s*Section (\d+(?:\.\d+)*)', page):
    anchor, num = m.group(1), m.group(2)
    if anchor not in headings:
        errors.append(f'anchor #{anchor} has no numbered heading (token "Section {num}")')
    elif headings[anchor] != num and headings[anchor].split('.')[0] != num:
        # Exception: a bare "Section N" is allowed to link to a subsection anchor
        # N.M, deep-linking to the relevant part of a section while naming the
        # section as a whole. Only the section-level prefix must agree; a
        # cross-subsection or cross-section mismatch (e.g. token says Section 3
        # but the anchor's heading is 4.2) still fails.
        errors.append(f'anchor #{anchor} is heading {headings[anchor]} but the token says Section {num}')
# An anchored token that carries words, "Section N, Words,</a>", must carry the heading's own title.
# Prose wraps across a line break inside the token text (word-wrapped source), so the
# comparison collapses whitespace the same way the title text above already does.
for m in re.finditer(r'<a href="#([^"]+)">\s*Section (\d+(?:\.\d+)*),\s*([^<]*?)\s*</a>', page):
    anchor, num = m.group(1), m.group(2)
    words = re.sub(r'\s+', ' ', m.group(3)).rstrip(',').strip()
    if anchor in titles and words != titles[anchor]:
        errors.append(f'anchor #{anchor} is titled "{titles[anchor]}" but the token says "Section {num}, {words}"')
for m in re.finditer(r'\bSection (\d+(?:\.\d+)*)', page):
    if m.group(1) not in numbers:
        errors.append(f'"Section {m.group(1)}" names no heading')
for m in re.finditer(r'\bSections ((?:\d+(?:\.\d+)?)(?:(?:, | and | to | through |, and )\d+(?:\.\d+)?)*)', page):
    for num in re.findall(r'\d+(?:\.\d+)?', m.group(1)):
        if num not in numbers:
            errors.append(f'"Sections ... {num}" names no heading')
for m in re.finditer(r'\bTables? (\d+)(?!\d)', page):
    if m.group(1) not in tables:
        errors.append(f'"Table {m.group(1)}" has no label')
for m in re.finditer(r'\bFigures? (\d+)(?!\d)', page):
    if m.group(1) not in figures:
        errors.append(f'"Figure {m.group(1)}" has no figure id')
seen = set()
errors = [e for e in errors if not (e in seen or seen.add(e))]
if errors:
    print('\n'.join(errors)); sys.exit(1)
print(f'check-section-refs: {len(headings)} numbered headings, {len(tables)} tables, {len(figures)} figures, every token resolves')
