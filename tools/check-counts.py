#!/usr/bin/env python3
"""Verify qualified evidence-population and prior-survey counts."""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
POPULATIONS = ("algorithm", "deployment", "both")
COVERAGE_AXES = set("ABCDEFGHIJKL")
UNQUALIFIED_HEADLINE_KEYS = {
    "algorithm_count",
    "deployment_count",
    "both_count",
    "paper_count",
    "papers_count",
    "population_count",
    "population_total",
    "total_papers",
    "headline_count",
    "headline_counts",
}


def load_json(path: Path) -> object:
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"cannot read JSON from {path}: {error}") from error


def population_counts(document: object) -> tuple[dict[str, Any], list[str]]:
    """Return exclusive, inclusive, and unique totals for evidence papers."""
    errors: list[str] = []
    if not isinstance(document, dict) or not isinstance(document.get("papers"), list):
        return {}, ["evidence-papers.json must contain a papers array"]
    counts: Counter[str] = Counter()
    ids: list[str] = []
    for index, paper in enumerate(document["papers"]):
        label = f"evidence-papers.papers[{index}]"
        if not isinstance(paper, dict):
            errors.append(f"{label}: record must be an object")
            continue
        paper_id = paper.get("id")
        if not isinstance(paper_id, str) or not paper_id.strip():
            errors.append(f"{label}: id must be a nonempty string")
        else:
            ids.append(paper_id)
        population = paper.get("population")
        if population not in POPULATIONS:
            errors.append(f"{label}: invalid population {population!r}")
        else:
            counts[population] += 1
    duplicates = sorted(item for item, count in Counter(ids).items() if count > 1)
    if duplicates:
        errors.append(f"evidence-papers has duplicate IDs: {duplicates}")
    exclusive = {population: counts[population] for population in POPULATIONS}
    result = {
        "exclusive": exclusive,
        "inclusive": {
            "algorithm": exclusive["algorithm"] + exclusive["both"],
            "deployment": exclusive["deployment"] + exclusive["both"],
        },
        "total_unique": sum(exclusive.values()),
    }
    return result, errors


def stale_headline_errors(
    document: object,
    label: str,
    expected_counts: dict[str, Any] | None = None,
) -> list[str]:
    """Reject generated population headlines that omit their count policy."""
    errors: list[str] = []

    def walk(value: object, path: str) -> None:
        if isinstance(value, dict):
            keys = set(value)
            suspicious = sorted(keys & UNQUALIFIED_HEADLINE_KEYS)
            qualified = {"exclusive", "inclusive"} <= keys
            if suspicious and not qualified:
                errors.append(
                    f"{label}:{path or '<root>'}: unqualified population headline "
                    f"field(s): {', '.join(suspicious)}"
                )
            if "population_counts" in value:
                count_value = value["population_counts"]
                if not isinstance(count_value, dict) or not {
                    "exclusive", "inclusive", "total_unique"
                } <= set(count_value):
                    errors.append(
                        f"{label}:{path or '<root>'}.population_counts: "
                        "unqualified population count policy"
                    )
                elif expected_counts is not None and count_value != expected_counts:
                    errors.append(
                        f"{label}:{path or '<root>'}.population_counts: stale "
                        f"population totals {count_value!r}; expected {expected_counts!r}"
                    )
            for key, child in value.items():
                child_path = f"{path}.{key}" if path else str(key)
                walk(child, child_path)
        elif isinstance(value, list):
            for index, child in enumerate(value):
                walk(child, f"{path}[{index}]")

    walk(document, "")
    return errors


def validate_surveys(document: object) -> tuple[dict[str, int], list[str]]:
    errors: list[str] = []
    if not isinstance(document, dict) or not isinstance(document.get("surveys"), list):
        return {}, ["prior-survey-coverage.json must contain a surveys array"]
    surveys = document["surveys"]
    if len(surveys) != 37:
        errors.append(f"prior-survey coverage expected 37 surveys, found {len(surveys)}")
    all_axes: set[str] = set()
    for index, survey in enumerate(surveys):
        label = f"prior-survey-coverage.surveys[{index}]"
        coverage = survey.get("coverage") if isinstance(survey, dict) else None
        if not isinstance(coverage, dict):
            errors.append(f"{label}: coverage must be an object")
            continue
        axes = set(coverage)
        all_axes.update(axes)
        if axes != COVERAGE_AXES:
            missing = sorted(COVERAGE_AXES - axes)
            unexpected = sorted(axes - COVERAGE_AXES)
            errors.append(
                f"{label}: coverage axes mismatch; missing={missing}, "
                f"unexpected={unexpected}"
            )
    if all_axes != COVERAGE_AXES:
        errors.append(
            f"prior-survey coverage expected exactly 12 axes A-L, found "
            f"{sorted(all_axes)}"
        )
    return {"surveys": len(surveys), "axes": len(all_axes)}, errors


