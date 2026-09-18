#!/usr/bin/env python3
"""Verify canonical bibliography generation and citation-key coverage."""
from __future__ import annotations

import json
import re
import runpy
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
EXPECTED_REPORT = {
    "aliased": 0,
    "ambiguous": 0,
    "ambiguous_keys": [],
    "analysis_only": 3,
    "analysis_only_cited": 1,
    "analysis_only_ids": [
        "a14-application-survey",
        "a17-two-populations",
        "a18-sourcecode-comparison"
    ],
    "cited": 312,
    "cited_aliased": 0,
    "cited_keys": 312,
    "defined": 454,
    "duplicate": 0,
    "match_methods": {
        "registry": 312
    },
    "reference_keys": 0,
    "reference_only": 0,
    "reference_only_unresolved": 0,
    "uncited": 142,
    "unresolved": 0,
    "unresolved_cited": [],
    "unresolved_reference_only": []
}
EXPECTED_REFERENCE_ONLY_UNRESOLVED = set()
ENTRY = re.compile(r"@(\w+)\{([^,\s]+),\n(.*?)\n\}", re.S)
FIELD = re.compile(r"^  (\w+) = \{(.*)\},$", re.M)


def parse_generated_bib(text: str) -> tuple[list[str], dict[str, dict[str, str]]]:
    keys: list[str] = []
    entries: dict[str, dict[str, str]] = {}
    for entry_type, key, body in ENTRY.findall(text):
        keys.append(key)
        fields = {name: value for name, value in FIELD.findall(body)}
        fields["entry_type"] = entry_type
        entries[key] = fields
    return keys, entries


def decoded(value: str) -> str:
    if value.startswith("{") and value.endswith("}"):
        value = value[1:-1]
    return (
        value.replace(r"\%", "%")
        .replace(r"\_", "_")
        .replace(r"\#", "#")
        .replace(r"\&", "&")
    )


def fail(message: str) -> None:
    raise AssertionError(message)


