#!/usr/bin/env python3
"""Generate canonical BibTeX, legacy aliases, and citation coverage."""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import parse_qsl, unquote, urlencode, urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parent.parent
REF_LI = re.compile(r'<li[^>]*\bdata-ref="([^"]+)"[^>]*>(.*?)</li>', re.S | re.I)
D_CITE = re.compile(r'<d-cite\b[^>]*\bkey="([^"]+)"', re.I)
A_CITE = re.compile(
    r'<a\b(?=[^>]*\bclass="[^"]*\bcite\b)(?=[^>]*\bdata-ref="([^"]+)")[^>]*>', re.I
)
TITLE_Q = re.compile(r'[\u201c"\u2018]([^\u201d"\u2019]{12,})[\u201d"\u2019]')
PURPOSES = {"external", "internal_analysis"}


def detag(value: str) -> str:
    value = re.sub(r'<span class="src-type">.*?</span>', '', value, flags=re.S)
    value = re.sub(r'<[^>]+>', '', value)
    value = html.unescape(value).replace('\u00a0', ' ').strip()
    return re.sub(r'^\[[^\]]{2,60}\]\s*', '', value).strip()


def parse_reference_identity(key: str, body: str) -> dict[str, str]:
    """Extract exact identity evidence without producing bibliography metadata."""
    plain = detag(body)
    match = TITLE_Q.search(plain)
    if match:
        title = re.sub(r'\s+', ' ', match.group(1)).strip().rstrip('.,')
    else:
        body_text = plain
        author_match = re.match(
            r'^((?:[A-Z][\w\'\u2019\-\u00c0-\u017e]+,\s*(?:[A-Z]\.\s*){1,4},?\s*)+)', plain
        )
        if author_match:
            body_text = plain[author_match.end():]
        else:
            org_match = re.match(r'^([A-Z][\w&/.\- ]{2,34}?)\.\s+(?=[A-Z])', plain)
            if org_match and not re.match(r'^[A-Z]\.', org_match.group(1)):
                body_text = plain[org_match.end():]
        title_end = re.search(r'\.\s+(?=[A-Z0-9])|\s+https?://|\s+arXiv:', body_text)
        title = (body_text[:title_end.start()] if title_end else body_text)[:220]
        title = re.sub(r'\s+', ' ', title).strip(' .,;:')
    doi_match = re.search(
        r'(?:doi\.org/|DOI:\s*|doi:\s*)(10\.[^\s,;)\]]+)', plain, re.I
    )
    url_match = re.search(r'https?://[^\s,;)\]<]+', plain)
    arxiv_match = re.search(r'arXiv:\s*([0-9]{4}\.[0-9]{4,5})', plain)
    url = url_match.group(0).rstrip('.') if url_match else ''
    if not url and arxiv_match:
        url = f'https://arxiv.org/abs/{arxiv_match.group(1)}'
    return {
        "key": key,
        "title": title,
        "doi": doi_match.group(1).rstrip('.') if doi_match else '',
        "url": url,
    }


def normalize_title(value: object) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", value).strip() or None


def normalize_doi(value: object) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    value = re.sub(r"^https?://(?:www\.)?doi\.org/", "", value.strip(), flags=re.I)
    return value.rstrip("/.").lower() or None


def normalize_url(value: object) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    parsed = urlsplit(value.strip().replace("\\ ", " "))
    if parsed.scheme.lower() not in {"http", "https"} or not parsed.netloc:
        return None
    host = parsed.netloc.lower().removeprefix("www.")
    path = re.sub(r"/+", "/", unquote(parsed.path)).rstrip("/") or "/"
    query = [
        (key, item) for key, item in parse_qsl(parsed.query, keep_blank_values=True)
        if key.lower() not in {"fbclid", "gclid"} and not key.lower().startswith("utm_")
    ]
    if host == "arxiv.org":
        match = re.match(r"^/(?:abs|html|pdf)/([^/]+?)(?:\.pdf)?$", path, re.I)
        if match:
            path = "/abs/" + re.sub(r"v\d+$", "", match.group(1), flags=re.I)
            query = []
    if host == "openreview.net":
        review_id = dict(query).get("id")
        if review_id and path.lower() in {"/forum", "/pdf", "/attachment"}:
            path, query = "/forum", [("id", review_id)]
    return urlunsplit((parsed.scheme.lower(), host, path, urlencode(sorted(query)), ""))


