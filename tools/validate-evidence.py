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
    "capability_status", "official_technical_source_id", "source_locator",
    "document_version", "toolchain_version", "verification_status", "reviewed_on",
}
CAPABILITY_STATUSES = {
    "native", "transformed", "emulated", "host-assisted", "unsupported", "undocumented",
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
    if not isinstance(evidence_classes, list) or not isinstance(verification_states, list):
        return errors + ["schema evidence_classes and verification_states must be arrays"]
    source_ids = {source.get("id") for source in registry["sources"] if isinstance(source, dict)}
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
        if not isinstance(claim["source_ids"], list) or not claim["source_ids"]:
            errors.append(f"{label}: source_ids must be a nonempty array")
        else:
            for source_id in claim["source_ids"]:
                if not isinstance(source_id, str) or source_id not in source_ids:
                    errors.append(f"{label}: unresolved source_id {source_id!r}")
        for field in ("locators", "conflicts_with"):
            value = claim[field]
            if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
                errors.append(f"{label}: {field} must be an array of strings")
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


def validate_platform_capabilities(schema: object, registry: object, platform_document: object) -> list[str]:
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
    sources = {
        source.get("id"): source
        for source in registry["sources"]
        if isinstance(source, dict) and isinstance(source.get("id"), str)
    }
    ids: set[str] = set()
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
            "official_technical_source_id", "source_locator",
        ):
            if not isinstance(record[field], str) or not record[field].strip():
                errors.append(f"{label}: {field} must be a nonempty string")
        record_id = record.get("id")
        if isinstance(record_id, str):
            if record_id in ids:
                errors.append(f"{label}: duplicate id {record_id!r}")
            ids.add(record_id)
        if not isinstance(record["capability_status"], str) or record["capability_status"] not in CAPABILITY_STATUSES:
            errors.append(f"{label}: invalid capability_status {record['capability_status']!r}")
        if not isinstance(record["verification_status"], str) or record["verification_status"] not in verification_states:
            errors.append(f"{label}: invalid verification_status {record['verification_status']!r}")
        if not valid_date(record["reviewed_on"]):
            errors.append(f"{label}: reviewed_on must be an ISO YYYY-MM-DD date")
        for field in ("document_version", "toolchain_version"):
            value = record[field]
            if value is not None and (not isinstance(value, str) or not value.strip()):
                errors.append(f"{label}: {field} must be null or a nonempty string")
        source_id = record["official_technical_source_id"]
        source = sources.get(source_id) if isinstance(source_id, str) else None
        if source is None:
            errors.append(f"{label}: unresolved official_technical_source_id {source_id!r}")
        elif record["verification_status"] == "verified":
            source_type = source.get("source_type")
            if not isinstance(source_type, str) or source_type not in OFFICIAL_TECHNICAL_SOURCE_TYPES:
                errors.append(f"{label}: verified capability requires an official technical source")
            if record["document_version"] is None and record["toolchain_version"] is None:
                errors.append(f"{label}: verified capability requires a document_version or toolchain_version")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schema", type=Path, default=ROOT / "data/schema-version.json")
    parser.add_argument("--sources", type=Path, default=ROOT / "data/source-registry.json")
    parser.add_argument("--claims", type=Path, default=ROOT / "data/claims.json")
    parser.add_argument("--platform-capabilities", type=Path, default=ROOT / "data/platform-capabilities.json")
    args = parser.parse_args()
    try:
        schema = load_json(args.schema)
        registry = load_json(args.sources)
        claims_document = load_json(args.claims)
        platform_document = load_json(args.platform_capabilities)
        errors = validate(schema, registry, claims_document)
        errors.extend(validate_platform_capabilities(schema, registry, platform_document))
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