def validate_measurement_view(
    papers_document: object, measurement_document: object
) -> list[str]:
    if not isinstance(papers_document, dict) or not isinstance(
        papers_document.get("papers"), list
    ):
        return ["evidence-papers.json must contain a papers array"]
    if not isinstance(measurement_document, dict) or not isinstance(
        measurement_document.get("measurements"), list
    ):
        return ["measurement-index.json must contain a measurements array"]
    expected = {
        paper.get("id"): paper.get("population")
        for paper in papers_document["papers"]
        if isinstance(paper, dict)
    }
    actual: dict[object, object] = {}
    errors: list[str] = []
    for index, measurement in enumerate(measurement_document["measurements"]):
        if not isinstance(measurement, dict):
            errors.append(f"measurement-index.measurements[{index}]: record must be an object")
            continue
        measurement_id = measurement.get("id")
        if measurement_id in actual:
            errors.append(f"measurement-index has duplicate ID {measurement_id!r}")
        actual[measurement_id] = measurement.get("population")
    if actual != expected:
        missing = sorted(set(expected) - set(actual))
        unexpected = sorted(set(actual) - set(expected))
        changed = sorted(
            item for item in set(expected) & set(actual) if expected[item] != actual[item]
        )
        errors.append(
            "measurement-index population projection is stale; "
            f"missing={missing}, unexpected={unexpected}, changed={changed}"
        )
    return errors


def validate_counts(
    papers_document: object,
    surveys_document: object,
    generated_documents: dict[str, object],
) -> tuple[dict[str, Any], list[str]]:
    counts, errors = population_counts(papers_document)
    survey_counts, survey_errors = validate_surveys(surveys_document)
    errors.extend(survey_errors)
    for label in sorted(generated_documents):
        document = generated_documents[label]
        errors.extend(stale_headline_errors(document, label, counts))
    measurement = generated_documents.get("measurement-index.json")
    if measurement is None:
        errors.append("generated artifacts are missing measurement-index.json")
    else:
        errors.extend(validate_measurement_view(papers_document, measurement))
    return {"population": counts, "coverage": survey_counts}, errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--papers", type=Path, default=ROOT / "data/evidence-papers.json"
    )
    parser.add_argument(
        "--surveys", type=Path, default=ROOT / "data/prior-survey-coverage.json"
    )
    parser.add_argument(
        "--generated-dir", type=Path, default=ROOT / "data/generated"
    )
    args = parser.parse_args()
    try:
        papers = load_json(args.papers)
        surveys = load_json(args.surveys)
        generated = {
            path.name: load_json(path)
            for path in sorted(args.generated_dir.glob("*.json"))
        }
        summary, errors = validate_counts(papers, surveys, generated)
    except ValueError as error:
        errors = [str(error)]
        summary = {}
    if errors:
        print("check-counts: FAILED", file=sys.stderr)
        print("\n".join(f"- {error}" for error in errors), file=sys.stderr)
        return 1
    population = summary["population"]
    exclusive = population["exclusive"]
    inclusive = population["inclusive"]
    coverage = summary["coverage"]
    print(
        "check-counts: population exclusive "
        f"algorithm={exclusive['algorithm']} deployment={exclusive['deployment']} "
        f"both={exclusive['both']} total_unique={population['total_unique']}"
    )
    print(
        "check-counts: population inclusive "
        f"algorithm={inclusive['algorithm']} deployment={inclusive['deployment']} "
        f"total_unique={population['total_unique']}"
    )
    print(
        "check-counts: survey coverage "
        f"surveys={coverage['surveys']} axes={coverage['axes']}"
    )
    print(
        "check-counts: "
        f"{len(generated)} generated artifact(s), no stale unqualified population headlines"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
