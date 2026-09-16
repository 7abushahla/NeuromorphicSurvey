#!/usr/bin/env python3
"""Validate canonical prior-work coverage records and their source references."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parent.parent
REQUIRED_FIELDS = {
    "id", "source_id", "full_text_status", "retrieval_sources", "coverage",
    "strongest_contribution", "deployment_depth", "omissions", "verification",
}
COVERAGE_AXES = set("ABCDEFGHIJKL")
REQUIRED_SURVEY_IDENTIFIERS = {f"S{number:02d}" for number in range(1, 38)}
SURVEY_IDENTIFIER_PATTERN = re.compile(r"^(S\d{2})(?:-|$)")
ACCESS_LIMIT_TERMS = {
    "not assessed",
    "not retrieved",
    "not accessible",
    "inaccessible",
    "partial retrieval",
    "retrieval limit",
    "full text unavailable",
}


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


def validate_coverage(
    coverage: object,
    errors: list[str],
    label: str,
    allowed_scores: set[str],
    full_text_status: object,
) -> None:
    if not isinstance(coverage, dict):
        errors.append(f"{label}: coverage must be an object")
        return
    unexpected = sorted(set(coverage) - COVERAGE_AXES)
    if unexpected:
        errors.append(f"{label}: invalid coverage axes: {', '.join(unexpected)}")
    missing = sorted(COVERAGE_AXES - set(coverage))
    if missing:
        errors.append(f"{label}: coverage is missing axes: {', '.join(missing)}")
    for axis, entry in coverage.items():
        axis_label = f"{label}: coverage.{axis}"
        if not isinstance(entry, dict):
            errors.append(f"{axis_label} must be an object")
            continue
        required = {"score", "basis", "locator"}
        absent = sorted(required - entry.keys())
        if absent:
            errors.append(f"{axis_label} missing required field(s): {', '.join(absent)}")
            continue
        score = entry["score"]
        if not isinstance(score, str) or score not in allowed_scores:
            errors.append(f"{axis_label}: invalid score {entry['score']!r}")
        for field in ("basis", "locator"):
            if not isinstance(entry[field], str) or not entry[field].strip():
                errors.append(f"{axis_label}: {field} must be a nonempty string")
        if score == "unassessed":
            if full_text_status not in {"partial", "not_retrieved"}:
                errors.append(
                    f"{axis_label}: unassessed is allowed only for partial or "
                    "not_retrieved full text"
                )
            access_text = " ".join(
                value.lower() for value in (entry.get("basis"), entry.get("locator"))
                if isinstance(value, str)
            )
            if not any(term in access_text for term in ACCESS_LIMIT_TERMS):
                errors.append(
                    f"{axis_label}: unassessed basis or locator must state the "
                    "retrieval or access limit"
                )
        elif full_text_status == "not_retrieved":
            errors.append(
                f"{axis_label}: not_retrieved records must use unassessed, not {score!r}"
            )


def validate(schema: object, registry: object, coverage_document: object) -> list[str]:
    errors: list[str] = []
    if not isinstance(schema, dict):
        return ["schema-version.json must contain an object"]
    if not isinstance(registry, dict) or not isinstance(registry.get("sources"), list):
        return ["source-registry.json must contain a sources array"]
    if not isinstance(coverage_document, dict):
        return ["prior-survey-coverage.json must contain an object"]
    if coverage_document.get("schema_version") != schema.get("schema_version"):
        errors.append("prior-survey-coverage schema_version does not match schema-version.json")
    surveys = coverage_document.get("surveys")
    if not isinstance(surveys, list):
        return errors + ["prior-survey-coverage surveys must be an array"]
    verification_states = schema.get("verification_states")
    full_text_statuses = schema.get("survey_full_text_statuses")
    coverage_scores = schema.get("coverage_scores")
    if not all(isinstance(value, list) for value in (
        verification_states, full_text_statuses, coverage_scores,
    )):
        return errors + [
            "schema verification_states, survey_full_text_statuses, and coverage_scores "
            "must be arrays"
        ]
    allowed_scores = set(coverage_scores)
    source_ids = {source.get("id") for source in registry["sources"] if isinstance(source, dict)}
    ids: set[str] = set()
    survey_identifier_counts: dict[str, int] = {}
    for index, survey in enumerate(surveys):
        label = f"surveys[{index}]"
        if not isinstance(survey, dict):
            errors.append(f"{label}: record must be an object")
            continue
        missing = sorted(REQUIRED_FIELDS - survey.keys())
        if missing:
            errors.append(f"{label}: missing required field(s): {', '.join(missing)}")
            continue
        for field in ("id", "source_id", "strongest_contribution", "deployment_depth"):
            if not isinstance(survey[field], str) or not survey[field].strip():
                errors.append(f"{label}: {field} must be a nonempty string")
        survey_id = survey.get("id")
        if isinstance(survey_id, str):
            if survey_id in ids:
                errors.append(f"{label}: duplicate id {survey_id!r}")
            ids.add(survey_id)
            match = SURVEY_IDENTIFIER_PATTERN.match(survey_id)
            if match is None:
                errors.append(
                    f"{label}: id must begin with a survey identifier such as 'S01-'"
                )
            else:
                identifier = match.group(1)
                survey_identifier_counts[identifier] = (
                    survey_identifier_counts.get(identifier, 0) + 1
                )
        if not isinstance(survey["source_id"], str) or survey["source_id"] not in source_ids:
            errors.append(f"{label}: unresolved source_id {survey['source_id']!r}")
        if not isinstance(survey["full_text_status"], str) or survey["full_text_status"] not in full_text_statuses:
            errors.append(f"{label}: invalid full_text_status {survey['full_text_status']!r}")
        retrieval_sources = survey["retrieval_sources"]
        if not isinstance(retrieval_sources, list) or not retrieval_sources:
            errors.append(f"{label}: retrieval_sources must be a nonempty array")
        elif not all(valid_http_url(value) for value in retrieval_sources):
            errors.append(f"{label}: retrieval_sources must contain absolute HTTP(S) URLs")
        if not isinstance(survey["omissions"], list) or not all(isinstance(item, str) for item in survey["omissions"]):
            errors.append(f"{label}: omissions must be an array of strings")
        validate_coverage(
            survey["coverage"], errors, label, allowed_scores, survey["full_text_status"]
        )
        verification = survey["verification"]
        if not isinstance(verification, dict):
            errors.append(f"{label}: verification must be an object")
            continue
        for field in ("status", "reviewed_on", "reviewer"):
            if field not in verification:
                errors.append(f"{label}: verification missing required field {field}")
        if verification.get("status") not in verification_states:
            errors.append(f"{label}: invalid verification.status {verification.get('status')!r}")
        if not valid_date(verification.get("reviewed_on")):
            errors.append(f"{label}: verification.reviewed_on must be an ISO YYYY-MM-DD date")
        if not isinstance(verification.get("reviewer"), str) or not verification["reviewer"].strip():
            errors.append(f"{label}: verification.reviewer must be a nonempty string")

    if len(surveys) != len(REQUIRED_SURVEY_IDENTIFIERS):
        errors.append(
            "prior-survey-coverage must contain exactly 37 survey records, "
            f"found {len(surveys)}"
        )
    observed_identifiers = set(survey_identifier_counts)
    missing_identifiers = sorted(REQUIRED_SURVEY_IDENTIFIERS - observed_identifiers)
    if missing_identifiers:
        errors.append(
            f"missing survey identifier(s): {', '.join(missing_identifiers)}"
        )
    unexpected_identifiers = sorted(observed_identifiers - REQUIRED_SURVEY_IDENTIFIERS)
    if unexpected_identifiers:
        errors.append(
            f"unexpected survey identifier(s): {', '.join(unexpected_identifiers)}"
        )
    duplicate_identifiers = sorted(
        identifier
        for identifier, count in survey_identifier_counts.items()
        if count > 1
    )
    if duplicate_identifiers:
        errors.append(
            f"duplicate survey identifier(s): {', '.join(duplicate_identifiers)}"
        )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schema", type=Path, default=ROOT / "data/schema-version.json")
    parser.add_argument("--sources", type=Path, default=ROOT / "data/source-registry.json")
    parser.add_argument("--coverage", type=Path, default=ROOT / "data/prior-survey-coverage.json")
    args = parser.parse_args()
    try:
        schema = load_json(args.schema)
        registry = load_json(args.sources)
        coverage_document = load_json(args.coverage)
        errors = validate(schema, registry, coverage_document)
    except ValueError as error:
        errors = [str(error)]
    if errors:
        print("validate-survey-coverage: FAILED", file=sys.stderr)
        print("\n".join(f"- {error}" for error in errors), file=sys.stderr)
        return 1
    print(f"validate-survey-coverage: {len(coverage_document['surveys'])} survey record(s) valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
