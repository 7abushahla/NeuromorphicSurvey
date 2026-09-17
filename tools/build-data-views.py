#!/usr/bin/env python3
"""Build deterministic, provenance-preserving downstream evidence views."""
from __future__ import annotations

import argparse
import json
import os
import runpy
import sys
import tempfile
import unittest
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_DIR = ROOT / "data/generated"
VIEW_FILENAMES = (
    "prior-survey-family-summary.json",
    "prior-survey-targets-summary.json",
    "evidence-population-summary.json",
    "claim-index.json",
    "route-index.json",
    "measurement-index.json",
    "figure-inputs.json",
)
EVIDENCE_POPULATION_FAMILY_ORDER = (
    "classical-conversion",
    "low-latency-conversion",
    "mixed-timestep",
    "early-exit",
    "population-coding",
    "direct-training",
    "hardware-accelerator",
    "application",
)
AXIS_LABELS = {
    "A": "neuron models",
    "B": "encodings and neural codes",
    "C": "direct training",
    "D": "ANN-to-SNN conversion",
    "E": "software frameworks",
    "F": "compilers and hardware mapping",
    "G": "interchange formats",
    "H": "hardware platforms",
    "I": "edge semantics",
    "J": "evidence classification",
    "K": "applications with measured results",
    "L": "end-to-end traceable routes",
}
FAMILY_DEFINITIONS = (
    ("learning", "models and learning", ("A", "C", "D")),
    ("coding", "coding", ("B",)),
    ("software", "software", ("E", "F", "G")),
    ("hardware", "hardware", ("H",)),
    ("benchmarking", "benchmarking", ("J",)),
    ("deployment", "deployment", ("I", "L")),
    ("applications", "applications", ("K",)),
)
EVIDENCE_BOUNDARIES = {
    "E1": "physical hardware with latency, energy, power, or system performance measurement",
    "E2": "physical hardware with accuracy or fidelity measurement only",
    "E3": "documented but unexercised deployment route",
    "E4": "hardware model, synthesis, or cycle-level simulation without fabricated silicon",
    "E5": "software simulation, analytical proxy, or algorithm-only evidence",
}


