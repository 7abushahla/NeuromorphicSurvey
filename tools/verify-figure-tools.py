#!/usr/bin/env python3
"""Regression tests for manifest-driven static figure tooling."""

import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET


SOURCE_ROOT = Path(__file__).resolve().parent.parent


def valid_fragment(number=7, *, aria="labelledby"):
    if aria == "label":
        accessible = 'role="img" aria-label="A valid explanatory diagram"'
        labels = ""
    else:
        accessible = f'role="img" aria-labelledby="f{number}title f{number}desc"'
        labels = (
            f'<title id="f{number}title">Valid diagram</title>'
            f'<desc id="f{number}desc">A test diagram with a numerical time axis.</desc>'
        )
    return f'''<figure class="pfig l-body" id="figure-{number}">
  <svg viewBox="0 0 100 100" {accessible}>
    {labels}
    <defs><marker id="f{number}arrow"><path d="M0,0 L4,2 L0,4 Z"/></marker></defs>
    <g class="numerical-axis" data-axis="numerical" data-unit="ms">
      <line x1="0" y1="90" x2="100" y2="90" marker-end="url(#f{number}arrow)"/>
      <text x="5" y="98">time (ms)</text>
    </g>
  </svg>
  <figcaption><b>Figure {number}:</b> A complete, accessible test figure.</figcaption>
</figure>
'''


def figure_record(number=7, *, identifier="sample-static", status="implemented"):
    return {
        "id": identifier,
        "display_number": number,
        "fragment": f"site/figures/figure-{number}.html",
        "css": f"site/figures/figure-{number}.css",
        "destination_section": "section-target",
        "concept": "Test concept",
        "question": "What behavior does this fixture verify?",
        "interactive": False,
        "status": status,
    }


def figure_like_axis_fragment(number=7, *, unit_label=""):
    label = f'<text x="50" y="99">{unit_label}</text>' if unit_label else ""
    return f'''<figure class="pfig l-body" id="figure-{number}">
  <svg viewBox="0 0 100 100" role="img" aria-label="A numerical trace">
    <line x1="10" y1="80" x2="90" y2="80"/>
    <line x1="10" y1="76" x2="10" y2="84"/>
    <line x1="50" y1="76" x2="50" y2="84"/>
    <line x1="90" y1="76" x2="90" y2="84"/>
    <text x="10" y="94">0</text>
    <text x="50" y="94">5</text>
    <text x="90" y="94">10</text>
    {label}
  </svg>
  <figcaption><b>Figure {number}:</b> A numerical trace with visible ticks.</figcaption>
</figure>
'''


def figure_like_decorative_fragment(number=7):
    return f'''<figure class="pfig l-body" id="figure-{number}">
  <svg viewBox="0 0 100 100" role="img" aria-label="A decorative comparison">
    <line x1="10" y1="50" x2="90" y2="50"/>
    <text x="10" y="57">0.73</text>
    <text x="90" y="57">2</text>
    <text x="50" y="35">activation value and callout badge</text>
  </svg>
  <figcaption><b>Figure {number}:</b> Decorative values beside a comparison line.</figcaption>
</figure>
'''


# The fifteen section ids and titles the hardware-first reorder produces (data/section-reorder.json
# through reorder-sections.py's slug rule). The architecture builder looks each one up by id suffix.
ARCHITECTURE_SECTIONS = (
    (1, "section-01-introduction", "Introduction"),
    (2, "section-02-computation-and-representation", "Computation and Representation"),
    (3, "section-03-neuron-and-synapse-dynamics", "Neuron and Synapse Dynamics"),
    (4, "section-04-temporal-semantics-neural-codes-and-decoding", "Temporal Semantics, Neural Codes, and Decoding"),
    (5, "section-05-where-an-snn-runs", "Where an SNN Runs"),
    (6, "section-06-the-two-branches", "The Two Branches"),
    (7, "section-07-direct-snn-training", "Direct SNN Training"),
    (8, "section-08-ann-to-snn-conversion", "ANN-to-SNN Conversion"),
    (9, "section-09-the-deployable-snn-contract", "The Deployable SNN Contract"),
    (10, "section-10-software-interchange-and-compilation", "Software, Interchange, and Compilation"),
    (11, "section-11-complete-deployment-routes", "Complete Deployment Routes"),
    (12, "section-12-deployment-measurement", "Deployment Measurement"),
    (13, "section-13-deployment-evidence-and-findings", "Deployment Evidence and Findings"),
    (14, "section-14-open-problems-and-research-agenda", "Open Problems and Research Agenda"),
    (15, "section-15-researcher-entry-guide-and-conclusion", "Researcher Entry Guide and Conclusion"),
)


def architecture_site_manifest(sections=ARCHITECTURE_SECTIONS):
    fragments = [{"id": "shell-head", "kind": "shell", "fragment": "site/shell-head.html"}]
    for number, identifier, title in sections:
        fragments.append(
            {
                "id": identifier,
                "kind": "section",
                "display_number": number,
                "title": title,
                "fragment": f"site/sec-{number:02d}.html",
            }
        )
    return {"schema_version": 1, "fragments": fragments}


