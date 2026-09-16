#!/usr/bin/env python3
"""Validate implemented static figures declared by the figure manifest."""

import html
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "data/figure-manifest.json"
XA = ("x", "x1", "x2", "cx")
YA = ("y", "y1", "y2", "cy")
RESOURCE_TAGS = ("img", "image", "iframe", "object", "embed", "video", "audio", "source")
FORBIDDEN_TEXT = (
    "FIGURE TO DRAW",
    "TODO",
    "TBD",
    "PLACEHOLDER",
    "Redraw of",
    "source file",
    "vault",
)


def attr(tag, name):
    match = re.search(rf"\b{re.escape(name)}\s*=\s*(['\"])(.*?)\1", tag, re.I | re.S)
    return match.group(2) if match else None


def local_name(tag):
    return tag.rsplit("}", 1)[-1]


def load_records(errors):
    try:
        payload = json.loads(MANIFEST.read_text())
    except FileNotFoundError:
        errors.append(f"figure manifest does not exist: {MANIFEST}")
        return []
    except json.JSONDecodeError as exc:
        errors.append(f"invalid JSON in figure manifest: {exc}")
        return []
    records = payload.get("figures") if isinstance(payload, dict) else None
    if not isinstance(records, list):
        errors.append("figure manifest must contain a figures list")
        return []
    return records


def check_css(record, css_text, errors):
    number = record["display_number"]
    label = f"{record['id']} (Figure {number})"
    scope = f"#figure-{number}"
    clean = re.sub(r"/\*.*?\*/", "", css_text, flags=re.S)
    if clean.count("{") != clean.count("}"):
        errors.append(f"{label}: css has unbalanced braces")
    if re.search(r"@import\b|url\(\s*['\"]?(?:https?:|/|\.)", clean, re.I):
        errors.append(f"{label}: css references an external asset")
    for prelude in re.findall(r"([^{}]+)\{", clean):
        prelude = prelude.strip()
        if not prelude or prelude.startswith("@"):
            continue
        for selector in prelude.split(","):
            selector = selector.strip()
            if not selector or selector in {"from", "to"} or re.fullmatch(r"\d+(?:\.\d+)?%", selector):
                continue
            if scope not in selector:
                errors.append(f"{label}: css selector {selector!r} is not scoped to {scope}")


def check_accessibility(svg, own_ids, label, errors):
    if svg.get("role") != "img":
        errors.append(f"{label}: inline svg must declare role=\"img\"")
    aria_label = (svg.get("aria-label") or "").strip()
    labelledby = (svg.get("aria-labelledby") or "").split()
    if aria_label:
        return
    direct = {local_name(child.tag): child for child in list(svg)}
    if labelledby:
        missing = [identifier for identifier in labelledby if identifier not in own_ids]
        if missing:
            errors.append(f"{label}: aria-labelledby has unresolved id(s): {', '.join(missing)}")
            return
        referenced = set(labelledby)
        title_id = direct.get("title").get("id") if direct.get("title") is not None else None
        desc_id = direct.get("desc").get("id") if direct.get("desc") is not None else None
        if title_id in referenced and desc_id in referenced:
            return
    errors.append(
        f"{label}: svg needs an accessible title and description via aria-labelledby, "
        "or an equivalent non-empty aria-label"
    )


def check_axis_units(svg, label, errors):
    for element in svg.iter():
        classes = set((element.get("class") or "").split())
        axis_kind = (element.get("data-axis") or "").strip().lower()
        explicit = axis_kind in {"numeric", "numerical"} or bool(
            classes & {"numeric-axis", "numerical-axis"}
        )
        numeric_labels = [
            "".join(child.itertext()).strip()
            for child in element.iter()
            if local_name(child.tag) == "text"
            and re.fullmatch(r"[+−-]?(?:\d+(?:\.\d*)?|\.\d+)", "".join(child.itertext()).strip())
        ]
        inferred = "axis" in classes and len(set(numeric_labels)) >= 2
        if not explicit and not inferred:
            continue
        unit = element.get("data-unit")
        if unit is None:
            unit = element.get("data-axis-unit")
        text = " ".join(part.strip() for part in element.itertext() if part.strip())
        textual_unit = bool(re.search(r"\([^()\d\s][^()]*\)|\b(?:dimensionless|unitless)\b", text, re.I))
        if (unit is None or not unit.strip()) and (explicit or not textual_unit):
            errors.append(f"{label}: numerical axis must declare a non-empty unit")