class DataViewError(ValueError):
    """Raised when canonical inputs cannot produce a defensible view."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise DataViewError(message)


def require_unique_ids(records: Iterable[dict[str, Any]], label: str) -> None:
    ids = [record.get("id") for record in records]
    require(all(isinstance(item, str) and item for item in ids), f"{label} has a missing ID")
    duplicates = sorted(item for item, count in Counter(ids).items() if count > 1)
    require(not duplicates, f"{label} has duplicate IDs: {duplicates}")


def sorted_unique_strings(values: Iterable[Any]) -> list[str]:
    materialized = [str(value) for value in values]
    return sorted(dict.fromkeys(materialized))


def build_source_lookup(sources: list[dict[str, Any]]) -> dict[str, object]:
    require_unique_ids(sources, "source registry")
    records = {str(source["id"]): source for source in sources}
    aliases: dict[str, str] = {}
    for source in sources:
        canonical_id = str(source["id"])
        for alias_value in source.get("aliases", []):
            alias = str(alias_value)
            require(alias not in records, f"source alias collides with canonical ID: {alias}")
            prior = aliases.get(alias)
            require(
                prior in (None, canonical_id),
                f"source alias resolves to multiple canonical IDs: {alias}",
            )
            aliases[alias] = canonical_id
    return {"records": records, "aliases": aliases}


def canonical_source_id(source_id: Any, source_lookup: dict[str, object]) -> str:
    value = str(source_id)
    records = source_lookup["records"]
    aliases = source_lookup["aliases"]
    assert isinstance(records, dict)
    assert isinstance(aliases, dict)
    if value in records:
        return value
    if value in aliases:
        return str(aliases[value])
    raise DataViewError(f"unknown source ID: {value}")


def canonical_source_ids(
    source_ids: Iterable[Any], source_lookup: dict[str, object]
) -> list[str]:
    return sorted_unique_strings(
        canonical_source_id(source_id, source_lookup) for source_id in source_ids
    )


def source_statuses(
    source_ids: Iterable[Any], source_lookup: dict[str, object]
) -> list[dict[str, Any]]:
    records = source_lookup["records"]
    assert isinstance(records, dict)
    statuses = []
    for source_id in canonical_source_ids(source_ids, source_lookup):
        source = records[source_id]
        statuses.append(
            {
                "source_id": source_id,
                "retrieval_status": source.get("retrieval_status"),
                "verification_status": source.get("verification_status"),
            }
        )
    return statuses


def conservative_verification_status(
    source_ids: Iterable[Any], source_lookup: dict[str, object]
) -> str:
    statuses = source_statuses(source_ids, source_lookup)
    require(statuses, "a generated evidence record has no sources")
    verification = {status["verification_status"] for status in statuses}
    retrieval = {status["retrieval_status"] for status in statuses}
    if "rejected" in verification:
        return "rejected"
    if "conflicted" in verification:
        return "conflicted"
    if verification != {"verified"} or retrieval != {"full_text"}:
        return "provisional"
    return "verified"


def registry_source_refs(
    source_ids: Iterable[Any], source_lookup: dict[str, object]
) -> list[dict[str, Any]]:
    records = source_lookup["records"]
    assert isinstance(records, dict)
    refs = []
    for source_id in canonical_source_ids(source_ids, source_lookup):
        refs.append(
            {
                "source_id": source_id,
                "locators": sorted_unique_strings(records[source_id].get("locators", [])),
            }
        )
    return refs


def normalize_source_refs(
    refs: Iterable[dict[str, Any]], source_lookup: dict[str, object]
) -> list[dict[str, Any]]:
    merged: dict[str, set[str]] = defaultdict(set)
    for ref in refs:
        require(isinstance(ref, dict), "source_refs entries must be objects")
        source_id = canonical_source_id(ref.get("source_id"), source_lookup)
        locators = ref.get("locators", [])
        require(isinstance(locators, list), f"source_ref locators must be a list: {source_id}")
        merged[source_id].update(str(locator) for locator in locators)
    return [
        {"source_id": source_id, "locators": sorted(merged[source_id])}
        for source_id in sorted(merged)
    ]


def merge_source_refs(
    refs: Iterable[dict[str, Any]],
    source_ids: Iterable[Any],
    source_lookup: dict[str, object],
) -> list[dict[str, Any]]:
    normalized = normalize_source_refs(refs, source_lookup)
    merged = {ref["source_id"]: set(ref["locators"]) for ref in normalized}
    for source_id in canonical_source_ids(source_ids, source_lookup):
        merged.setdefault(source_id, set())
    return [
        {"source_id": source_id, "locators": sorted(merged[source_id])}
        for source_id in sorted(merged)
    ]


def build_prior_survey_family_summary(
    surveys: list[dict[str, Any]],
    source_lookup: dict[str, object] | None = None,
) -> dict[str, Any]:
    families = []
    for key, label, axes in FAMILY_DEFINITIONS:
        score_counts: Counter[str] = Counter()
        survey_records = []
        for survey in sorted(surveys, key=lambda item: str(item["id"])):
            coverage = survey["coverage"]
            family_coverage = {
                axis: {
                    "score": coverage[axis]["score"],
                    "basis": coverage[axis]["basis"],
                    "locator": coverage[axis]["locator"],
                }
                for axis in axes
            }
            score_counts.update(item["score"] for item in family_coverage.values())
            source_id = str(survey["source_id"])
            if source_lookup is not None:
                source_id = canonical_source_id(source_id, source_lookup)
            survey_records.append(
                {
                    "id": survey["id"],
                    "source_id": source_id,
                    "full_text_status": survey["full_text_status"],
                    "retrieval_sources": sorted_unique_strings(
                        survey.get("retrieval_sources", [])
                    ),
                    "coverage": family_coverage,
                    "strongest_contribution": survey["strongest_contribution"],
                    "deployment_depth": survey["deployment_depth"],
                    "omissions": list(survey.get("omissions", [])),
                    "verification": survey["verification"],
                }
            )
        families.append(
            {
                "key": key,
                "label": label,
                "coverage_axes": list(axes),
                "axis_labels": {axis: AXIS_LABELS[axis] for axis in axes},
                "survey_count": len(survey_records),
                "score_counts": {
                    score: score_counts.get(score, 0)
                    for score in ("full", "partial", "mentioned", "none", "unassessed")
                },
                "surveys": survey_records,
            }
        )
    return {"families": families}


def build_prior_survey_targets_summary(
    surveys: list[dict[str, Any]],
    kinds_document: dict[str, Any],
    source_lookup: dict[str, object] | None = None,
) -> dict[str, Any]:
    kind_words = [str(kind["word"]) for kind in kinds_document["kinds"]]
    kind_bucket = {str(kind["word"]): str(kind["bucket"]) for kind in kinds_document["kinds"]}
    bucket_names = [str(bucket["name"]) for bucket in kinds_document["buckets"]]

    kind_survey_counts: dict[str, int] = {word: 0 for word in kind_words}
    bucket_survey_counts: dict[str, int] = {name: 0 for name in bucket_names}
    surveys_covering_all_three_buckets = 0
    survey_records = []
    for survey in sorted(surveys, key=lambda item: str(item["id"])):
        targets = survey.get("targets") or {}
        kinds = list(targets.get("kinds") or [])
        require(
            all(kind in kind_bucket for kind in kinds),
            f"survey {survey['id']} names an undeclared target kind",
        )
        buckets = sorted_unique_strings(kind_bucket[kind] for kind in kinds)
        for kind in kinds:
            kind_survey_counts[kind] += 1
        for bucket in buckets:
            bucket_survey_counts[bucket] += 1
        if set(buckets) == set(bucket_names):
            surveys_covering_all_three_buckets += 1
        source_id = str(survey["source_id"])
        if source_lookup is not None:
            source_id = canonical_source_id(source_id, source_lookup)
        survey_records.append(
            {
                "id": survey["id"],
                "source_id": source_id,
                "kinds": kinds,
                "buckets": buckets,
            }
        )
    return {
        "survey_total": len(survey_records),
        "kind_survey_counts": kind_survey_counts,
        "bucket_survey_counts": bucket_survey_counts,
        "surveys_covering_all_three_buckets": surveys_covering_all_three_buckets,
        "surveys": survey_records,
    }


def build_evidence_population_summary(
    paper_payload: dict[str, Any],
    target_kinds_payload: dict[str, Any],
) -> dict[str, Any]:
    """Population and family counts for evidence-papers.json, plus deploying records.

    The population_counts block below is built with the exact counting rule of
    tools/check-counts.py's population_counts() (loaded here via runpy, since
    tools/ is a script directory rather than an importable package), so that
    check-counts.py's staleness guard can compare a future edit against this
    view without the two ever disagreeing on how a count is taken.
    """
    papers = paper_payload["papers"]
    count_module = runpy.run_path(str(ROOT / "tools/check-counts.py"))
    counts, count_errors = count_module["population_counts"](paper_payload)
    require(not count_errors, "; ".join(count_errors))

    kind_bucket = {
        str(kind["word"]): str(kind["bucket"]) for kind in target_kinds_payload["kinds"]
    }

    record_total = len(papers)
    source_groups: dict[tuple[str, ...], list[str]] = defaultdict(list)
    for paper in papers:
        source_groups[tuple(sorted(paper.get("sources") or []))].append(str(paper["id"]))
    paper_total = len(source_groups)

    family_counts: dict[str, Counter[str]] = {
        family: Counter() for family in EVIDENCE_POPULATION_FAMILY_ORDER
    }
    for paper in papers:
        family = paper.get("family")
        require(
            family in family_counts,
            f"evidence paper {paper.get('id')!r} has family {family!r}, "
            "not one of the eight families Table 31 rows",
        )
        family_counts[family][paper["population"]] += 1

    family_population = []
    for family in EVIDENCE_POPULATION_FAMILY_ORDER:
        tally = family_counts[family]
        algorithm = tally.get("algorithm", 0)
        deployment = tally.get("deployment", 0)
        both = tally.get("both", 0)
        family_population.append(
            {
                "family": family,
                "algorithm": algorithm,
                "deployment": deployment,
                "both": both,
                "total": algorithm + deployment + both,
            }
        )

    deploying_records = []
    for paper in sorted(papers, key=lambda item: str(item["id"])):
        if paper.get("population") not in ("deployment", "both"):
            continue
        target_kind = paper.get("target_kind")
        bucket = kind_bucket.get(str(target_kind))
        require(
            bucket is not None,
            f"evidence paper {paper['id']!r} has target_kind {target_kind!r}, "
            "not one of data/target-kinds.json's declared kinds",
        )
        deploying_records.append(
            {
                "id": paper["id"],
                "family": paper["family"],
                "population": paper["population"],
                "target_kind": target_kind,
                "target_qualifier": paper.get("target_qualifier"),
                "bucket": bucket,
            }
        )

    return {
        "record_total": record_total,
        "paper_total": paper_total,
        "population_counts": counts,
        "family_population": family_population,
        "deploying_records": deploying_records,
    }


def build_claim_index(
    claims: list[dict[str, Any]],
    audit_claims: list[dict[str, Any]],
    source_lookup: dict[str, object],
) -> dict[str, Any]:
    audits_by_id = {str(claim["id"]): claim for claim in audit_claims}
    require_unique_ids(audit_claims, "audited claims")
    require(
        set(audits_by_id) == {str(claim["id"]) for claim in claims},
        "canonical claims and audited source_refs do not cover the same claim IDs",
    )
    indexed = []
    for claim in sorted(claims, key=lambda item: str(item["id"])):
        audit_claim = audits_by_id[str(claim["id"])]
        source_ids = canonical_source_ids(claim["source_ids"], source_lookup)
        refs = normalize_source_refs(audit_claim["source_refs"], source_lookup)
        conflicts = sorted_unique_strings(claim.get("conflicts_with", []))
        measurement_boundary = claim.get("measurement_boundary")
        scope = claim.get("scope")
        status = claim["verification_status"]
        record = {
            "id": claim["id"],
            "claim_type": claim["claim_type"],
            "statement": claim["statement"],
            "evidence_class": claim.get("evidence_class"),
            "reports_deployment_evidence": claim["reports_deployment_evidence"],
            "source_ids": source_ids,
            "locators": sorted_unique_strings(claim.get("locators", [])),
            "source_refs": refs,
            "source_statuses": source_statuses(source_ids, source_lookup),
            "verification_status": status,
            "measurement_boundary": measurement_boundary,
            "conflicts_with": conflicts,
            "scope": scope,
            "caveats": {
                "scope": scope,
                "measurement_boundary": measurement_boundary,
                "conflicts_with": conflicts,
            },
            "interpretation_flags": {
                "reports_deployment_evidence": claim["reports_deployment_evidence"],
                "has_evidence_class": claim.get("evidence_class") is not None,
                "has_measurement_boundary": measurement_boundary is not None,
                "has_conflict": bool(conflicts),
                "requires_qualified_reading": bool(
                    conflicts or measurement_boundary or scope or status != "verified"
                ),
            },
        }
        if "inspection_paths" in claim:
            record["inspection_paths"] = list(claim["inspection_paths"])
        indexed.append(record)
    return {"claims": indexed}


def platform_capability_source_refs(
    capability: dict[str, Any], source_lookup: dict[str, object]
) -> list[dict[str, Any]]:
    refs: list[dict[str, Any]] = []
    if capability.get("source_ids"):
        locators = list(capability.get("locators", []))
        refs.extend(
            {"source_id": source_id, "locators": locators}
            for source_id in capability["source_ids"]
        )
    pairs = (
        ("official_technical_source_id", "source_locator"),
        ("official_exercised_example_source_id", "official_exercised_example_locator"),
    )
    for source_key, locator_key in pairs:
        source_id = capability.get(source_key)
        if source_id:
            locator = capability.get(locator_key)
            refs.append(
                {
                    "source_id": source_id,
                    "locators": [locator] if locator else [],
                }
            )
    return normalize_source_refs(refs, source_lookup)


def normalize_platform_capability(
    capability: dict[str, Any], source_lookup: dict[str, object]
) -> dict[str, Any]:
    refs = platform_capability_source_refs(capability, source_lookup)
    source_ids = [ref["source_id"] for ref in refs]
    fields = (
        "id",
        "platform_id",
        "manufacturer",
        "chip_generation",
        "contract_field",
        "contract_requirement",
        "capability_status",
        "support_detail",
        "mapper_limits",
        "precision_constraints",
        "routing_constraints",
        "host_responsibilities",
        "access_path",
        "route_state",
        "document_date",
        "document_version",
        "toolchain_version",
        "verification_status",
        "reviewed_on",
    )
    normalized = {field: capability.get(field) for field in fields}
    normalized.update(
        {
            "route_ids": sorted_unique_strings(capability.get("route_ids", [])),
            "official_technical_source_id": (
                canonical_source_id(
                    capability["official_technical_source_id"], source_lookup
                )
                if capability.get("official_technical_source_id")
                else None
            ),
            "source_locator": capability.get("source_locator"),
            "official_exercised_example_source_id": (
                canonical_source_id(
                    capability["official_exercised_example_source_id"], source_lookup
                )
                if capability.get("official_exercised_example_source_id")
                else None
            ),
            "official_exercised_example_locator": capability.get(
                "official_exercised_example_locator"
            ),
            "source_ids": source_ids,
            "source_refs": refs,
            "source_statuses": source_statuses(source_ids, source_lookup),
        }
    )
    return normalized


def node_summary(node: dict[str, Any] | None) -> dict[str, Any] | None:
    if node is None:
        return None
    return {
        "id": node["id"],
        "type": node["type"],
        "name": node["name"],
        "layer": node["layer"],
    }


def normalize_route_edge(
    edge: dict[str, Any],
    *,
    node_ids: set[str],
    source_lookup: dict[str, object],
    schema: dict[str, object],
    node_lookup: dict[str, dict[str, Any]] | None = None,
    capabilities: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    edge_id = str(edge["id"])
    from_id = str(edge["from"])
    to_id = str(edge["to"])
    require(from_id in node_ids, f"route {edge_id} has unknown from endpoint: {from_id}")
    require(to_id in node_ids, f"route {edge_id} has unknown to endpoint: {to_id}")

    legacy_evidence = edge.get("evidence")
    rich_evidence = edge.get("evidence_class")
    if rich_evidence is not None and legacy_evidence is not None:
        require(
            rich_evidence == legacy_evidence,
            f"route {edge_id} has conflicting evidence fields",
        )
    evidence_class = rich_evidence if rich_evidence is not None else legacy_evidence
    valid_evidence = set(schema["evidence_classes"])
    require(
        evidence_class is None or evidence_class in valid_evidence,
        f"route {edge_id} has invalid evidence class: {evidence_class}",
    )

    route_state = edge.get("route_state")
    require(
        route_state is None or route_state in set(schema["route_states"]),
        f"route {edge_id} has invalid route state: {route_state}",
    )
    capability_class = edge.get("capability_class")
    require(
        capability_class is None
        or capability_class in set(schema["platform_capability_statuses"]),
        f"route {edge_id} has invalid capability class: {capability_class}",
    )

    source_ids = canonical_source_ids(edge.get("sources", []), source_lookup)
    if "source_refs" in edge:
        refs = normalize_source_refs(edge["source_refs"], source_lookup)
    else:
        refs = registry_source_refs(source_ids, source_lookup)

    legacy_preserves = list(edge.get("preserves", []))
    legacy_breaks = list(edge.get("breaks", []))
    is_rich = any(
        field in edge
        for field in (
            "typed_input",
            "typed_output",
            "preserved",
            "transformed",
            "rejected",
            "source_refs",
        )
    )
    normalized_capabilities = sorted(
        capabilities or [], key=lambda item: str(item["id"])
    )
    return {
        "id": edge_id,
        "from": from_id,
        "to": to_id,
        "from_node": node_summary(node_lookup.get(from_id) if node_lookup else None),
        "to_node": node_summary(node_lookup.get(to_id) if node_lookup else None),
        "typed_input": edge.get("typed_input"),
        "typed_output": edge.get("typed_output"),
        "preserved": list(edge.get("preserved", legacy_preserves)),
        "transformed": list(edge.get("transformed", [])),
        "rejected": list(edge.get("rejected", [])),
        "legacy_preserves": legacy_preserves,
        "legacy_breaks": legacy_breaks,
        "mechanism": edge["mechanism"],
        "notes": edge.get("notes"),
        "capability_class": capability_class,
        "route_state": route_state,
        "reports_deployment_evidence": edge.get("reports_deployment_evidence"),
        "evidence": legacy_evidence,
        "evidence_class": evidence_class,
        "measurement_boundary": edge.get("measurement_boundary"),
        "platform_generation": edge.get("platform_generation"),
        "toolchain_version": edge.get("toolchain_version"),
        "source_ids": source_ids,
        "source_refs": refs,
        "source_statuses": source_statuses(source_ids, source_lookup),
        "input_shape": "rich" if is_rich else "legacy",
        "platform_capabilities": normalized_capabilities,
    }


def build_route_index(
    edges: list[dict[str, Any]],
    nodes: list[dict[str, Any]],
    capabilities: list[dict[str, Any]],
    source_lookup: dict[str, object],
    schema: dict[str, object],
) -> dict[str, Any]:
    node_lookup = {str(node["id"]): node for node in nodes}
    normalized_capabilities = [
        normalize_platform_capability(capability, source_lookup)
        for capability in capabilities
    ]
    capabilities_by_route: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for capability in normalized_capabilities:
        for route_id in capability["route_ids"]:
            capabilities_by_route[route_id].append(capability)

    normalized_nodes = []
    for node in sorted(nodes, key=lambda item: str(item["id"])):
        source_ids = canonical_source_ids(node.get("sources", []), source_lookup)
        normalized_nodes.append(
            {
                "id": node["id"],
                "type": node["type"],
                "name": node["name"],
                "layer": node["layer"],
                "summary": node["summary"],
                "attributes": node["attributes"],
                "source_ids": source_ids,
                "source_refs": registry_source_refs(source_ids, source_lookup),
                "source_statuses": source_statuses(source_ids, source_lookup),
            }
        )
    routes = [
        normalize_route_edge(
            edge,
            node_ids=set(node_lookup),
            node_lookup=node_lookup,
            source_lookup=source_lookup,
            schema=schema,
            capabilities=capabilities_by_route.get(str(edge["id"]), []),
        )
        for edge in sorted(edges, key=lambda item: str(item["id"]))
    ]
    return {
        "nodes": normalized_nodes,
        "routes": routes,
        "platform_capabilities": sorted(
            normalized_capabilities, key=lambda item: str(item["id"])
        ),
    }


def build_measurement_index(
    papers: list[dict[str, Any]], source_lookup: dict[str, object]
) -> dict[str, Any]:
    measurements = []
    for paper in sorted(papers, key=lambda item: str(item["id"])):
        evidence_class = paper["evidence"]
        source_ids = canonical_source_ids(paper.get("sources", []), source_lookup)
        measurements.append(
            {
                "id": paper["id"],
                "title": paper["title"],
                "authors": paper["authors"],
                "year": paper["year"],
                "venue": paper["venue"],
                "url": paper["url"],
                "family": paper["family"],
                "population": paper["population"],
                "method_summary": paper["method_summary"],
                "neuron": paper["neuron"],
                "reset": paper["reset"],
                "encoding": paper["encoding"],
                "input_encoding": paper["input_encoding"],
                "timesteps": paper["timesteps"],
                "metric": paper["what_was_measured"],
                "boundary": {
                    "evidence_class": evidence_class,
                    "description": EVIDENCE_BOUNDARIES[evidence_class],
                    "paper_specific_notes": paper["evidence_notes"],
                },
                "workload": list(paper["datasets"]),
                "platform": {
                    "target_hardware": paper["target_hardware"],
                    "toolchain": paper["toolchain"],
                },
                "comparability_notes": paper["evidence_notes"],
                "evidence_class": evidence_class,
                "is_physical_measurement": evidence_class in {"E1", "E2"},
                "source_ids": source_ids,
                "source_refs": registry_source_refs(source_ids, source_lookup),
                "source_statuses": source_statuses(source_ids, source_lookup),
                "verification_status": conservative_verification_status(
                    source_ids, source_lookup
                ),
            }
        )
    return {"measurements": measurements}


def combine_verification_statuses(*statuses: str) -> str:
    priority = {"verified": 0, "provisional": 1, "conflicted": 2, "rejected": 3}
    require(all(status in priority for status in statuses), f"invalid verification status: {statuses}")
    return max(statuses, key=lambda status: priority[status])


def build_figure_inputs(
    *,
    papers: list[dict[str, Any]],
    claims: list[dict[str, Any]],
    routes: list[dict[str, Any]],
    capabilities: list[dict[str, Any]],
    source_lookup: dict[str, object],
    schema: dict[str, object],
) -> dict[str, Any]:
    measurements = build_measurement_index(papers, source_lookup)["measurements"]
    entries: list[dict[str, Any]] = []
    for measurement in measurements:
        classification = (
            "measured" if measurement["is_physical_measurement"] else "conceptual"
        )
        entries.append(
            {
                "id": f"paper:{measurement['id']}",
                "origin_type": "paper",
                "origin_id": measurement["id"],
                "classification": classification,
                "classification_basis": (
                    "E1 or E2 physical measurement"
                    if classification == "measured"
                    else "E3, E4, or E5 non-physical evidence boundary"
                ),
                "label": measurement["title"],
                "metric": measurement["metric"],
                "boundary": measurement["boundary"],
                "workload": measurement["workload"],
                "platform": measurement["platform"],
                "evidence_class": measurement["evidence_class"],
                "source_ids": measurement["source_ids"],
                "source_refs": measurement["source_refs"],
                "source_statuses": measurement["source_statuses"],
                "verification_status": measurement["verification_status"],
                "eligible_for_substantive_use": measurement["verification_status"]
                == "verified",
            }
        )

    for claim in sorted(claims, key=lambda item: str(item["id"])):
        source_ids = canonical_source_ids(claim.get("source_ids", []), source_lookup)
        refs = (
            normalize_source_refs(claim["source_refs"], source_lookup)
            if claim.get("source_refs")
            else registry_source_refs(source_ids, source_lookup)
        )
        source_status = conservative_verification_status(source_ids, source_lookup)
        canonical_status = claim["verification_status"]
        status = combine_verification_statuses(canonical_status, source_status)
        measured = bool(
            claim.get("reports_deployment_evidence")
            and claim.get("evidence_class") in {"E1", "E2"}
            and claim.get("measurement_boundary")
        )
        entries.append(
            {
                "id": f"claim:{claim['id']}",
                "origin_type": "claim",
                "origin_id": claim["id"],
                "classification": "measured" if measured else "conceptual",
                "classification_basis": (
                    "deployment claim with E1 or E2 evidence and an explicit measurement boundary"
                    if measured
                    else "claim does not satisfy the physical-measurement classification rule"
                ),
                "label": claim["statement"],
                "metric": None,
                "boundary": claim.get("measurement_boundary"),
                "workload": [],
                "platform": None,
                "evidence_class": claim.get("evidence_class"),
                "source_ids": source_ids,
                "source_refs": refs,
                "source_statuses": source_statuses(source_ids, source_lookup),
                "canonical_verification_status": canonical_status,
                "verification_status": status,
                "eligible_for_substantive_use": status == "verified",
                "scope": claim.get("scope"),
                "conflicts_with": sorted_unique_strings(
                    claim.get("conflicts_with", [])
                ),
            }
        )

    for route in sorted(routes, key=lambda item: str(item["id"])):
        source_ids = canonical_source_ids(route.get("source_ids", []), source_lookup)
        status = conservative_verification_status(source_ids, source_lookup)
        entries.append(
            {
                "id": f"route:{route['id']}",
                "origin_type": "route",
                "origin_id": route["id"],
                "classification": "conceptual",
                "classification_basis": "route and semantic-transition record",
                "label": route["mechanism"],
                "metric": None,
                "boundary": route.get("measurement_boundary"),
                "workload": [],
                "platform": route.get("platform_generation"),
                "evidence_class": route.get("evidence_class"),
                "source_ids": source_ids,
                "source_refs": normalize_source_refs(
                    route.get("source_refs", []), source_lookup
                ),
                "source_statuses": source_statuses(source_ids, source_lookup),
                "verification_status": status,
                "eligible_for_substantive_use": status == "verified",
                "route_state": route.get("route_state"),
                "capability_class": route.get("capability_class"),
            }
        )

    for capability_input in sorted(capabilities, key=lambda item: str(item["id"])):
        capability = (
            capability_input
            if "source_refs" in capability_input
            else normalize_platform_capability(capability_input, source_lookup)
        )
        source_ids = canonical_source_ids(capability.get("source_ids", []), source_lookup)
        source_status = conservative_verification_status(source_ids, source_lookup)
        canonical_status = capability["verification_status"]
        require(
            canonical_status in set(schema["verification_states"]),
            f"capability {capability['id']} has invalid verification status",
        )
        status = combine_verification_statuses(canonical_status, source_status)
        entries.append(
            {
                "id": f"capability:{capability['id']}",
                "origin_type": "platform_capability",
                "origin_id": capability["id"],
                "classification": "conceptual",
                "classification_basis": "platform contract capability, not a measurement record",
                "label": capability.get("support_detail")
                or capability.get("contract_requirement")
                or capability["id"],
                "metric": None,
                "boundary": None,
                "workload": [],
                "platform": {
                    "platform_id": capability["platform_id"],
                    "chip_generation": capability.get("chip_generation"),
                    "toolchain_version": capability.get("toolchain_version"),
                },
                "evidence_class": None,
                "source_ids": source_ids,
                "source_refs": normalize_source_refs(
                    capability.get("source_refs", []), source_lookup
                ),
                "source_statuses": source_statuses(source_ids, source_lookup),
                "canonical_verification_status": canonical_status,
                "verification_status": status,
                "eligible_for_substantive_use": status == "verified",
                "route_state": capability.get("route_state"),
                "capability_status": capability.get("capability_status"),
            }
        )

    return {"entries": sorted(entries, key=lambda item: item["id"])}


def validate_generated_views(
    outputs: dict[str, dict[str, Any]], schema: dict[str, object]
) -> None:
    figure = outputs.get("figure-inputs.json")
    if figure is not None:
        entries = figure.get("entries")
        require(isinstance(entries, list), "figure inputs lacks an entries array")
        require_unique_ids(entries, "figure inputs")
        for entry in entries:
            entry_id = str(entry["id"])
            require(
                entry.get("classification") in {"conceptual", "measured"},
                f"figure entry {entry_id} lacks a valid classification",
            )
            require(
                entry.get("verification_status") in set(schema["verification_states"]),
                f"figure entry {entry_id} has invalid verification status",
            )
            if entry.get("classification") == "measured":
                require(
                    entry.get("evidence_class") in {"E1", "E2"},
                    f"figure entry {entry_id} labels non-physical evidence as measured",
                )
            statuses = entry.get("source_statuses", [])
            if entry.get("verification_status") == "verified":
                metadata_only = [
                    status["source_id"]
                    for status in statuses
                    if status.get("retrieval_status") != "full_text"
                    or status.get("verification_status") != "verified"
                ]
                require(
                    not metadata_only,
                    f"figure entry {entry_id} promoted metadata-only or unverified sources: {metadata_only}",
                )
            refs = entry.get("source_refs", [])
            require(refs, f"figure entry {entry_id} lacks source provenance")
            require(
                any(ref.get("locators") for ref in refs),
                f"figure entry {entry_id} lacks locator provenance",
            )

    route_index = outputs.get("route-index.json")
    if route_index is not None:
        routes = route_index.get("routes")
        require(isinstance(routes, list), "route index lacks a routes array")
        require_unique_ids(routes, "route index")
        for route in routes:
            route_id = str(route["id"])
            require(
                route.get("route_state") is None
                or route["route_state"] in set(schema["route_states"]),
                f"route {route_id} has an undeclared route state",
            )
            require(
                route.get("capability_class") is None
                or route["capability_class"]
                in set(schema["platform_capability_statuses"]),
                f"route {route_id} has an undeclared capability class",
            )
            require(
                route.get("evidence_class") is None
                or route["evidence_class"] in set(schema["evidence_classes"]),
                f"route {route_id} has an undeclared evidence class",
            )
            for field in ("preserved", "transformed", "rejected"):
                require(
                    isinstance(route.get(field), list),
                    f"route {route_id} lacks normalized {field} semantics",
                )

    claims = outputs.get("claim-index.json")
    if claims is not None:
        records = claims.get("claims")
        require(isinstance(records, list), "claim index lacks a claims array")
        require_unique_ids(records, "claim index")
        for claim in records:
            require(
                claim["claim_type"] in set(schema["claim_types"]),
                f"claim {claim['id']} has an undeclared claim type",
            )
            require(
                claim["verification_status"] in set(schema["verification_states"]),
                f"claim {claim['id']} has an undeclared verification status",
            )


def serialize_view(payload: dict[str, Any]) -> bytes:
    return (json.dumps(payload, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DataViewError(f"could not load {path}: {exc}") from exc
    require(isinstance(payload, dict), f"JSON root must be an object: {path}")
    return payload


def validate_audit_claims(
    claims: list[dict[str, Any]],
    audit_claims: list[dict[str, Any]],
    source_lookup: dict[str, object],
) -> None:
    require_unique_ids(claims, "canonical claims")
    require_unique_ids(audit_claims, "audited claims")
    canonical = {str(claim["id"]): claim for claim in claims}
    audited = {str(claim["id"]): claim for claim in audit_claims}
    require(
        set(canonical) == set(audited),
        "canonical claim IDs differ from audited claim IDs",
    )
    comparison_fields = (
        "claim_type",
        "statement",
        "evidence_class",
        "reports_deployment_evidence",
        "verification_status",
        "measurement_boundary",
        "conflicts_with",
    )
    registry_records = source_lookup["records"]
    assert isinstance(registry_records, dict)
    for claim_id in sorted(canonical):
        claim = canonical[claim_id]
        audit = audited[claim_id]
        for field in comparison_fields:
            require(
                claim.get(field) == audit.get(field),
                f"claim {claim_id} differs from its audit in {field}",
            )
        canonical_source_ids(claim["source_ids"], source_lookup)
        refs = normalize_source_refs(audit.get("source_refs", []), source_lookup)
        for ref in refs:
            registry_locators = set(
                map(str, registry_records[ref["source_id"]].get("locators", []))
            )
            missing = sorted(set(ref["locators"]) - registry_locators)
            require(
                not missing,
                f"claim {claim_id} locators absent from canonical source "
                f"{ref['source_id']}: {missing}",
            )


def validate_canonical_inputs(
    *,
    schema: dict[str, Any],
    sources: list[dict[str, Any]],
    claims: list[dict[str, Any]],
    audit_claims: list[dict[str, Any]],
    surveys: list[dict[str, Any]],
    nodes: list[dict[str, Any]],
    edges: list[dict[str, Any]],
    papers: list[dict[str, Any]],
    capabilities: list[dict[str, Any]],
    source_lookup: dict[str, object],
) -> None:
    for vocabulary in (
        "evidence_classes",
        "route_states",
        "platform_capability_statuses",
        "verification_states",
        "coverage_scores",
        "survey_full_text_statuses",
        "claim_types",
        "platform_capability_platforms",
        "deployable_contract_fields",
    ):
        require(isinstance(schema.get(vocabulary), list), f"schema lacks {vocabulary}")

    for label, records in (
        ("surveys", surveys),
        ("stack nodes", nodes),
        ("stack edges", edges),
        ("evidence papers", papers),
        ("platform capabilities", capabilities),
    ):
        require_unique_ids(records, label)

    verification_states = set(schema["verification_states"])
    for source in sources:
        require(
            source.get("verification_status") in verification_states,
            f"source {source['id']} has an undeclared verification status",
        )

    validate_audit_claims(claims, audit_claims, source_lookup)
    evidence_classes = set(schema["evidence_classes"])
    claim_types = set(schema["claim_types"])
    for claim in claims:
        require(
            claim["claim_type"] in claim_types,
            f"claim {claim['id']} has an undeclared claim type",
        )
        require(
            claim.get("evidence_class") is None
            or claim["evidence_class"] in evidence_classes,
            f"claim {claim['id']} has an undeclared evidence class",
        )
        require(
            claim["verification_status"] in verification_states,
            f"claim {claim['id']} has an undeclared verification status",
        )

    expected_axes = set(AXIS_LABELS)
    coverage_scores = set(schema["coverage_scores"])
    survey_statuses = set(schema["survey_full_text_statuses"])
    for survey in surveys:
        canonical_source_id(survey["source_id"], source_lookup)
        require(
            survey["full_text_status"] in survey_statuses,
            f"survey {survey['id']} has an undeclared full-text status",
        )
        coverage = survey.get("coverage")
        require(
            isinstance(coverage, dict) and set(coverage) == expected_axes,
            f"survey {survey['id']} must define exactly axes A through L",
        )
        for axis, result in coverage.items():
            require(
                result.get("score") in coverage_scores,
                f"survey {survey['id']} axis {axis} has an undeclared score",
            )

    node_ids = {str(node["id"]) for node in nodes}
    edge_ids = {str(edge["id"]) for edge in edges}
    for node in nodes:
        canonical_source_ids(node.get("sources", []), source_lookup)
    for edge in edges:
        normalize_route_edge(
            edge,
            node_ids=node_ids,
            source_lookup=source_lookup,
            schema=schema,
        )

    for paper in papers:
        require(
            paper["evidence"] in evidence_classes,
            f"paper {paper['id']} has an undeclared evidence class",
        )
        require(
            bool(str(paper.get("what_was_measured", "")).strip()),
            f"paper {paper['id']} lacks a metric description",
        )
        canonical_source_ids(paper.get("sources", []), source_lookup)

    platform_ids = set(schema["platform_capability_platforms"])
    contract_fields = set(schema["deployable_contract_fields"])
    capability_statuses = set(schema["platform_capability_statuses"])
    route_states = set(schema["route_states"])
    capability_pairs: list[tuple[str, str]] = []
    for capability in capabilities:
        platform_id = capability["platform_id"]
        contract_field = capability["contract_field"]
        require(
            platform_id in platform_ids,
            f"capability {capability['id']} has an undeclared platform ID",
        )
        require(
            contract_field in contract_fields,
            f"capability {capability['id']} has an undeclared contract field",
        )
        require(
            capability["capability_status"] in capability_statuses,
            f"capability {capability['id']} has an undeclared capability status",
        )
        require(
            capability["route_state"] in route_states,
            f"capability {capability['id']} has an undeclared route state",
        )
        require(
            capability["verification_status"] in verification_states,
            f"capability {capability['id']} has an undeclared verification status",
        )
        unknown_routes = sorted(set(capability.get("route_ids", [])) - edge_ids)
        require(
            not unknown_routes,
            f"capability {capability['id']} references unknown routes: {unknown_routes}",
        )
        platform_capability_source_refs(capability, source_lookup)
        capability_pairs.append((platform_id, contract_field))
    duplicates = sorted(
        pair for pair, count in Counter(capability_pairs).items() if count > 1
    )
    require(not duplicates, f"duplicate platform capability pairs: {duplicates}")
    expected_pairs = {
        (platform_id, contract_field)
        for platform_id in platform_ids
        for contract_field in contract_fields
    }
    require(
        set(capability_pairs) == expected_pairs,
        "platform capability matrix does not cover every declared platform/contract pair",
    )


def load_audit_claims(root: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    audit_paths = sorted((root / "research/claim-audits").glob("audit-*.json"))
    require(audit_paths, "no structured claim audits were found")
    for audit_path in audit_paths:
        payload = load_json(audit_path)
        claims = payload.get("claims")
        require(isinstance(claims, list), f"claim audit lacks claims: {audit_path}")
        records.extend(claims)
    return records


def add_view_metadata(
    payload: dict[str, Any],
    *,
    schema_version: str,
    view: str,
    generated_from: Iterable[str],
) -> dict[str, Any]:
    return {
        "schema_version": schema_version,
        "view": view,
        "generated_by": "tools/build-data-views.py",
        "generated_from": sorted_unique_strings(generated_from),
        **payload,
    }


def build_outputs(root: Path = ROOT) -> dict[str, dict[str, Any]]:
    data_dir = root / "data"
    schema = load_json(data_dir / "schema-version.json")
    source_payload = load_json(data_dir / "source-registry.json")
    claim_payload = load_json(data_dir / "claims.json")
    survey_payload = load_json(data_dir / "prior-survey-coverage.json")
    stack_payload = load_json(data_dir / "evidence-stack.json")
    paper_payload = load_json(data_dir / "evidence-papers.json")
    capability_payload = load_json(data_dir / "platform-capabilities.json")
    target_kinds_payload = load_json(data_dir / "target-kinds.json")

    sources = source_payload["sources"]
    claims = claim_payload["claims"]
    surveys = survey_payload["surveys"]
    nodes = stack_payload["nodes"]
    edges = stack_payload["edges"]
    papers = paper_payload["papers"]
    capabilities = capability_payload["records"]
    audit_claims = load_audit_claims(root)
    source_lookup = build_source_lookup(sources)

    validate_canonical_inputs(
        schema=schema,
        sources=sources,
        claims=claims,
        audit_claims=audit_claims,
        surveys=surveys,
        nodes=nodes,
        edges=edges,
        papers=papers,
        capabilities=capabilities,
        source_lookup=source_lookup,
    )

    schema_version = str(schema["schema_version"])
    family = build_prior_survey_family_summary(surveys, source_lookup)
    family.update(
        {
            "family_order": [key for key, _, _ in FAMILY_DEFINITIONS],
            "axis_to_family": {
                axis: key
                for key, _, axes in FAMILY_DEFINITIONS
                for axis in axes
            },
        }
    )
    targets_summary = build_prior_survey_targets_summary(
        surveys, target_kinds_payload, source_lookup
    )
    evidence_population_summary = build_evidence_population_summary(
        paper_payload, target_kinds_payload
    )
    claim_index = build_claim_index(claims, audit_claims, source_lookup)
    route_index = build_route_index(
        edges, nodes, capabilities, source_lookup, schema
    )
    measurement_index = build_measurement_index(papers, source_lookup)
    figure_inputs = build_figure_inputs(
        papers=papers,
        claims=claim_index["claims"],
        routes=route_index["routes"],
        capabilities=route_index["platform_capabilities"],
        source_lookup=source_lookup,
        schema=schema,
    )

    outputs = {
        "prior-survey-family-summary.json": add_view_metadata(
            family,
            schema_version=schema_version,
            view="prior-survey-family-summary",
            generated_from=("data/prior-survey-coverage.json", "data/source-registry.json"),
        ),
        "prior-survey-targets-summary.json": add_view_metadata(
            targets_summary,
            schema_version=schema_version,
            view="prior-survey-targets-summary",
            generated_from=("data/prior-survey-coverage.json", "data/target-kinds.json"),
        ),
        "evidence-population-summary.json": add_view_metadata(
            evidence_population_summary,
            schema_version=schema_version,
            view="evidence-population-summary",
            generated_from=("data/evidence-papers.json", "data/target-kinds.json"),
        ),
        "claim-index.json": add_view_metadata(
            claim_index,
            schema_version=schema_version,
            view="claim-index",
            generated_from=(
                "data/claims.json",
                "data/source-registry.json",
                "research/claim-audits/audit-A-temporal-horizons.json",
                "research/claim-audits/audit-B-reset-semantics.json",
                "research/claim-audits/audit-C-rate-coded-silicon.json",
            ),
        ),
        "route-index.json": add_view_metadata(
            route_index,
            schema_version=schema_version,
            view="route-index",
            generated_from=(
                "data/evidence-stack.json",
                "data/platform-capabilities.json",
                "data/source-registry.json",
            ),
        ),
        "measurement-index.json": add_view_metadata(
            measurement_index,
            schema_version=schema_version,
            view="measurement-index",
            generated_from=("data/evidence-papers.json", "data/source-registry.json"),
        ),
        "figure-inputs.json": add_view_metadata(
            figure_inputs,
            schema_version=schema_version,
            view="figure-inputs",
            generated_from=(
                "data/claims.json",
                "data/evidence-papers.json",
                "data/evidence-stack.json",
                "data/platform-capabilities.json",
                "data/source-registry.json",
                "research/claim-audits/*.json",
            ),
        ),
    }
    validate_generated_views(outputs, schema)
    return outputs


def render_outputs(outputs: dict[str, dict[str, Any]]) -> dict[str, bytes]:
    require(
        set(outputs) == set(VIEW_FILENAMES),
        f"generator produced an unexpected output set: {sorted(outputs)}",
    )
    return {filename: serialize_view(outputs[filename]) for filename in VIEW_FILENAMES}


def write_outputs(rendered: dict[str, bytes], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    staged: list[tuple[Path, Path]] = []
    try:
        for filename in VIEW_FILENAMES:
            fd, temporary_name = tempfile.mkstemp(
                prefix=f".{filename}.", suffix=".tmp", dir=output_dir
            )
            temporary_path = Path(temporary_name)
            with os.fdopen(fd, "wb") as handle:
                handle.write(rendered[filename])
                handle.flush()
                os.fsync(handle.fileno())
            staged.append((temporary_path, output_dir / filename))
        for temporary_path, final_path in staged:
            os.replace(temporary_path, final_path)
    finally:
        for temporary_path, _ in staged:
            if temporary_path.exists():
                temporary_path.unlink()


def check_outputs(rendered: dict[str, bytes], output_dir: Path) -> None:
    differences = []
    for filename in VIEW_FILENAMES:
        path = output_dir / filename
        if not path.is_file():
            differences.append(f"missing {path}")
        elif path.read_bytes() != rendered[filename]:
            differences.append(f"stale {path}")
    require(not differences, "; ".join(differences))


class DataViewFixtureTests(unittest.TestCase):
    """Focused contract fixtures for the generated evidence views."""

    def test_family_projection_is_exhaustive_and_uses_stable_keys(self) -> None:
        survey = {
            "id": "survey-fixture",
            "source_id": "source-fixture",
            "full_text_status": "verified",
            "retrieval_sources": ["https://example.test/paper"],
            "coverage": {
                axis: {
                    "score": "full",
                    "basis": f"basis {axis}",
                    "locator": f"locator {axis}",
                }
                for axis in "ABCDEFGHIJKL"
            },
            "strongest_contribution": "fixture contribution",
            "deployment_depth": "fixture depth",
            "omissions": [],
            "verification": "fixture verification",
        }

        result = build_prior_survey_family_summary([survey])

        self.assertEqual(
            [family["key"] for family in result["families"]],
            [
                "learning",
                "coding",
                "software",
                "hardware",
                "benchmarking",
                "deployment",
                "applications",
            ],
        )
        self.assertEqual(result["families"][0]["label"], "models and learning")
        projected_axes = [
            axis
            for family in result["families"]
            for axis in family["coverage_axes"]
        ]
        self.assertEqual(sorted(projected_axes), list("ABCDEFGHIJKL"))
        self.assertEqual(len(projected_axes), len(set(projected_axes)))

    def test_claim_index_preserves_source_specific_provenance_and_flags(self) -> None:
        claim = {
            "id": "claim-fixture",
            "claim_type": "deployment",
            "statement": "Fixture claim.",
            "evidence_class": "E1",
            "reports_deployment_evidence": True,
            "source_ids": ["source-alias"],
            "locators": ["pooled locator"],
            "verification_status": "conflicted",
            "measurement_boundary": "chip only",
            "conflicts_with": ["claim-counter"],
            "scope": "fixture scope",
        }
        audit_claim = {
            **claim,
            "source_refs": [
                {"source_id": "source-alias", "locators": ["specific locator"]}
            ],
        }
        source_lookup = fixture_source_lookup()

        result = build_claim_index([claim], [audit_claim], source_lookup)
        indexed = result["claims"][0]

        self.assertEqual(indexed["source_ids"], ["source-canonical"])
        self.assertEqual(
            indexed["source_refs"],
            [{"source_id": "source-canonical", "locators": ["specific locator"]}],
        )
        self.assertEqual(indexed["locators"], ["pooled locator"])
        self.assertEqual(indexed["verification_status"], "conflicted")
        self.assertEqual(indexed["scope"], "fixture scope")
        self.assertEqual(indexed["conflicts_with"], ["claim-counter"])
        self.assertTrue(indexed["interpretation_flags"]["has_conflict"])
        self.assertTrue(
            indexed["interpretation_flags"]["reports_deployment_evidence"]
        )

    def test_route_normalization_keeps_legacy_breaks_distinct_from_rejection(self) -> None:
        edge = {
            "id": "route-fixture",
            "from": "node-a",
            "to": "node-b",
            "mechanism": "fixture mechanism",
            "preserves": ["reset semantics"],
            "breaks": ["portability"],
            "evidence": "E3",
            "sources": ["source-alias"],
        }

        normalized = normalize_route_edge(
            edge,
            node_ids={"node-a", "node-b"},
            source_lookup=fixture_source_lookup(),
            schema=fixture_schema(),
        )

        self.assertEqual(normalized["typed_input"], None)
        self.assertEqual(normalized["typed_output"], None)
        self.assertEqual(normalized["preserved"], ["reset semantics"])
        self.assertEqual(normalized["transformed"], [])
        self.assertEqual(normalized["rejected"], [])
        self.assertEqual(normalized["legacy_breaks"], ["portability"])
        self.assertEqual(normalized["evidence_class"], "E3")
        self.assertEqual(normalized["source_ids"], ["source-canonical"])

    def test_provisional_capability_cannot_be_promoted_to_verified_measurement(self) -> None:
        paper = {
            "id": "paper-fixture",
            "title": "Fixture paper",
            "authors": "A. Author",
            "year": 2026,
            "venue": "Fixture venue",
            "url": "https://example.test/paper",
            "population": "fixture",
            "family": "application",
            "method_summary": "fixture method",
            "neuron": "IF",
            "reset": "subtractive",
            "encoding": "rate",
            "input_encoding": "direct",
            "timesteps": "4",
            "datasets": ["FixtureSet"],
            "toolchain": "FixtureTool",
            "target_hardware": "Fixture chip",
            "what_was_measured": "accuracy in software simulation",
            "evidence": "E5",
            "evidence_notes": "No physical execution.",
            "sources": ["source-alias"],
        }
        capability = {
            "id": "capability-fixture",
            "platform_id": "fixture-platform",
            "contract_field": "reset_semantics",
            "capability_status": "native",
            "route_state": "physical",
            "verification_status": "provisional",
            "route_ids": [],
            "chip_generation": "fixture generation",
            "toolchain_version": "1.0",
            "source_ids": ["source-alias"],
            "locators": ["metadata locator"],
        }

        measurement = build_measurement_index([paper], fixture_source_lookup())["measurements"][0]
        figure = build_figure_inputs(
            papers=[paper],
            claims=[],
            routes=[],
            capabilities=[capability],
            source_lookup=fixture_source_lookup(),
            schema=fixture_schema(),
        )

        self.assertFalse(measurement["is_physical_measurement"])
        paper_entry = next(entry for entry in figure["entries"] if entry["id"] == "paper:paper-fixture")
        capability_entry = next(
            entry
            for entry in figure["entries"]
            if entry["id"] == "capability:capability-fixture"
        )
        self.assertEqual(paper_entry["classification"], "conceptual")
        self.assertEqual(capability_entry["classification"], "conceptual")
        self.assertEqual(capability_entry["verification_status"], "provisional")

    def test_generated_view_validation_rejects_metadata_only_promotion(self) -> None:
        outputs = {
            "figure-inputs.json": {
                "entries": [
                    {
                        "id": "paper:bad-fixture",
                        "classification": "measured",
                        "evidence_class": "E1",
                        "verification_status": "verified",
                        "source_statuses": [
                            {
                                "source_id": "source-canonical",
                                "retrieval_status": "metadata_only",
                                "verification_status": "provisional",
                            }
                        ],
                    }
                ]
            }
        }

        with self.assertRaisesRegex(DataViewError, "metadata-only"):
            validate_generated_views(outputs, fixture_schema())

    def test_json_serialization_is_byte_stable(self) -> None:
        payload = {"z": [2, 1], "a": "µJ"}

        first = serialize_view(payload)
        second = serialize_view(payload)

        self.assertEqual(first, second)
        self.assertTrue(first.endswith(b"\n"))

    def test_audit_refs_may_be_source_specific_subset_of_context_sources(self) -> None:
        primary = {
            "id": "source-primary",
            "aliases": [],
            "retrieval_status": "full_text",
            "verification_status": "verified",
            "locators": ["specific locator"],
        }
        context = {
            "id": "source-context",
            "aliases": [],
            "retrieval_status": "full_text",
            "verification_status": "verified",
            "locators": ["context locator"],
        }
        source_lookup = build_source_lookup([primary, context])
        claim = {
            "id": "claim-fixture",
            "claim_type": "deployment",
            "statement": "Fixture claim.",
            "evidence_class": "E1",
            "reports_deployment_evidence": True,
            "source_ids": ["source-primary", "source-context"],
            "locators": ["specific locator"],
            "verification_status": "verified",
            "measurement_boundary": "chip",
            "conflicts_with": [],
            "scope": "fixture scope",
        }
        audited = {
            **{
                key: claim[key]
                for key in (
                    "id",
                    "claim_type",
                    "statement",
                    "evidence_class",
                    "reports_deployment_evidence",
                    "verification_status",
                    "measurement_boundary",
                    "conflicts_with",
                    "scope",
                )
            },
            "source_refs": [
                {"source_id": "source-primary", "locators": ["specific locator"]}
            ],
        }

        validate_audit_claims([claim], [audited], source_lookup)
        indexed = build_claim_index([claim], [audited], source_lookup)["claims"][0]
        self.assertEqual(
            indexed["source_refs"],
            [{"source_id": "source-primary", "locators": ["specific locator"]}],
        )
        self.assertEqual(
            indexed["source_ids"], ["source-context", "source-primary"]
        )


def fixture_source_lookup() -> dict[str, object]:
    record = {
        "id": "source-canonical",
        "aliases": ["source-alias"],
        "retrieval_status": "metadata_only",
        "verification_status": "provisional",
        "locators": ["metadata locator"],
    }
    return {
        "records": {"source-canonical": record},
        "aliases": {"source-alias": "source-canonical"},
    }


def fixture_schema() -> dict[str, object]:
    return {
        "evidence_classes": ["E1", "E2", "E3", "E4", "E5"],
        "route_states": [
            "exact",
            "approximate",
            "blocked",
            "obsolete",
            "unexercised",
            "physical",
        ],
        "platform_capability_statuses": [
            "native",
            "transformed",
            "emulated",
            "host-assisted",
            "unsupported",
            "undocumented",
        ],
        "verification_states": ["verified", "provisional", "conflicted", "rejected"],
        "coverage_scores": ["full", "partial", "mentioned", "none", "unassessed"],
        "survey_full_text_statuses": [
            "verified",
            "provisional",
            "partial",
            "not_retrieved",
        ],
        "claim_types": ["deployment"],
        "platform_capability_platforms": ["fixture-platform"],
        "deployable_contract_fields": ["reset_semantics"],
    }


def main() -> int:
    if "--self-test" in sys.argv:
        argv = [sys.argv[0]] + [arg for arg in sys.argv[1:] if arg != "--self-test"]
        result = unittest.main(argv=argv, exit=False)
        return 0 if result.result.wasSuccessful() else 1
    parser = argparse.ArgumentParser(
        description="Build deterministic downstream research-evidence views."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="compare generated bytes with the destination without writing",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="destination directory (default: data/generated)",
    )
    args = parser.parse_args()
    try:
        rendered = render_outputs(build_outputs(ROOT))
        if args.check:
            check_outputs(rendered, args.output_dir)
            print(f"data views are current in {args.output_dir}")
        else:
            write_outputs(rendered, args.output_dir)
            print(f"wrote {len(rendered)} data views to {args.output_dir}")
    except DataViewError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
