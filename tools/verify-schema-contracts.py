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


def expect_error(errors: list[str], fragment: str, label: str) -> None:
    if not any(fragment in error for error in errors):
        raise AssertionError(
            f"expected {label} to report {fragment!r}; validator errors: {errors}"
        )


def expect_valid(errors: list[str], label: str) -> None:
    if errors:
        raise AssertionError(f"expected {label} to validate: {errors}")


def record_by_id(records: list[object], record_id: str, label: str) -> dict[str, object]:
    matches = [
        record
        for record in records
        if isinstance(record, dict) and record.get("id") == record_id
    ]
    if len(matches) != 1:
        raise AssertionError(f"expected exactly one {label} with id {record_id!r}")
    return matches[0]


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

    checks = 0

    def check_valid(errors: list[str], label: str) -> None:
        nonlocal checks
        expect_valid(errors, label)
        checks += 1

    def check_error(errors: list[str], fragment: str, label: str) -> None:
        nonlocal checks
        expect_error(errors, fragment, label)
        checks += 1

    check_valid(source_validate(schema, registry), "canonical source registry")
    check_valid(claim_validate(schema, registry, claims), "canonical claim registry")
    check_valid(platform_validate(schema, registry, platforms), "canonical platform registry")
    check_valid(coverage_validate(schema, registry, coverage), "canonical coverage registry")

    bad_registry = copy.deepcopy(registry)
    record_by_id(
        bad_registry["sources"], "pedersen-2024-nir", "source",
    )["source_type"] = []
    check_error(
        source_validate(schema, bad_registry),
        "invalid source_type",
        "malformed source type",
    )

    missing_flag_claims = copy.deepcopy(claims)
    del record_by_id(
        missing_flag_claims["claims"], "claim-nir-reset-semantics", "claim",
    )["reports_deployment_evidence"]
    check_error(
        claim_validate(schema, registry, missing_flag_claims),
        "missing required field",
        "claim missing reports_deployment_evidence",
    )

    non_boolean_flag_claims = copy.deepcopy(claims)
    record_by_id(
        non_boolean_flag_claims["claims"], "claim-nir-reset-semantics", "claim",
    )["reports_deployment_evidence"] = "false"
    check_error(
        claim_validate(schema, registry, non_boolean_flag_claims),
        "reports_deployment_evidence must be a boolean",
        "claim with non-Boolean reports_deployment_evidence",
    )

    deployment_claims = copy.deepcopy(claims)
    deployment_claim = record_by_id(
        deployment_claims["claims"], "claim-nir-reset-semantics", "claim",
    )
    deployment_claim["reports_deployment_evidence"] = True
    deployment_claim["measurement_boundary"] = "fixture measurement boundary"
    check_error(
        claim_validate(schema, registry, deployment_claims),
        "requires an E1-E5 evidence_class",
        "deployment claim without an evidence class",
    )

    boundaryless_claims = copy.deepcopy(claims)
    boundaryless_claim = record_by_id(
        boundaryless_claims["claims"], "claim-nir-reset-semantics", "claim",
    )
    boundaryless_claim["reports_deployment_evidence"] = True
    boundaryless_claim["evidence_class"] = "E1"
    check_error(
        claim_validate(schema, registry, boundaryless_claims),
        "requires a measurement_boundary",
        "deployment claim without a measurement boundary",
    )

    non_deployment_claims = copy.deepcopy(claims)
    record_by_id(
        non_deployment_claims["claims"], "claim-nir-reset-semantics", "claim",
    )["evidence_class"] = "E2"
    check_error(
        claim_validate(schema, registry, non_deployment_claims),
        "non-deployment claims require a null evidence_class",
        "non-deployment claim with a non-null evidence class",
    )

    nir_source = record_by_id(registry["sources"], "pedersen-2024-nir", "source")
    official_registry = {
        "schema_version": registry["schema_version"],
        "sources": [copy.deepcopy(nir_source)],
    }
    record_by_id(
        official_registry["sources"], "pedersen-2024-nir", "source",
    )["source_type"] = "official_sdk_documentation"
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
    check_valid(
        platform_validate(schema, official_registry, verified_platforms),
        "verified official platform capability",
    )

    unresolved_source_platforms = copy.deepcopy(verified_platforms)
    unresolved_source_platforms["records"][0]["official_technical_source_id"] = "missing-source"
    check_error(
        platform_validate(schema, official_registry, unresolved_source_platforms),
        "unresolved official_technical_source_id",
        "verified capability with an unresolved official source",
    )

    invalid_date_platforms = copy.deepcopy(verified_platforms)
    invalid_date_platforms["records"][0]["reviewed_on"] = "2026-02-30"
    check_error(
        platform_validate(schema, official_registry, invalid_date_platforms),
        "reviewed_on must be an ISO YYYY-MM-DD date",
        "verified capability with an invalid review date",
    )

    versionless_platforms = copy.deepcopy(verified_platforms)
    versionless_platforms["records"][0]["document_version"] = None
    check_error(
        platform_validate(schema, official_registry, versionless_platforms),
        "requires a document_version or toolchain_version",
        "verified capability without a document or toolchain version",
    )

    invalid_status_platforms = copy.deepcopy(verified_platforms)
    invalid_status_platforms["records"][0]["capability_status"] = []
    check_error(
        platform_validate(schema, official_registry, invalid_status_platforms),
        "invalid capability_status",
        "platform capability with an invalid capability status",
    )

    for source_type in (
        "peer_reviewed",
        "marketing_material",
        "general_web",
        "secondary_material",
    ):
        non_official_registry = copy.deepcopy(official_registry)
        record_by_id(
            non_official_registry["sources"], "pedersen-2024-nir", "source",
        )["source_type"] = source_type
        check_error(
            platform_validate(schema, non_official_registry, verified_platforms),
            "requires an official technical source",
            f"verified capability backed by {source_type}",
        )

    for status in ("verified", "provisional", "partial", "not_retrieved"):
        candidate = copy.deepcopy(coverage)
        record_by_id(
            candidate["surveys"], "S01-pedersen-2024-nir", "survey",
        )["full_text_status"] = status
        check_valid(
            coverage_validate(schema, registry, candidate),
            f"survey full-text status {status!r}",
        )
    for status in ("conflicted", "rejected", True, "unknown"):
        candidate = copy.deepcopy(coverage)
        record_by_id(
            candidate["surveys"], "S01-pedersen-2024-nir", "survey",
        )["full_text_status"] = status
        check_error(
            coverage_validate(schema, registry, candidate),
            "invalid full_text_status",
            f"survey full-text status {status!r}",
        )

    def populated_coverage(score: str, basis: str, locator: str) -> dict[str, object]:
        return {
            axis: {"score": score, "basis": basis, "locator": locator}
            for axis in "ABCDEFGHIJKL"
        }

    for status in ("partial", "not_retrieved"):
        candidate = copy.deepcopy(coverage)
        survey = record_by_id(
            candidate["surveys"], "S01-pedersen-2024-nir", "survey",
        )
        survey["full_text_status"] = status
        survey["coverage"] = populated_coverage(
            "unassessed",
            "Not assessed because full text was not retrieved completely.",
            "Retrieval limit documented in the audit note.",
        )
        check_valid(
            coverage_validate(schema, registry, candidate),
            f"unassessed coverage with {status} retrieval",
        )

    verified_unassessed = copy.deepcopy(coverage)
    verified_survey = record_by_id(
        verified_unassessed["surveys"], "S01-pedersen-2024-nir", "survey",
    )
    verified_survey["full_text_status"] = "verified"
    verified_survey["coverage"] = populated_coverage(
        "unassessed", "Not assessed due to a retrieval limit.", "Retrieval limit.",
    )
    check_error(
        coverage_validate(schema, registry, verified_unassessed),
        "unassessed is allowed only",
        "verified full text with unassessed coverage",
    )

    unknown_score = copy.deepcopy(coverage)
    unknown_survey = record_by_id(
        unknown_score["surveys"], "S01-pedersen-2024-nir", "survey",
    )
    unknown_survey["full_text_status"] = "verified"
    unknown_survey["coverage"] = populated_coverage(
        "unknown", "Fixture basis.", "Fixture locator.",
    )
    check_error(
        coverage_validate(schema, registry, unknown_score),
        "invalid score",
        "unknown coverage score",
    )

    vague_unassessed = copy.deepcopy(coverage)
    vague_survey = record_by_id(
        vague_unassessed["surveys"], "S01-pedersen-2024-nir", "survey",
    )
    vague_survey["full_text_status"] = "partial"
    vague_survey["coverage"] = populated_coverage(
        "unassessed", "No conclusion recorded.", "Audit note.",
    )
    check_error(
        coverage_validate(schema, registry, vague_unassessed),
        "must state the retrieval or access limit",
        "unassessed coverage without an access boundary",
    )

    expected_checks = 32
    if checks != expected_checks:
        raise AssertionError(f"expected {expected_checks} contract checks, executed {checks}")
    print(f"verify-schema-contracts: {checks} contract checks passed")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as error:
        print(f"verify-schema-contracts: FAILED: {error}", file=sys.stderr)
        raise SystemExit(1)
