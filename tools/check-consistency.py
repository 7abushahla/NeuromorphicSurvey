#!/usr/bin/env python3
"""Check global identity, reference, evidence, and provenance consistency."""
from __future__ import annotations

import argparse
import json
import runpy
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parent.parent
GENERATED_FILES = (
    "claim-index.json", "figure-inputs.json", "measurement-index.json",
    "prior-survey-family-summary.json", "route-index.json",
)
OFFICIAL_SOURCE_TYPES = {
    "official_vendor_documentation", "official_manufacturer_documentation",
    "official_sdk_documentation", "official_devkit_manual", "official_repository",
    "official_model_zoo", "official_mapper_constraints", "official_release_note",
    "official_measured_example",
}


def load_json(path: Path) -> object:
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"cannot read JSON from {path}: {error}") from error


def load_documents(root: Path) -> dict[str, object]:
    data = root / "data"
    names = (
        "schema-version.json", "source-registry.json", "sources.json",
        "bibliography-migration-sources.json", "legacy-citation-aliases.json",
        "refmap.json", "claims.json", "evidence-stack.json", "evidence-papers.json",
        "prior-survey-coverage.json", "platform-capabilities.json",
    )
    documents = {name: load_json(data / name) for name in names}
    documents.update({
        f"generated/{name}": load_json(data / "generated" / name)
        for name in GENERATED_FILES
    })
    return documents


def object_array(document: object, key: str, label: str, errors: list[str]) -> list[dict[str, Any]]:
    if not isinstance(document, dict) or not isinstance(document.get(key), list):
        errors.append(f"{label} must contain a {key} array")
        return []
    result = []
    for index, record in enumerate(document[key]):
        if not isinstance(record, dict):
            errors.append(f"{label}.{key}[{index}]: record must be an object")
        else:
            result.append(record)
    return result


def unique_ids(records: Iterable[dict[str, Any]], label: str) -> tuple[set[str], list[str]]:
    ids: list[str] = []
    errors: list[str] = []
    for index, record in enumerate(records):
        record_id = record.get("id")
        if not isinstance(record_id, str) or not record_id.strip():
            errors.append(f"{label}[{index}]: id must be a nonempty string")
        else:
            ids.append(record_id)
    duplicates = sorted(item for item, count in Counter(ids).items() if count > 1)
    if duplicates:
        errors.append(f"{label} has duplicate IDs: {duplicates}")
    return set(ids), errors


def build_source_lookup(source_document: object) -> tuple[dict[str, dict[str, Any]], dict[str, str], list[str]]:
    errors: list[str] = []
    sources = object_array(source_document, "sources", "source-registry.json", errors)
    source_ids, id_errors = unique_ids(sources, "source-registry.sources")
    errors.extend(id_errors)
    records = {source["id"]: source for source in sources if source.get("id") in source_ids}
    aliases: dict[str, str] = {}
    for source in sources:
        source_id = source.get("id")
        values = source.get("aliases")
        if not isinstance(values, list):
            errors.append(f"source {source_id!r}: aliases must be an array")
            continue
        for alias in values:
            if not isinstance(alias, str) or not alias.strip():
                errors.append(f"source {source_id!r}: alias must be a nonempty string")
                continue
            if alias in records and alias != source_id:
                errors.append(f"source alias {alias!r} collides with a canonical ID")
            previous = aliases.get(alias)
            if previous is not None and previous != source_id:
                errors.append(f"source alias {alias!r} resolves to multiple canonical IDs")
            aliases[alias] = source_id
    return records, aliases, errors


def resolve_source_id(value: object, records: dict[str, dict[str, Any]], aliases: dict[str, str]) -> str | None:
    if not isinstance(value, str):
        return None
    return value if value in records else aliases.get(value)


