#!/usr/bin/env python3
"""Generate Section 1's prior-survey coverage matrix from canonical inputs.

The source coverage matrix remains twelve-dimensional. This reader-facing table
merges it into eight display columns, retaining the stronger score within each
approved pair. Row identity, coverage, verification status, author labels, and
years are all read from structured canonical data. No legacy survey ledger or
hand-maintained list of survey identifiers participates in generation.
"""
from __future__ import annotations

import html
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent

DISPLAY_COLUMNS = (
    ("Codes &amp; neurons", "Codes", ("A", "B")),
    ("Training &amp; conversion", "Conversion", ("C", "D")),
    ("Software frameworks", "Software", ("E",)),
    ("Compilers &amp; interchange", "Compilers", ("F", "G")),
    ("Hardware platforms", "Hardware", ("H",)),
    ("Boundary semantics", "Boundaries", ("I",)),
    ("Evidence types", "Evidence", ("J",)),
    ("Traced chip routes", "Routes", ("L",)),
)
SCORE_RANK = {"full": 3, "partial": 2, "mentioned": 1, "none": 0}
CELL_STYLE = {
    3: ("cov-full", "Full"),
    2: ("cov-part", "Partial"),
    1: ("cov-ment", "Mentioned"),
    0: ("cov-none", ""),
}


def load_json(path: Path) -> dict[str, Any]:
    try:
        document = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"cannot read JSON from {path}: {error}") from error
    if not isinstance(document, dict):
        raise ValueError(f"expected a JSON object in {path}")
    return document


