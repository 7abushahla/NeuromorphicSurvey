#!/usr/bin/env python3
"""Regression tests for section and table renumbering and the reference guard."""
import json, re, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"


def fixture(tmp: Path) -> Path:
    site = tmp / "site"; data = tmp / "data"; tools = tmp / "tools"
    site.mkdir(); data.mkdir(); tools.mkdir(); (site / "figures").mkdir(); (tmp / "assets").mkdir(); (tmp / "research/rewrite").mkdir(parents=True)
    (site / "shell-head.html").write_text("<html><body>")
    (site / "sec-01.html").write_text('<h2 id="intro">1 Introduction</h2><p>See <a href="#routes">Section 2, Routes,</a> and <a href="#routes-named">Section 2.1</a>. Table 1 and Table 2.</p>\n<div class="ptable-wrap" id="table-a"><table><caption><b>Table 1:</b> A.</caption></table></div>')
    (site / "sec-02.html").write_text('<h2 id="routes">2 Routes</h2><h3 id="routes-named">2.1 Named</h3><p>Back to <a href="#intro">Section 1</a>. Tables 1 and 2 and Sections 1 and 2.</p>\n<div class="ptable-wrap" id="table-b"><table><caption><b>Table 2:</b> B.</caption></table></div>')
    (site / "shell-tail.html").write_text("</body></html>")
    (site / "figures" / "x.html").write_text('<figure id="figure-1"><figcaption>see Section 2.1</figcaption></figure>')
    (tmp / "assets/figure.js").write_text("const NOTE = 'Section 2 and Section 2.1';")
    (tmp / "research/rewrite/section-map.md").write_text("| 1. Introduction | `intro` | | |\n| 2. Routes | `routes` | | |\n")
    (data / "site-manifest.json").write_text(json.dumps({"schema_version": 1, "fragments": [
        {"id": "shell-head", "kind": "shell", "fragment": "site/shell-head.html"},
        {"id": "section-01-introduction", "kind": "section", "display_number": 1, "title": "Introduction", "fragment": "site/sec-01.html"},
        {"id": "section-02-where", "kind": "section", "display_number": 2, "title": "Where", "fragment": "site/sec-02.html"},
        {"id": "section-02-routes", "kind": "section", "display_number": 2, "title": "Routes", "fragment": "site/sec-02.html"},
        {"id": "shell-tail", "kind": "shell", "fragment": "site/shell-tail.html"}]}))
    (site / "sec-new.html").write_text('<h2 id="where">2 Where</h2>')
    (data / "figure-manifest.json").write_text(json.dumps({"schema_version": 1, "figures": [
        {"id": "x", "display_number": 1, "fragment": "site/figures/x.html", "css": "site/figures/x.css", "destination_section": "section-02-routes", "concept": "", "question": "", "interactive": False, "status": "implemented"}]}))
    subprocess.run(["git", "init", "-q"], cwd=tmp, check=True); subprocess.run(["git", "add", "-A"], cwd=tmp, check=True)
    subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "fixture"], cwd=tmp, check=True)
    for name in ("renumber-sections.py", "renumber-tables.py", "check-section-refs.py"):
        shutil.copy(TOOLS / name, tools / name)
    return tmp


