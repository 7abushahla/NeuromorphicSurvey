#!/usr/bin/env python3
"""Validate the survey's source manifests before installation or site assembly."""

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SITE_MANIFEST = ROOT / "data/site-manifest.json"
FIGURE_MANIFEST = ROOT / "data/figure-manifest.json"
SECTION_KEYS = ("id", "kind", "display_number", "title", "fragment")
FIGURE_KEYS = (
    "id",
    "display_number",
    "fragment",
    "css",
    "destination_section",
    "concept",
    "question",
    "interactive",
    "status",
)


def load_manifest(path, label, errors):
    try:
        data = json.loads(path.read_text())
    except FileNotFoundError:
        errors.append(f"missing {label} manifest: {path}")
        return {}
    except json.JSONDecodeError as exc:
        errors.append(f"invalid JSON in {label} manifest: {exc}")
        return {}
    if not isinstance(data, dict):
        errors.append(f"{label} manifest must be a JSON object")
        return {}
    if data.get("schema_version") != 1:
        errors.append(f"{label} manifest must declare schema_version 1")
    return data


def require_nonempty(record, keys, label, errors):
    for key in keys:
        if key not in record:
            errors.append(f"{label} is missing {key!r}")
        elif isinstance(record[key], str) and not record[key].strip():
            errors.append(f"{label} has an empty {key!r}")


def require_strings(record, keys, label, errors):
    for key in keys:
        if key in record and (not isinstance(record[key], str) or not record[key].strip()):
            errors.append(f"{label} {key!r} must be a non-empty string")


def validate_site(site, errors):
    fragments = site.get("fragments")
    if not isinstance(fragments, list):
        errors.append("site manifest fragments must be a list")
        return set()

    ids = []
    sections = []
    for index, record in enumerate(fragments):
        label = f"site fragment {index}"
        if not isinstance(record, dict):
            errors.append(f"{label} must be an object")
            continue
        require_nonempty(record, ("id", "kind", "fragment"), label, errors)
        require_strings(record, ("id", "kind", "fragment"), label, errors)
        identifier = record.get("id")
        if isinstance(identifier, str):
            ids.append(identifier)
        kind = record.get("kind")
        if kind not in {"shell", "section", "interactive"}:
            errors.append(f"{label} has invalid kind {kind!r}")
        if kind == "section":
            require_nonempty(record, SECTION_KEYS, label, errors)
            require_strings(record, ("id", "kind", "title", "fragment"), label, errors)
            sections.append(record)

    duplicates = sorted({identifier for identifier in ids if ids.count(identifier) > 1})
    if duplicates:
        errors.append("site manifest has duplicate IDs: " + ", ".join(duplicates))
    if len(sections) != 18:
        errors.append(f"site manifest must contain exactly 18 sections, found {len(sections)}")
    numbers = [record.get("display_number") for record in sections]
    if any(type(number) is not int for number in numbers):
        errors.append("site section display_number values must be integers")
    if numbers != list(range(1, 19)):
        errors.append("site section display numbers must be ordered 1 through 18")
    if not fragments or fragments[0].get("id") != "shell-head":
        errors.append("site manifest must begin with shell-head")
    if not fragments or fragments[-1].get("id") != "shell-tail":
        errors.append("site manifest must end with shell-tail")

    maps = [record for record in fragments if record.get("kind") == "interactive"]
    if len(maps) != 1 or maps[0].get("id") != "interactive-deployment-map":
        errors.append("site manifest must contain one interactive-deployment-map fragment")
    else:
        try:
            map_index = fragments.index(maps[0])
            section_13_index = next(
                index for index, record in enumerate(fragments)
                if record.get("id") == "section-13-complete-deployment-routes"
            )
            if map_index != section_13_index + 1:
                errors.append("interactive-deployment-map must follow Section 13 directly")
        except StopIteration:
            errors.append("site manifest is missing section-13-complete-deployment-routes")
    return {record.get("id") for record in sections if isinstance(record.get("id"), str)}


def validate_figures(figures_data, section_ids, strict, errors):
    figures = figures_data.get("figures")
    if not isinstance(figures, list):
        errors.append("figure manifest figures must be a list")
        return
    if len(figures) != 22:
        errors.append(f"figure manifest must contain 22 records, found {len(figures)}")

    ids = []
    numbers = []
    interactive = []
    for index, record in enumerate(figures):
        label = f"figure record {index}"
        if not isinstance(record, dict):
            errors.append(f"{label} must be an object")
            continue
        require_nonempty(record, FIGURE_KEYS, label, errors)
        require_strings(
            record,
            ("id", "fragment", "css", "destination_section", "concept", "question", "status"),
            label,
            errors,
        )
        identifier = record.get("id")
        if isinstance(identifier, str):
            ids.append(identifier)
        number = record.get("display_number")
        if type(number) is not int or number < 1:
            errors.append(f"{label} has invalid display_number {number!r}")
        else:
            numbers.append(number)
        if not isinstance(record.get("interactive"), bool):
            errors.append(f"{label} interactive must be boolean")
        elif record["interactive"]:
            interactive.append(record)
        if record.get("status") not in {"planned", "implemented"}:
            errors.append(f"{label} has invalid status {record.get('status')!r}")
        destination = record.get("destination_section")
        if destination not in section_ids:
            errors.append(f"{label} has unknown destination section {destination!r}")

        if record.get("status") == "implemented" or strict:
            for key in ("fragment", "css"):
                value = record.get(key)
                if not isinstance(value, str) or not value.strip():
                    continue
                if not (ROOT / value).is_file():
                    errors.append(f"{label} {key} does not exist: {value}")
        if strict and record.get("status") != "implemented":
            errors.append(f"{label} is planned; strict validation requires implemented status")

    duplicate_ids = sorted({identifier for identifier in ids if ids.count(identifier) > 1})
    if duplicate_ids:
        errors.append("figure manifest has duplicate IDs: " + ", ".join(duplicate_ids))
    duplicate_numbers = sorted({number for number in numbers if numbers.count(number) > 1})
    if duplicate_numbers:
        errors.append("figure manifest has duplicate display numbers: " + ", ".join(map(str, duplicate_numbers)))
    if len(interactive) != 1:
        errors.append(f"figure manifest must contain exactly one interactive figure, found {len(interactive)}")
    elif (
        interactive[0].get("id") != "deployment-stack-map"
        or interactive[0].get("destination_section") != "section-13-complete-deployment-routes"
    ):
        errors.append("the interactive figure must be deployment-stack-map in Section 13")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--strict",
        action="store_true",
        help="require every figure record to be implemented and every figure file to exist",
    )
    args = parser.parse_args()
    errors = []
    site = load_manifest(SITE_MANIFEST, "site", errors)
    figures = load_manifest(FIGURE_MANIFEST, "figure", errors)
    section_ids = validate_site(site, errors)
    validate_figures(figures, section_ids, args.strict, errors)

    if errors:
        print(f"manifest validation failed with {len(errors)} problem(s):", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        raise SystemExit(1)
    mode = "strict" if args.strict else "normal"
    print(f"manifest validation passed ({mode} mode)")


if __name__ == "__main__":
    main()
