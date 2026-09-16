#!/usr/bin/env python3
"""Verify durable canonical-schema contracts through the production validators."""
from __future__ import annotations

import copy
import json
import runpy
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def load_json(path: Path) -> object:
    return json.loads(path.read_text())


def expect_error(errors: list[str], fragment: str) -> None:
    if not any(fragment in error for error in errors):
        raise AssertionError(f"expected {fragment!r} in validator errors: {errors}")


def expect_valid(errors: list[str], label: str) -> None:
    if errors:
        raise AssertionError(f"expected {label} to validate: {errors}")


def main() -> int:
    schema = load_json(ROOT / "data/schema-version.json")
    registry = load_json(ROOT / "data/source-registry.json")
    claims = load_json(ROOT / "data/claims.json")
    platforms = load_json(ROOT / "data/platform-capabilities.json")
    coverage = load_json(ROOT / "data/prior-survey-coverage.json")

    source_validate = runpy.run_path(ROOT / "tools/validate-sources.py")["validate"]
    evidence_module = runpy.run_path(ROOT / "tools/validate-evidence.py")
    claim_validate = evidence_module["validate"]
    platform_validate = evidence_module["validate_platform_capabilities"]
    coverage_validate = runpy.run_path(ROOT / "tools/validate-survey-coverage.py")["validate"]

    expect_valid(source_validate(schema, registry), "canonical source registry")
    expect_valid(claim_validate(schema, registry, claims), "canonical claim registry")
    expect_valid(platform_validate(schema, registry, platforms), "canonical platform registry")
    expect_valid(coverage_validate(schema, registry, coverage), "canonical coverage registry")

    bad_registry = copy.deepcopy(registry)
    bad_registry["sources"][0]["source_type"] = []
    expect_error(source_validate(schema, bad_registry), "invalid source_type")

    deployment_claims = copy.deepcopy(claims)
    deployment_claims["claims"][0]["reports_deployment_evidence"] = True
    expect_error(
        claim_validate(schema, registry, deployment_claims),
        "requires an E1-E5 evidence_class",
    )
    non_deployment_claims = copy.deepcopy(claims)
    non_deployment_claims["claims"][0]["evidence_class"] = "E2"
    expect_error(
        claim_validate(schema, registry, non_deployment_claims),
        "non-deployment claims require a null evidence_class",
    )

    official_registry = copy.deepcopy(registry)
    official_registry["sources"][0]["source_type"] = "official_sdk_documentation"
    verified_platforms = copy.deepcopy(platforms)
    verified_platforms["records"] = [{
        "id": "capability-fixture",
        "platform_id": "fixture-platform",
        "manufacturer": "Fixture Manufacturer",
        "chip_generation": "Fixture Generation",
        "contract_field": "reset_semantics",
        "capability_status": "native",
        "official_technical_source_id": "pedersen-2024-nir",
        "source_locator": "Section 2",
        "document_version": "1.0",
        "toolchain_version": None,
        "verification_status": "verified",
        "reviewed_on": "2026-09-16",
    }]
    expect_valid(
        platform_validate(schema, official_registry, verified_platforms),
        "verified official platform capability",
    )
    non_official_registry = copy.deepcopy(official_registry)
    non_official_registry["sources"][0]["source_type"] = "general_web"
    expect_error(
        platform_validate(schema, non_official_registry, verified_platforms),
        "requires an official technical source",
    )
    versionless_platforms = copy.deepcopy(verified_platforms)
    versionless_platforms["records"][0]["document_version"] = None
    expect_error(
        platform_validate(schema, official_registry, versionless_platforms),
        "requires a document_version or toolchain_version",
    )
    invalid_status_platforms = copy.deepcopy(verified_platforms)
    invalid_status_platforms["records"][0]["capability_status"] = []
    expect_error(
        platform_validate(schema, official_registry, invalid_status_platforms),
        "invalid capability_status",
    )

    for status in ("verified", "provisional", "partial", "not_retrieved"):
        candidate = copy.deepcopy(coverage)
        candidate["surveys"][0]["full_text_status"] = status
        expect_valid(coverage_validate(schema, registry, candidate), status)
    for status in ("conflicted", "rejected", True, "unknown"):
        candidate = copy.deepcopy(coverage)
        candidate["surveys"][0]["full_text_status"] = status
        expect_error(coverage_validate(schema, registry, candidate), "invalid full_text_status")

    print("verify-schema-contracts: 19 contract checks passed")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as error:
        print(f"verify-schema-contracts: FAILED: {error}", file=sys.stderr)
        raise SystemExit(1)