def check_geometry(svg, label, errors):
    raw_viewbox = svg.get("viewBox")
    if raw_viewbox is None:
        errors.append(f"{label}: svg has no viewBox")
        return None
    try:
        values = [float(value) for value in raw_viewbox.replace(",", " ").split()]
        if len(values) != 4:
            raise ValueError("expected four numbers")
        x0, y0, width, height = values
        if width <= 0 or height <= 0:
            raise ValueError("width and height must be positive")
    except (TypeError, ValueError) as exc:
        errors.append(f"{label}: invalid viewBox {raw_viewbox!r}: {exc}")
        return None
    for element in svg.iter():
        name = local_name(element.tag)
        for attribute in XA:
            value = element.get(attribute)
            if value and re.fullmatch(r"-?(?:\d+(?:\.\d*)?|\.\d+)", value):
                coordinate = float(value)
                if not x0 - 1 <= coordinate <= x0 + width + 1:
                    errors.append(
                        f"{label}: {name} {attribute}={value} outside viewBox width {width:g}"
                    )
        for attribute in YA:
            value = element.get(attribute)
            if value and re.fullmatch(r"-?(?:\d+(?:\.\d*)?|\.\d+)", value):
                coordinate = float(value)
                if not y0 - 1 <= coordinate <= y0 + height + 1:
                    errors.append(
                        f"{label}: {name} {attribute}={value} outside viewBox height {height:g}"
                    )
    return raw_viewbox


def check_fragment(record, source, errors, global_ids):
    number = record["display_number"]
    semantic_id = record["id"]
    dom_id = f"figure-{number}"
    prefix = f"f{number}"
    label = f"{semantic_id} (Figure {number})"

    figure_tags = re.findall(r"<figure\b[^>]*>", source, re.I)
    if len(figure_tags) != 1 or len(re.findall(r"</figure\s*>", source, re.I)) != 1:
        errors.append(f"{label}: fragment must hold exactly one <figure> element")
    elif attr(figure_tags[0], "id") != dom_id:
        errors.append(
            f"{label}: semantic manifest id {semantic_id!r} expected DOM id {dom_id!r}"
        )

    captions = re.findall(r"<figcaption\b[^>]*>.*?</figcaption\s*>", source, re.I | re.S)
    if len(captions) != 1:
        errors.append(f"{label}: fragment must hold exactly one <figcaption> element")
        caption = ""
    else:
        caption = captions[0]
        if not re.match(
            rf"<figcaption\b[^>]*>\s*<b>\s*Figure\s+{number}\s*:\s*</b>",
            caption,
            re.I | re.S,
        ):
            errors.append(f"{label}: caption must open with <b>Figure {number}:</b>")

    svg_blocks = re.findall(r"<svg\b.*?</svg\s*>", source, re.I | re.S)
    if len(svg_blocks) != 1:
        errors.append(f"{label}: fragment must hold exactly one inline <svg> element")
        return None
    svg_source = svg_blocks[0]
    svg_open = re.match(r"<svg\b[^>]*>", svg_source, re.I | re.S).group(0)
    if attr(svg_open, "width") is not None or attr(svg_open, "height") is not None:
        errors.append(f"{label}: svg must scale by viewBox alone, without width or height attributes")

    if re.search(r"<(?:script|link)\b", source, re.I):
        errors.append(f"{label}: fragment references an external asset or script")
    for tag_name in RESOURCE_TAGS:
        if re.search(rf"<{tag_name}\b", source, re.I):
            errors.append(f"{label}: fragment references an external asset or script")
            break
    if re.search(r"url\(\s*['\"]?(?:https?:|/|\.)", source, re.I):
        errors.append(f"{label}: fragment references an external asset or script")
    if re.search(r"<use\b[^>]*(?:href|xlink:href)\s*=\s*['\"](?!#)", source, re.I):
        errors.append(f"{label}: fragment references an external asset or script")
    if "prefers-color-scheme" in source:
        errors.append(f"{label}: dark mode rules do not belong in a figure fragment")

    visible = html.unescape(re.sub(r"<[^>]+>", " ", source))
    for phrase in FORBIDDEN_TEXT:
        if re.search(rf"(?<![\w-]){re.escape(phrase)}(?![\w-])", visible, re.I):
            errors.append(
                f"{label}: forbidden placeholder/editorial language {phrase!r}"
            )
    if "—" in caption or "&#8212;" in caption.lower() or "&mdash;" in caption.lower():
        errors.append(f"{label}: em dash in figure caption")
    for leak in (".pdf", "Chapter", "thesis"):
        if leak.lower() in re.sub(r"<[^>]+>", "", caption).lower():
            errors.append(f"{label}: caption still contains editorial term {leak!r}")

    try:
        svg = ET.fromstring(svg_source)
    except Exception as exc:
        errors.append(f"{label}: svg is not well formed: {exc}")
        return None

    svg_ids = [element.get("id") for element in svg.iter() if element.get("id")]
    own_ids = set(svg_ids)
    duplicates = sorted({identifier for identifier in svg_ids if svg_ids.count(identifier) > 1})
    for identifier in duplicates:
        errors.append(f"{label}: duplicate SVG id {identifier!r}")
    for identifier in svg_ids:
        if not identifier.startswith(prefix):
            errors.append(f"{label}: SVG id {identifier!r} is not prefixed {prefix!r}")
        global_ids[identifier].append(semantic_id)
    references = set(
        re.findall(r"url\(\s*['\"]?#([^)\s'\"]+)['\"]?\s*\)", svg_source)
    )
    for reference in sorted(references):
        if reference not in own_ids:
            errors.append(f"{label}: url(#{reference}) has no definition in this figure")
    for reference in re.findall(r"(?:href|xlink:href)\s*=\s*['\"]#([^'\"]+)['\"]", svg_source):
        if reference not in own_ids:
            errors.append(f"{label}: local href #{reference} has no definition in this figure")

    check_accessibility(svg, own_ids, label, errors)
    check_axis_units(svg, label, errors)
    viewbox = check_geometry(svg, label, errors)
    figure_class = attr(figure_tags[0], "class") if figure_tags else None
    return viewbox, figure_class or "?"


