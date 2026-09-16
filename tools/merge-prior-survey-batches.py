#!/usr/bin/env python3
"""Normalize and merge the four Exa prior-work audit batches."""
from __future__ import annotations

import argparse
import copy
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
BATCH_DIR = ROOT / "research/prior-surveys"
AXES = tuple("ABCDEFGHIJKL")

SOURCE_TYPE_MAP = {
    "accepted_manuscript": "peer_reviewed",
    "benchmark_framework_article": "peer_reviewed",
    "peer_reviewed": "peer_reviewed",
    "peer_reviewed_benchmark_framework": "peer_reviewed",
    "peer_reviewed_perspective": "peer_reviewed",
    "peer_reviewed_research_article": "peer_reviewed",
    "peer_reviewed_review": "peer_reviewed",
    "peer_reviewed_review_perspective": "peer_reviewed",
    "peer_reviewed_survey": "peer_reviewed",
    "peer_reviewed_tutorial_review": "peer_reviewed",
    "preprint": "preprint",
    "preprint_survey": "preprint",
    "single_platform_survey": "peer_reviewed",
}

FULL_TEXT_STATUS_MAP = {
    "full_text": "verified",
    "verified": "verified",
    "partial": "partial",
    "partial_text": "partial",
    "metadata_only": "not_retrieved",
    "not_retrieved": "not_retrieved",
    "provisional": "provisional",
}

SOURCE_RETRIEVAL_MAP = {
    "full_text": "full_text",
    "verified": "full_text",
    "partial": "partial_text",
    "partial_text": "partial_text",
    "metadata_only": "metadata_only",
    "not_retrieved": "not_retrieved",
    "provisional": "metadata_only",
}

D_SYNTHESIS = {
    "S29-ayasi-2025-practical-tutorial": (
        "Combines a broad tutorial with controlled neuron, code, framework, and proxy-energy experiments.",
        "Software experiments only; no physical neuromorphic deployment is reported.",
        ["Energy is an operation-count proxy rather than instrumented chip energy."],
    ),
    "S30-alabdulwahid-2024-neuromorphic-architectures": (
        "Provides a compact comparison of representative neuromorphic architecture families.",
        "Descriptive hardware comparison without a traced model-to-chip route.",
        ["Software handoffs and measurement boundaries are not systematized."],
    ),
    "S31-tayaraninajaran-2021-event-based-sensing": (
        "Unifies event-based visual, auditory, and olfactory sensing principles.",
        "Covers sensor systems rather than trained SNN deployment toolchains.",
        ["Sensor address-event representation is not a model interchange format."],
    ),
    "S32-cimarelli-2025-neuromorphic-vision": (
        "Connects neuromorphic vision sensor hardware with algorithms and applications.",
        "Focuses on sensing rather than compute-chip execution routes.",
        ["No general compiler, mapper, or executable-semantics taxonomy is provided."],
    ),
    "S33-hegao-2026-four-stage": (
        "Organizes SNN development as a four-stage structural evolution from binary ANNs.",
        "Algorithmic perspective with no named physical deployment route.",
        ["The review deliberately narrows its treatment of codes, platforms, and applications."],
    ),
    "S34-luu-2026-foundation": (
        "Presents a broad foundation-and-progress overview according to the publisher abstract.",
        "Deployment depth remains unassessed because full text was only partially retrieved.",
        ["Full-text retrieval is required before negative coverage judgments are defensible."],
    ),
    "S35-caviglia-2026-neurotrain": (
        "Pairs a local-learning taxonomy with an open snnTorch benchmarking framework.",
        "Benchmarking is software-based and does not establish a named physical route.",
        ["Compiler, interchange, and cross-platform execution semantics remain outside scope."],
    ),
    "S36-du-2026-edge-modalities": (
        "Proposes a cross-modal edge-device benchmark according to the arXiv abstract.",
        "Deployment depth is unassessed because the body and supplement were not retrieved.",
        ["No axis-level absence claim is made from abstract-only access."],
    ),
    "S37-farsa-2026-gpu-riscv": (
        "Provides a GPU and RISC-V accelerator taxonomy and identifies incompatible reporting practices.",
        "Synthesizes accelerator studies but does not trace a standard network across complete routes.",
        ["The accepted manuscript is not yet the final version of record."],
    ),
}


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text())


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def survey_number(record: dict[str, object]) -> int:
    match = re.match(r"S(\d{2})-", str(record.get("id", "")))
    if not match:
        raise ValueError(f"invalid survey id {record.get('id')!r}")
    return int(match.group(1))