def validate_registry(sources: object) -> list[dict[str, object]]:
    if not isinstance(sources, list):
        raise ValueError("source-registry.json must contain a sources array")
    ids: set[str] = set()
    addresses: dict[str, str] = {}
    for index, source in enumerate(sources):
        if not isinstance(source, dict):
            raise ValueError(f"canonical source {index} is not an object")
        source_id = source.get("id")
        if not isinstance(source_id, str) or not source_id or source_id in ids:
            raise ValueError(f"invalid or duplicate canonical source id {source_id!r}")
        ids.add(source_id)
        if source.get("purpose") not in PURPOSES:
            raise ValueError(f"canonical source {source_id!r} has invalid purpose")
        if not isinstance(source.get("title"), str) or not str(source["title"]).strip():
            raise ValueError(f"canonical source {source_id!r} lacks a title")
        if source["purpose"] == "internal_analysis" and source.get("source_type") != "internal_analysis":
            raise ValueError(f"canonical source {source_id!r} labels internal analysis as external")
        aliases = source.get("aliases")
        if not isinstance(aliases, list):
            raise ValueError(f"canonical source {source_id!r} has invalid aliases")
        for address in [source_id, source.get("canonical_key"), *aliases]:
            if not isinstance(address, str) or not address:
                raise ValueError(f"canonical source {source_id!r} has an invalid address")
            if address in addresses and addresses[address] != source_id:
                raise ValueError(f"canonical address {address!r} resolves more than once")
            addresses[address] = source_id
    return sources


def scan_fragments(root: Path) -> tuple[dict[str, dict[str, str]], set[str]]:
    bodies: dict[str, str] = {}
    cited: set[str] = set()
    fragments = sorted((root / "site").glob("sec-*.html"))
    if not fragments:
        raise ValueError("no section fragments found")
    for fragment in fragments:
        text = fragment.read_text()
        for key, body in REF_LI.findall(text):
            body = body.strip()
            old = bodies.get(key)
            if old is None or (len(body), body) > (len(old), old):
                bodies[key] = body
        for group in D_CITE.findall(text):
            cited.update(key.strip() for key in group.split(",") if key.strip())
        cited.update(A_CITE.findall(text))
    return ({key: parse_reference_identity(key, body) for key, body in sorted(bodies.items())}, cited)


def resolve_references(
    references: dict[str, dict[str, str]], sources: list[dict[str, object]]
) -> tuple[dict[str, str], dict[str, str], dict[str, list[str]]]:
    addresses: dict[str, str] = {}
    indexes: dict[str, dict[str, set[str]]] = {
        "doi": defaultdict(set), "url": defaultdict(set), "title": defaultdict(set)
    }
    for source in sources:
        source_id = str(source["id"])
        for address in [source_id, str(source["canonical_key"]), *source["aliases"]]:
            addresses[str(address)] = source_id
        for kind, identity in (
            ("doi", normalize_doi(source.get("doi"))),
            ("url", normalize_url(source.get("url"))),
            ("title", normalize_title(source.get("title"))),
        ):
            if identity:
                indexes[kind][identity].add(source_id)
    resolved: dict[str, str] = {}
    methods: dict[str, str] = {}
    ambiguous: dict[str, list[str]] = {}
    for key, evidence in sorted(references.items()):
        if key in addresses:
            resolved[key], methods[key] = addresses[key], "registry"
            continue
        for kind, normalizer in (("doi", normalize_doi), ("url", normalize_url), ("title", normalize_title)):
            identity = normalizer(evidence.get(kind))
            candidates = indexes[kind].get(identity, set()) if identity else set()
            if not candidates:
                continue
            if len(candidates) == 1:
                resolved[key], methods[key] = next(iter(candidates)), kind
            else:
                ambiguous[key] = sorted(candidates)
            break
    return resolved, methods, ambiguous


def bib_escape(value: object) -> str:
    return (str(value).replace("\\", "/").replace("{", "(").replace("}", ")")
            .replace("%", r"\%").replace("_", r"\_").replace("#", r"\#").replace("&", r"\&"))


def render_entry(source: dict[str, object]) -> str:
    article = source["source_type"] == "peer_reviewed"
    lines = [
        f"@{'article' if article else 'misc'}{{{source['id']},",
        f"  title = {{{bib_escape(source['title'])}}},",
    ]
    if source.get("authors") is not None:
        lines.append(f"  author = {{{{{bib_escape(source['authors'])}}}}},")
    if source.get("venue") is not None:
        lines.append(f"  {'journal' if article else 'howpublished'} = {{{bib_escape(source['venue'])}}},")
    for field in ("year", "doi", "url"):
        if source.get(field) is not None:
            lines.append(f"  {field} = {{{bib_escape(source[field])}}},")
    if source["purpose"] == "internal_analysis":
        lines.append("  note = {Internal analysis. Not an external publication.},")
    lines.append("}")
    return "\n".join(lines)