def validate_records(records, errors):
    semantic_ids = []
    dom_ids = []
    valid = []
    for index, record in enumerate(records):
        if not isinstance(record, dict) or record.get("interactive") is not False:
            continue
        semantic_id = record.get("id")
        number = record.get("display_number")
        label = semantic_id if isinstance(semantic_id, str) and semantic_id else f"record {index}"
        if not isinstance(semantic_id, str) or not re.fullmatch(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*", semantic_id):
            errors.append(f"{label}: static manifest id must be a non-empty semantic slug")
            continue
        if type(number) is not int or number < 1:
            errors.append(f"{label}: display_number must be a positive integer")
            continue
        if record.get("status") not in {"implemented", "planned"}:
            errors.append(f"{label}: status must be 'implemented' or 'planned'")
            continue
        semantic_ids.append(semantic_id)
        dom_ids.append(f"figure-{number}")
        valid.append(record)
    for identifier in sorted({value for value in semantic_ids if semantic_ids.count(value) > 1}):
        errors.append(f"duplicate semantic figure id {identifier!r}")
    for identifier in sorted({value for value in dom_ids if dom_ids.count(value) > 1}):
        errors.append(f"duplicate figure DOM id {identifier!r}")
    return valid


def main():
    errors = []
    records = validate_records(load_records(errors), errors)
    global_ids = defaultdict(list)
    summaries = []
    implemented_count = 0
    planned_count = 0

    for record in records:
        semantic_id = record["id"]
        number = record["display_number"]
        if record["status"] == "planned":
            planned_count += 1
            missing = [key for key in ("fragment", "css") if not (ROOT / record[key]).is_file()]
            detail = "missing planned " + " and ".join(missing) if missing else "planned assets already present"
            print(f"planned {semantic_id} (Figure {number}): {detail}")
            continue

        implemented_count += 1
        fragment_path = ROOT / record.get("fragment", "")
        css_path = ROOT / record.get("css", "")
        label = f"{semantic_id} (Figure {number})"
        if not fragment_path.is_file():
            errors.append(f"{label}: implemented fragment does not exist: {record.get('fragment')}")
            continue
        if not css_path.is_file():
            errors.append(f"{label}: implemented css does not exist: {record.get('css')}")
            continue
        summary = check_fragment(record, fragment_path.read_text(), errors, global_ids)
        check_css(record, css_path.read_text(), errors)
        if summary:
            summaries.append((semantic_id, number, *summary))

    for identifier, owners in sorted(global_ids.items()):
        if len(owners) > 1:
            errors.append(f"duplicate SVG id {identifier!r} in figures {owners}")

    for semantic_id, number, viewbox, figure_class in summaries:
        print(f"implemented {semantic_id} (Figure {number}): viewBox {viewbox or '?'} [{figure_class}]")
    print()
    if errors:
        print(f"figure validation failed with {len(errors)} problem(s):", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        raise SystemExit(1)
    print(
        f"all implemented static figures passed ({implemented_count}); "
        f"planned static figures: {planned_count}"
    )


if __name__ == "__main__":
    main()
