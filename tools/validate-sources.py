#!/usr/bin/env python3
"""Validate the versioned canonical source registry.

Official deployment evidence is deliberately distinct from peer-reviewed and general
web sources. The accepted official source types cover vendor and manufacturer
documentation, SDKs, devkits, model zoos, mapper constraints, release notes, and
official measured examples.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parent.parent
REQUIRED_FIELDS = {
    "id", "canonical_key", "title", "authors", "year", "venue", "doi", "url",
    "source_type", "retrieval_status", "verification_status", "retrieved_on",
    "locators", "aliases", "notes",
}
SOURCE_TYPES = {
    "peer_reviewed",
    "preprint",
    "official_vendor_documentation",
    "official_manufacturer_documentation",
    "official_sdk_documentation",
    "official_devkit_manual",
    "official_repository",
    "official_model_zoo",
    "official_mapper_constraints",
    "official_release_note",
    "official_measured_example",
    "marketing_material",
    "secondary_material",
    "general_web",
}
RETRIEVAL_STATES = {"full_text", "partial_text", "metadata_only", "not_retrieved"}


def load_json(path: Path) -> object:
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"cannot read JSON from {path}: {error}") from error


def valid_date(value: object) -> bool:
    if not isinstance(value, str):
        return False
    try:
        return dt.date.fromisoformat(value).isoformat() == value
    except ValueError:
        return False


def valid_http_url(value: object) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def require_nonempty_string(record: dict[str, object], field: str, errors: list[str], label: str) -> None:
    if not isinstance(record.get(field), str) or not record[field].strip():
        errors.append(f"{label}: {field} must be a nonempty string")


def validate(schema: object, registry: object) -> list[str]:
    errors: list[str] = []
    if not isinstance(schema, dict):
        return ["schema-version.json must contain an object"]
    if not isinstance(registry, dict):
        return ["source-registry.json must contain an object"]
    if registry.get("schema_version") != schema.get("schema_version"):
        errors.append("source-registry schema_version does not match schema-version.json")
    sources = registry.get("sources")
    if not isinstance(sources, list):
        return errors + ["source-registry sources must be an array"]

    verification_states = schema.get("verification_states")
    if not isinstance(verification_states, list):
        return errors + ["schema verification_states must be an array"]
    verification_states = set(verification_states)
    ids: set[str] = set()
    canonical_keys: set[str] = set()
    for index, source in enumerate(sources):
        label = f"sources[{index}]"
        if not isinstance(source, dict):
            errors.append(f"{label}: record must be an object")
            continue
        missing = sorted(REQUIRED_FIELDS - source.keys())
        if missing:
            errors.append(f"{label}: missing required field(s): {', '.join(missing)}")
            continue
        for field in ("id", "canonical_key", "title", "authors", "venue"):
            require_nonempty_string(source, field, errors, label)
        doi = source["doi"]
        if doi is not None and (not isinstance(doi, str) or not doi.strip()):
            errors.append(f"{label}: doi must be null or a nonempty string")
        elif isinstance(doi, str) and doi.strip().lower().startswith("unassigned:"):
            errors.append(
                f"{label}: doi must not use the synthetic 'unassigned:' prefix"
            )
        if not isinstance(source["year"], int) or isinstance(source["year"], bool):
            errors.append(f"{label}: year must be an integer")
        if not valid_http_url(source["url"]):
            errors.append(f"{label}: url must be an absolute HTTP(S) URL")
        if not isinstance(source["source_type"], str) or source["source_type"] not in SOURCE_TYPES:
            errors.append(f"{label}: invalid source_type {source['source_type']!r}")
        if not isinstance(source["retrieval_status"], str) or source["retrieval_status"] not in RETRIEVAL_STATES:
            errors.append(f"{label}: invalid retrieval_status {source['retrieval_status']!r}")
        if not isinstance(source["verification_status"], str) or source["verification_status"] not in verification_states:
            errors.append(f"{label}: invalid verification_status {source['verification_status']!r}")
        if not valid_date(source["retrieved_on"]):
            errors.append(f"{label}: retrieved_on must be an ISO YYYY-MM-DD date")
        for field in ("locators", "aliases"):
            value = source[field]
            if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
                errors.append(f"{label}: {field} must be an array of strings")
        if not isinstance(source["notes"], str):
            errors.append(f"{label}: notes must be a string")

        source_id = source.get("id")
        if isinstance(source_id, str):
            if source_id in ids:
                errors.append(f"{label}: duplicate id {source_id!r}")
            ids.add(source_id)
        canonical_key = source.get("canonical_key")
        if isinstance(canonical_key, str):
            if canonical_key in canonical_keys:
                errors.append(f"{label}: duplicate canonical_key {canonical_key!r}")
            canonical_keys.add(canonical_key)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schema", type=Path, default=ROOT / "data/schema-version.json")
    parser.add_argument("--sources", type=Path, default=ROOT / "data/source-registry.json")
    args = parser.parse_args()
    try:
        schema, registry = load_json(args.schema), load_json(args.sources)
        errors = validate(schema, registry)
    except ValueError as error:
        errors = [str(error)]
    if errors:
        print("validate-sources: FAILED", file=sys.stderr)
        print("\n".join(f"- {error}" for error in errors), file=sys.stderr)
        return 1
    print(f"validate-sources: {len(registry['sources'])} source record(s) valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