def check_source_references(value: object, label: str, records: dict[str, dict[str, Any]], aliases: dict[str, str]) -> list[str]:
    errors: list[str] = []
    singular = {"source_id", "official_technical_source_id", "official_exercised_example_source_id"}
    if isinstance(value, dict):
        for key, child in value.items():
            path = f"{label}.{key}"
            if key in singular and child is not None:
                if resolve_source_id(child, records, aliases) is None:
                    errors.append(f"{path}: unresolved source reference {child!r}")
            elif key == "source_ids":
                if not isinstance(child, list):
                    errors.append(f"{path}: source_ids must be an array")
                else:
                    for index, source_id in enumerate(child):
                        if resolve_source_id(source_id, records, aliases) is None:
                            errors.append(f"{path}[{index}]: unresolved source reference {source_id!r}")
            else:
                errors.extend(check_source_references(child, path, records, aliases))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(check_source_references(child, f"{label}[{index}]", records, aliases))
    return errors


def check_legacy_sources(values: object, label: str, records: dict[str, dict[str, Any]], aliases: dict[str, str]) -> list[str]:
    if not isinstance(values, list):
        return [f"{label} must be an array"]
    rows = [item for item in values if isinstance(item, dict)]
    errors = [] if len(rows) == len(values) else [f"{label}: every source must be an object"]
    _, id_errors = unique_ids(rows, label)
    errors.extend(id_errors)
    for index, source in enumerate(rows):
        if resolve_source_id(source.get("id"), records, aliases) is None:
            errors.append(f"{label}[{index}]: unresolved legacy source ID {source.get('id')!r}")
    return errors


