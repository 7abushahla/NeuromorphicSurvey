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


class ReorderSectionsTests(unittest.TestCase):
    def reorder_fixture(self, d):
        tmp = fixture(Path(d))
        # Three old sections: 1 Intro (1.1 a1, 1.2 a2), 2 Routes (2.1 b1), 3 Tail (3.1 c1). The plan
        # makes Tail the new 1, folds a2 into a1, and moves Routes' intro under a1 as new 2.
        (tmp / "site/sec-01.html").write_text('<h2 id="intro">1 Introduction</h2>\n\n<p>Intro para. See <a href="#tail">Section 3, Tail,</a> and <a href="#a2">Section 1.2</a>. Sections 1 and 2 together. Sections 2 and 3 apart.</p>\n\n<h3 id="a1">1.1 First</h3>\n\n<p>First body.</p>\n\n<h3 id="a2">1.2 Second</h3>\n\n<p>Second body cites Section 2.1.</p>\n')
        (tmp / "site/sec-02.html").write_text('<h2 id="routes">2 Routes</h2>\n\n<p>Routes intro.</p>\n\n<h3 id="b1">2.1 Named</h3>\n\n<p>Named body.</p>\n')
        (tmp / "site/sec-03.html").write_text('<h2 id="tail">3 Tail</h2>\n\n<h3 id="c1">3.1 Last</h3>\n\n<p>Last body, back to <a href="#intro">Section 1, Introduction,</a>.</p>\n')
        (tmp / "data/site-manifest.json").write_text(json.dumps({"schema_version": 1, "fragments": [
            {"id": "shell-head", "kind": "shell", "fragment": "site/shell-head.html"},
            {"id": "section-01-introduction", "kind": "section", "display_number": 1, "title": "Introduction", "fragment": "site/sec-01.html"},
            {"id": "section-02-routes", "kind": "section", "display_number": 2, "title": "Routes", "fragment": "site/sec-02.html"},
            {"id": "map", "kind": "interactive", "fragment": "site/shell-figure.html"},
            {"id": "section-03-tail", "kind": "section", "display_number": 3, "title": "Tail", "fragment": "site/sec-03.html"},
            {"id": "shell-tail", "kind": "shell", "fragment": "site/shell-tail.html"}]}))
        (tmp / "site/shell-figure.html").write_text('<figure><figcaption id="figure-1">map of Section 2</figcaption></figure>')
        (tmp / "data/figure-manifest.json").write_text(json.dumps({"schema_version": 1, "figures": [
            {"id": "x", "display_number": 1, "fragment": "site/figures/x.html", "css": "site/figures/x.css", "destination_section": "section-02-routes", "concept": "", "question": "", "interactive": False, "status": "implemented"}]}))
        (tmp / "data/evidence-stack.json").write_text('{"note": "see Section 3.1"}')
        (tmp / "data/section-reorder.json").write_text(json.dumps({"schema_version": 1, "map_after": "intro", "sections": [
            {"number": 1, "title": "Tail", "anchor": "tail", "intro_from": ["tail"], "subsections": [{"title": "Last", "from": ["c1"]}]},
            {"number": 2, "title": "Introduction and Routes", "anchor": "intro", "intro_from": ["intro"], "subsections": [
                {"title": "First and Second", "from": ["a1", "a2"]},
                {"title": "Named", "intro_from": ["routes"], "from": ["b1"]}]}]}))
        shutil.copy(TOOLS / "reorder-sections.py", tmp / "tools/reorder-sections.py")
        subprocess.run(["git", "add", "-A"], cwd=tmp, check=True)
        subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "reorder fixture"], cwd=tmp, check=True)
        return tmp

    def test_apply_rebuilds_fragments_tokens_anchors_and_manifests(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = self.reorder_fixture(d)
            out = subprocess.run([sys.executable, "tools/reorder-sections.py", "--apply"], cwd=tmp, capture_output=True, text=True)
            self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
            self.assertFalse((tmp / "site/sec-03.html").exists())
            one = (tmp / "site/sec-01.html").read_text(); two = (tmp / "site/sec-02.html").read_text()
            self.assertTrue(one.startswith('<h2 id="tail">1 Tail</h2>')); self.assertIn('<h3 id="c1">1.1 Last</h3>', one)
            self.assertIn('<a href="#intro">Section 2, Introduction and Routes,</a>', one)
            self.assertIn('<h3 id="a1">2.1 First and Second</h3>', two); self.assertIn('<span id="a2"></span>\n<p>Second body cites Section 2.2.</p>', two)
            self.assertIn('<h3 id="b1">2.2 Named</h3>\n\n<span id="routes"></span>\n<p>Routes intro.</p>', two)
            self.assertIn('<a href="#tail">Section 1, Tail,</a>', two); self.assertIn('<a href="#a1">Section 2.1</a>', two)
            self.assertIn("Sections 2 and 1 apart", two)
            self.assertNotIn('href="#routes"', two)  # no token pointed at the folded h2; the span keeps the id
            self.assertIn('<span id="routes"></span>', two)
            self.assertIn("COLLAPSED plural token", out.stdout); self.assertIn("Sections 1 and 2 together", two)
            self.assertIn("map of Section 2", (tmp / "site/shell-figure.html").read_text())
            self.assertIn("see Section 1.1", (tmp / "data/evidence-stack.json").read_text())
            sm = json.loads((tmp / "data/site-manifest.json").read_text())
            self.assertEqual([f["id"] for f in sm["fragments"]], ["shell-head", "section-01-tail", "section-02-introduction-and-routes", "map", "shell-tail"])
            self.assertEqual(sm["fragments"][2]["fragment"], "site/sec-02.html")
            self.assertEqual(json.loads((tmp / "data/figure-manifest.json").read_text())["figures"][0]["destination_section"], "section-02-introduction-and-routes")

    def test_dry_run_writes_nothing_and_unplaced_block_fails(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = self.reorder_fixture(d)
            before = (tmp / "site/sec-01.html").read_text()
            subprocess.run([sys.executable, "tools/reorder-sections.py"], cwd=tmp, check=True, capture_output=True)
            self.assertEqual((tmp / "site/sec-01.html").read_text(), before)
            plan = json.loads((tmp / "data/section-reorder.json").read_text()); plan["sections"][1]["subsections"][0]["from"] = ["a1"]
            (tmp / "data/section-reorder.json").write_text(json.dumps(plan))
            bad = subprocess.run([sys.executable, "tools/reorder-sections.py"], cwd=tmp, capture_output=True, text=True)
            self.assertNotEqual(bad.returncode, 0); self.assertIn("a2", bad.stdout + bad.stderr)

    def test_guard_rejects_content_before_h2(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = self.reorder_fixture(d)
            (tmp / "site/sec-01.html").write_text('stray leading text\n' + (tmp / "site/sec-01.html").read_text())
            bad = subprocess.run([sys.executable, "tools/reorder-sections.py"], cwd=tmp, capture_output=True, text=True)
            self.assertNotEqual(bad.returncode, 0)
            self.assertIn("content before the <h2> would be dropped", bad.stdout + bad.stderr)

    def test_dry_run_is_idempotent(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = self.reorder_fixture(d)
            before = {p.name: p.read_text() for p in (tmp / "site").glob("*.html")}
            first = subprocess.run([sys.executable, "tools/reorder-sections.py"], cwd=tmp, capture_output=True, text=True)
            second = subprocess.run([sys.executable, "tools/reorder-sections.py"], cwd=tmp, capture_output=True, text=True)
            self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
            self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
            self.assertEqual(first.stdout, second.stdout)
            after = {p.name: p.read_text() for p in (tmp / "site").glob("*.html")}
            self.assertEqual(before, after)

    def test_external_link_onto_folded_h2_retargets_to_new_section(self):
        # 'routes' is a folded old h2 (its intro opens the "Named" subsection of new section 2);
        # an external link into it, from unrelated prose, must retarget to the new section's own
        # h2 ('intro') and pick up the new section's title, not the subsection it landed in.
        with tempfile.TemporaryDirectory() as d:
            tmp = self.reorder_fixture(d)
            text = (tmp / "site/sec-01.html").read_text()
            text = text.replace(
                '<h3 id="a1">',
                '<p>External note, see <a href="#routes">Section 2, Routes,</a> for context.</p>\n\n<h3 id="a1">')
            (tmp / "site/sec-01.html").write_text(text)
            out = subprocess.run([sys.executable, "tools/reorder-sections.py", "--apply"], cwd=tmp, capture_output=True, text=True)
            self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
            two = (tmp / "site/sec-02.html").read_text()
            self.assertIn('<a href="#intro">Section 2, Introduction and Routes,</a>', two)

    def test_external_link_title_wraps_after_comma_still_retargets(self):
        # Same folded-h2 case, but the line break falls after the number's comma rather than
        # between the anchor tag and "Section" (the second wrapped shape found on the real tree).
        with tempfile.TemporaryDirectory() as d:
            tmp = self.reorder_fixture(d)
            text = (tmp / "site/sec-01.html").read_text()
            text = text.replace(
                '<h3 id="a1">',
                '<p>External note, see <a href="#routes">Section 2,\nRoutes,</a> for context.</p>\n\n<h3 id="a1">')
            (tmp / "site/sec-01.html").write_text(text)
            out = subprocess.run([sys.executable, "tools/reorder-sections.py", "--apply"], cwd=tmp, capture_output=True, text=True)
            self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
            two = (tmp / "site/sec-02.html").read_text()
            self.assertIn('<a href="#intro">Section 2, Introduction and Routes,</a>', two)

    def test_repeated_singular_collapse_is_reported_and_left_unrewritten(self):
        # Old sections 2 and 3 both fold into new section 1; a "Section 2 ... and Section 3 ..."
        # chain (repeated singular "Section", not the plural "Sections") must be caught the same
        # way a colliding "Sections A and B" token is: reported in COLLAPSED and left untouched.
        with tempfile.TemporaryDirectory() as d:
            tmp = fixture(Path(d))
            (tmp / "site/sec-01.html").write_text(
                '<h2 id="two">2 Two</h2>\n\n<p><a href="#a">Section 2</a> and <a href="#b">Section 3</a> collide.</p>\n')
            (tmp / "site/sec-02.html").write_text('<h2 id="three">3 Three</h2>\n\n<p>Three body.</p>\n')
            (tmp / "site/shell-figure.html").write_text('<div>no sections referenced</div>')
            (tmp / "data/evidence-stack.json").write_text('{}')
            (tmp / "data/site-manifest.json").write_text(json.dumps({"schema_version": 1, "fragments": [
                {"id": "shell-head", "kind": "shell", "fragment": "site/shell-head.html"},
                {"id": "section-02-two", "kind": "section", "display_number": 2, "title": "Two", "fragment": "site/sec-01.html"},
                {"id": "map", "kind": "interactive", "fragment": "site/shell-figure.html"},
                {"id": "section-03-three", "kind": "section", "display_number": 3, "title": "Three", "fragment": "site/sec-02.html"},
                {"id": "shell-tail", "kind": "shell", "fragment": "site/shell-tail.html"}]}))
            (tmp / "data/figure-manifest.json").write_text(json.dumps({"schema_version": 1, "figures": []}))
            (tmp / "data/section-reorder.json").write_text(json.dumps({"schema_version": 1, "map_after": "merged", "sections": [
                {"number": 1, "title": "Merged", "anchor": "merged", "intro_from": ["two", "three"], "subsections": []}]}))
            shutil.copy(TOOLS / "reorder-sections.py", tmp / "tools/reorder-sections.py")
            subprocess.run(["git", "add", "-A"], cwd=tmp, check=True)
            subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "singular collapse fixture"], cwd=tmp, check=True)
            out = subprocess.run([sys.executable, "tools/reorder-sections.py", "--apply"], cwd=tmp, capture_output=True, text=True)
            self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
            self.assertIn("COLLAPSED plural token", out.stdout)
            merged = (tmp / "site/sec-01.html").read_text()
            self.assertIn('<a href="#a">Section 2</a> and <a href="#b">Section 3</a> collide.', merged)


if __name__ == "__main__":
    unittest.main()
