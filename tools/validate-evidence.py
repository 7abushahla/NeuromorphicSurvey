#!/usr/bin/env python3
"""Validate canonical claim records and their source references."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
REQUIRED_FIELDS = {
    "id", "claim_type", "statement", "evidence_class", "source_ids", "locators",
    "verification_status", "measurement_boundary", "conflicts_with", "scope",
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
        if claim["verification_status"] not in verification_states:
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
        evidence_class = claim["evidence_class"]
        if evidence_class is None:
            # A non-null measurement boundary states that deployment evidence is reported.
            if boundary is not None:
                errors.append(f"{label}: deployment evidence requires an evidence_class")
            if claim.get("claim_type") == "measurement":
                errors.append(f"{label}: measurement claims require an evidence_class")
        elif evidence_class not in evidence_classes:
            errors.append(f"{label}: invalid evidence_class {evidence_class!r}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schema", type=Path, default=ROOT / "data/schema-version.json")
    parser.add_argument("--sources", type=Path, default=ROOT / "data/source-registry.json")
    parser.add_argument("--claims", type=Path, default=ROOT / "data/claims.json")
    args = parser.parse_args()
    try:
        schema = load_json(args.schema)
        registry = load_json(args.sources)
        claims_document = load_json(args.claims)
        errors = validate(schema, registry, claims_document)
    except ValueError as error:
        errors = [str(error)]
    if errors:
        print("validate-evidence: FAILED", file=sys.stderr)
        print("\n".join(f"- {error}" for error in errors), file=sys.stderr)
        return 1
    print(f"validate-evidence: {len(claims_document['claims'])} claim record(s) valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
