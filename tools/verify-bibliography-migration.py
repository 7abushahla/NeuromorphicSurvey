#!/usr/bin/env python3
"""Verify the frozen legacy-citation migration input.

The tracked gap inventory is the reviewed authority for group membership. The
migration file may preserve legacy metadata, but it may not add, drop, split, or
combine any reviewed legacy target.
"""
from __future__ import annotations

import datetime as dt
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parent.parent
MIGRATION_PATH = ROOT / "data/bibliography-migration-sources.json"
INVENTORY_PATH = ROOT / "research/bibliography-gap-inventory.md"
REGISTRY_PATH = ROOT / "data/source-registry.json"

REQUIRED_FIELDS = {
    "id",
    "title",
    "authors",
    "year",
    "venue",
    "doi",
    "url",
    "source_type",
    "retrieval_status",
    "verification_status",
    "retrieved_on",
    "locators",
    "aliases",
    "notes",
    "purpose",
}
EXTERNAL_SOURCE_TYPES = {
    "peer_reviewed",
    "preprint",
    "official_vendor_documentation",
    "official_manufacturer_documentation",
    "official_sdk_documentation",
    "official_devkit_manual",
    "official_repository",
    "official_model_zoo",
    "official_mapper_constraints",
    "official_release_note",
    "official_measured_example",
    "marketing_material",
    "secondary_material",
    "general_web",
}
INTERNAL_ARTIFACTS = {
    "A18-Research": "research/raw/a18-snntoolbox-vs-spikingjelly.md",
    "a14-application-survey": "research/raw/a14-applications-sensors.md",
    "a17-two-populations": "research/raw/a17-two-populations.md",
}
EXPECTED_MULTI_ALIAS_GROUPS = {
    frozenset({"NIR-Porting", "nir-porting-guide"}),
    frozenset({"SJ-LavaExchangeSource", "jelly-lava-source"}),
}


def fail(message: str) -> None:
    raise AssertionError(message)


def load_json(path: Path) -> object:
    try:
        return json.loads(path.read_text())
    except FileNotFoundError as error:
        raise AssertionError(f"missing migration input: {path}") from error
    except json.JSONDecodeError as error:
        raise AssertionError(f"invalid JSON in {path}: {error}") from error


def valid_date(value: object) -> bool:
    if not isinstance(value, str):
        return False
    try:
        return dt.date.fromisoformat(value).isoformat() == value
    except ValueError:
        return False


def parse_reviewed_groups() -> tuple[list[frozenset[str]], dict[str, str]]:
    """Read the 108 reviewed group rows, not the later target-resolution table."""
    try:
        text = INVENTORY_PATH.read_text()
    except OSError as error:
        raise AssertionError(f"cannot read reviewed inventory: {error}") from error

    section = text.split("## Unresolved targets grouped into distinct works", 1)
    if len(section) != 2:
        fail("reviewed inventory lacks the distinct-work section")
    table = section[1].split("## Complete cited legacy-target inventory", 1)[0]

    groups: list[frozenset[str]] = []
    classifications: dict[str, str] = {}
    row_pattern = re.compile(
        r"^\| G\d{3} \| (?P<targets>.*?) \| (?P<classification>.*?) \|",
        re.MULTILINE,
    )
    for match in row_pattern.finditer(table):
        targets = frozenset(re.findall(r"`([^`]+)`", match.group("targets")))
        if not targets:
            fail(f"inventory group has no targets: {match.group(0)}")
        groups.append(targets)
        classification = match.group("classification").strip()
        for target in targets:
            if target in classifications:
                fail(f"inventory target appears in multiple groups: {target}")
            classifications[target] = classification

    if len(groups) != 108:
        fail(f"expected 108 reviewed inventory groups, found {len(groups)}")
    if len(classifications) != 110:
        fail(f"expected 110 reviewed unresolved targets, found {len(classifications)}")
    return groups, classifications