def main() -> int:
    module = runpy.run_path(ROOT / "tools/build-bib.py")
    build_outputs = module.get("build_outputs")
    if not callable(build_outputs):
        fail("build-bib does not expose canonical build_outputs(root)")

    with tempfile.TemporaryDirectory() as temp_directory:
        fixture_root = Path(temp_directory)
        (fixture_root / "data").mkdir()
        (fixture_root / "site").mkdir()
        (fixture_root / "data/source-registry.json").write_text(
            json.dumps({
                "sources": [{
                    "id": "direct-source",
                    "canonical_key": "direct-source",
                    "aliases": ["legacy-source"],
                    "purpose": "external",
                    "source_type": "peer_reviewed",
                    "title": "Direct canonical citation fixture",
                    "authors": "A. Author",
                    "venue": "Fixture Journal",
                    "year": 2026,
                    "doi": None,
                    "url": None,
                }]
            })
        )
        (fixture_root / "site/sec-01.html").write_text(
            '<p><d-cite key="direct-source,legacy-source"></d-cite></p>\n'
        )
        try:
            _, direct_refmap, direct_report = build_outputs(fixture_root)
        except ValueError as error:
            fail(f"direct canonical and alias citations need no local identity list: {error}")
        if direct_refmap != {"legacy-source": "direct-source"}:
            fail("direct alias citation did not generate its canonical refmap entry")
        if direct_report["cited"] != 1 or direct_report["cited_keys"] != 2:
            fail("direct canonical citations did not resolve to one canonical work")

    table_module = runpy.run_path(ROOT / "tools/build-table1.py")
    build_table = table_module.get("build_table")
    if not callable(build_table):
        fail("build-table1 does not expose build_table(root)")
    table_citations = set(re.findall(r'<d-cite key="([^"]+)"></d-cite>', build_table(ROOT)))
    survey_ids = {
        record["source_id"]
        for record in json.loads((ROOT / "data/prior-survey-coverage.json").read_text())["surveys"]
    }
    if not survey_ids <= table_citations:
        fail("Table 1 does not cite every survey by its canonical source ID")

    bibliography, refmap, report = build_outputs(ROOT)
    if report != EXPECTED_REPORT:
        fail(f"bibliography report changed: {report}")

    committed_bib = (ROOT / "assets/bibliography/references.bib").read_text()
    committed_refmap = json.loads((ROOT / "data/refmap.json").read_text())
    committed_report = json.loads((ROOT / "data/bibliography-report.json").read_text())
    if bibliography != committed_bib or refmap != committed_refmap:
        fail("committed bibliography outputs differ from a fresh canonical build")
    if report != committed_report:
        fail("committed bibliography report differs from a fresh canonical build")

    registry = json.loads((ROOT / "data/source-registry.json").read_text())["sources"]
    sources = {str(source["id"]): source for source in registry}
    keys, entries = parse_generated_bib(bibliography)
    duplicate_count = len(keys) - len(set(keys))
    if duplicate_count != 0 or set(keys) != set(sources):
        fail("BibTeX definitions are not one-to-one with canonical source IDs")

    for source_id, source in sources.items():
        entry = entries[source_id]
        required = {
            "title": source["title"],
            "author": source["authors"],
            "year": str(source["year"]) if source["year"] is not None else None,
            "doi": source["doi"],
            "url": source["url"],
        }
        venue_field = "journal" if source["source_type"] == "peer_reviewed" else "howpublished"
        required[venue_field] = source["venue"]
        for field, expected in required.items():
            actual = entry.get(field)
            if expected is None:
                if actual is not None:
                    fail(f"{source_id} fabricated null canonical field {field}")
            elif actual is None or decoded(actual) != str(expected):
                fail(
                    f"{source_id} BibTeX field {field} does not equal canonical metadata"
                )
        is_analysis = source["purpose"] == "internal_analysis"
        analysis_label = entry.get("note") == (
            "Internal analysis. Not an external publication."
        )
        if is_analysis != analysis_label:
            fail(f"{source_id} has an incorrect analysis-only BibTeX label")

    canonical_ids = set(sources)
    if not all(key != value and value in canonical_ids for key, value in refmap.items()):
        fail("refmap contains a self-map or noncanonical target")
    if len(refmap) != EXPECTED_REPORT["aliased"]:
        fail("refmap does not contain every resolved legacy alias")

    unresolved_reference_only = set(report.get("unresolved_reference_only", []))
    if unresolved_reference_only != EXPECTED_REFERENCE_ONLY_UNRESOLVED:
        fail(
            "the uncited unresolved reference-only keys were not reported exactly"
        )

    with tempfile.TemporaryDirectory() as temp_directory:
        fixture_root = Path(temp_directory)
        (fixture_root / "data").mkdir()
        (fixture_root / "site").mkdir()
        (fixture_root / "assets/bibliography").mkdir(parents=True)
        (fixture_root / "data/source-registry.json").write_text(
            (ROOT / "data/source-registry.json").read_text()
        )
        for fragment in sorted((ROOT / "site").glob("sec-*.html")):
            (fixture_root / "site" / fragment.name).write_text(fragment.read_text())
        (fixture_root / "assets/bibliography/references.bib").write_text(
            "@misc{poisoned-legacy-authority, title={Must not be consumed}}\n"
        )
        (fixture_root / "data/refmap.json").write_text(
            json.dumps({"poisoned": "legacy-authority"})
        )
        isolated_bib, isolated_refmap, isolated_report = build_outputs(fixture_root)
        if (isolated_bib, isolated_refmap, isolated_report) != (
            bibliography,
            refmap,
            report,
        ):
            fail("legacy BibTeX or refmap content still influences canonical generation")

        broken_registry = json.loads(
            (fixture_root / "data/source-registry.json").read_text()
        )
        broken_registry["sources"][0].pop("purpose")
        (fixture_root / "data/source-registry.json").write_text(
            json.dumps(broken_registry)
        )
        try:
            build_outputs(fixture_root)
        except ValueError as error:
            if "purpose" not in str(error):
                fail(f"unlabeled registry rejection named the wrong cause: {error}")
        else:
            fail("an unlabeled canonical record was accepted")

    print(
        "check-bibliography: PASS "
        f"(defined={report['defined']}, cited={report['cited']} works/"
        f"{report['cited_keys']} keys, uncited={report['uncited']}, "
        f"aliased={report['aliased']}, unresolved={report['unresolved']}, "
        f"duplicate={report['duplicate']}, analysis-only={report['analysis_only']}; "
        f"reference-only unresolved={report['reference_only_unresolved']})"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, KeyError, OSError, TypeError, ValueError) as error:
        print(f"check-bibliography: FAILED: {error}", file=sys.stderr)
        raise SystemExit(1)