def validate_claim_semantics(claims: Iterable[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    for index, claim in enumerate(claims):
        label = f"claims[{index}]"
        if claim.get("evidence_class") is not None:
            if not isinstance(claim.get("scope"), str) or not claim["scope"].strip():
                errors.append(f"{label}: evidence class requires explicit scope")
            if claim.get("reports_deployment_evidence") is not True:
                errors.append(f"{label}: evidence class requires an explicit deployment-evidence claim")
        measurement = claim.get("claim_type") in {"metric", "result"} or claim.get("reports_deployment_evidence") is True
        boundary = claim.get("measurement_boundary")
        if measurement and (not isinstance(boundary, str) or not boundary.strip()):
            errors.append(f"{label}: measurement claim requires an explicit measurement boundary")
    return errors


def validate_hardware_records(capabilities: Iterable[dict[str, Any]], schema: object, records: dict[str, dict[str, Any]], aliases: dict[str, str], label: str) -> list[str]:
    errors: list[str] = []
    statuses = set(schema.get("platform_capability_statuses", [])) if isinstance(schema, dict) else set()
    for index, capability in enumerate(capabilities):
        item = f"{label}[{index}]"
        source_id = resolve_source_id(capability.get("official_technical_source_id"), records, aliases)
        if source_id is None or records[source_id].get("source_type") not in OFFICIAL_SOURCE_TYPES:
            errors.append(f"{item}: hardware-support claim requires an official source")
        if not isinstance(capability.get("chip_generation"), str) or not capability["chip_generation"].strip():
            errors.append(f"{item}: hardware-support claim requires a platform generation")
        versions = (capability.get("document_version"), capability.get("toolchain_version"))
        if not any(isinstance(value, str) and value.strip() for value in versions):
            errors.append(f"{item}: hardware-support claim requires a document or SDK/toolchain version")
        if capability.get("capability_status") not in statuses:
            errors.append(f"{item}: hardware-support claim requires an explicit capability status")
    return errors


def validate_hardware_routes(routes: Iterable[dict[str, Any]], records: dict[str, dict[str, Any]], aliases: dict[str, str], label: str) -> list[str]:
    errors: list[str] = []
    for index, route in enumerate(routes):
        if route.get("reports_deployment_evidence") is not True:
            continue
        item = f"{label}[{index}]"
        source_values = route.get("sources", route.get("source_ids", []))
        resolved = [resolve_source_id(value, records, aliases) for value in source_values] if isinstance(source_values, list) else []
        if not any(source_id and records[source_id].get("source_type") in OFFICIAL_SOURCE_TYPES for source_id in resolved):
            errors.append(f"{item}: hardware-support route requires an official source")
        for field, description in (
            ("platform_generation", "platform generation"), ("toolchain_version", "SDK/toolchain version"),
            ("capability_class", "capability status"), ("route_state", "route status"),
            ("measurement_boundary", "measurement boundary"),
        ):
            if not isinstance(route.get(field), str) or not route[field].strip():
                errors.append(f"{item}: hardware-support route requires an explicit {description}")
    return errors


def compare_ids(expected: set[str], actual: Iterable[dict[str, Any]], label: str) -> list[str]:
    actual_ids, errors = unique_ids(actual, label)
    if actual_ids != expected:
        errors.append(f"{label} identity projection mismatch; missing={sorted(expected - actual_ids)}, unexpected={sorted(actual_ids - expected)}")
    return errors


def validate_documents(documents: dict[str, object], root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    schema = documents["schema-version.json"]
    records, aliases, lookup_errors = build_source_lookup(documents["source-registry.json"])
    errors.extend(lookup_errors)
    stack = documents["evidence-stack.json"]
    paper_doc = documents["evidence-papers.json"]
    collections = {
        "nodes": object_array(stack, "nodes", "evidence-stack.json", errors),
        "edges": object_array(stack, "edges", "evidence-stack.json", errors),
        "papers": object_array(paper_doc, "papers", "evidence-papers.json", errors),
        "claims": object_array(documents["claims.json"], "claims", "claims.json", errors),
        "surveys": object_array(documents["prior-survey-coverage.json"], "surveys", "prior-survey-coverage.json", errors),
        "capabilities": object_array(documents["platform-capabilities.json"], "records", "platform-capabilities.json", errors),
    }
    ids: dict[str, set[str]] = {}
    for label, rows in collections.items():
        ids[label], id_errors = unique_ids(rows, label)
        errors.extend(id_errors)

    errors.extend(check_legacy_sources(documents["sources.json"], "sources.json", records, aliases))
    errors.extend(check_legacy_sources(stack.get("sources") if isinstance(stack, dict) else None, "evidence-stack.sources", records, aliases))
    errors.extend(check_legacy_sources(paper_doc.get("sources") if isinstance(paper_doc, dict) else None, "evidence-papers.sources", records, aliases))
    migration = object_array(documents["bibliography-migration-sources.json"], "sources", "bibliography-migration-sources.json", errors)
    errors.extend(check_legacy_sources(migration, "bibliography-migration-sources.sources", records, aliases))

    alias_doc = documents["legacy-citation-aliases.json"]
    alias_rows = object_array(alias_doc, "aliases", "legacy-citation-aliases.json", errors)
    alias_values = [row.get("alias") for row in alias_rows]
    duplicate_aliases = sorted(str(item) for item, count in Counter(alias_values).items() if count > 1)
    if duplicate_aliases:
        errors.append(f"legacy-citation-aliases has duplicate aliases: {duplicate_aliases}")
    errors.extend(check_source_references(alias_rows, "legacy-citation-aliases.aliases", records, aliases))
    unresolved = alias_doc.get("unresolved", []) if isinstance(alias_doc, dict) else []
    if not isinstance(unresolved, list):
        errors.append("legacy-citation-aliases.unresolved must be an array")
    else:
        for index, item in enumerate(unresolved):
            if not isinstance(item, dict) or not all(isinstance(item.get(field), str) and item[field].strip() for field in ("alias", "legacy_target", "reason")):
                errors.append(f"legacy-citation-aliases.unresolved[{index}] must identify alias, target, and reason")
    refmap = documents["refmap.json"]
    if not isinstance(refmap, dict):
        errors.append("refmap.json must contain an object")
    else:
        for citation_key, source_id in sorted(refmap.items()):
            if resolve_source_id(source_id, records, aliases) is None:
                errors.append(f"refmap.json[{citation_key!r}]: unresolved source reference {source_id!r}")

    for label, rows in collections.items():
        errors.extend(check_source_references(rows, label, records, aliases))
    for label in ("nodes", "edges", "papers"):
        for index, row in enumerate(collections[label]):
            values = row.get("sources")
            if not isinstance(values, list) or not values:
                errors.append(f"{label}[{index}]: sources must be a nonempty array")
            else:
                for value in values:
                    if resolve_source_id(value, records, aliases) is None:
                        errors.append(f"{label}[{index}]: unresolved source reference {value!r}")
    for index, edge in enumerate(collections["edges"]):
        for field in ("from", "to"):
            if edge.get(field) not in ids["nodes"]:
                errors.append(f"edges[{index}].{field}: unresolved node reference {edge.get(field)!r}")
    conflict_ids = ids["claims"] | {path.stem for path in (root / "research/conflicts").glob("*.md")}
    for index, claim in enumerate(collections["claims"]):
        for target in claim.get("conflicts_with", []):
            if target not in conflict_ids:
                errors.append(f"claims[{index}]: unresolved conflict reference {target!r}")
    for index, capability in enumerate(collections["capabilities"]):
        route_ids = capability.get("route_ids")
        if not isinstance(route_ids, list) or not route_ids:
            errors.append(f"capabilities[{index}]: route_ids must be nonempty")
        elif any(route_id not in ids["edges"] for route_id in route_ids):
            errors.append(f"capabilities[{index}]: unresolved route reference")

    errors.extend(validate_claim_semantics(collections["claims"]))
    errors.extend(validate_hardware_records(collections["capabilities"], schema, records, aliases, "platform-capabilities.records"))
    errors.extend(validate_hardware_routes(collections["edges"], records, aliases, "evidence-stack.edges"))

    claim_view = documents["generated/claim-index.json"]
    route_view = documents["generated/route-index.json"]
    measure_view = documents["generated/measurement-index.json"]
    survey_view = documents["generated/prior-survey-family-summary.json"]
    figure_view = documents["generated/figure-inputs.json"]
    generated = {
        "claims": object_array(claim_view, "claims", "generated claim index", errors),
        "nodes": object_array(route_view, "nodes", "generated route index", errors),
        "edges": object_array(route_view, "routes", "generated route index", errors),
        "capabilities": object_array(route_view, "platform_capabilities", "generated route index", errors),
        "papers": object_array(measure_view, "measurements", "generated measurement index", errors),
    }
    for key, rows in generated.items():
        errors.extend(compare_ids(ids[key], rows, f"generated {key}"))
    entries = object_array(figure_view, "entries", "generated figure inputs", errors)
    _, entry_errors = unique_ids(entries, "generated figure inputs")
    errors.extend(entry_errors)
    origin_sets = {"claim": ids["claims"], "route": ids["edges"], "paper": ids["papers"], "platform_capability": ids["capabilities"]}
    seen = {key: set() for key in origin_sets}
    for index, entry in enumerate(entries):
        kind, origin = entry.get("origin_type"), entry.get("origin_id")
        if kind not in origin_sets or origin not in origin_sets.get(kind, set()):
            errors.append(f"generated figure inputs[{index}]: unresolved origin {kind!r}/{origin!r}")
        else:
            seen[kind].add(origin)
        if entry.get("classification") == "measured" and not entry.get("boundary"):
            errors.append(f"generated figure inputs[{index}]: measured entry requires an explicit boundary")
    for kind in origin_sets:
        if seen[kind] != origin_sets[kind]:
            errors.append(f"generated figure inputs do not cover every {kind} origin")
    for index, measurement in enumerate(generated["papers"]):
        boundary = measurement.get("boundary")
        if not isinstance(boundary, dict) or not isinstance(boundary.get("description"), str) or not boundary["description"].strip():
            errors.append(f"generated measurements[{index}]: measurement requires an explicit boundary")

    families = object_array(survey_view, "families", "generated survey summary", errors)
    family_keys = [{"id": family.get("key")} for family in families]
    _, family_errors = unique_ids(family_keys, "generated survey families")
    errors.extend(family_errors)
    generated_axes: set[str] = set()
    for index, family in enumerate(families):
        family_surveys = family.get("surveys")
        if not isinstance(family_surveys, list):
            errors.append(f"generated survey families[{index}]: surveys must be an array")
        else:
            errors.extend(compare_ids(ids["surveys"], [item for item in family_surveys if isinstance(item, dict)], f"generated survey families[{index}].surveys"))
        if isinstance(family.get("coverage_axes"), list):
            generated_axes.update(str(axis) for axis in family["coverage_axes"])
    if generated_axes != set("ABCDEFGHIJKL"):
        errors.append(f"generated survey summary must cover exactly 12 axes A-L, found {sorted(generated_axes)}")

    for name in GENERATED_FILES:
        errors.extend(check_source_references(documents[f"generated/{name}"], f"generated/{name}", records, aliases))
    errors.extend(validate_hardware_records(generated["capabilities"], schema, records, aliases, "generated platform capabilities"))
    errors.extend(validate_hardware_routes(generated["edges"], records, aliases, "generated routes"))
    return errors


def expect_error(errors: list[str], fragment: str, label: str) -> None:
    if not any(fragment in error for error in errors):
        raise AssertionError(f"{label} did not report {fragment!r}; errors: {errors}")


def run_contract_tests(records: dict[str, dict[str, Any]], aliases: dict[str, str], schema: object) -> int:
    count_module = runpy.run_path(ROOT / "tools/check-counts.py")
    counts, errors = count_module["population_counts"]({"papers": [
        {"id": "algorithm", "population": "algorithm"},
        {"id": "deployment", "population": "deployment"},
        {"id": "both", "population": "both"},
    ]})
    assert not errors and counts == {
        "exclusive": {"algorithm": 1, "deployment": 1, "both": 1},
        "inclusive": {"algorithm": 2, "deployment": 2}, "total_unique": 3,
    }
    expect_error(count_module["stale_headline_errors"]({"algorithm_count": 2}, "fixture.json"), "unqualified", "headline fixture")
    expect_error(unique_ids([{"id": "same"}, {"id": "same"}], "fixture")[1], "duplicate IDs", "ID fixture")
    expect_error(check_source_references({"source_ids": ["missing"]}, "fixture", records, aliases), "unresolved", "reference fixture")
    expect_error(validate_claim_semantics([{"evidence_class": "E1", "reports_deployment_evidence": True, "scope": "", "claim_type": "deployment", "measurement_boundary": "bounded"}]), "explicit scope", "scope fixture")
    expect_error(validate_claim_semantics([{"evidence_class": None, "reports_deployment_evidence": False, "scope": "fixture", "claim_type": "metric", "measurement_boundary": None}]), "measurement boundary", "boundary fixture")
    fixture = {"official_technical_source_id": next(iter(records)), "chip_generation": "", "document_version": None, "toolchain_version": None, "capability_status": None}
    hardware_errors = validate_hardware_records([fixture], schema, records, aliases, "fixture")
    for fragment in ("official source", "platform generation", "SDK/toolchain version", "capability status"):
        expect_error(hardware_errors, fragment, "hardware fixture")
    return 6


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    try:
        documents = load_documents(args.root)
        records, aliases, lookup_errors = build_source_lookup(documents["source-registry.json"])
        if lookup_errors:
            raise ValueError("; ".join(lookup_errors))
        contracts = run_contract_tests(records, aliases, documents["schema-version.json"])
        errors = validate_documents(documents, args.root)
        count_module = runpy.run_path(args.root / "tools/check-counts.py")
        summary, count_errors = count_module["validate_counts"](
            documents["evidence-papers.json"], documents["prior-survey-coverage.json"],
            {name: documents[f"generated/{name}"] for name in GENERATED_FILES},
        )
        errors.extend(count_errors)
    except (AssertionError, KeyError, ValueError) as error:
        errors, contracts, summary = [str(error)], 0, {}
    if errors:
        print("check-consistency: FAILED", file=sys.stderr)
        print("\n".join(f"- {error}" for error in errors), file=sys.stderr)
        return 1
    print(
        f"check-consistency: {contracts} regression contracts passed; "
        f"sources={len(records)} claims={len(documents['claims.json']['claims'])} "
        f"nodes={len(documents['evidence-stack.json']['nodes'])} "
        f"edges={len(documents['evidence-stack.json']['edges'])} "
        f"papers={summary['population']['total_unique']} surveys={summary['coverage']['surveys']} "
        f"platform_capabilities={len(documents['platform-capabilities.json']['records'])}"
    )
    print("check-consistency: all IDs and references resolve; evidence scope, measurement boundaries, and hardware-support provenance are explicit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
