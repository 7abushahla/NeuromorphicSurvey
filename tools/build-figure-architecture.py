#!/usr/bin/env python3
"""Generate Figure 1, the survey architecture, from data/site-manifest.json and data/target-kinds.json.

The figure is a map of the survey's order, read top to bottom. Section 1 opens it. A dashed
Foundations band holds the three foundation sections. Where an SNN Runs is one box striped in
the three target-bucket hues of data/target-kinds.json, so the palette the graded claims use
is met here first. The Two Branches forks into direct training and conversion, drawn side by
side at equal width, and both end at the deployable contract. A dashed Deployment path band
holds software, routes and measurement in a row, the evidence section follows, and a dashed
Closing band holds the open problems and the entry guide.

Section numbers and titles are read from the manifest by the anchor suffix of each section id,
so a renumber or a retitle cannot strand the figure, and a missing section stops the build with
a message naming the suffix. The drawn topology is fixed, so the numbers must increase along the
drawn sequence; a manifest that moves a section out of that sequence stops the build naming the
first pair out of order. Labels wrap to fit their box by Helvetica metrics, and a label that
cannot fit within two lines also stops the build rather than overflowing silently. The two files
written, site/figures/survey-architecture.html and site/figures/survey-architecture.css, are
generated files. The build is idempotent, so the gate chain runs it before install-figures.py.
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE_MANIFEST = ROOT / "data/site-manifest.json"
TARGET_KINDS = ROOT / "data/target-kinds.json"
FRAGMENT_OUT = ROOT / "site/figures/survey-architecture.html"
CSS_OUT = ROOT / "site/figures/survey-architecture.css"

# The section each drawn box stands for, keyed by the anchor suffix of its manifest id.
SUFFIX = {
    "intro": "-introduction",
    "comp": "-computation-and-representation",
    "neur": "-neuron-and-synapse-dynamics",
    "code": "-temporal-semantics-neural-codes-and-decoding",
    "hw": "-where-an-snn-runs",
    "fork": "-the-two-branches",
    "direct": "-direct-snn-training",
    "conv": "-ann-to-snn-conversion",
    "contract": "-the-deployable-snn-contract",
    "sw": "-software-interchange-and-compilation",
    "routes": "-complete-deployment-routes",
    "meas": "-deployment-measurement",
    "evid": "-deployment-evidence-and-findings",
    "open": "-open-problems-and-research-agenda",
    "guide": "-researcher-entry-guide-and-conclusion",
}
# The order the figure draws the sections in, top to bottom and left to right. The manifest's
# display numbers must increase along it.
DRAWN_ORDER = tuple(SUFFIX)
# The stripe order of Section 5; guarded against the bucket order in data/target-kinds.json.
BUCKET_ORDER = ("conventional", "simulated", "neuromorphic")
# The Section 5 subsection each bucket stripe links to.
BUCKET_ANCHOR = {
    "conventional": "conventional-platforms",
    "simulated": "simulated-emulated-neuromorphic",
    "neuromorphic": "physical-neuromorphic-silicon",
}

# Canvas and type. The label size is chosen against the 720 px column the site gives a figure,
# where a 1200-unit viewBox renders at 0.6 scale, so a 20-unit label is 12 px on screen.
W = 1200
MARGIN = 40
CX = W // 2
LABEL_PX = 20
LINE_H = 24
BAND_PX = 14
BUCKET_PX = 16
PAD_X = 14
FONT = "Arial, Helvetica, sans-serif"

INK, LINE, FILL = "#2b3440", "#8a94a0", "#f6f7f9"
CONTRACT_FILL, CONTRACT_LINE = "#fff8e6", "#c9a227"
BOX_STROKE, STRIPE_STROKE, BAND_STROKE, ARROW_STROKE, MARKER_SIZE = 1.8, 1.5, 1.5, 2, 8

# Helvetica advance widths per 1000 em, the metric set Arial matches. Used only to wrap and to
# refuse a label that would overflow its box; the browser does the real layout.
_W = {
    " ": 278, "!": 278, '"': 355, "#": 556, "$": 556, "%": 889, "&": 667, "'": 191, "(": 333,
    ")": 333, "*": 389, "+": 584, ",": 278, "-": 333, ".": 278, "/": 278, ":": 278, ";": 278,
    "<": 584, "=": 584, ">": 584, "?": 556, "@": 1015, "[": 278, "\\": 278, "]": 278, "^": 469,
    "_": 556, "`": 333, "{": 334, "|": 260, "}": 334, "~": 584,
    "A": 667, "B": 667, "C": 722, "D": 722, "E": 667, "F": 611, "G": 778, "H": 722, "I": 278,
    "J": 500, "K": 667, "L": 556, "M": 833, "N": 722, "O": 778, "P": 667, "Q": 778, "R": 722,
    "S": 667, "T": 611, "U": 722, "V": 667, "W": 944, "X": 667, "Y": 667, "Z": 611,
    "a": 556, "b": 556, "c": 500, "d": 556, "e": 556, "f": 278, "g": 556, "h": 556, "i": 222,
    "j": 222, "k": 500, "l": 222, "m": 833, "n": 556, "o": 556, "p": 556, "q": 556, "r": 333,
    "s": 500, "t": 278, "u": 556, "v": 500, "w": 722, "x": 500, "y": 500, "z": 500,
}
for _digit in "0123456789":
    _W[_digit] = 556
SAFETY = 1.05  # a fallback sans face may run a little wider than Helvetica


def text_width(text, px):
    return sum(_W.get(ch, 600) for ch in text) * px / 1000 * SAFETY


def wrap(label, max_width, px=LABEL_PX):
    """Split a label into one line, or the two lines that fit max_width most evenly."""
    words = label.split()
    if text_width(label, px) <= max_width:
        return [label]
    best = None
    for cut in range(1, len(words)):
        lines = [" ".join(words[:cut]), " ".join(words[cut:])]
        widest = max(text_width(line, px) for line in lines)
        if widest <= max_width and (best is None or widest < best[0]):
            best = (widest, lines)
    if best is None:
        raise SystemExit(
            f"build-figure-architecture: label {label!r} does not fit a {max_width:.0f}-unit box "
            f"within two lines; widen the box or shorten the title"
        )
    return best[1]


def load_sections():
    manifest = json.loads(SITE_MANIFEST.read_text())
    records = [r for r in manifest.get("fragments", []) if r.get("kind") == "section"]
    sections = {}
    for key, suffix in SUFFIX.items():
        matches = [r for r in records if str(r.get("id", "")).endswith(suffix)]
        if len(matches) != 1:
            raise SystemExit(
                f"build-figure-architecture: expected exactly one section id ending in "
                f"{suffix!r} in {SITE_MANIFEST.relative_to(ROOT)}, found {len(matches)}"
            )
        fragment = ROOT / str(matches[0]["fragment"])
        anchor = re.search(r'<h2 id="([^"]+)"', fragment.read_text())
        if not anchor:
            raise SystemExit(f"build-figure-architecture: no <h2 id> in {fragment.relative_to(ROOT)}")
        sections[key] = (int(matches[0]["display_number"]), str(matches[0]["title"]), anchor.group(1))
    for before, after in zip(DRAWN_ORDER, DRAWN_ORDER[1:]):
        if sections[after][0] <= sections[before][0]:
            raise SystemExit(
                f"build-figure-architecture: the manifest orders {after!r} ({sections[after][0]}) "
                f"before {before!r} ({sections[before][0]}) but the figure draws {before} first; "
                "redraw or restore the order"
            )
    return sections


def load_buckets():
    kinds = json.loads(TARGET_KINDS.read_text())
    buckets = {b["name"]: b for b in kinds["buckets"]}
    missing = [name for name in BUCKET_ORDER if name not in buckets]
    if missing:
        raise SystemExit(f"build-figure-architecture: target-kinds.json lacks bucket(s) {missing}")
    if tuple(b["name"] for b in kinds["buckets"]) != BUCKET_ORDER:
        raise SystemExit(
            "build-figure-architecture: BUCKET_ORDER no longer matches the order in data/target-kinds.json"
        )
    return buckets


class Canvas:
    def __init__(self, sections):
        self.sections = sections
        self.parts = []

    def label(self, key):
        number, title, _anchor = self.sections[key]
        return f"{number} {title}"

    def label_lines(self, key, width):
        return wrap(self.label(key), width - 2 * PAD_X)

    def row_height(self, keys, width):
        lines = max(len(self.label_lines(key, width)) for key in keys)
        return 24 + lines * LINE_H

    def text_block(self, lines, cx, cy, fill=INK, px=LABEL_PX):
        """A centered text element; the first token (the section number) is set bold."""
        first = cy - (len(lines) - 1) * LINE_H / 2 + px * 0.35
        runs = []
        for index, line in enumerate(lines):
            if index == 0:
                head, _, rest = line.partition(" ")
                lead = f'<tspan font-weight="700">{html.escape(head)}</tspan>'
                runs.append(f"{lead} {html.escape(rest)}" if rest else lead)
            else:
                runs.append(f'<tspan x="{cx:.0f}" dy="{LINE_H}">{html.escape(line)}</tspan>')
        return (
            f'<text x="{cx:.0f}" y="{first:.0f}" text-anchor="middle" fill="{fill}" '
            f'font-size="{px}">' + "".join(runs) + "</text>"
        )

    def box(self, key, x, y, w, h, fill=FILL, line=LINE):
        lines = self.label_lines(key, w)
        number, title, anchor = self.sections[key]
        self.parts.append(
            f'<a href="#{anchor}" class="f1-link"><title>Go to Section {number}, {html.escape(title)}</title>'
            f'<g id="f1-{key}" class="f1-box">'
            f'<rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}" rx="6" '
            f'fill="{fill}" stroke="{line}" stroke-width="{BOX_STROKE}"/>'
            + self.text_block(lines, x + w / 2, y + h / 2)
            + "</g></a>"
        )

    def band(self, key, title, x, y, w, h):
        self.parts.append(
            f'<g id="f1-band-{key}" class="f1-band">'
            f'<rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}" rx="10" '
            f'fill="none" stroke="{LINE}" stroke-width="{BAND_STROKE}" stroke-dasharray="5 4"/>'
            f'<text x="{x + 16:.0f}" y="{y + 21:.0f}" fill="{LINE}" font-size="{BAND_PX}" '
            f'letter-spacing="1.2">{html.escape(title.upper())}</text></g>'
        )

    def line(self, key, points, head=True):
        """A connector; with head it ends in the arrow marker, without it is a shared stem or rail."""
        d = "M" + " L".join(f"{x:.0f},{y:.0f}" for x, y in points)
        marker = ' marker-end="url(#f1-arrow)"' if head else ""
        self.parts.append(
            f'<path id="f1-{key}" class="f1-arrow" d="{d}" fill="none" stroke="{INK}" '
            f'stroke-width="{ARROW_STROKE}" stroke-linejoin="round"{marker}/>'
        )

    def bucket_box(self, key, x, y, w, buckets):
        """The hardware section as one box whose lower part is three stripes in the bucket hues.

        The title block takes the height row_height() would give it, so a wrapped title moves the
        stripes down instead of colliding with them. Returns the box height.
        """
        lines = self.label_lines(key, w)
        title_h = 24 + len(lines) * LINE_H
        stripe_top = y + title_h + 6
        stripe_h = 40
        h = title_h + 6 + stripe_h + 10
        inset, gap = 10, 8
        stripe_w = (w - 2 * inset - (len(BUCKET_ORDER) - 1) * gap) / len(BUCKET_ORDER)
        number, title, anchor = self.sections[key]
        parts = [
            f'<a href="#{anchor}" class="f1-link"><title>Go to Section {number}, {html.escape(title)}</title>'
            f'<g id="f1-{key}" class="f1-box">'
            f'<rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}" rx="6" '
            f'fill="{FILL}" stroke="{LINE}" stroke-width="{BOX_STROKE}"/>',
            self.text_block(lines, x + w / 2, y + title_h / 2),
            "</g></a>",
        ]
        for index, name in enumerate(BUCKET_ORDER):
            b = buckets[name]
            sx = x + inset + index * (stripe_w + gap)
            parts.append(
                f'<a href="#{BUCKET_ANCHOR[name]}" class="f1-link"><g id="f1-bucket-{name}">'
                f'<rect x="{sx:.0f}" y="{stripe_top:.0f}" width="{stripe_w:.0f}" height="{stripe_h:.0f}" '
                f'rx="4" fill="{b["fill"]}" stroke="{b["line"]}" stroke-width="{STRIPE_STROKE}"/>'
                f'<text x="{sx + stripe_w / 2:.0f}" y="{stripe_top + stripe_h / 2 + BUCKET_PX * 0.35:.0f}" '
                f'text-anchor="middle" fill="{b["ink"]}" font-size="{BUCKET_PX}">{html.escape(name)}</text></g></a>'
            )
        self.parts.append("".join(parts))
        return h


def draw(sections, buckets):
    c = Canvas(sections)
    inner_x, inner_w = MARGIN, W - 2 * MARGIN
    band_pad_x, band_head, band_foot = 20, 34, 16
    band_inner_x, band_inner_w = inner_x + band_pad_x, inner_w - 2 * band_pad_x
    gap, elbow_gap = 30, 56
    y = 30

    # Section 1 opens the map.
    intro_w = 360
    intro_h = c.row_height(("intro",), intro_w)
    c.box("intro", CX - intro_w / 2, y, intro_w, intro_h)
    y += intro_h
    c.line("intro-to-foundations", [(CX, y), (CX, y + gap)])
    y += gap

    # Foundations band, three boxes.
    three_gap = 24
    three_w = (band_inner_w - 2 * three_gap) / 3
    foundation_keys = ("comp", "neur", "code")
    box_h = c.row_height(foundation_keys, three_w)
    band_h = band_head + box_h + band_foot
    c.band("foundations", "Foundations", inner_x, y, inner_w, band_h)
    for index, key in enumerate(foundation_keys):
        c.box(key, band_inner_x + index * (three_w + three_gap), y + band_head, three_w, box_h)
    y += band_h
    c.line("foundations-to-hw", [(CX, y), (CX, y + gap)])
    y += gap

    # Where an SNN Runs, striped in the three bucket hues.
    y += c.bucket_box("hw", inner_x, y, inner_w, buckets)
    c.line("hw-to-fork", [(CX, y), (CX, y + gap)])
    y += gap

    # The fork. One stem to a rail, then one elbow per branch.
    fork_w = 360
    fork_h = c.row_height(("fork",), fork_w)
    c.box("fork", CX - fork_w / 2, y, fork_w, fork_h)
    y += fork_h
    branch_w = 440
    left_cx, right_cx = CX - 280, CX + 280
    rail = y + elbow_gap / 2
    c.line("fork-stem", [(CX, y), (CX, rail)], head=False)
    c.line("fork-left", [(CX, rail), (left_cx, rail), (left_cx, y + elbow_gap)])
    c.line("fork-right", [(CX, rail), (right_cx, rail), (right_cx, y + elbow_gap)])
    y += elbow_gap

    # Two branches, the same width. One elbow per branch to a rail, then one stem to the contract.
    branch_h = c.row_height(("direct", "conv"), branch_w)
    c.box("direct", left_cx - branch_w / 2, y, branch_w, branch_h)
    c.box("conv", right_cx - branch_w / 2, y, branch_w, branch_h)
    y += branch_h
    rail = y + elbow_gap / 2
    c.line("join-left", [(left_cx, y), (left_cx, rail), (CX, rail)], head=False)
    c.line("join-right", [(right_cx, y), (right_cx, rail), (CX, rail)], head=False)
    c.line("join-stem", [(CX, rail), (CX, y + elbow_gap)])
    y += elbow_gap

    # The contract, where the branches meet.
    contract_w = 560
    contract_h = c.row_height(("contract",), contract_w) + 4
    c.box("contract", CX - contract_w / 2, y, contract_w, contract_h, fill=CONTRACT_FILL, line=CONTRACT_LINE)
    y += contract_h
    c.line("contract-to-deployment", [(CX, y), (CX, y + gap)])
    y += gap

    # Deployment path band, three boxes chained by arrows.
    chain_gap = 42
    chain_w = (band_inner_w - 2 * chain_gap) / 3
    chain_keys = ("sw", "routes", "meas")
    box_h = c.row_height(chain_keys, chain_w)
    band_h = band_head + box_h + band_foot
    c.band("deployment", "Deployment path", inner_x, y, inner_w, band_h)
    for index, key in enumerate(chain_keys):
        bx = band_inner_x + index * (chain_w + chain_gap)
        c.box(key, bx, y + band_head, chain_w, box_h)
        if index:
            mid = y + band_head + box_h / 2
            c.line(f"chain-{index}", [(bx - chain_gap + 2, mid), (bx - 2, mid)])
    y += band_h
    c.line("deployment-to-evid", [(CX, y), (CX, y + gap)])
    y += gap

    # Evidence and findings.
    evid_w = 560
    evid_h = c.row_height(("evid",), evid_w)
    c.box("evid", CX - evid_w / 2, y, evid_w, evid_h)
    y += evid_h
    c.line("evid-to-closing", [(CX, y), (CX, y + gap)])
    y += gap

    # Closing band, two boxes.
    pair_gap = 40
    pair_w = (band_inner_w - pair_gap) / 2
    pair_keys = ("open", "guide")
    box_h = c.row_height(pair_keys, pair_w)
    band_h = band_head + box_h + band_foot
    c.band("closing", "Closing", inner_x, y, inner_w, band_h)
    for index, key in enumerate(pair_keys):
        c.box(key, band_inner_x + index * (pair_w + pair_gap), y + band_head, pair_w, box_h)
    y += band_h
    height = y + 30
    return c.parts, height


def section_token(sections, key):
    number, title, _anchor = sections[key]
    return f"Section {number}, {title},"


def accessible_text(sections):
    s = lambda key: section_token(sections, key)  # noqa: E731
    hues = ", ".join(BUCKET_ORDER[:-1]) + ", and " + BUCKET_ORDER[-1]
    title = (
        "The order of this survey, from the foundations through the hardware targets, the two "
        "learning branches and the contract, to the deployment path and its findings"
    )
    desc = (
        "A flow diagram of the survey's fifteen sections, read top to bottom. "
        f"{s('intro')} opens it and leads to a Foundations band holding {s('comp')} {s('neur')} "
        f"and {s('code')} side by side. The band leads to {s('hw')} drawn as one box whose lower "
        f"part is three stripes in the {hues} hues of the target buckets. {s('fork')} follows and "
        f"forks into {s('direct')} and {s('conv')} drawn side by side at the same width, and both "
        f"end at {s('contract')} drawn in a gold tint. One deployment path follows in a band, "
        f"{s('sw')} then {s('routes')} then {s('meas')} chained left to right, and leads to "
        f"{s('evid')} which a Closing band follows, holding {s('open')} and {s('guide')} side by "
        "side. Conceptual figure; no measured quantity is drawn."
    )
    return html.escape(title), html.escape(desc)


def build():
    sections = load_sections()
    buckets = load_buckets()
    parts, height = draw(sections, buckets)
    title, desc = accessible_text(sections)
    svg = (
        f'<svg viewBox="0 0 {W} {height:.0f}" role="img" aria-labelledby="f1-title f1-desc" '
        f'font-family="{FONT}" font-size="{LABEL_PX}">\n'
        f'  <title id="f1-title">{title}</title>\n'
        f'  <desc id="f1-desc">{desc}</desc>\n'
        f'  <defs><marker id="f1-arrow" viewBox="0 0 10 10" refX="9" refY="5" '
        f'markerWidth="{MARKER_SIZE}" markerHeight="{MARKER_SIZE}" orient="auto">'
        f'<path d="M0,0 L10,5 L0,10 z" fill="{INK}"/></marker></defs>\n  '
        + "\n  ".join(parts)
        + "\n</svg>"
    )
    caption = (
        "<figcaption><b>Figure 1:</b> The order of this survey. The silicon is met before any "
        "network is fitted to it, so the chip and the grade beside every claim are defined by the "
        "time the first claim appears, and the three hues of the target buckets are met here in "
        "the same order the claims use them. The two learning branches are drawn the same width "
        "and end at one contract, which is also where the platforms met earlier are compared "
        "field by field. One deployment path follows, software, routes, and measurement, and the "
        "evidence read along it closes with what it shows. Conceptual figure; no measured "
        "quantity is drawn.</figcaption>"
    )
    fragment = (
        '<figure class="pfig l-body" id="figure-1">\n'
        "<!-- Generated by tools/build-figure-architecture.py from data/site-manifest.json and "
        "data/target-kinds.json. Do not edit by hand; rerun the builder. Conceptual figure; no "
        "measured quantity is drawn. -->\n"
        f"{svg}\n"
        '<div class="fig-hint">Click any block to jump to that part of the survey.</div>\n'
        f"{caption}\n</figure>\n"
    )
    css = (
        "/* Generated by tools/build-figure-architecture.py; do not edit by hand. */\n"
        "#figure-1 svg { display: block; width: 100%; max-width: 720px; height: auto; margin: 0 auto; }\n"
        "#figure-1 a.f1-link { cursor: pointer; text-decoration: none; }\n"
        "#figure-1 a.f1-link:hover rect, #figure-1 a.f1-link:focus rect { filter: brightness(0.94); }\n"
    )
    return fragment, css


def main():
    fragment, css = build()
    changed = []
    for path, content in ((FRAGMENT_OUT, fragment), (CSS_OUT, css)):
        if not path.exists() or path.read_text() != content:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
            changed.append(path.relative_to(ROOT).as_posix())
    if changed:
        print("build-figure-architecture: wrote " + " and ".join(changed))
    else:
        print("build-figure-architecture: site/figures/survey-architecture.html and .css already current")


if __name__ == "__main__":
    main()