def svg_text_labels(fragment):
    """Every <text> element's visible label, its runs (number tspan, wrapped lines) joined by one space."""
    svg = ET.fromstring(re.search(r"<svg\b.*?</svg\s*>", fragment, re.S).group(0))
    labels = []
    for element in svg.iter():
        if element.tag.rsplit("}", 1)[-1] == "text":
            runs = [piece.strip() for piece in element.itertext() if piece.strip()]
            labels.append(" ".join(" ".join(runs).split()))
    return labels


def section_numbers_in_order(labels):
    """The leading number of every section label, in document order."""
    return [int(label.split(" ", 1)[0]) for label in labels if re.match(r"\d+ ", label)]


class FigureToolTests(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "NeuromorphicSurvey"
        for relative in ("tools", "data", "site/figures", "assets"):
            (self.root / relative).mkdir(parents=True, exist_ok=True)
        for script in ("install-figures.py", "check-figures.py"):
            shutil.copy2(SOURCE_ROOT / "tools" / script, self.root / "tools" / script)
        self.write_json(
            "data/site-manifest.json",
            {
                "schema_version": 1,
                "fragments": [
                    {
                        "id": "section-target",
                        "kind": "section",
                        "display_number": 9,
                        "title": "Target",
                        "fragment": "site/sec-target.html",
                    }
                ],
            },
        )

    def tearDown(self):
        self.temp.cleanup()

    def write_json(self, relative, value):
        (self.root / relative).write_text(json.dumps(value, indent=2) + "\n")

    def write_figure(self, record, fragment=None, css=None):
        number = record["display_number"]
        fragment_path = self.root / record["fragment"]
        css_path = self.root / record["css"]
        fragment_path.parent.mkdir(parents=True, exist_ok=True)
        css_path.parent.mkdir(parents=True, exist_ok=True)
        fragment_path.write_text(fragment if fragment is not None else valid_fragment(number))
        css_path.write_text(css if css is not None else f"#figure-{number} .numerical-axis {{ color: #000; }}\n")

    def write_manifest(self, records):
        self.write_json("data/figure-manifest.json", {"schema_version": 1, "figures": records})

    def run_tool(self, script, *args):
        return subprocess.run(
            [sys.executable, str(self.root / "tools" / script), *args],
            cwd=self.root,
            text=True,
            capture_output=True,
            check=False,
        )

    def snapshot(self, *paths):
        return {
            path: hashlib.sha256((self.root / path).read_bytes()).hexdigest()
            for path in paths
        }

    def test_check_is_byte_for_byte_dry_run_and_uses_manifest_destination(self):
        record = figure_record(2, identifier="representation-comparison")
        self.write_manifest([record])
        self.write_figure(record)
        wrong = "<section><figure id=\"figure-2\">wrong destination</figure></section>\n"
        target = "<section><figure id=\"figure-2\">target placeholder</figure></section>\n"
        (self.root / "site/sec-02.html").write_text(wrong)
        (self.root / "site/sec-target.html").write_text(target)
        (self.root / "assets/figures.css").write_text("sentinel css\n")
        watched = ("site/sec-02.html", "site/sec-target.html", "assets/figures.css")
        before = self.snapshot(*watched)

        result = self.run_tool("install-figures.py", "--check")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.snapshot(*watched), before, "--check changed repository bytes")
        self.assertIn("section-target", result.stdout)
        self.assertIn("would replace", result.stdout)
        self.assertNotIn("site/sec-02.html", result.stdout)

    def test_install_routes_and_generates_css_in_manifest_order(self):
        first = figure_record(7, identifier="first-semantic-id")
        second = figure_record(2, identifier="second-semantic-id")
        planned = figure_record(8, identifier="future-semantic-id", status="planned")
        self.write_manifest([first, second, planned])
        self.write_figure(first, css="#figure-7 .first { color: black; }\n")
        self.write_figure(second, css="#figure-2 .second { color: red; }\n")
        (self.root / "site/sec-target.html").write_text(
            '<section><figure id="figure-7">old 7</figure><figure id="figure-2">old 2</figure></section>\n'
        )

        result = self.run_tool("install-figures.py")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        installed = (self.root / "site/sec-target.html").read_text()
        self.assertIn("A complete, accessible test figure", installed)
        self.assertNotIn("old 7", installed)
        self.assertNotIn("old 2", installed)
        css = (self.root / "assets/figures.css").read_text()
        self.assertLess(css.index("first-semantic-id"), css.index("second-semantic-id"))
        self.assertNotIn("future-semantic-id", css)
        self.assertIn("planned", result.stdout)

    def test_planned_missing_assets_are_reported_not_failed(self):
        implemented = figure_record(7)
        planned = figure_record(8, identifier="future-static", status="planned")
        self.write_manifest([implemented, planned])
        self.write_figure(implemented)

        result = self.run_tool("check-figures.py")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("planned", result.stdout)
        self.assertIn("future-static", result.stdout)
        self.assertIn("all implemented static figures passed", result.stdout)

    def test_accessible_svg_accepts_aria_label_and_aria_labelledby(self):
        record = figure_record(7)
        self.write_manifest([record])
        for aria in ("label", "labelledby"):
            with self.subTest(aria=aria):
                self.write_figure(record, fragment=valid_fragment(7, aria=aria))
                result = self.run_tool("check-figures.py")
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_css_scope_requires_exact_non_escaping_figure_root(self):
        record = figure_record(7)
        self.write_manifest([record])
        cases = {
            "prefix collision": "#figure-70 .inside { color: red; }\n",
            "adjacent sibling escape": "#figure-7 + .outside { color: red; }\n",
            "column combinator escape": "#figure-7 || .outside { color: red; }\n",
            "negated ancestor": "body:not(#figure-7) .outside { color: red; }\n",
        }
        for name, css in cases.items():
            with self.subTest(case=name):
                self.write_figure(record, css=css)
                result = self.run_tool("check-figures.py")
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn("not scoped to #figure-7", result.stdout + result.stderr)

    def test_bare_relative_urls_are_rejected_in_css_and_svg(self):
        record = figure_record(7)
        self.write_manifest([record])
        cases = {
            "css relative URL": (
                valid_fragment(7),
                "#figure-7 { background-image: url(texture.svg); }\n",
            ),
            "SVG presentation URL": (
                valid_fragment(7).replace('<svg viewBox=', '<svg fill="url(texture.svg#paint)" viewBox='),
                "#figure-7 { color: black; }\n",
            ),
            "SVG style URL": (
                valid_fragment(7).replace('<svg viewBox=', '<svg style="filter:url(texture.svg#paint)" viewBox='),
                "#figure-7 { color: black; }\n",
            ),
            "SVG external gradient href": (
                valid_fragment(7).replace(
                    "</defs>",
                    '<linearGradient id="f7gradient" href="palette.svg#paint"></linearGradient></defs>',
                ),
                "#figure-7 { color: black; }\n",
            ),
        }
        for name, (fragment, css) in cases.items():
            with self.subTest(case=name):
                self.write_figure(record, fragment=fragment, css=css)
                result = self.run_tool("check-figures.py")
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn("external asset", result.stdout + result.stderr)

    def test_internal_section_link_is_allowed(self):
        record = figure_record(7)
        self.write_manifest([record])
        fragment = valid_fragment(7).replace(
            "</svg>",
            '<a href="#section-03-neuron-and-synapse-dynamics"><text x="5" y="70">Section 3</text></a></svg>',
        )
        self.write_figure(record, fragment=fragment)

        result = self.run_tool("check-figures.py")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_visible_numeric_ticks_require_and_accept_visible_units(self):
        record = figure_record(7)
        self.write_manifest([record])
        self.write_figure(record, fragment=figure_like_axis_fragment(7, unit_label="time (ms)"))
        result = self.run_tool("check-figures.py")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        self.write_figure(record, fragment=figure_like_axis_fragment(7))
        result = self.run_tool("check-figures.py")
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("visible numeric ticks", result.stdout + result.stderr)
        self.assertIn("non-empty unit", result.stdout + result.stderr)

    def test_unrelated_unit_like_prose_does_not_label_numeric_axis(self):
        record = figure_record(7)
        self.write_manifest([record])
        fragment = figure_like_axis_fragment(7).replace(
            "</svg>",
            '<text x="5" y="20">Unrelated spike events</text></svg>',
        )
        self.write_figure(record, fragment=fragment)

        result = self.run_tool("check-figures.py")

        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("visible numeric ticks", result.stdout + result.stderr)
        self.assertIn("non-empty unit", result.stdout + result.stderr)

    def test_decorative_numeric_badges_near_line_are_not_inferred_as_axis(self):
        record = figure_record(7)
        self.write_manifest([record])
        self.write_figure(record, fragment=figure_like_decorative_fragment(7))

        result = self.run_tool("check-figures.py")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_categorical_axis_does_not_require_numerical_units(self):
        record = figure_record(7)
        self.write_manifest([record])
        fragment = valid_fragment(7).replace(
            'class="numerical-axis" data-axis="numerical" data-unit="ms"',
            'class="axis"',
        ).replace(
            '<text x="5" y="98">time (ms)</text>',
            '<text x="5" y="98">low</text><text x="50" y="98">high</text>',
        )
        self.write_figure(record, fragment=fragment)

        result = self.run_tool("check-figures.py")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_invalid_implemented_fragments_fail_with_specific_diagnostic(self):
        record = figure_record(7)
        base = valid_fragment(7)
        cases = {
            "two figures": (base + base, "exactly one <figure>"),
            "missing caption": (base.replace("<figcaption>", "<p>").replace("</figcaption>", "</p>"), "exactly one <figcaption>"),
            "two svgs": (base.replace("</svg>", "</svg><svg viewBox=\"0 0 1 1\" aria-label=\"extra\"></svg>"), "exactly one inline <svg>"),
            "fixed svg width": (base.replace("viewBox=", 'width="100" viewBox='), "viewBox alone"),
            "wrong DOM identity": (base.replace("figure-7", "figure-70", 1), "expected DOM id 'figure-7'"),
            "script": (base.replace("</svg>", "<script>bad()</script></svg>"), "external asset or script"),
            "external image": (base.replace("</svg>", '<image href="plot.png"/></svg>'), "external asset or script"),
            "external SVG use": (base.replace("</svg>", '<use href="symbols.svg#mark"/></svg>'), "external asset or script"),
            "unprefixed SVG id": (base.replace("f7arrow", "arrow", 1), "not prefixed 'f7'"),
            "duplicate SVG id": (base.replace("</defs>", '<g id="f7arrow"></g></defs>'), "duplicate SVG id"),
            "unresolved url": (base.replace("url(#f7arrow)", "url(#f7missing)"), "has no definition"),
            "outside coordinate": (base.replace('x2="100"', 'x2="102"'), "outside viewBox width"),
            "no accessible name": (base.replace('role="img" aria-labelledby="f7title f7desc"', 'role="img"'), "accessible title and description"),
            "empty axis unit": (base.replace('data-unit="ms"', 'data-unit=""'), "non-empty unit"),
            "unannotated numerical axis": (
                base.replace(
                    'class="numerical-axis" data-axis="numerical" data-unit="ms"',
                    'class="axis"',
                ).replace('<text x="5" y="98">time (ms)</text>', '<text x="5" y="98">0</text><text x="50" y="98">1</text>'),
                "non-empty unit",
            ),
            "placeholder": (base.replace("complete, accessible", "FIGURE TO DRAW"), "forbidden placeholder/editorial language"),
        }
        self.write_manifest([record])
        for name, (fragment, diagnostic) in cases.items():
            with self.subTest(case=name):
                self.write_figure(record, fragment=fragment)
                result = self.run_tool("check-figures.py")
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn(diagnostic, result.stdout + result.stderr)

    def test_invalid_css_and_missing_implemented_assets_fail(self):
        record = figure_record(7)
        self.write_manifest([record])
        self.write_figure(record, css=".global { color: red; }\n")

        result = self.run_tool("check-figures.py")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not scoped to #figure-7", result.stdout + result.stderr)

        (self.root / record["fragment"]).unlink()
        result = self.run_tool("install-figures.py", "--check")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("implemented fragment does not exist", result.stdout + result.stderr)

    def test_install_and_check_fail_atomically_when_implemented_figure_cannot_be_placed(self):
        placeable = figure_record(2, identifier="placeable-static")
        blocked = figure_record(7, identifier="blocked-static")
        self.write_manifest([placeable, blocked])
        self.write_figure(placeable)
        self.write_figure(blocked)
        (self.root / "site/sec-target.html").write_text(
            '<section><figure id="figure-2">old 2</figure><p>No figure 7 target.</p></section>\n'
        )
        (self.root / "assets/figures.css").write_text("sentinel css\n")
        watched = ("site/sec-target.html", "assets/figures.css")

        for args in ((), ("--check",)):
            with self.subTest(args=args):
                before = self.snapshot(*watched)
                result = self.run_tool("install-figures.py", *args)
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertEqual(self.snapshot(*watched), before)
                self.assertIn("cannot place", result.stdout + result.stderr)
                self.assertIn("section-target", result.stdout + result.stderr)
                if not args:
                    self.assertNotIn(": replaced", result.stdout)

        (self.root / "site/sec-target.html").unlink()
        result = self.run_tool("install-figures.py", "--check")
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("destination fragment unavailable", result.stdout + result.stderr)

    def install_architecture_fixture(self):
        """The builder, the real palette, the fifteen reordered sections, and an implemented record."""
        shutil.copy2(
            SOURCE_ROOT / "tools/build-figure-architecture.py",
            self.root / "tools/build-figure-architecture.py",
        )
        shutil.copy2(SOURCE_ROOT / "data/target-kinds.json", self.root / "data/target-kinds.json")
        self.write_json("data/site-manifest.json", architecture_site_manifest())
        # The builder links each drawn box to its section's <h2 id>, read from the fragment.
        for number, identifier, title in ARCHITECTURE_SECTIONS:
            (self.root / f"site/sec-{number:02d}.html").write_text(
                f'<h2 id="{identifier.split("-", 2)[-1]}">{number} {title}</h2>\n'
            )
        record = figure_record(1, identifier="survey-architecture")
        record["fragment"] = "site/figures/survey-architecture.html"
        record["css"] = "site/figures/survey-architecture.css"
        self.write_manifest([record])
        return self.root / record["fragment"], self.root / record["css"]

    def test_architecture_builder_reads_manifest_and_is_idempotent(self):
        fragment_path, css_path = self.install_architecture_fixture()

        result = self.run_tool("build-figure-architecture.py")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        fragment = fragment_path.read_text()
        css = css_path.read_text()
        labels = svg_text_labels(fragment)
        for number, _identifier, title in ARCHITECTURE_SECTIONS:
            self.assertIn(f"{number} {title}", labels)
        numbers = section_numbers_in_order(labels)
        self.assertEqual(numbers, sorted(numbers), "section labels are not in ascending order")
        self.assertEqual(len(numbers), len(ARCHITECTURE_SECTIONS))
        kinds = json.loads((SOURCE_ROOT / "data/target-kinds.json").read_text())
        for bucket in kinds["buckets"]:
            self.assertIn(bucket["name"], labels)
            for key in ("fill", "ink", "line"):
                self.assertIn(bucket[key], fragment)
        for forbidden in ("\u2014", "&mdash;", "&#8212;"):
            self.assertNotIn(forbidden, fragment)

        check = self.run_tool("check-figures.py")
        self.assertEqual(check.returncode, 0, check.stdout + check.stderr)
        self.assertIn("survey-architecture (Figure 1)", check.stdout)

        again = self.run_tool("build-figure-architecture.py")
        self.assertEqual(again.returncode, 0, again.stdout + again.stderr)
        self.assertEqual(fragment, fragment_path.read_text())
        self.assertEqual(css, css_path.read_text())

        # The palette must be read from target-kinds.json, not typed into the builder.
        sentinel = {"fill": "#010203", "ink": "#040506", "line": "#070809"}
        original = next(b for b in kinds["buckets"] if b["name"] == "neuromorphic")
        recolored = json.loads(json.dumps(kinds))
        for bucket in recolored["buckets"]:
            if bucket["name"] == "neuromorphic":
                bucket.update(sentinel)
        self.write_json("data/target-kinds.json", recolored)
        result = self.run_tool("build-figure-architecture.py")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        recolored_fragment = fragment_path.read_text()
        for key, value in sentinel.items():
            self.assertIn(value, recolored_fragment)
            self.assertNotIn(original[key], recolored_fragment)
        self.write_json("data/target-kinds.json", kinds)

        retitled = [
            (number, identifier, "Where a Network Runs" if number == 5 else title)
            for number, identifier, title in ARCHITECTURE_SECTIONS
        ]
        self.write_json("data/site-manifest.json", architecture_site_manifest(retitled))
        result = self.run_tool("build-figure-architecture.py")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        labels = svg_text_labels(fragment_path.read_text())
        self.assertIn("5 Where a Network Runs", labels)
        self.assertNotIn("5 Where an SNN Runs", labels)

        without_contract = [entry for entry in ARCHITECTURE_SECTIONS if entry[0] != 9]
        self.write_json("data/site-manifest.json", architecture_site_manifest(without_contract))
        result = self.run_tool("build-figure-architecture.py")
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("-the-deployable-snn-contract", result.stdout + result.stderr)

    def test_architecture_builder_refuses_a_manifest_that_moves_a_section(self):
        fragment_path, _css_path = self.install_architecture_fixture()
        swapped = [
            (9 if number == 5 else 5 if number == 9 else number, identifier, title)
            for number, identifier, title in ARCHITECTURE_SECTIONS
        ]
        self.write_json("data/site-manifest.json", architecture_site_manifest(swapped))

        result = self.run_tool("build-figure-architecture.py")

        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("draws hw first", result.stdout + result.stderr)
        self.assertFalse(fragment_path.exists(), "a refused build must write nothing")


