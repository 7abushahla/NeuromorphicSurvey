#!/usr/bin/env python3
"""Verify qualified evidence-population and prior-survey counts."""
from __future__ import annotations

import argparse
import json
import re
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
        if not isinstance(survey.get("targets"), dict) or not isinstance(survey["targets"].get("kinds"), list):
            errors.append(f"{label}: targets.kinds is required")
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


def population_fragment(site_manifest_path: Path) -> Path:
    """The section fragment that holds the stable anchor population-counts."""
    manifest = load_json(site_manifest_path)
    for record in manifest.get("fragments", []):
        if record.get("kind") != "section":
            continue
        path = ROOT / record["fragment"]
        if 'id="population-counts"' in path.read_text():
            return path
    raise ValueError("no section fragment holds the population-counts anchor")


def check_population_prose(
    html_text: str, view: dict[str, Any] | None, fragment_name: str
) -> tuple[str, list[str]]:
    """Guard the population-counts anchor's 'Each of its N records' sentence and
    the Total row of the first table after it against the evidence-population-
    summary view, so a future corpus edit that forgets to update the prose fails
    the build instead of drifting.
    """
    errors: list[str] = []
    if not isinstance(view, dict):
        return "", [f"evidence-population-summary.json is missing; cannot guard {fragment_name} population counts prose"]
    record_total = view.get("record_total")
    exclusive = (view.get("population_counts") or {}).get("exclusive") or {}

    sentence_match = re.search(r"Each of its (\d+) records", html_text)
    sentence_n = int(sentence_match.group(1)) if sentence_match else None
    if sentence_match is None:
        errors.append(f"{fragment_name}: population counts 'Each of its N records' sentence not found")
    elif sentence_n != record_total:
        errors.append(
            f"{fragment_name}: population counts 'Each of its {sentence_n} records' does not match "
            f"the view's record_total {record_total}"
        )

    table_match = re.search(r'id="population-counts".*?<caption><b>Table (\d+):</b>', html_text, re.S)
    row: tuple[int, int, int, int] | None = None
    if table_match is None:
        errors.append(f"{fragment_name}: population counts table caption not found after id=\"population-counts\"")
    else:
        table_number = table_match.group(1)
        row_match = re.search(
            r"<tr><td><strong>Total</strong></td>"
            r"<td class=\"ctr\"><strong>(\d+)</strong></td>"
            r"<td class=\"ctr\"><strong>(\d+)</strong></td>"
            r"<td class=\"ctr\"><strong>(\d+)</strong></td>"
            r"<td class=\"ctr\"><strong>(\d+)</strong></td>",
            html_text[table_match.end():],
        )
        if row_match is None:
            errors.append(f"{fragment_name}: population counts Table {table_number}'s Total row not found after its caption")
        else:
            row = (
                int(row_match.group(1)), int(row_match.group(2)),
                int(row_match.group(3)), int(row_match.group(4)),
            )
            expected = (
                exclusive.get("algorithm"), exclusive.get("deployment"),
                exclusive.get("both"), record_total,
            )
            if row != expected:
                errors.append(
                    f"{fragment_name}: population counts Table {table_number}'s Total row "
                    f"(algorithm={row[0]}, deployment={row[1]}, both={row[2]}, total={row[3]}) "
                    f"does not match the view's exclusive counts and record_total {expected}"
                )

    summary = (
        f"check-counts: {fragment_name} population counts 'Each of its N records' "
        f"N={sentence_n} and Table Total row {row} compared against "
        f"evidence-population-summary record_total={record_total} exclusive={exclusive}"
    )
    return summary, errors


NUMBER_WORDS = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
}


