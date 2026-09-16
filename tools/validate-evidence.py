#!/usr/bin/env python3
"""Validate canonical claim records and their source references."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
REQUIRED_FIELDS = {
    "id", "claim_type", "statement", "evidence_class", "reports_deployment_evidence",
    "source_ids", "locators", "verification_status", "measurement_boundary",
    "conflicts_with", "scope",
}
PLATFORM_REQUIRED_FIELDS = {
    "id", "platform_id", "manufacturer", "chip_generation", "contract_field",
    "contract_requirement", "capability_status", "support_detail", "mapper_limits",
    "precision_constraints", "routing_constraints", "host_responsibilities",
    "access_path", "route_ids", "route_state", "official_technical_source_id", "source_locator",
    "document_date", "document_version", "toolchain_version",
    "official_exercised_example_source_id", "official_exercised_example_locator",
    "verification_status", "reviewed_on",
}
OFFICIAL_TECHNICAL_SOURCE_TYPES = {
    "official_vendor_documentation",
    "official_manufacturer_documentation",
    "official_sdk_documentation",
    "official_devkit_manual",
    "official_repository",
    "official_model_zoo",
    "official_mapper_constraints",
    "official_release_note",
    "official_measured_example",
}
OFFICIAL_EXAMPLE_SOURCE_TYPES = {
    "official_devkit_manual",
    "official_repository",
    "official_sdk_documentation",
    "official_model_zoo",
    "official_measured_example",
}


def load_json(path: Path) -> object:
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"cannot read JSON from {path}: {error}") from error


def validate(schema: object, registry: object, claims_document: object) -> list[str]:
    errors: list[str] = []
    if not isinstance(schema, dict):
        return ["schema-version.json must contain an object"]
    if not isinstance(registry, dict) or not isinstance(registry.get("sources"), list):
        return ["source-registry.json must contain a sources array"]
    if not isinstance(claims_document, dict):
        return ["claims.json must contain an object"]
    if claims_document.get("schema_version") != schema.get("schema_version"):
        errors.append("claims schema_version does not match schema-version.json")
    claims = claims_document.get("claims")
    if not isinstance(claims, list):
        return errors + ["claims must be an array"]
    evidence_classes = schema.get("evidence_classes")
    verification_states = schema.get("verification_states")
    claim_types = schema.get("claim_types")
    if (
        not isinstance(evidence_classes, list)
        or not isinstance(verification_states, list)
        or not isinstance(claim_types, list)
    ):
        return errors + [
            "schema evidence_classes, verification_states, and claim_types must be arrays"
        ]
    source_ids = {source.get("id") for source in registry["sources"] if isinstance(source, dict)}
    claim_ids = {
        claim.get("id")
        for claim in claims
        if isinstance(claim, dict) and isinstance(claim.get("id"), str)
    }
    conflict_note_ids = {
        path.stem for path in (ROOT / "research/conflicts").glob("*.md")
    }
    ids: set[str] = set()
    for index, claim in enumerate(claims):
        label = f"claims[{index}]"
        if not isinstance(claim, dict):
            errors.append(f"{label}: record must be an object")
            continue
        missing = sorted(REQUIRED_FIELDS - claim.keys())
        if missing:
            errors.append(f"{label}: missing required field(s): {', '.join(missing)}")
            continue
        for field in ("id", "claim_type", "statement", "scope"):
            if not isinstance(claim[field], str) or not claim[field].strip():
                errors.append(f"{label}: {field} must be a nonempty string")
        claim_id = claim.get("id")
        if isinstance(claim_id, str):
            if claim_id in ids:
                errors.append(f"{label}: duplicate id {claim_id!r}")
            ids.add(claim_id)
        if not isinstance(claim["verification_status"], str) or claim["verification_status"] not in verification_states:
            errors.append(f"{label}: invalid verification_status {claim['verification_status']!r}")
        if not isinstance(claim["claim_type"], str) or claim["claim_type"] not in claim_types:
            errors.append(f"{label}: invalid claim_type {claim['claim_type']!r}")
        if not isinstance(claim["source_ids"], list) or not claim["source_ids"]:
            errors.append(f"{label}: source_ids must be a nonempty array")
        else:
            for source_id in claim["source_ids"]:
                if not isinstance(source_id, str) or source_id not in source_ids:
                    errors.append(f"{label}: unresolved source_id {source_id!r}")
        locators = claim["locators"]
        if (
            not isinstance(locators, list)
            or not all(isinstance(item, str) and item.strip() for item in locators)
        ):
            errors.append(f"{label}: locators must contain nonempty strings")
        conflicts = claim["conflicts_with"]
        if not isinstance(conflicts, list) or not all(
            isinstance(item, str) and item.strip() for item in conflicts
        ):
            errors.append(f"{label}: conflicts_with must contain nonempty strings")
        else:
            for conflict in conflicts:
                if conflict not in claim_ids and conflict not in conflict_note_ids:
                    errors.append(f"{label}: unresolved conflicts_with value {conflict!r}")
        boundary = claim["measurement_boundary"]
        if boundary is not None and (not isinstance(boundary, str) or not boundary.strip()):
            errors.append(f"{label}: measurement_boundary must be null or a nonempty string")
        reports_deployment_evidence = claim["reports_deployment_evidence"]
        if not isinstance(reports_deployment_evidence, bool):
            errors.append(f"{label}: reports_deployment_evidence must be a boolean")
        evidence_class = claim["evidence_class"]
        if reports_deployment_evidence is True:
            if not isinstance(evidence_class, str) or evidence_class not in evidence_classes:
                errors.append(f"{label}: deployment evidence requires an E1-E5 evidence_class")
            if boundary is None:
                errors.append(f"{label}: deployment evidence requires a measurement_boundary")
        elif reports_deployment_evidence is False and evidence_class is not None:
            errors.append(f"{label}: non-deployment claims require a null evidence_class")
        elif reports_deployment_evidence is not False and evidence_class is not None:
            errors.append(f"{label}: invalid evidence_class {evidence_class!r}")
    return errors


def valid_date(value: object) -> bool:
    if not isinstance(value, str):
        return False
    try:
        from datetime import date
        return date.fromisoformat(value).isoformat() == value
    except ValueError:
        return False


def validate_platform_capabilities(
    schema: object,
    registry: object,
    platform_document: object,
    evidence_stack: object,
) -> list[str]:
    errors: list[str] = []
    if not isinstance(schema, dict):
        return ["schema-version.json must contain an object"]
    if not isinstance(registry, dict) or not isinstance(registry.get("sources"), list):
        return ["source-registry.json must contain a sources array"]
    if not isinstance(platform_document, dict):
        return ["platform-capabilities.json must contain an object"]
    if platform_document.get("schema_version") != schema.get("schema_version"):
        errors.append("platform-capabilities schema_version does not match schema-version.json")
    records = platform_document.get("records")
    if not isinstance(records, list):
        return errors + ["platform-capabilities records must be an array"]
    verification_states = schema.get("verification_states")
    if not isinstance(verification_states, list):
        return errors + ["schema verification_states must be an array"]
    contract_fields = schema.get("deployable_contract_fields")
    if not isinstance(contract_fields, list) or not contract_fields:
        return errors + ["schema deployable_contract_fields must be a nonempty array"]
    platform_ids = schema.get("platform_capability_platforms")
    if not isinstance(platform_ids, list) or not platform_ids:
        return errors + ["schema platform_capability_platforms must be a nonempty array"]
    capability_statuses = schema.get("platform_capability_statuses")
    if not isinstance(capability_statuses, list) or not capability_statuses:
        return errors + ["schema platform_capability_statuses must be a nonempty array"]
    route_states = schema.get("route_states")
    if not isinstance(route_states, list) or not route_states:
        return errors + ["schema route_states must be a nonempty array"]
    if not isinstance(evidence_stack, dict) or not isinstance(evidence_stack.get("edges"), list):
        return errors + ["evidence-stack.json must contain an edges array"]
    edges = {
        edge.get("id"): edge
        for edge in evidence_stack["edges"]
        if isinstance(edge, dict) and isinstance(edge.get("id"), str)
    }
    sources = {
        source.get("id"): source
        for source in registry["sources"]
        if isinstance(source, dict) and isinstance(source.get("id"), str)
    }
    expected_pairs = {
        (platform_id, contract_field)
        for platform_id in platform_ids
        for contract_field in contract_fields
    }
    expected_count = len(expected_pairs)
    if len(records) != expected_count:
        errors.append(
            f"platform-capabilities expected exactly {expected_count} records, found {len(records)}"
        )
    ids: set[str] = set()
    pairs: set[tuple[str, str]] = set()
    platform_metadata: dict[str, tuple[object, ...]] = {}
    for index, record in enumerate(records):
        label = f"platform-capabilities.records[{index}]"
        if not isinstance(record, dict):
            errors.append(f"{label}: record must be an object")
            continue
        missing = sorted(PLATFORM_REQUIRED_FIELDS - record.keys())
        if missing:
            errors.append(f"{label}: missing required field(s): {', '.join(missing)}")
            continue
        for field in (
            "id", "platform_id", "manufacturer", "chip_generation", "contract_field",
            "contract_requirement", "support_detail", "mapper_limits",
            "precision_constraints", "routing_constraints", "host_responsibilities",
            "access_path", "official_technical_source_id", "source_locator",
        ):
            if not isinstance(record[field], str) or not record[field].strip():
                errors.append(f"{label}: {field} must be a nonempty string")
        record_id = record.get("id")
        if isinstance(record_id, str):
            if record_id in ids:
                errors.append(f"{label}: duplicate id {record_id!r}")
            ids.add(record_id)
        platform_id = record.get("platform_id")
        contract_field = record.get("contract_field")
        if isinstance(platform_id, str) and isinstance(contract_field, str):
            pair = (platform_id, contract_field)
            if pair in pairs:
                errors.append(f"{label}: duplicate platform/contract-field pair {pair!r}")
            pairs.add(pair)
            expected_id = f"cap-{platform_id}-{contract_field}"
            if record_id != expected_id:
                errors.append(f"{label}: id must equal {expected_id!r}")
        if not isinstance(record["capability_status"], str) or record["capability_status"] not in capability_statuses:
            errors.append(f"{label}: invalid capability_status {record['capability_status']!r}")
        if not isinstance(record["contract_field"], str) or record["contract_field"] not in contract_fields:
            errors.append(f"{label}: invalid contract_field {record['contract_field']!r}")
        if not isinstance(record["verification_status"], str) or record["verification_status"] not in verification_states:
            errors.append(f"{label}: invalid verification_status {record['verification_status']!r}")
        if not isinstance(record["route_state"], str) or record["route_state"] not in route_states:
            errors.append(f"{label}: invalid route_state {record['route_state']!r}")
        if not valid_date(record["reviewed_on"]):
            errors.append(f"{label}: reviewed_on must be an ISO YYYY-MM-DD date")
        document_date = record["document_date"]
        if document_date is not None and not valid_date(document_date):
            errors.append(f"{label}: document_date must be null or an ISO YYYY-MM-DD date")
        route_ids = record["route_ids"]
        if (
            not isinstance(route_ids, list)
            or not route_ids
            or not all(isinstance(route_id, str) and route_id.strip() for route_id in route_ids)
        ):
            errors.append(f"{label}: route_ids must be a nonempty array of nonempty strings")
        else:
            resolved_edges: list[dict[str, object]] = []
            for route_id in route_ids:
                edge = edges.get(route_id)
                if edge is None:
                    errors.append(f"{label}: unresolved route_id {route_id!r}")
                else:
                    resolved_edges.append(edge)
            if len(resolved_edges) == len(route_ids):
                for left, right in zip(resolved_edges, resolved_edges[1:]):
                    if left.get("to") != right.get("from"):
                        errors.append(
                            f"{label}: route edge chain is disconnected between "
                            f"{left.get('id')!r} and {right.get('id')!r}"
                        )
                if (
                    any(edge.get("route_state") == "blocked" for edge in resolved_edges)
                    and record.get("route_state") != "blocked"
                ):
                    errors.append(
                        f"{label}: blocked route edge requires route_state 'blocked'"
                    )
        for field in ("document_version", "toolchain_version"):
            value = record[field]
            if value is not None and (not isinstance(value, str) or not value.strip()):
                errors.append(f"{label}: {field} must be null or a nonempty string")
        source_id = record["official_technical_source_id"]
        source = sources.get(source_id) if isinstance(source_id, str) else None
        if source is None:
            errors.append(f"{label}: unresolved official_technical_source_id {source_id!r}")
        elif source.get("source_type") not in OFFICIAL_TECHNICAL_SOURCE_TYPES:
            errors.append(f"{label}: capability requires an official technical source")
        elif record["verification_status"] == "verified":
            if record["document_version"] is None and record["toolchain_version"] is None:
                errors.append(f"{label}: verified capability requires a document_version or toolchain_version")
            if source.get("verification_status") != "verified" or source.get("retrieval_status") != "full_text":
                errors.append(f"{label}: verified capability requires a verified full-text source")
            if document_date is None:
                errors.append(f"{label}: verified capability requires a document_date")
        elif source is not None and source.get("verification_status") == "rejected":
            errors.append(f"{label}: capability cannot cite a rejected technical source")
        example_source_id = record["official_exercised_example_source_id"]
        example_locator = record["official_exercised_example_locator"]
        if (example_source_id is None) != (example_locator is None):
            errors.append(
                f"{label}: example source and locator must either both be null or both be set"
            )
        if example_source_id is not None:
            if not isinstance(example_source_id, str) or not example_source_id.strip():
                errors.append(
                    f"{label}: official_exercised_example_source_id must be null or a nonempty string"
                )
            if not isinstance(example_locator, str) or not example_locator.strip():
                errors.append(
                    f"{label}: official_exercised_example_locator must be null or a nonempty string"
                )
            example_source = sources.get(example_source_id) if isinstance(example_source_id, str) else None
            if example_source is None:
                errors.append(
                    f"{label}: unresolved official_exercised_example_source_id {example_source_id!r}"
                )
            elif example_source.get("source_type") not in OFFICIAL_EXAMPLE_SOURCE_TYPES:
                errors.append(
                    f"{label}: exercised example requires an example-capable official source"
                )
            elif record["verification_status"] == "verified" and (
                example_source.get("verification_status") != "verified"
                or example_source.get("retrieval_status") != "full_text"
            ):
                errors.append(f"{label}: verified exercised example requires a verified full-text source")
            elif example_source.get("verification_status") == "rejected":
                errors.append(f"{label}: exercised example cannot cite a rejected source")
        if isinstance(platform_id, str):
            metadata = (
                record.get("manufacturer"),
                record.get("chip_generation"),
                tuple(record.get("route_ids", [])) if isinstance(record.get("route_ids"), list) else None,
                record.get("route_state"),
                record.get("document_date"),
                record.get("document_version"),
                record.get("toolchain_version"),
                record.get("access_path"),
            )
            previous = platform_metadata.setdefault(platform_id, metadata)
            if previous != metadata:
                errors.append(f"{label}: inconsistent platform-wide metadata for {platform_id!r}")
    missing_pairs = sorted(expected_pairs - pairs)
    unexpected_pairs = sorted(pairs - expected_pairs)
    if missing_pairs:
        errors.append(f"platform-capabilities missing platform/contract-field pair(s): {missing_pairs}")
    if unexpected_pairs:
        errors.append(f"platform-capabilities has unexpected platform/contract-field pair(s): {unexpected_pairs}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schema", type=Path, default=ROOT / "data/schema-version.json")
    parser.add_argument("--sources", type=Path, default=ROOT / "data/source-registry.json")
    parser.add_argument("--claims", type=Path, default=ROOT / "data/claims.json")
    parser.add_argument("--platform-capabilities", type=Path, default=ROOT / "data/platform-capabilities.json")
    parser.add_argument("--evidence-stack", type=Path, default=ROOT / "data/evidence-stack.json")
    args = parser.parse_args()
    try:
        schema = load_json(args.schema)
        registry = load_json(args.sources)
        claims_document = load_json(args.claims)
        platform_document = load_json(args.platform_capabilities)
        evidence_stack = load_json(args.evidence_stack)
        errors = validate(schema, registry, claims_document)
        errors.extend(
            validate_platform_capabilities(schema, registry, platform_document, evidence_stack)
        )
    except ValueError as error:
        errors = [str(error)]
    if errors:
        print("validate-evidence: FAILED", file=sys.stderr)
        print("\n".join(f"- {error}" for error in errors), file=sys.stderr)
        return 1
    print(
        "validate-evidence: "
        f"{len(claims_document['claims'])} claim record(s) and "
        f"{len(platform_document['records'])} platform capability record(s) valid"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
