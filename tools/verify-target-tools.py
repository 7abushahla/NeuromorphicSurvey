#!/usr/bin/env python3
"""Regression tests for the target vocabulary and its consumers."""
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KINDS = json.loads((ROOT / "data/target-kinds.json").read_text())
WORDS = {k["word"] for k in KINDS["kinds"]}
BUCKETS = {b["name"] for b in KINDS["buckets"]}


class VocabularyTests(unittest.TestCase):
    def test_nine_words_three_buckets(self):
        self.assertEqual(WORDS, {"CPU", "GPU", "MCU", "RISC-V", "NPU", "event NPU", "simulator", "neuromorphic", "FPGA"})
        self.assertEqual(BUCKETS, {"conventional", "simulated", "neuromorphic"})
        for kind in KINDS["kinds"]:
            self.assertIn(kind["bucket"], BUCKETS)
            self.assertEqual(kind["css"], "tk-" + kind["word"].lower().replace(" ", "-"))

    def test_event_npu_is_conventional_and_akida_carries_it(self):
        event_npu = next(k for k in KINDS["kinds"] if k["word"] == "event NPU")
        self.assertEqual(event_npu["bucket"], "conventional")
        nodes = json.loads((ROOT / "data/evidence-stack.json").read_text())["nodes"]
        akida = next(n for n in nodes if n["id"] == "akida")
        self.assertEqual(akida["attributes"]["target_kind"], "event NPU")

    def test_every_evidence_paper_has_a_target_kind(self):
        papers = json.loads((ROOT / "data/evidence-papers.json").read_text())["papers"]
        for paper in papers:
            self.assertIn(paper.get("target_kind"), WORDS | {"none"}, paper["id"])
            self.assertIsInstance(paper.get("target_qualifier"), str, paper["id"])
            if paper["target_kind"] == "none":
                self.assertEqual(paper["evidence"], "E5", paper["id"])

    def test_every_hardware_node_has_a_target_kind(self):
        nodes = json.loads((ROOT / "data/evidence-stack.json").read_text())["nodes"]
        for node in nodes:
            if node.get("type") == "hardware":
                self.assertIn(node.get("attributes", {}).get("target_kind"), WORDS, node["id"])

    def test_check_consistency_rejects_a_bad_kind(self):
        import tempfile, shutil
        with tempfile.TemporaryDirectory() as tmp:
            copy = Path(tmp) / "survey"
            shutil.copytree(ROOT, copy, ignore=shutil.ignore_patterns("index.html", "__pycache__", "research", "assets", ".git", "raw"))
            path = copy / "data/evidence-papers.json"
            doc = json.loads(path.read_text())
            doc["papers"][0]["target_kind"] = "abacus"
            path.write_text(json.dumps(doc))
            result = subprocess.run([sys.executable, str(copy / "tools/check-consistency.py")], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("target_kind", result.stdout + result.stderr)

    def test_chip_css_present_once(self):
        head = (ROOT / "site/shell-head.html").read_text()
        for kind in KINDS["kinds"]:
            self.assertEqual(head.count("." + kind["css"] + " {"), 1, kind["css"])


class CoverageTargetsTests(unittest.TestCase):
    def test_every_survey_has_targets(self):
        surveys = json.loads((ROOT / "data/prior-survey-coverage.json").read_text())["surveys"]
        self.assertEqual(len(surveys), 37)
        for survey in surveys:
            targets = survey.get("targets")
            self.assertIsInstance(targets, dict, survey["id"])
            self.assertIsInstance(targets.get("kinds"), list, survey["id"])
            self.assertTrue(set(targets["kinds"]) <= WORDS, survey["id"])
            self.assertEqual(len(targets["kinds"]), len(set(targets["kinds"])), survey["id"])
            self.assertTrue(targets.get("basis", "").strip(), survey["id"])
            self.assertTrue(targets.get("locator", "").strip(), survey["id"])

    def test_table1_renders_chip_cells(self):
        sys.path.insert(0, str(ROOT / "tools"))
        import importlib.util
        spec = importlib.util.spec_from_file_location("build_table1", ROOT / "tools/build-table1.py")
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        table = module.build_table(ROOT)
        self.assertIn('<th class="ctr" data-chip="Targets">Targets covered</th>', table)
        self.assertNotIn('data-chip="Hardware"', table)
        self.assertIn('<td class="hwcell">', table)
        self.assertIn('<span class="tk tk-gpu">GPU</span>', table)

    def test_targets_summary_view(self):
        view = json.loads((ROOT / "data/generated/prior-survey-targets-summary.json").read_text())
        self.assertEqual(view["view"], "prior-survey-targets-summary")
        self.assertEqual(view["survey_total"], 37)
        self.assertEqual(set(view["bucket_survey_counts"]), BUCKETS)
        self.assertIsInstance(view["surveys_covering_all_three_buckets"], int)


class FigureMapTests(unittest.TestCase):
    """The stack map (assets/figure.js) agrees with the route data and the target vocabulary."""

    def test_check_figure_map_passes(self):
        result = subprocess.run([sys.executable, str(ROOT / "tools/check-figure-map.py")], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("check-figure-map:", result.stdout)

    def test_five_conventional_routes_carry_a_chip_word(self):
        guide = json.loads((ROOT / "data/figure-guide.json").read_text())
        new = {"spikingjelly-gpu": "GPU", "mlgenn-gpu": "GPU", "nest-cpu": "CPU", "ttfs-cortex-m4": "MCU", "fenn-riscv": "RISC-V"}
        for tid, word in new.items():
            self.assertEqual(guide["toolchains"][tid]["tk"], word, tid)
        for tid, t in guide["toolchains"].items():
            self.assertIn(t["tk"], WORDS, tid)

    def test_hardware_rows_carry_the_three_buckets(self):
        guide = json.loads((ROOT / "data/figure-guide.json").read_text())
        hw = [L for L in guide["layers"] if L["id"] == "hw"][0]
        self.assertEqual({r["bucket"] for r in hw["rows"]}, BUCKETS)
        css = (ROOT / "assets/figure.css").read_text()
        for bucket in KINDS["buckets"]:
            self.assertIn(f'[data-bucket="{bucket["name"]}"]', css)
            self.assertIn(bucket["line"], css)

    def test_physical_routes_draw_through_their_runtime(self):
        guide = json.loads((ROOT / "data/figure-guide.json").read_text())
        expected = {
            "snntoolbox-spinnaker": (["snn-toolbox", "spynnaker", "spinnaker-runtime"], "spinnaker-1"),
            "quantizeml-akida": (["quantizeml", "cnn2snn", "akida-runtime"], "akida"),
            "rockpool-xylo": (["rockpool", "xylo-mapper", "samna"], "xylo"),
            "quartz-loihi": (["quartz", "nxsdk"], "loihi-1"),
        }
        edges = {(e["from"], e["to"]) for e in json.loads((ROOT / "data/evidence-stack.json").read_text())["edges"]}
        for tid, (sw, target) in expected.items():
            steps = guide["toolchains"][tid]["steps"]
            drawn = []
            for s in ("dev", "export", "compile", "run"):
                v = steps.get(s)
                drawn += v if isinstance(v, list) else ([v] if v else [])
            self.assertEqual(drawn, sw, tid)
            self.assertIn(target, guide["toolchains"][tid]["targets"], tid)
            for a, b in zip(drawn + [target], (drawn + [target])[1:]):
                self.assertIn((a, b), edges, f"{tid}: {a} -> {b}")

    def test_check_figure_map_rejects_a_chip_in_the_wrong_bucket(self):
        import tempfile, shutil
        with tempfile.TemporaryDirectory() as tmp:
            copy = Path(tmp) / "survey"
            shutil.copytree(ROOT, copy, ignore=shutil.ignore_patterns("index.html", "__pycache__", "research", ".git", "raw"))
            path = copy / "data/figure-guide.json"
            guide = json.loads(path.read_text())
            hw = [L for L in guide["layers"] if L["id"] == "hw"][0]
            rows = {r["bucket"] + "::" + r["label"]: r for r in hw["rows"]}
            sync = rows["neuromorphic::Synchronous digital"]; conv = rows["conventional::Conventional processors"]
            chip = [c for c in sync["chips"] if c["id"] == "loihi-2"][0]
            sync["chips"].remove(chip); conv["chips"].append(chip)
            path.write_text(json.dumps(guide))
            result = subprocess.run([sys.executable, str(copy / "tools/check-figure-map.py")], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("'loihi-2' sits in the 'conventional' row", result.stdout + result.stderr)


def fragment_holding(needle: str) -> Path:
    """The one site fragment whose text contains needle; sections move, the sentence does not."""
    hits = [p for p in sorted((ROOT / "site").glob("sec-*.html")) if needle in p.read_text()]
    assert len(hits) == 1, f"expected exactly one fragment holding {needle[:40]!r}, found {[h.name for h in hits]}"
    return hits[0]


class EvidenceMarkerCheckerTests(unittest.TestCase):
    def test_checker_catches_a_stripped_chip_and_passes_on_the_real_tree(self):
        import tempfile, shutil
        with tempfile.TemporaryDirectory() as tmp:
            copy = Path(tmp) / "survey"
            (copy / "site").mkdir(parents=True)
            (copy / "data").mkdir(parents=True)
            (copy / "tools").mkdir(parents=True)
            fragment = fragment_holding("CIFAR-10 EDP uses an estimated placement correction")
            shutil.copy(fragment, copy / "site" / fragment.name)
            shutil.copy(ROOT / "data/target-kinds.json", copy / "data/target-kinds.json")
            shutil.copy(ROOT / "data/evidence-papers.json", copy / "data/evidence-papers.json")
            shutil.copy(ROOT / "data/source-registry.json", copy / "data/source-registry.json")
            shutil.copy(ROOT / "data/refmap.json", copy / "data/refmap.json")
            shutil.copy(ROOT / "tools/check-evidence-markers.py", copy / "tools/check-evidence-markers.py")
            broken = (copy / "site" / fragment.name).read_text()
            # Strip the chip from the Quartz row specifically: it sits inside a <tr>, which the
            # checker's BLOCK regex (tr|li|p) scans directly in its first pass.
            quartz_old = '<td>Latency, static/dynamic power, energy per inference, EDP; CIFAR-10 EDP uses an estimated placement correction</td><td><span class="ev ev-e1">E1</span> <span class="tk tk-neuromorphic">neuromorphic</span></td></tr>'
            quartz_new = '<td>Latency, static/dynamic power, energy per inference, EDP; CIFAR-10 EDP uses an estimated placement correction</td><td><span class="ev ev-e1">E1</span></td></tr>'
            self.assertEqual(broken.count(quartz_old), 1, "expected exactly one Quartz row to strip a chip from")
            stripped = broken.replace(quartz_old, quartz_new, 1)
            self.assertNotEqual(broken, stripped)
            (copy / "site" / fragment.name).write_text(stripped)
            result = subprocess.run([sys.executable, str(copy / "tools/check-evidence-markers.py")], capture_output=True, text=True, cwd=copy)
            self.assertNotEqual(result.returncode, 0)

            real = subprocess.run([sys.executable, str(ROOT / "tools/check-evidence-markers.py")], capture_output=True, text=True, cwd=ROOT)
            self.assertEqual(real.returncode, 0, real.stdout + real.stderr)

    def test_checker_catches_a_stripped_chip_in_a_caveat_div(self):
        import tempfile, shutil
        with tempfile.TemporaryDirectory() as tmp:
            copy = Path(tmp) / "survey"
            (copy / "site").mkdir(parents=True)
            (copy / "data").mkdir(parents=True)
            (copy / "tools").mkdir(parents=True)
            fragment = fragment_holding("result for a baseline the QCFS paper itself never deployed")
            shutil.copy(fragment, copy / "site" / fragment.name)
            shutil.copy(ROOT / "data/target-kinds.json", copy / "data/target-kinds.json")
            shutil.copy(ROOT / "data/evidence-papers.json", copy / "data/evidence-papers.json")
            shutil.copy(ROOT / "data/source-registry.json", copy / "data/source-registry.json")
            shutil.copy(ROOT / "data/refmap.json", copy / "data/refmap.json")
            shutil.copy(ROOT / "tools/check-evidence-markers.py", copy / "tools/check-evidence-markers.py")
            broken = (copy / "site" / fragment.name).read_text()
            # This marker sits inside a bare <div class="caveat">, with no enclosing tr/li/p, the
            # case the checker's second scanning pass exists for.
            self.assertIn('<div class="caveat">', broken)
            caveat_old = 'an <span class="ev ev-e1">E1</span> <span class="tk tk-neuromorphic">neuromorphic</span> result for a baseline the QCFS paper itself never deployed'
            caveat_new = 'an <span class="ev ev-e1">E1</span> result for a baseline the QCFS paper itself never deployed'
            self.assertEqual(broken.count(caveat_old), 1, "expected exactly one caveat-div chip to strip")
            stripped = broken.replace(caveat_old, caveat_new, 1)
            self.assertNotEqual(broken, stripped)
            (copy / "site" / fragment.name).write_text(stripped)
            result = subprocess.run([sys.executable, str(copy / "tools/check-evidence-markers.py")], capture_output=True, text=True, cwd=copy)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("E1 marker without a target chip", result.stdout + result.stderr)

class PopulationSummaryTests(unittest.TestCase):
    """The evidence-population-summary view stays in lockstep with evidence-papers.json."""

    def test_record_total_matches_the_paper_count(self):
        view = json.loads((ROOT / "data/generated/evidence-population-summary.json").read_text())
        papers = json.loads((ROOT / "data/evidence-papers.json").read_text())["papers"]
        self.assertEqual(view["view"], "evidence-population-summary")
        self.assertEqual(view["record_total"], len(papers))

    def test_population_counts_match_check_counts(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("check_counts", ROOT / "tools/check-counts.py")
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        papers_document = json.loads((ROOT / "data/evidence-papers.json").read_text())
        expected, errors = module.population_counts(papers_document)
        self.assertEqual(errors, [])
        view = json.loads((ROOT / "data/generated/evidence-population-summary.json").read_text())
        self.assertEqual(view["population_counts"], expected)

    def test_family_rows_sum_to_the_total(self):
        view = json.loads((ROOT / "data/generated/evidence-population-summary.json").read_text())
        rows = view["family_population"]
        exclusive = view["population_counts"]["exclusive"]
        self.assertEqual(sum(row["algorithm"] for row in rows), exclusive["algorithm"])
        self.assertEqual(sum(row["deployment"] for row in rows), exclusive["deployment"])
        self.assertEqual(sum(row["both"] for row in rows), exclusive["both"])
        self.assertEqual(sum(row["total"] for row in rows), view["record_total"])
        for row in rows:
            self.assertEqual(row["total"], row["algorithm"] + row["deployment"] + row["both"], row["family"])

    def test_population_fragment_guard_finds_the_anchor_and_catches_a_stale_count(self):
        import importlib.util
        import tempfile
        spec = importlib.util.spec_from_file_location("check_counts_population", ROOT / "tools/check-counts.py")
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            (tmp / "site").mkdir(); (tmp / "data").mkdir()
            (tmp / "site/sec-a.html").write_text('<h2 id="a">1 A</h2><p>Nothing here.</p>')
            (tmp / "site/sec-b.html").write_text(
                '<h2 id="b">2 B</h2>\n'
                '<h3 id="population-counts">2.1 Population Counts</h3>\n'
                '<p>Each of its 4 records carry a population field.</p>\n'
                '<div class="ptable-wrap" id="table-population-counts"><table>'
                '<caption><b>Table 4:</b> counts.</caption>'
                '<tbody><tr><td><strong>Total</strong></td>'
                '<td class="ctr"><strong>1</strong></td>'
                '<td class="ctr"><strong>2</strong></td>'
                '<td class="ctr"><strong>1</strong></td>'
                '<td class="ctr"><strong>4</strong></td></tr></tbody></table></div>'
            )
            manifest = {"schema_version": 1, "fragments": [
                {"id": "section-01-a", "kind": "section", "display_number": 1, "title": "A", "fragment": "site/sec-a.html"},
                {"id": "section-02-b", "kind": "section", "display_number": 2, "title": "B", "fragment": "site/sec-b.html"},
            ]}
            manifest_path = tmp / "data/site-manifest.json"
            manifest_path.write_text(json.dumps(manifest))
            module.ROOT = tmp
            fragment_path = module.population_fragment(manifest_path)
            self.assertEqual(fragment_path, tmp / "site/sec-b.html")
            view = {"record_total": 4, "population_counts": {"exclusive": {"algorithm": 1, "deployment": 2, "both": 1}}}
            summary, errors = module.check_population_prose(fragment_path.read_text(), view, fragment_path.name)
            self.assertEqual(errors, [], errors)
            self.assertIn("sec-b.html", summary)
            bad_text = fragment_path.read_text().replace("Each of its 4 records", "Each of its 5 records")
            _, bad_errors = module.check_population_prose(bad_text, view, fragment_path.name)
            self.assertTrue(bad_errors)
            self.assertIn("sec-b.html", bad_errors[0])


if __name__ == "__main__":
    unittest.main()