def check_section_1_gap_prose(
    html_text: str, view: dict[str, Any] | None
) -> tuple[str, list[str]]:
    """Guard Section 1's gap paragraph against the prior-survey-targets-summary
    view: 'None of the 37 surveys covers all three targets' must agree with
    surveys_covering_all_three_buckets (0 renders as 'None'), and 'Seven cover at
    least one conventional target and two cover at least one chip model' with
    bucket_survey_counts.conventional and .simulated through a words-to-number
    map for zero to twelve.
    """
    errors: list[str] = []
    if not isinstance(view, dict):
        return "", ["prior-survey-targets-summary.json is missing; cannot guard Section 1 prose"]
    all_three = view.get("surveys_covering_all_three_buckets")
    survey_total = view.get("survey_total")
    buckets = view.get("bucket_survey_counts") or {}
    conventional = buckets.get("conventional")
    simulated = buckets.get("simulated")

    all_three_match = re.search(
        r"(\w+) of the (\d+) surveys covers all three targets", html_text
    )
    all_three_word: str | None = None
    all_three_total: int | None = None
    if all_three_match is None:
        errors.append(
            "site/sec-01.html: the gap paragraph's 'None of the N surveys covers all "
            "three targets' sentence not found"
        )
    else:
        all_three_word = all_three_match.group(1)
        all_three_total = int(all_three_match.group(2))
        if all_three_total != survey_total:
            errors.append(
                f"site/sec-01.html: 'of the {all_three_total} surveys' does not match "
                f"the view's survey_total {survey_total}"
            )
        if all_three == 0 and all_three_word != "None":
            errors.append(
                f"site/sec-01.html: the view counts 0 surveys covering all three "
                f"buckets but the sentence reads '{all_three_word} of the ...'"
            )
        elif all_three != 0 and all_three_word == "None":
            errors.append(
                f"site/sec-01.html: the sentence says 'None' but the view counts "
                f"{all_three} survey(s) covering all three buckets"
            )
        elif all_three != 0 and NUMBER_WORDS.get(all_three_word.lower()) != all_three:
            errors.append(
                f"site/sec-01.html: '{all_three_word} of the ...' does not match the "
                f"view's surveys_covering_all_three_buckets {all_three}"
            )

    bucket_match = re.search(
        r"(\w+) cover at least one conventional target and (\w+) cover\s+at least "
        r"one (?:simulated )?chip model",
        html_text,
    )
    prose_conventional: int | None = None
    prose_simulated: int | None = None
    if bucket_match is None:
        errors.append(
            "site/sec-01.html: the gap paragraph's 'N cover at least one conventional "
            "target and M cover at least one chip model' sentence not found"
        )
    else:
        prose_conventional = NUMBER_WORDS.get(bucket_match.group(1).lower())
        prose_simulated = NUMBER_WORDS.get(bucket_match.group(2).lower())
        if prose_conventional is None or prose_simulated is None:
            errors.append(
                "site/sec-01.html: the gap paragraph's bucket counts are not words "
                f"from zero to twelve: {bucket_match.group(1)!r}, {bucket_match.group(2)!r}"
            )
        else:
            if prose_conventional != conventional:
                errors.append(
                    f"site/sec-01.html: '{bucket_match.group(1)} cover at least one "
                    f"conventional target' does not match the view's "
                    f"bucket_survey_counts.conventional {conventional}"
                )
            if prose_simulated != simulated:
                errors.append(
                    f"site/sec-01.html: '{bucket_match.group(2)} cover at least one chip "
                    f"model' does not match the view's bucket_survey_counts.simulated "
                    f"{simulated}"
                )

    summary = (
        "check-counts: sec-01.html gap paragraph "
        f"'{all_three_word} of the {all_three_total} surveys covers all three targets' "
        f"and bucket words conventional={prose_conventional} simulated={prose_simulated} "
        f"compared against prior-survey-targets-summary "
        f"surveys_covering_all_three_buckets={all_three} survey_total={survey_total} "
        f"bucket_survey_counts conventional={conventional} simulated={simulated}"
    )
    return summary, errors


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
    parser.add_argument(
        "--site-manifest", type=Path, default=ROOT / "data/site-manifest.json"
    )
    parser.add_argument(
        "--section-1", type=Path, default=ROOT / "site/sec-01.html"
    )
    args = parser.parse_args()
    prose_summary = ""
    gap_summary = ""
    try:
        papers = load_json(args.papers)
        surveys = load_json(args.surveys)
        generated = {
            path.name: load_json(path)
            for path in sorted(args.generated_dir.glob("*.json"))
        }
        summary, errors = validate_counts(papers, surveys, generated)
        population_path = population_fragment(args.site_manifest)
        prose_summary, prose_errors = check_population_prose(
            population_path.read_text(),
            generated.get("evidence-population-summary.json"),
            population_path.name,
        )
        errors.extend(prose_errors)
        gap_summary, gap_errors = check_section_1_gap_prose(
            args.section_1.read_text(), generated.get("prior-survey-targets-summary.json")
        )
        errors.extend(gap_errors)
    except ValueError as error:
        errors = [str(error)]
        summary = {}
    except OSError as error:
        errors = [f"cannot read {args.site_manifest} or {args.section_1}: {error}"]
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
    print(prose_summary)
    print(gap_summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