GUIDE_FIXTURE = {
    "schema_version": 1,
    "layers": [
        {"id": "app", "n": 1, "name": "Application", "sub": "s", "rows": [
            {"label": "Task", "slot": "task", "chips": [{"id": "task-a", "label": "Task A"}]},
            {"label": "Input representation", "slot": "input", "chips": [{"id": "in-a", "label": "In A"}]}]},
        {"id": "sw", "n": 5, "name": "Software stack", "sub": "s", "rows": [
            {"label": "Develop and train", "slot": "dev", "chips": [
                {"id": "fw-a", "label": "FW A"}, {"id": "fw-b", "label": "FW B"}, {"id": "fw-c", "label": "FW C"}]},
            {"label": "Run on device", "slot": "run", "chips": [{"id": "rt-a", "label": "RT A"}]}]},
        {"id": "hw", "n": 6, "name": "Hardware", "sub": "s", "rows": [
            {"label": "Conventional processors", "slot": "hw", "bucket": "conventional", "chips": [{"id": "cpu-a", "label": "CPU A"}]},
            {"label": "Synchronous digital", "slot": "hw", "bucket": "neuromorphic", "chips": [
                {"id": "chip-a", "label": "Chip A"}, {"id": "chip-lonely", "label": "Lonely"}, {"id": "chip-b", "label": "Chip B"}]}]}],
    "slots": ["task", "input", "dev", "run", "hw"],
    "buckets": [{"name": "conventional", "meaning": "c"}, {"name": "simulated", "meaning": "s"}, {"name": "neuromorphic", "meaning": "n"}],
    "seams": {"sw": [{"pin": "S1", "title": "Operator coverage", "text": "t"}]},
    "rails": {"left": [], "right": []},
    "quick": ["Task A"],
    "toolchains": {
        "fw-a-chip-a": {"name": "FW A to Chip A", "rank": 1, "tk": "neuromorphic", "color": "#111111", "ev": "E1",
                        "story": "s", "note": "n",
                        "steps": {"task": None, "input": "in-a", "dev": "fw-a", "run": "rt-a"},
                        "can": {"input": ["in-a"], "dev": ["fw-a"], "run": ["rt-a"]},
                        "implies": [], "targets": ["chip-a"], "vendorFor": ["chip-a"],
                        "papers": [{"id": "paper-a", "via": {"input": "in-a", "hw": "chip-a"}}]},
        "multi-dev-chip-a": {"name": "Multi Dev to Chip A", "rank": 2, "tk": "neuromorphic", "color": "#222222", "ev": "E1",
                              "story": "s", "note": "n",
                              "steps": {"task": None, "input": "in-a", "dev": ["fw-b", "fw-c"], "run": "rt-a"},
                              "can": {"input": ["in-a"], "dev": ["fw-b", "fw-c"], "run": ["rt-a"]},
                              "implies": [], "targets": ["chip-b"], "papers": []}},
    "applications": {"task-a": {"prefer": ["fw-a-chip-a"], "via": {"input": "in-a"}, "note": "n"}},
    "notes": {"in-a": {"text": "t", "read": "#anchor-a"}},
    "unreached": {"chip-lonely": {"why": "No audited toolchain reaches it.", "read": "#anchor-a"}, "cpu-a": {"why": "w", "read": "#anchor-a"}},
}
ROUTE_INDEX_FIXTURE = {
    "nodes": [
        {"id": "task-a", "type": "application", "layer": "Applications", "name": "Task A"},
        {"id": "in-a", "type": "application", "layer": "Applications", "name": "In A"},
        {"id": "fw-a", "type": "framework", "layer": "Develop & simulate", "name": "FW A"},
        {"id": "fw-b", "type": "framework", "layer": "Develop & simulate", "name": "FW B"},
        {"id": "fw-c", "type": "framework", "layer": "Develop & simulate", "name": "FW C"},
        {"id": "rt-a", "type": "runtime", "layer": "Runtime", "name": "RT A"},
        {"id": "cpu-a", "type": "hardware", "layer": "Hardware", "name": "CPU A", "attributes": {"target_kind": "CPU"}},
        {"id": "chip-a", "type": "hardware", "layer": "Hardware", "name": "Chip A", "attributes": {"target_kind": "neuromorphic"}},
        {"id": "chip-lonely", "type": "hardware", "layer": "Hardware", "name": "Lonely", "attributes": {"target_kind": "neuromorphic"}},
        {"id": "chip-b", "type": "hardware", "layer": "Hardware", "name": "Chip B", "attributes": {"target_kind": "neuromorphic"}}],
    "routes": [
        {"id": "fw-a-to-rt-a", "from": "fw-a", "to": "rt-a", "route_state": "physical", "evidence_class": "E1", "source_ids": ["src-a"]},
        {"id": "fw-b-to-fw-c", "from": "fw-b", "to": "fw-c", "route_state": "physical", "evidence_class": "E1", "source_ids": ["src-a"]},
        {"id": "fw-c-to-rt-a", "from": "fw-c", "to": "rt-a", "route_state": "physical", "evidence_class": "E1", "source_ids": ["src-a"]},
        {"id": "rt-a-to-chip-a", "from": "rt-a", "to": "chip-a", "route_state": "physical", "evidence_class": "E1", "source_ids": ["src-a"]},
        {"id": "rt-a-to-chip-b", "from": "rt-a", "to": "chip-b", "route_state": "physical", "evidence_class": "E1", "source_ids": ["src-a"]}]}
