#!/usr/bin/env python3
"""Verify deterministic source-registry normalization and migration contracts."""
from __future__ import annotations

import json
import runpy
import sys
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    module = runpy.run_path(ROOT / "tools/build-source-registry.py")
    normalize_url = module["normalize_url"]
    extract_doi = module["extract_doi"]
    cluster_records = module["cluster_records"]
    resolve_cluster = module["resolve_cluster"]
    load_input_records = module["load_input_records"]
    build_outputs = module["build_outputs"]

    checks = 0

    arxiv_variants = {
        normalize_url("https://arxiv.org/abs/2505.06417"),
        normalize_url("https://arxiv.org/html/2505.06417v2"),
        normalize_url("https://arxiv.org/pdf/2505.06417v3.pdf"),
    }
    if arxiv_variants != {"https://arxiv.org/abs/2505.06417"}:
        raise AssertionError(f"arXiv URL variants did not merge: {arxiv_variants}")
    checks += 1

    openreview_forum = normalize_url("https://openreview.net/forum?id=WuiVAPrgi3")
    openreview_pdf = normalize_url("https://openreview.net/pdf?id=WuiVAPrgi3")
    different_openreview = normalize_url("https://openreview.net/forum?id=QCFS123")
    if openreview_forum != openreview_pdf:
        raise AssertionError("OpenReview forum and PDF URLs for one ID must merge")
    if openreview_forum == different_openreview:
        raise AssertionError("significant URL query parameters must preserve identity")
    checks += 1

    for placeholder in ("unknown", "not found", "", None):
        if normalize_url(placeholder) is not None:
            raise AssertionError(f"invalid URL placeholder became an identity: {placeholder!r}")
    checks += 1

    doi = extract_doi({"url": "https://doi.org/10.1109/MM.2018.112130359"})
    if doi != "10.1109/mm.2018.112130359":
        raise AssertionError(f"DOI URL did not normalize: {doi!r}")
    checks += 1

    version_fixture = [
        {
            "id": "preprint",
            "title": "One Work, Two Publication Forms",
            "authors": "A. Researcher, B. Scholar",
            "year": 2024,
            "url": "https://arxiv.org/abs/2401.01234v2",
            "_origin": "fixture-a.json",
            "_rank": 2,
            "_index": 0,
        },
        {
            "id": "published",
            "title": "One Work, Two Publication Forms",
            "authors": "A. Researcher and B. Scholar",
            "year": 2025,
            "doi": "10.1000/published.42",
            "url": "https://doi.org/10.1000/published.42",
            "_origin": "fixture-b.json",
            "_rank": 3,
            "_index": 0,
        },
    ]
    version_clusters, version_conflicts = cluster_records(version_fixture, {})
    if len(version_clusters) != 1 or version_conflicts:
        raise AssertionError(
            "an arXiv preprint and supported version-of-record identity must merge: "
            f"clusters={len(version_clusters)}, conflicts={version_conflicts}"
        )
    version_record, version_field_conflicts, _ = resolve_cluster(
        version_clusters[0], {}, set()
    )
    if version_field_conflicts or version_record["doi"] != "10.1000/published.42":
        raise AssertionError(
            "the publisher DOI must be canonical for a merged preprint/publication pair"
        )
    checks += 1

    def canonicalize_fixture(rows: list[dict[str, object]]) -> list[dict[str, object]]:
        clusters, conflicts = cluster_records(rows, {})
        if conflicts:
            raise AssertionError(f"fixture produced identity conflicts: {conflicts}")
        id_counts: dict[str, int] = {}
        for cluster in clusters:
            for item in {str(record["id"]) for record in cluster}:
                id_counts[item] = id_counts.get(item, 0) + 1
        ambiguous_ids = {item for item, count in id_counts.items() if count > 1}
        resolved = []
        for cluster in clusters:
            record, field_conflicts, _ = resolve_cluster(cluster, {}, ambiguous_ids)
            if field_conflicts:
                raise AssertionError(
                    f"fixture produced field conflicts: {field_conflicts}"
                )
            resolved.append(record)
        return sorted(resolved, key=lambda record: str(record["id"]))

    ordered_fixture = deepcopy(version_fixture)
    reversed_fixture = list(reversed(deepcopy(version_fixture)))
    for index, record in enumerate(ordered_fixture):
        record["_index"] = index
    for index, record in enumerate(reversed_fixture):
        record["_index"] = index
    if canonicalize_fixture(ordered_fixture) != canonicalize_fixture(reversed_fixture):
        raise AssertionError("canonicalization depends on structured-input row order")
    checks += 1

    registry, log_text, diagnostics = build_outputs(ROOT)
    first_bytes = json.dumps(registry, indent=2, ensure_ascii=False) + "\n"
    repeated_registry, repeated_log, repeated_diagnostics = build_outputs(ROOT)
    second_bytes = json.dumps(repeated_registry, indent=2, ensure_ascii=False) + "\n"
    if (first_bytes, log_text, diagnostics) != (
        second_bytes,
        repeated_log,
        repeated_diagnostics,
    ):
        raise AssertionError("source-registry build is not deterministic")
    checks += 1

    sources = registry.get("sources")
    if not isinstance(sources, list):
        raise AssertionError("generated registry lacks a sources array")
    canonical_ids = {record["id"] for record in sources}
    aliases = {
        alias
        for record in sources
        for alias in record.get("aliases", [])
    }
    legacy_ids = {
        record["id"]
        for record in json.loads((ROOT / "data/sources.json").read_text())
    }
    missing_legacy_ids = sorted(legacy_ids - canonical_ids - aliases)
    if missing_legacy_ids:
        raise AssertionError(f"legacy source IDs were lost: {missing_legacy_ids}")
    checks += 1

    input_records, _, input_counts = load_input_records(ROOT)
    if len(input_records) != 357 or sum(input_counts.values()) != 357:
        raise AssertionError(
            f"expected 357 structured input rows, got {len(input_records)}"
        )
    row_addresses = [
        f"{record['_origin']}:{record['id']}" for record in input_records
    ]
    if len(set(row_addresses)) != len(row_addresses):
        raise AssertionError("structured input rows do not have unique qualified addresses")
    output_addresses = [
        address
        for record in sources
        for address in [str(record["id"]), *map(str, record.get("aliases", []))]
    ]
    missing_rows = sorted(
        address for address in row_addresses if output_addresses.count(address) != 1
    )
    if missing_rows:
        raise AssertionError(
            "structured rows did not map exactly once through qualified aliases: "
            f"{missing_rows}"
        )
    checks += 1

    expected_bibliography_aliases = {
        "loihi1": "Davies18",
        "xylo-kws": "Bos24-XyloKWS",
        "spikerplus": "Carpegna24-SpikerPlus",
        "rueckauer": "Rueckauer17-SNNTB",
    }
    sources_by_id = {str(record["id"]): record for record in sources}
    missing_bibliography_aliases = {
        source_id: alias
        for source_id, alias in expected_bibliography_aliases.items()
        if alias not in sources_by_id[source_id].get("aliases", [])
    }
    if missing_bibliography_aliases:
        raise AssertionError(
            "bibliography metadata did not resolve refmap aliases: "
            f"{missing_bibliography_aliases}"
        )
    checks += 1

    if "arfa-2025-spinnaker2" in canonical_ids:
        raise AssertionError("a bibliography-only work was imported into the registry")
    if "Arfa25-SpiNN2NIR->arfa-2025-spinnaker2" not in diagnostics.get(
        "unmatched_refmap_targets", []
    ):
        raise AssertionError("a truly unmatched bibliography mapping was not deferred")
    checks += 1

    neuroflex = sources_by_id["neuroflex"]
    if neuroflex["title"] != (
        "NeuroFlex: Column-Exact ANN-SNN Co-Execution Accelerator with "
        "Cost-Guided Scheduling"
    ) or neuroflex["authors"] != (
        "Varun Manjunath, Pranav Ramesh, Gopalakrishnan Srinivasan"
    ):
        raise AssertionError("NeuroFlex did not use official primary-source metadata")
    gelneuro = sources_by_id["gelneuro"]
    if gelneuro["title"] != (
        "GelNeuro: A Sensing-Computing Integrated Neuromorphic Tactile System "
        "for Texture Recognition"
    ) or gelneuro["authors"] != (
        "Luoyang Bian, Xinpan Meng, Zhenghua Ma, Houcheng Li, Long Cheng"
    ):
        raise AssertionError("GelNeuro did not use official primary-source metadata")
    if "withdrawn" not in f"{gelneuro['venue']} {gelneuro['notes']}".lower():
        raise AssertionError("GelNeuro withdrawal status was not retained")
    checks += 1

    audited_ids = {
        "andrei2024-deep-unrolling-spinnaker2",
        "arfa2025-spiking-q-spinnaker2",
        "datta2025-snn-meets-ann",
        "mt-snn",
        "pascal",
        "qac",
        "temporal-flexibility",
    }
    stale_audited_sources = {
        source_id: (
            sources_by_id[source_id]["retrieval_status"],
            sources_by_id[source_id]["verification_status"],
        )
        for source_id in audited_ids
        if (
            sources_by_id[source_id]["retrieval_status"] != "full_text"
            or sources_by_id[source_id]["verification_status"] != "verified"
        )
    }
    if stale_audited_sources:
        raise AssertionError(
            "claim-audited sources were not promoted from their reviewed inputs: "
            f"{stale_audited_sources}"
        )
    checks += 1

    conflict_fixture = [
        {
            "id": "conflict-a",
            "title": "Materially Different First Title",
            "authors": "A. First",
            "year": 2024,
            "url": "https://example.org/same-work",
            "_origin": "fixture-a.json",
            "_rank": 2,
            "_index": 0,
        },
        {
            "id": "conflict-b",
            "title": "Unrelated Second Title",
            "authors": "B. Second",
            "year": 2024,
            "url": "https://example.org/same-work",
            "_origin": "fixture-b.json",
            "_rank": 3,
            "_index": 0,
        },
    ]
    conflict_clusters, identity_conflicts = cluster_records(conflict_fixture, {})
    if len(conflict_clusters) != 1 or identity_conflicts:
        raise AssertionError("conflict fixture must merge through its exact URL")
    _, metadata_conflicts, _ = resolve_cluster(conflict_clusters[0], {}, set())
    conflicting_fields = {item.get("field") for item in metadata_conflicts}
    if not {"title", "authors"} <= conflicting_fields:
        raise AssertionError(
            "material title and author differences were silently resolved: "
            f"{metadata_conflicts}"
        )
    checks += 1

    if diagnostics.get("true_duplicate_count") != 84:
        raise AssertionError(
            "duplicate-cluster accounting must include only the 84 multi-input "
            f"clusters, got {diagnostics.get('true_duplicate_count')!r}"
        )
    if len(diagnostics.get("merged_groups", [])) != 84:
        raise AssertionError("merged_groups contains singleton provenance aliases")
    checks += 1

    metadata_ids = diagnostics.get("metadata_only_ids", [])
    expected_metadata_line = (
        "- Metadata-only IDs: "
        + (", ".join(f"`{item}`" for item in metadata_ids) if metadata_ids else "none")
        + "."
    )
    if expected_metadata_line not in log_text:
        raise AssertionError("source-validation log does not enumerate metadata-only IDs")
    checks += 1

    address_counts: dict[str, int] = {}
    for record in sources:
        for address in [str(record["id"]), *map(str, record.get("aliases", []))]:
            address_counts[address] = address_counts.get(address, 0) + 1
    colliding_addresses = sorted(
        address for address, count in address_counts.items() if count > 1
    )
    if colliding_addresses:
        raise AssertionError(
            f"canonical IDs or aliases address multiple works: {colliding_addresses}"
        )
    slayer_paper = next(record for record in sources if record["id"] == "slayer")
    slayer_docs = next(
        record for record in sources if record["id"] == "lava-dl-slayer-docs"
    )
    if slayer_paper["title"] == slayer_docs["title"]:
        raise AssertionError("SLAYER paper and Lava-DL documentation were conflated")
    if "slayer" in slayer_docs.get("aliases", []):
        raise AssertionError("ambiguous plain alias 'slayer' was assigned to the docs")
    if "sources.json:slayer" not in slayer_docs.get("aliases", []):
        raise AssertionError("qualified SLAYER documentation alias was lost")
    checks += 1

    prior_ids = {
        survey["source_id"]
        for survey in json.loads(
            (ROOT / "data/prior-survey-coverage.json").read_text()
        )["surveys"]
    }
    if not prior_ids <= canonical_ids:
        raise AssertionError(
            f"prior-survey canonical IDs changed: {sorted(prior_ids - canonical_ids)}"
        )
    checks += 1

    if diagnostics.get("unresolved_conflicts"):
        raise AssertionError(
            f"unresolved source conflicts remain: {diagnostics['unresolved_conflicts']}"
        )
    checks += 1

    if not log_text.endswith("\n") or "# Source validation log" not in log_text:
        raise AssertionError("source validation log is incomplete")
    checks += 1

    print(f"verify-source-registry-build: {checks} contract checks passed")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, KeyError, OSError) as error:
        print(f"verify-source-registry-build: FAILED: {error}", file=sys.stderr)
        raise SystemExit(1)