def candidate_id(candidate: dict[str, object]) -> str:
    value = candidate.get("id") or candidate.get("source_id")
    if not isinstance(value, str) or not value:
        raise ValueError(f"source candidate lacks an id: {candidate}")
    return value


def normalized_full_text_status(
    survey: dict[str, object], candidate: dict[str, object],
) -> str:
    raw = candidate.get("retrieval_status") or survey.get("full_text_status")
    try:
        return FULL_TEXT_STATUS_MAP[str(raw)]
    except KeyError as error:
        raise ValueError(f"unknown retrieval status {raw!r}") from error


def normalize_coverage(
    coverage: dict[str, object], full_text_status: str,
) -> dict[str, object]:
    if set(coverage) != set(AXES):
        raise ValueError(f"coverage axes are {sorted(coverage)}, expected A-L")
    result = copy.deepcopy(coverage)
    for axis in AXES:
        entry = result[axis]
        if not isinstance(entry, dict):
            raise ValueError(f"coverage {axis} is not an object")
        score = entry.get("score")
        needs_unassessed = full_text_status == "not_retrieved" or (
            full_text_status == "partial" and score == "none"
        )
        if needs_unassessed:
            entry["score"] = "unassessed"
            entry["basis"] = (
                "Not assessed because full text was not retrieved."
                if full_text_status == "not_retrieved"
                else "Not assessed because full text was only partially retrieved."
            )
            entry["locator"] = "Retrieval limit documented in the corresponding audit note."
    return result


def normalize_survey(
    survey: dict[str, object], candidate: dict[str, object], batch_name: str,
) -> dict[str, object]:
    full_text_status = normalized_full_text_status(survey, candidate)
    inspected = [
        *list(survey.get("retrieval_sources") or []),
        *list(survey.get("inspected_urls") or []),
        *list(candidate.get("inspected_urls") or []),
    ]
    if not inspected:
        inspected = [
            candidate.get("canonical_url") or candidate.get("url")
            or survey.get("canonical_url")
        ]
    survey_id = str(survey["id"])
    strongest, depth, omissions = D_SYNTHESIS.get(
        survey_id,
        (
            survey.get("strongest_contribution"),
            survey.get("deployment_depth"),
            survey.get("omissions"),
        ),
    )
    return {
        "id": survey_id,
        "source_id": str(survey["source_id"]),
        "full_text_status": full_text_status,
        "retrieval_sources": list(dict.fromkeys(str(url) for url in inspected if url)),
        "coverage": normalize_coverage(survey["coverage"], full_text_status),
        "strongest_contribution": str(strongest),
        "deployment_depth": str(depth),
        "omissions": list(omissions),
        "verification": {
            "status": "verified" if full_text_status == "verified" else "provisional",
            "reviewed_on": "2026-09-16",
            "reviewer": f"exa-batch-{batch_name.lower()}",
        },
    }