PAPERS_FIXTURE = {"papers": [
    {"id": "paper-a", "title": "Paper A", "authors": "A", "year": 2025, "venue": "V", "url": "https://example.org/a",
     "evidence": "E1", "target_kind": "neuromorphic", "target_hardware": "Chip A", "sources": ["paper-a"]},
    {"id": "paper-b", "title": "Paper B", "authors": "B", "year": 2025, "venue": "V", "url": "https://example.org/b",
     "evidence": "E2", "target_kind": "neuromorphic", "target_hardware": "Chip A", "sources": ["paper-b"]}]}
KINDS_FIXTURE = {"kinds": [{"word": "CPU", "bucket": "conventional"}, {"word": "neuromorphic", "bucket": "neuromorphic"}, {"word": "simulator", "bucket": "simulated"}],
                 "buckets": [{"name": "conventional", "meaning": "c", "line": "#1F77B4", "fill": "#E4F0F9", "ink": "#123456"},
                             {"name": "simulated", "meaning": "s", "line": "#7F7F7F", "fill": "#EEEEEE", "ink": "#222222"},
                             {"name": "neuromorphic", "meaning": "n", "line": "#D9760C", "fill": "#FBEBDA", "ink": "#654321"}]}
CSS_FIXTURE = "".join(
    f'.nstk-bucket[data-bucket="{b["name"]}"] {{ --line: {b["line"]}; --fill: {b["fill"]}; --ink: {b["ink"]}; }}\n'
    for b in KINDS_FIXTURE["buckets"])