def require_string(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a nonempty string")
    return value.strip()


def coverage_scores(survey: dict[str, Any], label: str) -> dict[str, str]:
    coverage = survey.get("coverage")
    if not isinstance(coverage, dict):
        raise ValueError(f"{label}.coverage must be an object")
    scores: dict[str, str] = {}
    for axis, record in coverage.items():
        if not isinstance(record, dict):
            raise ValueError(f"{label}.coverage.{axis} must be an object")
        score = record.get("score")
        if score not in SCORE_RANK:
            raise ValueError(f"{label}.coverage.{axis}.score is invalid: {score!r}")
        scores[str(axis)] = score
    expected_axes = set("ABCDEFGHIJKL")
    if set(scores) != expected_axes:
        raise ValueError(
            f"{label}.coverage must contain axes A-L exactly; found {sorted(scores)}"
        )
    return scores


def canonical_surveys(coverage_document: dict[str, Any]) -> dict[str, dict[str, Any]]:
    surveys = coverage_document.get("surveys")
    if not isinstance(surveys, list) or len(surveys) != 37:
        raise ValueError("prior-survey coverage must contain exactly 37 surveys")
    result: dict[str, dict[str, Any]] = {}
    for index, survey in enumerate(surveys):
        label = f"prior-survey-coverage.surveys[{index}]"
        if not isinstance(survey, dict):
            raise ValueError(f"{label} must be an object")
        source_id = require_string(survey.get("source_id"), f"{label}.source_id")
        if source_id in result:
            raise ValueError(f"prior-survey coverage repeats source_id {source_id!r}")
        if survey.get("full_text_status") != "verified":
            raise ValueError(f"{label} is not a verified full-text survey")
        coverage_scores(survey, label)
        result[source_id] = survey
    return result


def verify_family_summary(
    summary_document: dict[str, Any], surveys: dict[str, dict[str, Any]]
) -> None:
    """Reject a stale generated family view before using it as the table cross-check."""
    if summary_document.get("view") != "prior-survey-family-summary":
        raise ValueError("prior-survey family summary has the wrong view identifier")
    families = summary_document.get("families")
    if not isinstance(families, list) or not families:
        raise ValueError("prior-survey family summary must contain nonempty families")

    expected_ids = set(surveys)
    for family_index, family in enumerate(families):
        label = f"prior-survey-family-summary.families[{family_index}]"
        if not isinstance(family, dict):
            raise ValueError(f"{label} must be an object")
        axes = family.get("coverage_axes")
        records = family.get("surveys")
        if not isinstance(axes, list) or not axes:
            raise ValueError(f"{label}.coverage_axes must be a nonempty array")
        if not isinstance(records, list) or len(records) != len(surveys):
            raise ValueError(f"{label}.surveys must contain all 37 canonical surveys")
        if family.get("survey_count") != len(surveys):
            raise ValueError(f"{label}.survey_count is stale")

        actual_ids: list[str] = []
        actual_scores: Counter[str] = Counter()
        for record_index, record in enumerate(records):
            record_label = f"{label}.surveys[{record_index}]"
            if not isinstance(record, dict):
                raise ValueError(f"{record_label} must be an object")
            source_id = require_string(record.get("source_id"), f"{record_label}.source_id")
            actual_ids.append(source_id)
            canonical = surveys.get(source_id)
            if canonical is None:
                raise ValueError(f"{record_label} is absent from canonical coverage")
            observed = record.get("coverage")
            if not isinstance(observed, dict):
                raise ValueError(f"{record_label}.coverage must be an object")
            canonical_scores = coverage_scores(canonical, f"canonical {source_id}")
            if set(observed) != set(axes):
                raise ValueError(f"{record_label}.coverage axes do not match its family")
            for axis in axes:
                score_record = observed.get(axis)
                if not isinstance(score_record, dict) or score_record.get("score") != canonical_scores[axis]:
                    raise ValueError(f"{record_label}.coverage.{axis} is stale")
                actual_scores[canonical_scores[axis]] += 1
        if set(actual_ids) != expected_ids or len(actual_ids) != len(set(actual_ids)):
            raise ValueError(f"{label}.surveys is not a one-to-one projection of canonical coverage")
        expected_counts = {
            **{score: actual_scores[score] for score in SCORE_RANK},
            "unassessed": 0,
        }
        if family.get("score_counts") != expected_counts:
            raise ValueError(f"{label}.score_counts is stale")


def source_index(source_document: dict[str, Any], survey_ids: set[str]) -> dict[str, dict[str, Any]]:
    records = source_document.get("sources")
    if not isinstance(records, list):
        raise ValueError("source registry must contain a sources array")
    sources: dict[str, dict[str, Any]] = {}
    for record in records:
        if not isinstance(record, dict) or not isinstance(record.get("id"), str):
            continue
        sources[record["id"]] = record
    missing = sorted(survey_ids - set(sources))
    if missing:
        raise ValueError(f"source registry is missing surveyed works: {missing}")
    for source_id in survey_ids:
        source = sources[source_id]
        require_string(source.get("authors"), f"source {source_id}.authors")
        if not isinstance(source.get("year"), int):
            raise ValueError(f"source {source_id}.year must be an integer")
    return sources


def citation_key_index(alias_document: dict[str, Any], survey_ids: set[str]) -> dict[str, str]:
    """Use the generated bibliography aliases without maintaining survey citation keys."""
    aliases_by_source: dict[str, list[str]] = {source_id: [] for source_id in survey_ids}
    for alias, source_id in alias_document.items():
        if source_id in aliases_by_source and isinstance(alias, str) and alias:
            aliases_by_source[source_id].append(alias)
    return {
        source_id: min(aliases) if aliases else source_id
        for source_id, aliases in aliases_by_source.items()
    }


def short_author_label(authors: str) -> str:
    """Return a compact first-author label without maintaining name exceptions."""
    has_multiple_authors = "et al" in authors.lower() or bool(re.search(r";|,|\band\b", authors))
    first = re.sub(r"\bet al\.?\s*$", "", authors, flags=re.IGNORECASE).strip()
    first = re.split(r";|,|\band\b", first, maxsplit=1)[0].strip()
    words = [word for word in re.split(r"\s+", first) if word and word != "et"]
    if not words:
        raise ValueError(f"cannot derive an author label from {authors!r}")
    surname = words[-1].rstrip(".")
    return f"{surname} et al." if has_multiple_authors else surname


def display_score(scores: dict[str, str], axes: tuple[str, ...]) -> int:
    return max(SCORE_RANK[scores[axis]] for axis in axes)


def tag_for(scores: dict[str, str]) -> tuple[str, str]:
    """Classify a row from its coverage, rather than its identifier or title."""
    rank = {axis: SCORE_RANK[score] for axis, score in scores.items()}
    if rank["L"] >= 2:
        return "Deployment", "tag-evaluation"
    if rank["J"] >= 2:
        return "Evaluation", "tag-evaluation"
    if rank["H"] >= 2:
        return "Hardware", "tag-hardware"
    if max(rank["F"], rank["G"]) >= 2:
        return "Toolchains", "tag-software"
    if rank["E"] >= 2:
        return "Frameworks", "tag-software"
    if rank["D"] >= 2:
        return "Conversion", "tag-methods"
    if rank["C"] >= 2:
        return "Training", "tag-methods"
    return "Overview", "tag-overview"


def end_of_div(text: str, start: int) -> int:
    """Return the index past the div that closes the wrapper beginning at start."""
    depth = 0
    for match in re.finditer(r"<div\b|</div>", text[start:]):
        depth += 1 if match.group(0) != "</div>" else -1
        if depth == 0:
            return start + match.end()
    raise ValueError("unbalanced Table 1 wrapper")


def render_table(
    surveys: dict[str, dict[str, Any]],
    sources: dict[str, dict[str, Any]],
    citation_keys: dict[str, str],
) -> str:
    rows: list[tuple[int, str, str]] = []
    for source_id, survey in surveys.items():
        source = sources[source_id]
        scores = coverage_scores(survey, f"canonical {source_id}")
        cells = []
        for _, _, axes in DISPLAY_COLUMNS:
            css_class, label = CELL_STYLE[display_score(scores, axes)]
            content = f"<span>{label}</span>" if label else ""
            cells.append(f'<td class="{css_class}">{content}</td>')
        tag, tag_class = tag_for(scores)
        author = html.escape(short_author_label(require_string(source["authors"], source_id)))
        year = source["year"]
        rows.append(
            (
                year,
                source_id,
                f'<tr><td>{author} <d-cite key="{html.escape(citation_keys[source_id])}"></d-cite>'
                f'<br><span class="survey-tag {tag_class}">{tag}</span></td>'
                f'<td class="ctr yr">{year}</td>{"".join(cells)}</tr>',
            )
        )
    rows.sort(key=lambda row: (row[0], row[1]))
    header = "\n".join(
        f'<th class="ctr" data-chip="{chip}">{title}</th>'
        for title, chip, _ in DISPLAY_COLUMNS
    )
    ours = (
        '<tr class="ours"><td><strong>Ours</strong></td><td class="ctr yr">2026</td>'
        + '<td class="cov-full"><span>Full</span></td>' * len(DISPLAY_COLUMNS)
        + "</tr>"
    )
    return f'''<div class="ptable-wrap l-page t1-wide cov-table" id="table-1" data-table-toolbar>
<table class="ptable">
<caption><b>Table 1:</b> Scope comparison of surveys on spiking neural networks, neuromorphic hardware, and ANN-to-SNN deployment. All 37 screened works are listed, ordered by year.</caption>
<thead><tr>
<th>Survey</th>
<th class="ctr yr" data-sort="num">Year</th>
{header}
</tr></thead>
<tbody>
{chr(10).join(row for _, _, row in rows)}
{ours}
</tbody>
</table>
<div class="t1-legend"><span><i class="sw sw-full"></i>surveyed</span><span><i class="sw sw-part"></i>partially surveyed</span><span><i class="sw sw-ment"></i>mentioned only</span><span><i class="sw sw-none"></i>not covered</span></div>
</div>'''


def build_table(root: Path | None = None) -> str:
    root = ROOT if root is None else root
    coverage_document = load_json(root / "data/prior-survey-coverage.json")
    summary_document = load_json(root / "data/generated/prior-survey-family-summary.json")
    source_document = load_json(root / "data/source-registry.json")
    alias_document = load_json(root / "data/refmap.json")
    surveys = canonical_surveys(coverage_document)
    verify_family_summary(summary_document, surveys)
    sources = source_index(source_document, set(surveys))
    citation_keys = citation_key_index(alias_document, set(surveys))
    return render_table(surveys, sources, citation_keys)


def main() -> None:
    table = build_table()
    section_path = ROOT / "site/sec-01.html"
    section = section_path.read_text()
    marker = "<!-- TABLE1 -->"
    if marker in section:
        if section.count(marker) != 1:
            raise ValueError("Section 1 must contain TABLE1 placement marker exactly once")
        replacement = section.replace(marker, table)
    else:
        start = section.index('<div class="ptable-wrap')
        end = end_of_div(section, start)
        replacement = section[:start] + table + section[end:]
    section_path.write_text(replacement)
    print("37 verified surveys, 8 display columns, plus Ours")


if __name__ == "__main__":
    main()