def build_outputs(root: Path = ROOT) -> tuple[str, dict[str, str], dict[str, object]]:
    document = json.loads((root / "data/source-registry.json").read_text())
    sources = validate_registry(document.get("sources") if isinstance(document, dict) else None)
    references, cited_keys = scan_fragments(root)
    resolved, methods, ambiguous = resolve_references(references, sources)
    reference_keys = set(references)
    unresolved = reference_keys - resolved.keys() - ambiguous.keys()
    unresolved_cited = sorted(cited_keys - resolved.keys())
    ambiguous_cited = sorted(cited_keys & ambiguous.keys())
    if unresolved_cited:
        raise ValueError(f"unresolved cited keys: {unresolved_cited}")
    if ambiguous_cited:
        raise ValueError(f"ambiguous cited keys: {ambiguous_cited}")
    if cited_keys - reference_keys:
        raise ValueError(f"cited keys lack inline identity evidence: {sorted(cited_keys-reference_keys)}")
    source_map = {str(source["id"]): source for source in sources}
    cited_ids = {resolved[key] for key in cited_keys}
    analysis_ids = sorted(key for key, source in source_map.items() if source["purpose"] == "internal_analysis")
    refmap = {key: value for key, value in sorted(resolved.items()) if key != value}
    entries = [render_entry(source) for source in sorted(sources, key=lambda item: str(item["id"]))]
    bibliography = "\n".join([
        "% Generated by tools/build-bib.py from data/source-registry.json.",
        "% Fragment reference prose is used only for exact legacy-key identity matching.",
        "% Do not edit by hand; update the canonical source registry.", "", *entries, ""
    ])
    report: dict[str, object] = {
        "defined": len(sources), "cited": len(cited_ids), "cited_keys": len(cited_keys),
        "uncited": len(source_map.keys() - cited_ids), "aliased": len(refmap),
        "cited_aliased": sum(key != resolved[key] for key in cited_keys),
        "unresolved": len(unresolved_cited), "duplicate": 0,
        "analysis_only": len(analysis_ids), "analysis_only_cited": len(cited_ids & set(analysis_ids)),
        "reference_keys": len(reference_keys), "reference_only": len(reference_keys - cited_keys),
        "reference_only_unresolved": len(unresolved - cited_keys), "ambiguous": len(ambiguous),
        "match_methods": dict(sorted(Counter(methods.values()).items())),
        "unresolved_cited": unresolved_cited,
        "unresolved_reference_only": sorted(unresolved - cited_keys),
        "ambiguous_keys": sorted(ambiguous), "analysis_only_ids": analysis_ids,
    }
    return bibliography, refmap, report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    bibliography, refmap, report = build_outputs(ROOT)
    outputs = {
        ROOT / "assets/bibliography/references.bib": bibliography,
        ROOT / "data/refmap.json": json.dumps(refmap, indent=2, sort_keys=True) + "\n",
        ROOT / "data/bibliography-report.json": json.dumps(report, indent=2, sort_keys=True) + "\n",
    }
    if args.check:
        stale = [str(path.relative_to(ROOT)) for path, text in outputs.items() if not path.exists() or path.read_text() != text]
        if stale:
            raise ValueError(f"stale outputs: {stale}")
        print(f"build-bib: {report['defined']} canonical entries current; {report['unresolved']} unresolved cited keys")
        return 0
    for path, text in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    print(
        f"defined      : {report['defined']} canonical BibTeX entries\n"
        f"cited        : {report['cited']} canonical works from {report['cited_keys']} keys\n"
        f"uncited      : {report['uncited']} canonical works\n"
        f"aliased      : {report['aliased']} reference keys ({report['cited_aliased']} cited)\n"
        f"unresolved   : {report['unresolved']} cited keys; {report['reference_only_unresolved']} uncited reference-only keys\n"
        f"duplicate    : {report['duplicate']} BibTeX definition keys\n"
        f"analysis-only: {report['analysis_only']} canonical works ({report['analysis_only_cited']} cited)"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (KeyError, OSError, TypeError, ValueError) as error:
        print(f"build-bib: FAILED: {error}", file=sys.stderr)
        raise SystemExit(1)
