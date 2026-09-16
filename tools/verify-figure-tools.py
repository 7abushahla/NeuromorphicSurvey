#!/usr/bin/env python3
"""Regression tests for manifest-driven static figure tooling."""

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


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


if __name__ == "__main__":
    unittest.main(verbosity=2)