class RenumberSectionsTests(unittest.TestCase):
    def test_insert_shifts_everything(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = fixture(Path(d))
            out = subprocess.run([sys.executable, "tools/renumber-sections.py", "--apply", "--new-fragment", "site/sec-new.html"], cwd=tmp, capture_output=True, text=True)
            self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
            self.assertEqual((tmp / "site/sec-02.html").read_text(), '<h2 id="where">2 Where</h2>')
            self.assertFalse((tmp / "site/sec-new.html").exists())
            manifest = json.loads((tmp / "data/site-manifest.json").read_text())
            self.assertEqual([f.get("display_number") for f in manifest["fragments"]], [None, 1, 2, 3, None])
            self.assertEqual(manifest["fragments"][3]["id"], "section-03-routes")
            self.assertEqual(manifest["fragments"][3]["fragment"], "site/sec-03.html")
            self.assertEqual(manifest["fragments"][2]["fragment"], "site/sec-02.html")
            routes = (tmp / "site/sec-03.html").read_text()
            self.assertIn('<h2 id="routes">3 Routes</h2>', routes); self.assertIn('<h3 id="routes-named">3.1 Named</h3>', routes)
            self.assertIn("Sections 1 and 3", routes)
            intro = (tmp / "site/sec-01.html").read_text()
            self.assertIn("Section 3, Routes,", intro); self.assertIn("Section 3.1</a>", intro)
            self.assertIn("see Section 3.1", (tmp / "site/figures/x.html").read_text())
            self.assertIn("Section 3 and Section 3.1", (tmp / "assets/figure.js").read_text())
            self.assertEqual(json.loads((tmp / "data/figure-manifest.json").read_text())["figures"][0]["destination_section"], "section-03-routes")
            self.assertIn("| 3. Routes |", (tmp / "research/rewrite/section-map.md").read_text())

    def test_sentence_final_and_split_plural_tokens(self):
        # Regression for the two regex defects found on the real corpus: a "Section N." at the end
        # of a sentence, and a "Sections A ... B" list wrapped across a line break or split across
        # two anchor tags, must all be renumbered.
        with tempfile.TemporaryDirectory() as d:
            tmp = fixture(Path(d))
            (tmp / "site/sec-01.html").write_text(
                '<h2 id="intro">1 Introduction</h2><p>Treated in Section 2. Also Sections 1\nthrough 2, '
                'and <a href="#intro">Sections 1</a> and <a href="#routes">2</a>. A random 2 stays.</p>')
            subprocess.run(["git", "add", "-A"], cwd=tmp, check=True)
            subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "edge"], cwd=tmp, check=True)
            out = subprocess.run([sys.executable, "tools/renumber-sections.py", "--apply", "--new-fragment", "site/sec-new.html"], cwd=tmp, capture_output=True, text=True)
            self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
            intro = (tmp / "site/sec-01.html").read_text()
            self.assertIn("Treated in Section 3.", intro)
            self.assertIn("Sections 1\nthrough 3,", intro)
            self.assertIn('<a href="#intro">Sections 1</a> and <a href="#routes">3</a>', intro)
            self.assertIn("A random 2 stays.", intro)

    def test_dry_run_changes_nothing(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = fixture(Path(d))
            before = (tmp / "site/sec-02.html").read_text()
            subprocess.run([sys.executable, "tools/renumber-sections.py", "--new-fragment", "site/sec-new.html"], cwd=tmp, check=True, capture_output=True)
            self.assertEqual((tmp / "site/sec-02.html").read_text(), before)


class RenumberTablesTests(unittest.TestCase):
    def test_reading_order_mapping(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = fixture(Path(d))
            subprocess.run([sys.executable, "tools/renumber-sections.py", "--apply", "--new-fragment", "site/sec-new.html"], cwd=tmp, check=True, capture_output=True)
            (tmp / "site/sec-02.html").write_text('<h2 id="where">2 Where</h2><div class="ptable-wrap" id="table-w"><table><caption><b>Table 9:</b> W.</caption></table></div>')
            subprocess.run([sys.executable, "tools/renumber-tables.py", "--apply"], cwd=tmp, check=True, capture_output=True)
            self.assertIn("<b>Table 2:</b> W.", (tmp / "site/sec-02.html").read_text())
            self.assertIn("<b>Table 3:</b> B.", (tmp / "site/sec-03.html").read_text())
            self.assertIn("Tables 1 and 3", (tmp / "site/sec-03.html").read_text())
            self.assertIn("Table 1 and Table 3.", (tmp / "site/sec-01.html").read_text())


class SectionRefsTests(unittest.TestCase):
    def test_guard_catches_a_stale_token(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = fixture(Path(d))
            subprocess.run([sys.executable, "tools/renumber-sections.py", "--apply", "--new-fragment", "site/sec-new.html"], cwd=tmp, check=True, capture_output=True)
            page = "".join((tmp / "site" / f).read_text() for f in ("shell-head.html", "sec-01.html", "sec-02.html", "sec-03.html", "shell-tail.html"))
            (tmp / "index.html").write_text(page)
            ok = subprocess.run([sys.executable, "tools/check-section-refs.py"], cwd=tmp, capture_output=True, text=True)
            self.assertEqual(ok.returncode, 0, ok.stdout + ok.stderr)
            (tmp / "index.html").write_text(page.replace('<a href="#routes">Section 3, Routes,</a>', '<a href="#routes">Section 2, Routes,</a>'))
            bad = subprocess.run([sys.executable, "tools/check-section-refs.py"], cwd=tmp, capture_output=True, text=True)
            self.assertNotEqual(bad.returncode, 0); self.assertIn("routes", bad.stdout + bad.stderr)

    def test_guard_accepts_a_section_token_on_a_subsection_anchor(self):
        # A "Section N" token may deep-link a subsection anchor whose heading is N.M (the survey's
        # own prose does this); a token naming a different section on that anchor still fails.
        with tempfile.TemporaryDirectory() as d:
            tmp = fixture(Path(d))
            subprocess.run([sys.executable, "tools/renumber-sections.py", "--apply", "--new-fragment", "site/sec-new.html"], cwd=tmp, check=True, capture_output=True)
            page = "".join((tmp / "site" / f).read_text() for f in ("shell-head.html", "sec-01.html", "sec-02.html", "sec-03.html", "shell-tail.html"))
            (tmp / "index.html").write_text(page.replace('<a href="#routes-named">Section 3.1</a>', '<a href="#routes-named">Section 3</a>'))
            ok = subprocess.run([sys.executable, "tools/check-section-refs.py"], cwd=tmp, capture_output=True, text=True)
            self.assertEqual(ok.returncode, 0, ok.stdout + ok.stderr)
            (tmp / "index.html").write_text(page.replace('<a href="#routes-named">Section 3.1</a>', '<a href="#routes-named">Section 1</a>'))
            bad = subprocess.run([sys.executable, "tools/check-section-refs.py"], cwd=tmp, capture_output=True, text=True)
            self.assertNotEqual(bad.returncode, 0)


if __name__ == "__main__":
    unittest.main()
