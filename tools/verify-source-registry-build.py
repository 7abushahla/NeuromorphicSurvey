#!/usr/bin/env python3
"""Verify deterministic source-registry normalization and migration contracts."""
from __future__ import annotations

import json
import runpy
import shutil
import sys
import tempfile
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
    load_legacy_alias_migration = module["load_legacy_alias_migration"]
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
    version_clusters, version_conflicts = cluster_records(version_fixture)
    if len(version_clusters) != 1 or version_conflicts:
        raise AssertionError(
            "an arXiv preprint and supported version-of-record identity must merge: "
            f"clusters={len(version_clusters)}, conflicts={version_conflicts}"
        )
    version_record, version_field_conflicts, _ = resolve_cluster(
        version_clusters[0], set()
    )
    if version_field_conflicts or version_record["doi"] != "10.1000/published.42":
        raise AssertionError(
            "the publisher DOI must be canonical for a merged preprint/publication pair"
        )
    checks += 1

    def canonicalize_fixture(rows: list[dict[str, object]]) -> list[dict[str, object]]:
        clusters, conflicts = cluster_records(rows)
        if conflicts:
            raise AssertionError(f"fixture produced identity conflicts: {conflicts}")
        id_counts: dict[str, int] = {}
        for cluster in clusters:
            for item in {str(record["id"]) for record in cluster}:
                id_counts[item] = id_counts.get(item, 0) + 1
        ambiguous_ids = {item for item, count in id_counts.items() if count > 1}
        resolved = []
        for cluster in clusters:
            record, field_conflicts, _ = resolve_cluster(cluster, ambiguous_ids)
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

    with tempfile.TemporaryDirectory() as temp_directory:
        isolated_root = Path(temp_directory) / "NeuromorphicSurvey"
        shutil.copytree(ROOT, isolated_root)
        (isolated_root / "assets/bibliography/references.bib").unlink()
        (isolated_root / "data/refmap.json").unlink()
        isolated_registry, isolated_log, _ = build_outputs(isolated_root)
    isolated_registry_bytes = (
        json.dumps(isolated_registry, indent=2, ensure_ascii=False) + "\n"
    )
    if (
        isolated_registry_bytes != (ROOT / "data/source-registry.json").read_text()
        or isolated_log != (ROOT / "research/source-validation-log.md").read_text()
    ):
        raise AssertionError(
            "registry outputs depend on downstream bibliography or refmap assets"
        )
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

    committed_registry = (ROOT / "data/source-registry.json").read_text()
    committed_log = (ROOT / "research/source-validation-log.md").read_text()
    if committed_registry != first_bytes or committed_log != log_text:
        raise AssertionError(
            "committed source-registry outputs differ from a fresh deterministic build"
        )
    checks += 1

    sources = registry.get("sources")
    if not isinstance(sources, list):
        raise AssertionError("generated registry lacks a sources array")
    registry_locator_pairs = {
        (str(source["id"]), str(locator))
        for source in sources
        for locator in source.get("locators", [])
    }
    expected_audit_locator_pairs: set[tuple[str, str]] = set()
    for audit_path in sorted((ROOT / "research/claim-audits").glob("audit-*.json")):
        audit = json.loads(audit_path.read_text())
        for section in ("claims", "route_edges"):
            for record in audit.get(section, []):
                for source_ref in record.get("source_refs", []):
                    expected_audit_locator_pairs.update(
                        (str(source_ref["source_id"]), str(locator))
                        for locator in source_ref["locators"]
                    )
    missing_audit_locator_pairs = sorted(
        expected_audit_locator_pairs - registry_locator_pairs
    )
    if missing_audit_locator_pairs:
        raise AssertionError(
            "canonical registry omitted source-specific audit provenance pairs "
            f"({len(missing_audit_locator_pairs)} missing): "
            f"{missing_audit_locator_pairs}"
        )
    checks += 1

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

    input_records, input_counts = load_input_records(ROOT)
    if input_counts.get("bibliography-migration-sources.json") != 108:
        raise AssertionError(
            "builder did not consume 108 frozen bibliography migration records"
        )
    foundations_rows = len(
        json.loads((ROOT / "data/foundations-sources.json").read_text())["sources"]
    )
    targets_rows = len(
        json.loads((ROOT / "data/targets-sources.json").read_text())["sources"]
    )
    expected_rows = 476 + foundations_rows + targets_rows
    if len(input_records) != expected_rows or sum(input_counts.values()) != expected_rows:
        raise AssertionError(
            f"expected {expected_rows} structured input rows, got {len(input_records)}"
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

    migrated_aliases, unresolved_aliases, alias_provenance = (
        load_legacy_alias_migration(ROOT)
    )
    if sum(len(aliases) for aliases in migrated_aliases.values()) != 89:
        raise AssertionError("expected 89 frozen pre-cycle alias assignments")
    if unresolved_aliases != ["furber-2004-nofm->furber2004"]:
        raise AssertionError(
            f"unexpected unresolved legacy aliases: {unresolved_aliases}"
        )
    if (
        alias_provenance.get("captured_at_commit")
        != "3d8b86cfb6e7564a6cd0ad4ca242607f427f6776"
        or alias_provenance.get("captured_from")
        != ["assets/bibliography/references.bib", "data/refmap.json"]
    ):
        raise AssertionError("legacy alias migration provenance is incomplete")
    if diagnostics.get("legacy_alias_count") != 89:
        raise AssertionError("builder did not report all frozen legacy aliases")
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
            "upstream alias migration did not preserve legacy aliases: "
            f"{missing_bibliography_aliases}"
        )
    checks += 1

    if "Arfa25-SpiNN2NIR->arfa-2025-spinnaker2" in diagnostics.get(
        "unresolved_legacy_aliases", []
    ):
        raise AssertionError("the migrated Arfa legacy alias remains unresolved")
    checks += 1

    migration = json.loads(
        (ROOT / "data/bibliography-migration-sources.json").read_text()
    )["sources"]
    address_to_source: dict[str, dict[str, object]] = {}
    for source in sources:
        for address in [str(source["id"]), *map(str, source.get("aliases", []))]:
            if address in address_to_source:
                raise AssertionError(f"canonical address collision: {address}")
            address_to_source[address] = source
    migration_aliases = {
        alias for record in migration for alias in record["aliases"]
    }
    if len(migration_aliases) != 110:
        raise AssertionError(
            f"expected 110 frozen migration aliases, got {len(migration_aliases)}"
        )
    missing_migration_aliases = sorted(migration_aliases - address_to_source.keys())
    if missing_migration_aliases:
        raise AssertionError(
            "migration aliases do not resolve through the canonical registry: "
            f"{missing_migration_aliases}"
        )
    if address_to_source["bhattacharjee-2023-hardware"]["doi"] is not None:
        raise AssertionError(
            "a null provisional migration DOI was synthesized from its URL"
        )
    checks += 1

    invalid_purposes = {
        str(source["id"]): source.get("purpose")
        for source in sources
        if source.get("purpose") not in {"external", "internal_analysis"}
    }
    if invalid_purposes:
        raise AssertionError(
            f"canonical records lack explicit valid purpose labels: {invalid_purposes}"
        )
    internal_expectations = {
        "a14-application-survey": "research/raw/a14-applications-sensors.md",
        "a17-two-populations": "research/raw/a17-two-populations.md",
        "A18-Research": "research/raw/a18-snntoolbox-vs-spikingjelly.md",
    }
    for address, artifact in internal_expectations.items():
        internal = address_to_source.get(address)
        if internal is None:
            raise AssertionError(f"internal analysis alias does not resolve: {address}")
        if (
            internal.get("purpose") != "internal_analysis"
            or internal.get("source_type") != "internal_analysis"
            or artifact not in internal.get("locators", [])
        ):
            raise AssertionError(
                f"internal analysis provenance was not preserved for {address}: {internal}"
            )
    if address_to_source["A18-Research"]["id"] != "a18-sourcecode-comparison":
        raise AssertionError("A18 legacy alias did not bind to its canonical analysis")
    checks += 1

    nir_arfa = address_to_source.get("arfa-2025-spinnaker2")
    q_arfa = address_to_source.get("arfa2025-spiking-q-spinnaker2")
    if nir_arfa is None or q_arfa is None:
        raise AssertionError("both reviewed Arfa records must resolve")
    if (
        str(nir_arfa.get("doi", "")).lower()
        != "10.1109/nice65350.2025.11065119"
        or str(q_arfa.get("doi", "")).lower()
        != "10.1109/icons69015.2025.00021"
        or nir_arfa["id"] == q_arfa["id"]
    ):
        raise AssertionError("the two Arfa records were conflated or misidentified")
    if address_to_source.get("arfa") is not nir_arfa:
        raise AssertionError("the Arfa preprint identity was not merged with the NIR paper")
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
        "mt-snn-withdrawn-iclr",
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


    frontiers = sources_by_id["mt-snn-frontiers-2026"]
    if (
        frontiers["retrieval_status"] != "partial_text"
        or frontiers["verification_status"] != "provisional"
    ):
        raise AssertionError("accepted MT-SNN access level must remain partial/provisional")
    if any("manuscript" in locator.lower() for locator in frontiers["locators"]):
        raise AssertionError("withdrawn-manuscript locators leaked into accepted MT-SNN")
    withdrawn = sources_by_id["mt-snn-withdrawn-iclr"]
    if any("frontiers" in locator.lower() for locator in withdrawn["locators"]):
        raise AssertionError("accepted-article locators leaked into withdrawn MT-SNN")
    if any("MT-SNN" in locator for locator in sources_by_id["pascal"]["locators"]):
        raise AssertionError("a co-cited MT-SNN locator was promoted onto PASCAL")
    arfa = sources_by_id["arfa2025-spiking-q-spinnaker2"]
    if arfa["title"] != (
        "Hardware-Aware Fine-Tuning of Spiking Q-Networks on the SpiNNaker2 "
        "Neuromorphic Platform"
    ) or arfa["doi"] != "10.1109/icons69015.2025.00021":
        raise AssertionError("Arfa exact title/DOI regression failed")
    checks += 1

    if (
        withdrawn["retrieval_status"] != "full_text"
        or withdrawn["verification_status"] != "verified"
    ):
        raise AssertionError("provisional migration metadata downgraded reviewed MT-SNN")
    gelneuro = sources_by_id["gelneuro"]
    if gelneuro["verification_status"] != "rejected":
        raise AssertionError("provisional migration metadata revived rejected GelNeuro")
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
    conflict_clusters, identity_conflicts = cluster_records(conflict_fixture)
    if len(conflict_clusters) != 1 or identity_conflicts:
        raise AssertionError("conflict fixture must merge through its exact URL")
    _, metadata_conflicts, _ = resolve_cluster(conflict_clusters[0], set())
    conflicting_fields = {item.get("field") for item in metadata_conflicts}
    if not {"title", "authors"} <= conflicting_fields:
        raise AssertionError(
            "material title and author differences were silently resolved: "
            f"{metadata_conflicts}"
        )
    checks += 1

    purpose_conflict_fixture = [
        {
            "id": "external-work",
            "title": "One Explicit Identity",
            "year": 2025,
            "url": "https://example.org/purpose-conflict",
            "purpose": "external",
            "_origin": "fixture-a.json",
            "_rank": 1,
            "_index": 0,
        },
        {
            "id": "internal-work",
            "title": "One Explicit Identity",
            "year": 2025,
            "url": "https://example.org/purpose-conflict",
            "purpose": "internal_analysis",
            "source_type": "internal_analysis",
            "locators": ["research/raw/internal.md"],
            "_origin": "fixture-b.json",
            "_rank": 4,
            "_index": 0,
        },
    ]
    purpose_clusters, purpose_identity_conflicts = cluster_records(
        purpose_conflict_fixture
    )
    if len(purpose_clusters) != 1 or purpose_identity_conflicts:
        raise AssertionError("purpose conflict fixture must share one exact identity")
    _, purpose_conflicts, _ = resolve_cluster(purpose_clusters[0], set())
    if "purpose" not in {item.get("field") for item in purpose_conflicts}:
        raise AssertionError("external/internal purpose conflict was silently resolved")
    checks += 1

    alias_collision_fixture = [
        {
            "id": "alias-owner-a",
            "title": "First Alias Owner",
            "year": 2025,
            "url": "https://example.org/alias-owner-a",
            "aliases": ["shared-reviewed-alias"],
            "_origin": "fixture-a.json",
            "_rank": 4,
            "_index": 0,
        },
        {
            "id": "alias-owner-b",
            "title": "Second Alias Owner",
            "year": 2025,
            "url": "https://example.org/alias-owner-b",
            "aliases": ["shared-reviewed-alias"],
            "_origin": "fixture-b.json",
            "_rank": 4,
            "_index": 1,
        },
    ]
    _, alias_conflicts = cluster_records(alias_collision_fixture)
    if "alias_collision" not in {item.get("kind") for item in alias_conflicts}:
        raise AssertionError("explicit alias collision was not rejected")
    checks += 1

    metadata_ids = diagnostics.get("metadata_only_ids", [])
    expected_metadata_line = (
        "- Metadata-only IDs: "
        + (", ".join(f"`{item}`" for item in metadata_ids) if metadata_ids else "none")
        + "."
    )
    if expected_metadata_line not in log_text:
        raise AssertionError("source-validation log does not enumerate metadata-only IDs")
    missing_metadata = diagnostics.get("missing_metadata", [])
    if not missing_metadata or "## Unresolved metadata" not in log_text:
        raise AssertionError("source-validation log omits preserved null metadata fields")
    expected_missing_lines = {
        f"- `{item['id']}`: "
        + ", ".join(f"`{field}`" for field in item["fields"])
        + "."
        for item in missing_metadata
    }
    if not expected_missing_lines <= set(log_text.splitlines()):
        raise AssertionError("source-validation log does not enumerate every metadata gap")
    if (
        "- All 110 frozen legacy aliases resolve exactly once through canonical IDs "
        "or aliases." not in log_text
        or "- Unmatched mappings: `furber-2004-nofm->furber2004`." not in log_text
    ):
        raise AssertionError(
            "source-validation log does not separate frozen alias coverage from the "
            "pre-existing uncited refmap target"
        )
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
