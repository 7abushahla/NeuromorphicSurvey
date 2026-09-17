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


if __name__ == "__main__":
    unittest.main()
