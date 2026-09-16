#!/usr/bin/env python3
"""Verify integrated research-evidence contracts and regression identities."""
from __future__ import annotations

import json
import runpy
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
ARFA_ID = "arfa2025-spiking-q-spinnaker2"
ARFA_TITLE = (
    "Hardware-Aware Fine-Tuning of Spiking Q-Networks on the SpiNNaker2 "
    "Neuromorphic Platform"
)
ARFA_DOI = "10.1109/ICONS69015.2025.00021"


def load(path: Path) -> object:
    return json.loads(path.read_text())


def indexed(rows: object, label: str) -> dict[str, dict[str, object]]:
    if not isinstance(rows, list):
        raise AssertionError(f"{label} must be an array")
    result: dict[str, dict[str, object]] = {}
    for index, row in enumerate(rows):
        if not isinstance(row, dict) or not isinstance(row.get("id"), str):
            raise AssertionError(f"{label}[{index}] lacks a string id")
        row_id = str(row["id"])
        if row_id in result:
            raise AssertionError(f"{label} contains duplicate id {row_id!r}")
        result[row_id] = row
    return result


def main() -> int:
    papers = load(ROOT / "data/evidence-papers.json")
    stack = load(ROOT / "data/evidence-stack.json")
    registry = load(ROOT / "data/source-registry.json")
    claims = load(ROOT / "data/claims.json")
    if not all(isinstance(item, dict) for item in (papers, stack, registry, claims)):
        raise AssertionError("canonical evidence documents must contain objects")

    checks = 0
    registry_sources = indexed(registry["sources"], "source-registry.sources")
    arfa = registry_sources[ARFA_ID]
    if arfa.get("title") != ARFA_TITLE or str(arfa.get("doi", "")).lower() != ARFA_DOI.lower():
        raise AssertionError(
            "Arfa identity regression: expected exact title and DOI "
            f"{ARFA_DOI}, got {arfa.get('title')!r}, {arfa.get('doi')!r}"
        )
    checks += 1

    audits = {
        path.name: load(path)
        for path in sorted((ROOT / "research/claim-audits").glob("audit-*.json"))
    }
    validator = runpy.run_path(ROOT / "tools/validate-research-evidence.py")
    validate_documents = validator["validate_documents"]
    clean_errors = validate_documents(papers, stack, registry, claims, audits)
    if clean_errors:
        raise AssertionError(f"research validator rejected canonical fixtures: {clean_errors}")
    missing_node_stack = deepcopy(stack)
    missing_node_stack["nodes"] = [
        node for node in missing_node_stack["nodes"]
        if node["id"] != "spikingjelly-nir-exporter"
    ]
    if not any(
        "unresolved to endpoint 'spikingjelly-nir-exporter'" in error
        for error in validate_documents(
            papers, missing_node_stack, registry, claims, audits
        )
    ):
        raise AssertionError("validator accepted a graph edge with a missing endpoint")
    missing_source_papers = deepcopy(papers)
    missing_source_papers["sources"] = [
        source for source in missing_source_papers["sources"]
        if source["id"] != "arfa2025-spiking-q-spinnaker2"
    ]
    if not any(
        "unresolved local source 'arfa2025-spiking-q-spinnaker2'" in error
        for error in validate_documents(
            missing_source_papers, stack, registry, claims, audits
        )
    ):
        raise AssertionError("validator accepted a non-self-contained paper source table")
    malformed_audits = deepcopy(audits)
    first_audit = malformed_audits[sorted(malformed_audits)[0]]
    first_audit["claims"][0]["source_refs"][0].pop("verification_status")
    if not any(
        "must contain exactly" in error
        for error in validate_documents(papers, stack, registry, claims, malformed_audits)
    ):
        raise AssertionError("validator accepted a malformed source-specific audit ref")
    checks += 1

    for audit_path in sorted((ROOT / "research/claim-audits").glob("audit-*.json")):
        audit = load(audit_path)
        if not isinstance(audit, dict) or not isinstance(audit.get("claims"), list):
            raise AssertionError(f"{audit_path.name} lacks a claims array")
        for index, claim in enumerate(audit["claims"]):
            if not isinstance(claim, dict):
                raise AssertionError(f"{audit_path.name} claim {index} is not an object")
            if "source_ids" in claim or "locators" in claim:
                raise AssertionError(
                    f"{audit_path.name} claim {claim.get('id')!r} retains claim-wide "
                    "source_ids or locators"
                )
            refs = claim.get("source_refs")
            if not isinstance(refs, list) or not refs:
                raise AssertionError(
                    f"{audit_path.name} claim {claim.get('id')!r} lacks source_refs"
                )
            for ref in refs:
                if not isinstance(ref, dict) or set(ref) != {
                    "source_id", "locators", "retrieval_status", "verification_status"
                }:
                    raise AssertionError(
                        f"{audit_path.name} claim {claim.get('id')!r} has malformed "
                        f"source ref {ref!r}"
                    )
                if ref["source_id"] not in registry_sources:
                    raise AssertionError(
                        f"{audit_path.name} has unresolved source ref {ref['source_id']!r}"
                    )
                if not isinstance(ref["locators"], list) or not ref["locators"]:
                    raise AssertionError(
                        f"{audit_path.name} source {ref['source_id']!r} lacks locators"
                    )
    checks += 1

    for document, record_key, label in (
        (papers, "papers", "evidence-papers"),
        (stack, "nodes", "evidence-stack nodes"),
        (stack, "edges", "evidence-stack edges"),
    ):
        local_sources = indexed(document["sources"], f"{label}.sources")
        for record in document[record_key]:
            for source_id in record.get("sources", []):
                if source_id not in local_sources:
                    raise AssertionError(
                        f"{label} record {record.get('id')!r} has unresolved local "
                        f"source {source_id!r}"
                    )
    checks += 1

    node_ids = set(indexed(stack["nodes"], "evidence-stack.nodes"))
    for edge in stack["edges"]:
        for endpoint in ("from", "to"):
            if edge.get(endpoint) not in node_ids:
                raise AssertionError(
                    f"edge {edge.get('id')!r} has unresolved {endpoint} endpoint "
                    f"{edge.get(endpoint)!r}"
                )
        for bridge_field in ("mechanism", "preserves", "breaks", "evidence", "sources"):
            if bridge_field not in edge:
                raise AssertionError(
                    f"edge {edge.get('id')!r} lacks established bridge field "
                    f"{bridge_field!r}"
                )
    checks += 1

    paper_records = indexed(papers["papers"], "evidence-papers.papers")
    if paper_records["adaptive-fission"].get("family") != "population-coding":
        raise AssertionError("Adaptive Fission must be classified as population-coding")
    for source_id in ("mt-snn-withdrawn-iclr", "mt-snn-frontiers-2026"):
        if source_id not in indexed(papers["sources"], "evidence-papers.sources"):
            raise AssertionError(f"missing distinct MT-SNN source {source_id!r}")
    checks += 1

    claim_ids = set(indexed(claims["claims"], "claims.claims"))
    for audit_path in sorted((ROOT / "research/claim-audits").glob("audit-*.json")):
        audit = load(audit_path)
        for claim in audit["claims"]:
            if claim["id"] not in claim_ids:
                raise AssertionError(
                    f"{audit_path.name} has orphan claim id {claim['id']!r}"
                )
    checks += 1

    print(f"Research evidence regression checks passed ({checks} checks).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