class FigureMapCheckerTests(unittest.TestCase):
    """tools/check-figure-map.py holds data/figure-guide.json to the route data."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "survey"
        for rel in ("tools", "data/generated", "assets", "site"):
            (self.root / rel).mkdir(parents=True)
        shutil.copy2(SOURCE_ROOT / "tools/check-figure-map.py", self.root / "tools/check-figure-map.py")
        self.guide = json.loads(json.dumps(GUIDE_FIXTURE))
        (self.root / "data/generated/route-index.json").write_text(json.dumps(ROUTE_INDEX_FIXTURE))
        (self.root / "data/evidence-papers.json").write_text(json.dumps(PAPERS_FIXTURE))
        (self.root / "data/target-kinds.json").write_text(json.dumps(KINDS_FIXTURE))
        (self.root / "assets/figure.css").write_text(CSS_FIXTURE)
        (self.root / "site/sec-x.html").write_text('<h3 id="anchor-a">A</h3>')

    def tearDown(self):
        self.temp.cleanup()

    def run_checker(self, *args):
        (self.root / "data/figure-guide.json").write_text(json.dumps(self.guide))
        return subprocess.run([sys.executable, str(self.root / "tools/check-figure-map.py"), *args],
                              cwd=self.root, text=True, capture_output=True, check=False)

    def assert_fails_with(self, fragment, *args):
        result = self.run_checker(*args)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(fragment, result.stdout + result.stderr)

    def test_fixture_passes(self):
        result = self.run_checker("--allow-unplaced-papers")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("check-figure-map:", result.stdout)

    def test_rule_1_chip_must_be_a_node(self):
        self.guide["layers"][0]["rows"][1]["chips"].append({"id": "ghost", "label": "Ghost"})
        self.assert_fails_with("rule 1: chip 'ghost' is not a node")

    def test_rule_1_hardware_chip_in_wrong_bucket(self):
        rows = self.guide["layers"][2]["rows"]
        rows[0]["chips"].append(rows[1]["chips"].pop(0))
        self.assert_fails_with("rule 1: hardware chip 'chip-a' sits in the 'conventional' row")

    def test_rule_1_css_bucket_color(self):
        (self.root / "assets/figure.css").write_text(CSS_FIXTURE.replace("#D9760C", "#000000"))
        self.assert_fails_with("rule 1: figure.css rule for [data-bucket=\"neuromorphic\"] lacks the bucket line color #D9760C")

    def test_rule_2_target_kind_matches_tk(self):
        self.guide["toolchains"]["fw-a-chip-a"]["tk"] = "CPU"
        self.assert_fails_with("rule 2: toolchain 'fw-a-chip-a' has tk 'CPU' but its target 'chip-a' records target_kind 'neuromorphic'")

    def test_rule_2_vendor_for_subset_of_targets(self):
        self.guide["toolchains"]["fw-a-chip-a"]["vendorFor"] = ["cpu-a"]
        self.assert_fails_with("rule 2: toolchain 'fw-a-chip-a' names vendorFor 'cpu-a' outside its targets")

    def test_rule_3_step_must_be_in_can(self):
        self.guide["toolchains"]["fw-a-chip-a"]["can"]["dev"] = []
        self.assert_fails_with("rule 3: toolchain 'fw-a-chip-a' step dev 'fw-a' is not in can.dev")

    def test_rule_3_chip_in_wrong_slot(self):
        self.guide["toolchains"]["fw-a-chip-a"]["can"]["dev"].append("rt-a")
        self.assert_fails_with("rule 3: toolchain 'fw-a-chip-a' names 'rt-a' under slot dev but it sits in slot run")

    def test_rule_3_list_valued_step_accepted_when_all_members_are_in_can(self):
        result = self.run_checker("--allow-unplaced-papers")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_rule_3_list_valued_step_member_must_be_in_can(self):
        self.guide["toolchains"]["multi-dev-chip-a"]["can"]["dev"] = ["fw-b"]
        self.assert_fails_with("rule 3: toolchain 'multi-dev-chip-a' step dev 'fw-c' is not in can.dev")

    def test_rule_3_after_chip_valid_passes(self):
        self.guide["toolchains"]["multi-dev-chip-a"]["after"] = ["fw-a"]
        result = self.run_checker("--allow-unplaced-papers")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_rule_3_after_chip_must_exist(self):
        self.guide["toolchains"]["multi-dev-chip-a"]["after"] = ["not-a-chip"]
        self.assert_fails_with("rule 3: toolchain 'multi-dev-chip-a' after names 'not-a-chip' which is not a chip on the map")

    def test_rule_3_after_chip_must_not_be_task_or_hw(self):
        self.guide["toolchains"]["multi-dev-chip-a"]["after"] = ["task-a"]
        self.assert_fails_with("rule 3: toolchain 'multi-dev-chip-a' after names 'task-a' which sits in slot task")

    def test_rule_4_missing_edge(self):
        self.guide["toolchains"]["fw-a-chip-a"]["targets"] = ["chip-lonely"]
        self.guide["toolchains"]["fw-a-chip-a"]["vendorFor"] = ["chip-lonely"]
        del self.guide["unreached"]["chip-lonely"]
        self.guide["unreached"]["chip-a"] = {"why": "w", "read": "#anchor-a"}
        self.guide["toolchains"]["fw-a-chip-a"]["papers"] = []
        self.assert_fails_with("rule 4: toolchain 'fw-a-chip-a' draws rt-a -> chip-lonely but no edge records it")

    def test_rule_4_missing_edge_between_list_valued_steps(self):
        ROUTE = json.loads(json.dumps(ROUTE_INDEX_FIXTURE))
        ROUTE["routes"] = [r for r in ROUTE["routes"] if not (r["from"] == "fw-b" and r["to"] == "fw-c")]
        (self.root / "data/generated/route-index.json").write_text(json.dumps(ROUTE))
        self.assert_fails_with("rule 4: toolchain 'multi-dev-chip-a' draws fw-b -> fw-c but no edge records it")

    def test_rule_4_break_must_not_be_physical(self):
        t = self.guide["toolchains"]["fw-a-chip-a"]
        t["breakAt"] = "rt-a"; t["breakWhy"] = "w"; t["seam"] = "S1"; t["ev"] = "BLOCKED"
        self.assert_fails_with("rule 4: toolchain 'fw-a-chip-a' breaks at 'rt-a' but the data records fw-a -> rt-a as exercised on silicon")

    def test_rule_4_seam_must_exist(self):
        t = self.guide["toolchains"]["fw-a-chip-a"]
        t["breakAt"] = "rt-a"; t["breakWhy"] = "w"; t["seam"] = "S9"; t["ev"] = "BLOCKED"
        ROUTE = json.loads(json.dumps(ROUTE_INDEX_FIXTURE)); ROUTE["routes"][0]["route_state"] = "documented"; ROUTE["routes"][0]["evidence_class"] = "E3"
        (self.root / "data/generated/route-index.json").write_text(json.dumps(ROUTE))
        self.assert_fails_with("rule 4: toolchain 'fw-a-chip-a' names seam 'S9' which is not a pin")

    def test_rule_5_paper_must_exist_with_matching_kind(self):
        self.guide["toolchains"]["fw-a-chip-a"]["papers"].append({"id": "paper-x", "via": {}})
        self.assert_fails_with("rule 5: toolchain 'fw-a-chip-a' lists paper 'paper-x' which is not an E1 or E2 record")

    def test_rule_5_via_must_be_carriable(self):
        self.guide["toolchains"]["fw-a-chip-a"]["papers"][0]["via"]["dev"] = "rt-a"
        self.assert_fails_with("rule 5: toolchain 'fw-a-chip-a' paper 'paper-a' via dev 'rt-a' is not in can.dev or implies")

    def test_rule_5b_every_deploying_record_is_placed_unless_allowed(self):
        self.assert_fails_with("rule 5b: E2 record 'paper-b' appears under no toolchain")
        self.assertEqual(self.run_checker("--allow-unplaced-papers").returncode, 0)

    def test_rule_6_application_prefer_and_via(self):
        self.guide["applications"]["task-a"]["prefer"].append("nope")
        self.assert_fails_with("rule 6: application 'task-a' prefers 'nope' which is not a toolchain")

    def test_rule_7_unreached_or_reachable(self):
        del self.guide["unreached"]["chip-lonely"]
        self.assert_fails_with("rule 7: chip 'chip-lonely' is reached by no toolchain and is not listed under unreached")

    def test_rule_7_reachable_chip_must_not_be_unreached(self):
        self.guide["unreached"]["chip-a"] = {"why": "w", "read": "#anchor-a"}
        self.assert_fails_with("rule 7: chip 'chip-a' is listed under unreached but toolchain 'fw-a-chip-a' reaches it")

    def test_rule_8_read_anchor_exists(self):
        self.guide["notes"]["in-a"]["read"] = "#nowhere"
        self.assert_fails_with("rule 8: read anchor '#nowhere' (notes in-a) is not an id in site/*.html")

    def test_rule_9_house_rules(self):
        self.guide["toolchains"]["fw-a-chip-a"]["story"] = "A story — with a dash"
        self.assert_fails_with("rule 9: toolchains.fw-a-chip-a.story contains an em dash")
        self.guide["toolchains"]["fw-a-chip-a"]["story"] = "A story: with a colon"
        self.assert_fails_with("rule 9: toolchains.fw-a-chip-a.story contains a prose colon")


if __name__ == "__main__":
    unittest.main(verbosity=2)