def normalize_source(
    candidate: dict[str, object], survey: dict[str, object], fallback: dict[str, object],
) -> dict[str, object]:
    source_id = candidate_id(candidate)
    retrieval_raw = str(
        candidate.get("retrieval_status") or survey.get("retrieval_status")
        or fallback.get("retrieval_status")
    )
    source_type_raw = str(
        candidate.get("source_type") or survey.get("source_type")
        or fallback.get("source_type")
    )
    canonical_url = (
        candidate.get("canonical_url") or candidate.get("url") or survey.get("canonical_url")
        or fallback.get("url")
    )
    doi = candidate.get("doi") or survey.get("doi") or fallback.get("doi")
    if isinstance(doi, str) and doi.startswith("unassigned:"):
        doi = None
    accepted_manuscript_note = (
        "Source is a peer-reviewed accepted manuscript, not the final version of record."
    )
    notes = str(candidate.get("notes") or survey.get("notes") or fallback.get("notes") or "")
    if source_type_raw == "accepted_manuscript":
        notes = notes.replace(accepted_manuscript_note, "").strip()
    note_parts = [notes]
    if not doi:
        doi = None
        note_parts.append("No DOI was established during the audit.")
    if source_type_raw == "accepted_manuscript":
        note_parts.append(accepted_manuscript_note)
    locators = (
        candidate.get("locators") or survey.get("locators") or fallback.get("locators")
        or ["Audit note"]
    )
    return {
        "id": source_id,
        "canonical_key": source_id,
        "title": str(candidate.get("title") or survey.get("title") or fallback.get("title")),
        "authors": str(candidate.get("authors") or survey.get("authors") or fallback.get("authors")),
        "year": int(candidate.get("year") or survey.get("year") or fallback.get("year")),
        "venue": str(candidate.get("venue") or survey.get("venue") or fallback.get("venue")),
        "doi": str(doi) if doi is not None else None,
        "url": str(canonical_url),
        "source_type": SOURCE_TYPE_MAP.get(source_type_raw, source_type_raw),
        "retrieval_status": SOURCE_RETRIEVAL_MAP[retrieval_raw],
        "verification_status": (
            "verified" if SOURCE_RETRIEVAL_MAP[retrieval_raw] == "full_text" else "provisional"
        ),
        "retrieved_on": "2026-09-16",
        "locators": [str(locator) for locator in locators],
        "aliases": [],
        "notes": " ".join(part for part in note_parts if part).strip(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validate merge inputs without writing")
    args = parser.parse_args()

    batch_paths = [BATCH_DIR / f"batch-{name}.json" for name in "ABCD"]
    batches = [read_json(path) for path in batch_paths]
    source_registry_path = ROOT / "data/source-registry.json"
    registry = read_json(source_registry_path)
    existing_sources = {record["id"]: record for record in registry["sources"]}
    all_surveys: list[dict[str, object]] = []
    candidate_sources: dict[str, dict[str, object]] = {}

    for path, batch in zip(batch_paths, batches):
        batch_name = str(batch["batch"])
        candidates = {
            candidate_id(candidate): candidate for candidate in batch["source_candidates"]
        }
        normalized_surveys = []
        inspected_urls: set[str] = set()
        for survey in batch["surveys"]:
            candidate = candidates[str(survey["source_id"])]
            normalized = normalize_survey(survey, candidate, batch_name)
            normalized_surveys.append(normalized)
            all_surveys.append(normalized)
            source_id = str(survey["source_id"])
            candidate_sources[source_id] = normalize_source(
                candidate, survey, existing_sources.get(source_id, {}),
            )
            inspected_urls.update(normalized["retrieval_sources"])
        batch["surveys"] = sorted(normalized_surveys, key=survey_number)
        batch["discovery_results_returned"] = batch["sources_reviewed"]
        batch["sources_reviewed_definition"] = (
            "Sum of numResults across Exa discovery searches, not a count of documents "
            "used as evidence."
        )
        batch["inspected_url_count"] = len(inspected_urls)
        if not args.check:
            write_json(path, batch)

    survey_numbers = [survey_number(record) for record in all_surveys]
    if sorted(survey_numbers) != list(range(1, 38)):
        raise ValueError(f"expected S01-S37 exactly, found {sorted(survey_numbers)}")

    existing = {record["id"]: record for record in registry["sources"]}
    existing.update(candidate_sources)
    registry["sources"] = [existing[key] for key in sorted(existing)]

    coverage_document = {
        "schema_version": 1,
        "surveys": sorted(all_surveys, key=survey_number),
    }
    if args.check:
        print(
            f"merge-prior-survey-batches: checked {len(all_surveys)} surveys and "
            f"{len(candidate_sources)} sources"
        )
        return 0
    write_json(source_registry_path, registry)
    write_json(ROOT / "data/prior-survey-coverage.json", coverage_document)
    print(
        f"merge-prior-survey-batches: wrote {len(all_surveys)} surveys and "
        f"{len(candidate_sources)} source candidates"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