def record_for_alias(
    alias_index: dict[str, dict[str, object]], alias: str
) -> dict[str, object]:
    try:
        return alias_index[alias]
    except KeyError as error:
        raise AssertionError(f"missing required migration alias: {alias}") from error


def verify_identity_hazards(alias_index: dict[str, dict[str, object]]) -> int:
    registry = load_json(REGISTRY_PATH)
    if not isinstance(registry, dict) or not isinstance(registry.get("sources"), list):
        fail("canonical registry must contain a sources array for identity checks")
    canonical_by_id = {
        record["id"]: record
        for record in registry["sources"]
        if isinstance(record, dict) and isinstance(record.get("id"), str)
    }
    checks = 0

    arfa = record_for_alias(alias_index, "arfa-2025-spinnaker2")
    arfa_q = canonical_by_id.get("arfa2025-spiking-q-spinnaker2")
    if not isinstance(arfa_q, dict):
        fail("canonical registry lacks the Spiking Q-Networks Arfa paper")
    expected_arfa_title = (
        "Efficient Deployment of Spiking Neural Networks on SpiNNaker2 for DVS "
        "Gesture Recognition Using Neuromorphic Intermediate Representation"
    )
    if arfa["title"] != expected_arfa_title:
        fail("the NIR deployment Arfa paper has the wrong title")
    if str(arfa["doi"]).lower() != "10.1109/nice65350.2025.11065119":
        fail("the NIR deployment Arfa paper has the wrong DOI")
    arfa_notes = str(arfa["notes"]).lower()
    if (
        "hardware-aware fine-tuning of spiking q-networks" not in arfa_notes
        or "10.1109/icons69015.2025.00021" not in arfa_notes
    ):
        fail("the migration record does not explicitly distinguish the second Arfa paper")
    if "arfa2025-spiking-q-spinnaker2" in arfa["aliases"]:
        fail("the two Arfa papers were combined through an alias")
    if (
        arfa_q.get("title")
        != "Hardware-Aware Fine-Tuning of Spiking Q-Networks on the SpiNNaker2 "
        "Neuromorphic Platform"
        or str(arfa_q.get("doi", "")).lower()
        != "10.1109/icons69015.2025.00021"
        or arfa["id"] == arfa_q.get("id")
        or str(arfa["doi"]).lower() == str(arfa_q.get("doi", "")).lower()
    ):
        fail("the two exact Arfa identities are not preserved as distinct works")
    checks += 1

    withdrawn = record_for_alias(alias_index, "guo-2026-mtsnn-withdrawn")
    accepted = canonical_by_id.get("mt-snn-frontiers-2026")
    if not isinstance(accepted, dict):
        fail("canonical registry lacks the accepted Frontiers MT-SNN paper")
    expected_withdrawn_title = (
        "Mixed-Timestep Spiking Neural Networks with Temporal Alignment for "
        "Ultra-Low Latency Conversion"
    )
    if withdrawn["title"] != expected_withdrawn_title:
        fail("the withdrawn MT-SNN record has the wrong title")
    if withdrawn["url"] != "https://openreview.net/forum?id=4dwAZRr9L5":
        fail("the withdrawn MT-SNN record has the wrong OpenReview identity")
    withdrawn_notes = str(withdrawn["notes"]).lower()
    if (
        "withdrawn" not in withdrawn_notes
        or "10.3389/fnins.2026.1783326" not in withdrawn_notes
    ):
        fail("the withdrawn and accepted MT-SNN versions are not explicitly distinct")
    if "guo-2026-mtsnn-frontiers" in withdrawn["aliases"]:
        fail("the withdrawn and accepted MT-SNN versions share a migration record")
    if (
        accepted.get("title")
        != "Mixed-Timestep Spiking Neural Networks: A Temporal Alignment Framework "
        "for High-Efficiency Neuromorphic Computing"
        or str(accepted.get("doi", "")).lower()
        != "10.3389/fnins.2026.1783326"
        or accepted.get("url") == withdrawn["url"]
        or accepted.get("title") == withdrawn["title"]
    ):
        fail("the withdrawn and accepted MT-SNN identities are not distinct")
    checks += 1

    gelneuro = record_for_alias(alias_index, "gelneuro-2026")
    canonical_gelneuro = canonical_by_id.get("gelneuro")
    if not isinstance(canonical_gelneuro, dict):
        fail("canonical registry lacks the rejected GelNeuro record")
    gelneuro_notes = str(gelneuro["notes"]).lower()
    if gelneuro["verification_status"] == "verified":
        fail("withdrawn GelNeuro metadata became verified evidence")
    if not ({"withdrawn", "rejected", "non-evidentiary"} & set(gelneuro_notes.split())):
        fail("GelNeuro is not labeled rejected or non-evidentiary")
    if canonical_gelneuro.get("verification_status") != "rejected":
        fail("the canonical GelNeuro identity is not rejected")
    checks += 1

    return checks


