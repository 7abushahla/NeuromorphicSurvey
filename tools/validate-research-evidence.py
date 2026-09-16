#!/usr/bin/env python3
"""Validate integrated paper, graph, audit, and registry evidence contracts."""
from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
RETRIEVAL_STATES = {"full_text", "partial_text", "metadata_only", "not_retrieved"}
VERIFICATION_STATES = {"verified", "provisional", "conflicted", "rejected"}
BRIDGE_FIELDS = {"mechanism", "preserves", "breaks", "evidence", "sources"}


def load(path: Path) -> object:
    return json.loads(path.read_text())


def rows_by_id(rows: object, label: str, errors: list[str]) -> dict[str, dict[str, object]]:
    if not isinstance(rows, list):
        errors.append(f"{label} must be an array")
        return {}
    result: dict[str, dict[str, object]] = {}
    for index, row in enumerate(rows):
        if not isinstance(row, dict) or not isinstance(row.get("id"), str):
            errors.append(f"{label}[{index}] must be an object with a string id")
            continue
        row_id = str(row["id"])
        if row_id in result:
            errors.append(f"{label} contains duplicate id {row_id!r}")
        result[row_id] = row
    return result


def validate_source_refs(
    refs: object, label: str, registry_ids: set[str], errors: list[str]
) -> None:
    if not isinstance(refs, list) or not refs:
        errors.append(f"{label} source_refs must be a nonempty array")
        return
    seen: set[str] = set()
    expected = {"source_id", "locators", "retrieval_status", "verification_status"}
    for index, ref in enumerate(refs):
        ref_label = f"{label}.source_refs[{index}]"
        if not isinstance(ref, dict) or set(ref) != expected:
            errors.append(f"{ref_label} must contain exactly {sorted(expected)}")
            continue
        source_id = ref["source_id"]
        if not isinstance(source_id, str) or source_id not in registry_ids:
            errors.append(f"{ref_label} has unresolved source_id {source_id!r}")
        elif source_id in seen:
            errors.append(f"{label} repeats source_id {source_id!r}")
        else:
            seen.add(source_id)
        locators = ref["locators"]
        if not isinstance(locators, list) or not locators or not all(
            isinstance(locator, str) and locator.strip() for locator in locators
        ):
            errors.append(f"{ref_label}.locators must contain nonempty strings")
        if ref["retrieval_status"] not in RETRIEVAL_STATES:
            errors.append(f"{ref_label} has invalid retrieval_status")
        if ref["verification_status"] not in VERIFICATION_STATES:
            errors.append(f"{ref_label} has invalid verification_status")