def verify() -> int:
    reviewed_groups, classifications = parse_reviewed_groups()
    payload = load_json(MIGRATION_PATH)
    if not isinstance(payload, dict):
        fail("migration input must contain a JSON object")
    if payload.get("schema_version") != 1:
        fail("migration input schema_version must be 1")
    records = payload.get("sources")
    if not isinstance(records, list):
        fail("migration input must contain a sources array")

    checks = 0
    if len(records) != 108:
        fail(f"expected 108 migration records, found {len(records)}")
    checks += 1

    external_count = sum(
        isinstance(record, dict) and record.get("purpose") == "external"
        for record in records
    )
    internal_count = sum(
        isinstance(record, dict) and record.get("purpose") == "internal_analysis"
        for record in records
    )
    if external_count != 105 or internal_count != 3:
        fail(
            "expected 105 external and 3 internal_analysis records, found "
            f"{external_count} and {internal_count}"
        )
    checks += 1

    ids: list[str] = []
    aliases: list[str] = []
    migration_groups: list[frozenset[str]] = []
    alias_index: dict[str, dict[str, object]] = {}
    for index, record in enumerate(records):
        label = f"sources[{index}]"
        if not isinstance(record, dict):
            fail(f"{label} must be an object")
        missing = REQUIRED_FIELDS - set(record)
        extra = set(record) - REQUIRED_FIELDS
        if missing or extra:
            fail(f"{label} fields differ, missing={sorted(missing)}, extra={sorted(extra)}")

        record_id = record["id"]
        if not isinstance(record_id, str) or not record_id.strip():
            fail(f"{label}.id must be a nonempty string")
        ids.append(record_id)

        if not isinstance(record["title"], str) or not record["title"].strip():
            fail(f"{label}.title must be a nonempty reviewed title")
        for nullable_string in ("authors", "venue", "doi", "url"):
            value = record[nullable_string]
            if value is not None and (
                not isinstance(value, str) or not value.strip()
            ):
                fail(f"{label}.{nullable_string} must be null or a nonempty string")
            if isinstance(value, str) and value.strip().casefold() in {
                "unknown",
                "not found",
                "n.d.",
                "n/a",
                "none",
                "null",
                "unconfirmed",
            }:
                fail(f"{label}.{nullable_string} must use null for unknown metadata")
        year = record["year"]
        if year is not None and (not isinstance(year, int) or isinstance(year, bool)):
            fail(f"{label}.year must be an integer or null")
        if record["url"] is not None:
            parsed_url = urlparse(str(record["url"]))
            if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
                fail(f"{label}.url must be an HTTP(S) URL or null")
        if record["doi"] is not None and not str(record["doi"]).lower().startswith("10."):
            fail(f"{label}.doi must be a DOI or null")
        if not valid_date(record["retrieved_on"]):
            fail(f"{label}.retrieved_on must be an ISO date")
        if not isinstance(record["notes"], str) or not record["notes"].strip():
            fail(f"{label}.notes must be a nonempty string")

        record_aliases = record["aliases"]
        if (
            not isinstance(record_aliases, list)
            or not record_aliases
            or any(not isinstance(alias, str) or not alias for alias in record_aliases)
            or len(record_aliases) != len(set(record_aliases))
        ):
            fail(f"{label}.aliases must be a nonempty list of unique strings")
        group = frozenset(record_aliases)
        migration_groups.append(group)
        for alias in record_aliases:
            aliases.append(alias)
            if alias in alias_index:
                fail(f"migration alias appears in multiple records: {alias}")
            alias_index[alias] = record

        locators = record["locators"]
        if (
            not isinstance(locators, list)
            or not locators
            or any(not isinstance(locator, str) or not locator.strip() for locator in locators)
        ):
            fail(f"{label}.locators must be a nonempty list of strings")

        purpose = record["purpose"]
        if purpose == "external":
            if record["source_type"] not in EXTERNAL_SOURCE_TYPES:
                fail(f"{label} uses an invalid external source type")
            if record["retrieval_status"] != "metadata_only":
                fail(f"{label} upgrades uninspected external retrieval status")
            if record["verification_status"] != "provisional":
                fail(f"{label} upgrades uninspected external verification status")
            if not any(
                locator.startswith("assets/bibliography/references.bib entry ")
                for locator in locators
            ) or not any(locator.startswith("site/") for locator in locators):
                fail(f"{label} does not identify both frozen migration evidence forms")
        elif purpose == "internal_analysis":
            if record["source_type"] != "internal_analysis":
                fail(f"{label} gives an internal analysis an external source type")
            if record["retrieval_status"] != "full_text":
                fail(f"{label} must identify its tracked full-text analysis artifact")
            if record["verification_status"] != "verified":
                fail(f"{label} must identify a verified tracked analysis artifact")
            if len(record_aliases) != 1 or record_aliases[0] not in INTERNAL_ARTIFACTS:
                fail(f"{label} is not one of the three reviewed internal analyses")
            artifact = INTERNAL_ARTIFACTS[record_aliases[0]]
            if artifact not in locators:
                fail(f"{label} does not locate its tracked analysis artifact")
            if not (ROOT / artifact).is_file():
                fail(f"{label} points to a missing analysis artifact: {artifact}")
        else:
            fail(f"{label}.purpose must be external or internal_analysis")

    if len(ids) != len(set(ids)):
        fail("migration record IDs must be unique")
    if ids != sorted(ids, key=lambda item: (item.casefold(), item)):
        fail("migration records must be sorted deterministically by ID")
    checks += 1

    reviewed_targets = set(classifications)
    migrated_targets = set(aliases)
    if reviewed_targets != migrated_targets:
        fail(
            "migration aliases do not exactly cover reviewed unresolved targets, "
            f"missing={sorted(reviewed_targets - migrated_targets)}, "
            f"extra={sorted(migrated_targets - reviewed_targets)}"
        )
    if len(aliases) != 110:
        fail(f"expected 110 unique migration aliases, found {len(aliases)}")
    checks += 1

    if set(migration_groups) != set(reviewed_groups):
        fail("migration records do not preserve the 108 reviewed identity groups")
    multi_alias_groups = {group for group in migration_groups if len(group) > 1}
    if multi_alias_groups != EXPECTED_MULTI_ALIAS_GROUPS:
        fail(f"unexpected multi-alias groups: {sorted(map(sorted, multi_alias_groups))}")
    checks += 1

    expected_internal_aliases = {
        target
        for target, classification in classifications.items()
        if classification == "analysis-only"
    }
    actual_internal_aliases = {
        alias
        for record in records
        if record["purpose"] == "internal_analysis"
        for alias in record["aliases"]
    }
    if expected_internal_aliases != actual_internal_aliases:
        fail("internal-analysis purpose labels do not match the reviewed inventory")
    checks += 1

    checks += verify_identity_hazards(alias_index)
    return checks


def main() -> int:
    try:
        checks = verify()
    except (AssertionError, OSError, TypeError, ValueError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print(
        "PASS: bibliography migration input "
        "(108 records, 105 external, 3 internal_analysis, 110 aliases, "
        f"{checks} contract groups)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