def validate_documents(
    papers: object,
    stack: object,
    registry: object,
    claims: object,
    audits: dict[str, object],
) -> list[str]:
    errors: list[str] = []
    if not all(isinstance(document, dict) for document in (papers, stack, registry, claims)):
        return ["paper, stack, registry, and claim documents must be objects"]
    registry_rows = rows_by_id(registry.get("sources"), "registry.sources", errors)
    registry_ids = set(registry_rows)
    canonical_claims = rows_by_id(claims.get("claims"), "claims.claims", errors)

    for document, records_key, label in (
        (papers, "papers", "evidence-papers"),
        (stack, "nodes", "evidence-stack.nodes"),
        (stack, "edges", "evidence-stack.edges"),
    ):
        local_sources = rows_by_id(document.get("sources"), f"{label}.sources", errors)
        records = document.get(records_key)
        if not isinstance(records, list):
            errors.append(f"{label} must be an array")
            continue
        for index, record in enumerate(records):
            if not isinstance(record, dict):
                errors.append(f"{label}[{index}] must be an object")
                continue
            sources = record.get("sources")
            if not isinstance(sources, list) or not all(isinstance(item, str) for item in sources):
                errors.append(f"{label}[{index}].sources must be an array of strings")
                continue
            for source_id in sources:
                if source_id not in local_sources:
                    errors.append(
                        f"{label} record {record.get('id')!r} has unresolved local "
                        f"source {source_id!r}"
                    )

    nodes = rows_by_id(stack.get("nodes"), "evidence-stack.nodes", errors)
    edges = stack.get("edges")
    if isinstance(edges, list):
        for index, edge in enumerate(edges):
            if not isinstance(edge, dict):
                continue
            for endpoint in ("from", "to"):
                if edge.get(endpoint) not in nodes:
                    errors.append(
                        f"evidence-stack.edges[{index}] has unresolved {endpoint} "
                        f"endpoint {edge.get(endpoint)!r}"
                    )
            missing_bridge = sorted(BRIDGE_FIELDS - edge.keys())
            if missing_bridge:
                errors.append(
                    f"evidence-stack edge {edge.get('id')!r} lacks bridge fields "
                    f"{missing_bridge}"
                )
            if str(edge.get("id", "")).startswith("audit-b-"):
                for rich_field in (
                    "typed_input", "typed_output", "preserved", "transformed",
                    "rejected", "capability_class", "route_state", "source_refs",
                ):
                    if rich_field not in edge:
                        errors.append(
                            f"Audit B edge {edge.get('id')!r} lacks rich field "
                            f"{rich_field!r}"
                        )
                validate_source_refs(
                    edge.get("source_refs"), f"edge {edge.get('id')!r}", registry_ids, errors
                )
                ref_ids = [
                    ref.get("source_id") for ref in edge.get("source_refs", [])
                    if isinstance(ref, dict)
                ]
                if edge.get("sources") != ref_ids:
                    errors.append(
                        f"Audit B edge {edge.get('id')!r} sources do not bridge source_refs"
                    )

    seen_audit_claims: set[str] = set()
    for audit_name, audit in sorted(audits.items()):
        if not isinstance(audit, dict) or not isinstance(audit.get("claims"), list):
            errors.append(f"{audit_name} must contain a claims array")
            continue
        for index, claim in enumerate(audit["claims"]):
            label = f"{audit_name}.claims[{index}]"
            if not isinstance(claim, dict):
                errors.append(f"{label} must be an object")
                continue
            claim_id = claim.get("id")
            if claim_id not in canonical_claims:
                errors.append(f"{label} has orphan claim id {claim_id!r}")
            elif claim_id in seen_audit_claims:
                errors.append(f"audit claim id {claim_id!r} is duplicated across audits")
            else:
                seen_audit_claims.add(str(claim_id))
            if "source_ids" in claim or "locators" in claim:
                errors.append(f"{label} retains claim-wide source_ids or locators")
            validate_source_refs(claim.get("source_refs"), label, registry_ids, errors)
        routes = audit.get("route_edges", [])
        if not isinstance(routes, list):
            errors.append(f"{audit_name}.route_edges must be an array")
        else:
            for index, edge in enumerate(routes):
                label = f"{audit_name}.route_edges[{index}]"
                if not isinstance(edge, dict):
                    errors.append(f"{label} must be an object")
                    continue
                if "source_ids" in edge or "locators" in edge:
                    errors.append(f"{label} retains route-wide source_ids or locators")
                validate_source_refs(edge.get("source_refs"), label, registry_ids, errors)

    arfa = registry_rows.get("arfa2025-spiking-q-spinnaker2", {})
    if arfa.get("title") != (
        "Hardware-Aware Fine-Tuning of Spiking Q-Networks on the SpiNNaker2 "
        "Neuromorphic Platform"
    ) or str(arfa.get("doi", "")).lower() != "10.1109/icons69015.2025.00021":
        errors.append("Arfa source must retain the exact title and DOI ending in .00021")
    return errors


def main() -> int:
    audits = {
        path.name: load(path)
        for path in sorted((ROOT / "research/claim-audits").glob("audit-*.json"))
    }
    errors = validate_documents(
        load(ROOT / "data/evidence-papers.json"),
        load(ROOT / "data/evidence-stack.json"),
        load(ROOT / "data/source-registry.json"),
        load(ROOT / "data/claims.json"),
        audits,
    )
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("Research evidence validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
