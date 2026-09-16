#!/usr/bin/env python3
"""Build the canonical source registry from structured legacy evidence inputs."""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import parse_qsl, unquote, urlencode, urlsplit, urlunsplit


ROOT = Path(__file__).resolve().parent.parent
AUDIT_DATE = "2026-09-16"
INPUTS = (
    ("sources.json", None, 1),
    ("evidence-papers.json", "sources", 2),
    ("evidence-stack.json", "sources", 3),
    ("bibliography-migration-sources.json", "sources", 4),
)
TRACKING_QUERY_PREFIXES = ("utm_",)
TRACKING_QUERY_KEYS = {"fbclid", "gclid"}
VALID_SOURCE_TYPES = {
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
    "internal_analysis",
}
PRIOR_SOURCE_TYPE_MAP = {
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
PRIOR_RETRIEVAL_MAP = {
    "full_text": "full_text",
    "verified": "full_text",
    "partial": "partial_text",
    "partial_text": "partial_text",
    "metadata_only": "metadata_only",
    "not_retrieved": "not_retrieved",
    "provisional": "metadata_only",
}
CANONICAL_ID_RESOLUTIONS = {
    "arfa": "arfa-2025-spinnaker2",
    "fission": "adaptive-fission",
    "lava-dl-slayer-docs": "lava-dl-slayer-docs",
    "mtt": "temporal-flexibility",
}

# These pairs are reviewed publication-version identities that cannot be inferred
# from exact normalized metadata alone. They remain deliberately narrow so that a
# shared author or topic can never collapse two different works.
REVIEWED_IDENTITY_MERGES = (
    ("arfa", "arfa-2025-spinnaker2"),
)

# A differing publication year is never resolved by input priority alone. Each known
# case states the bibliographic or versioned-document basis for the selected year.
YEAR_RESOLUTIONS: dict[str, tuple[int, str]] = {
    "nxtf": (
        2022,
        "Resolved to the ACM JETC publication year. The 2021 value describes the preprint.",
    ),
    "hiaer-spike-cri": (
        2026,
        "Resolved to the current official documentation snapshot represented by the audited record.",
    ),
    "quartz": (
        2024,
        "Resolved to the revised 2024 version; the 2023 value is the initial preprint submission.",
    ),
}

# Filled only from primary-source metadata. Keys may be any member ID in a cluster.
METADATA_OVERRIDES: dict[str, dict[str, object]] = {
    "a18-sourcecode-comparison": {
        "title": (
            "Source-level comparison of snn_toolbox and spikingjelly "
            "ann2snn/lava_exchange/nir_exchange code "
            "(fetched raw.githubusercontent.com, 2026-09-15)"
        ),
        "note": (
            "The reviewed source-inspection title is retained over the later "
            "bibliography summary."
        ),
    },
    "arfa-2025-spinnaker2": {
        "title": (
            "Efficient Deployment of Spiking Neural Networks on SpiNNaker2 for "
            "DVS Gesture Recognition Using Neuromorphic Intermediate Representation"
        ),
        "authors": (
            "Arfa, S. and Vogginger, B. and Liu, C. and Partzsch, J. and "
            "Schöne, M. and Mayr, C."
        ),
        "year": 2025,
        "venue": "NICE",
        "doi": "10.1109/nice65350.2025.11065119",
        "url": "https://doi.org/10.1109/nice65350.2025.11065119",
        "note": (
            "The legacy Arfa preprint record and the reviewed NICE publication "
            "describe the same NIR deployment work. The NICE publication metadata "
            "is canonical."
        ),
    },
    "davies-2021-loihi": {
        "title": "Advancing Neuromorphic Computing With Loihi: A Survey of Results and Outlook",
        "authors": "M. Davies, A. Wild, G. Orchard, Y. Sandamirskaya et al.",
        "note": "Title and author form resolved to the peer-reviewed article metadata.",
    },
    "prior-s29-ayasi-2025": {
        "title": (
            "A Practical Tutorial on Spiking Neural Networks: Comprehensive Review, "
            "Models, Experiments, Software Tools, and Implementation Guidelines"
        ),
        "authors": (
            "Bahgat Ayasi, Cristóbal J. Carmona, Mohammed Saleh, Angel M. García-Vico"
        ),
        "note": "Title and authors resolved to the reviewed full-text survey record.",
    },
    "brehove": {
        "title": "Sigma-Delta Neural Network Conversion on Loihi 2",
        "authors": "M. Brehove, S. A. Tumpa, E. Kyubwa, N. Menon, V. Narayanan",
        "note": "Title and authors resolved to the version-of-record metadata.",
    },
    "pascal": {
        "title": (
            "PASCAL: Precise and Efficient ANN-SNN Conversion using Spike "
            "Accumulation and Adaptive Layerwise Activation"
        ),
        "authors": "Pranav Ramesh, Gopalakrishnan Srinivasan",
        "note": "Expanded title and authors resolved to the paper metadata.",
    },
    "temporal-flexibility": {
        "title": (
            "Temporal Flexibility in Spiking Neural Networks: Towards "
            "Generalization Across Time Steps and Deployment Friendliness"
        ),
        "authors": "Kangrui Du, Yuhang Wu, Shikuang Deng, Shi Gu",
        "note": (
            "Title and complete author names resolved from the ICLR paper. "
            "The legacy MTT record names the paper's training method."
        ),
    },
    "qcfs": {
        "title": (
            "Optimal ANN-SNN Conversion for High-accuracy and Ultra-low-latency "
            "Spiking Neural Networks"
        ),
        "authors": "T. Bu, W. Fang, J. Ding, P. Dai, Z. Yu, T. Huang",
        "note": "The parenthetical QCFS label is retained as an alias, not title text.",
    },
    "quartz": {
        "title": "Ultra-low-power Image Classification on Neuromorphic Hardware",
        "authors": "C. Lenz, G. Orchard, S. Sheik",
        "note": "Title and authors resolved to the Quartz paper metadata.",
    },
    "richter": {
        "title": (
            "Speck: A Smart event-based Vision Sensor with a low latency 327K "
            "Neuron Convolutional Neural Network Processing Pipeline"
        ),
        "authors": "O. Richter, S. Xing, M. De Marchi et al.",
        "note": "Title and authors resolved to the Speck paper metadata.",
    },
    "spinnaker-chip": {
        "title": (
            "SpiNNaker: A 1-W 18-Core System-on-Chip for Massively-Parallel "
            "Neural Network Simulation"
        ),
        "note": "Expanded title resolved to the peer-reviewed chip paper metadata.",
    },
    "spj-lava": {
        "title": "Convert to Lava for Loihi Deployment",
        "authors": "SpikingJelly project",
        "note": "Title and authors resolved to the official SpikingJelly documentation.",
    },
    "apex": {
        "title": "APEX: A Dual-Sparsity Accelerator for Precise and Efficient SNN Inference",
        "authors": (
            "Devgokul Bawa Venkatesh, Sreeram Radhakrishnan, Rajshekhar "
            "Rakshit, Gopalakrishnan Srinivasan"
        ),
        "note": "Title and authors resolved from the official arXiv record for arXiv:2608.19046.",
    },
    "neuroflex": {
        "title": (
            "NeuroFlex: Column-Exact ANN-SNN Co-Execution Accelerator with "
            "Cost-Guided Scheduling"
        ),
        "authors": "Varun Manjunath, Pranav Ramesh, Gopalakrishnan Srinivasan",
        "year": 2025,
        "url": "https://arxiv.org/abs/2511.05215",
        "note": (
            "Title and authors resolved from the official arXiv record "
            "for arXiv:2511.05215."
        ),
    },
    "gelneuro": {
        "title": (
            "GelNeuro: A Sensing-Computing Integrated Neuromorphic Tactile "
            "System for Texture Recognition"
        ),
        "authors": (
            "Luoyang Bian, Xinpan Meng, Zhenghua Ma, Houcheng Li, Long Cheng"
        ),
        "year": 2026,
        "venue": "arXiv:2607.05241 (withdrawn)",
        "doi": "10.48550/arXiv.2607.05241",
        "url": "https://arxiv.org/abs/2607.05241",
        "verification_status": "rejected",
        "note": (
            "Official arXiv metadata records this preprint as withdrawn by the "
            "authors because it requires substantial revision and additional "
            "validation. It must not support substantive survey claims."
        ),
    },
    "sddpg": {
        "authors": "Guangzhi Tang, Neelesh Kumar, Konstantinos P. Michmizos",
        "note": "Authors resolved from the official arXiv record for arXiv:2003.01157.",
    },
    "sew-resnet": {
        "title": "Deep Residual Learning in Spiking Neural Networks",
        "note": "The parenthetical SEW-ResNet label is retained as an alias, not title text.",
    },
    "spinnaker-goalkeeper": {
        "title": (
            "System integration of neuromorphic SNN, DVS camera, SpiNNaker and "
            "servo motor for a goalkeeper robot"
        ),
        "authors": "S.-S. Cheng, D. Nikolić",
        "note": "Title and authors resolved to the paper metadata.",
    },
    "bootstrap": {
        "year": 2021,
        "note": "The exact rendered lava-docs source was finalized in commit d3ff31c on 2021-11-16.",
    },
    "netx": {
        "year": 2021,
        "note": "The exact rendered lava-docs source was last changed in commit 94b64f8 on 2021-11-13.",
    },
    "lava-exec": {
        "year": 2022,
        "note": "The exact notebook source was last changed in Lava commit 19132bb on 2022-07-13.",
    },
    "sinabs": {
        "year": 2025,
        "note": "The cited v3.1.1 documentation belongs to the 2025-11-27 release.",
    },
    "sinabs-nir": {
        "year": 2025,
        "note": "The cited v3.0.3 documentation belongs to the 2025-07-22 release.",
    },
    "nir-example": {
        "year": 2024,
        "note": "The exact tutorial source was added or updated in NIR commit a2e9318 on 2024-07-06.",
    },
    "snntorch": {
        "year": 2026,
        "note": "The rendered documentation identifies version 1.0.0, released on 2026-06-29.",
    },
    "nengo-dl": {
        "year": 2023,
        "note": "The unversioned page identifies NengoDL 3.6.1.dev0; stable v3.6.0 was released in 2023.",
    },
    "nengo-loihi": {
        "year": 2022,
        "note": "The documentation identifies v1.1.0, released 2022-01-25.",
    },
    "spinnaker2-tools": {
        "year": 2026,
        "note": "The current documentation corresponds to py-spinnaker2 v0.8.1 dated 2026-09-09.",
    },
    "spj-lynxi": {
        "year": 2026,
        "note": "The exact official tutorial source was last changed in commit db85038 on 2026-05-13.",
    },
    "spinnaker2-chip": {
        "year": 2024,
        "doi": "10.48550/arXiv.2401.04491",
        "url": "https://arxiv.org/abs/2401.04491",
        "note": "Identity resolved to the SpiNNaker2 system paper submitted 2024-01-09.",
    },
    "hxtorch": {
        "year": 2026,
        "note": "The exact current BrainScaleS-2 demo source was last changed in commit 7821187 on 2026-09-11.",
    },
    "bidl": {
        "title": "BIDL",
        "authors": "LynxiTech contributors",
        "year": 2025,
        "note": "The official BIDL repository was created on 2025-01-20 and has no tagged releases.",
    },
    "lava-dl-slayer-docs": {
        "title": "Lava-DL SLAYER documentation",
        "authors": "Intel Lava-nc contributors",
        "year": 2021,
        "note": "The Lava-DL SLAYER documentation source dates to the 2021 lava-docs publication.",
    },
    "toolbox": {
        "title": "SNN Toolbox documentation",
        "authors": "B. Rueckauer and SNN Toolbox contributors",
        "year": 2020,
        "note": "The exact SNN Toolbox introduction source is bound to the 2020 v0.5.0 release commit.",
    },
}


def read_json(path: Path) -> object:
    return json.loads(path.read_text())


def write_text(path: Path, text: str) -> None:
    path.write_text(text)


def _balanced_value(text: str, start: int, opener: str, closer: str) -> tuple[str, int]:
    if opener == closer:
        escaped = False
        for index in range(start + 1, len(text)):
            character = text[index]
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == closer:
                return text[start + 1:index], index + 1
        raise ValueError("unterminated quoted BibTeX value")
    depth = 0
    escaped = False
    for index in range(start, len(text)):
        character = text[index]
        if escaped:
            escaped = False
            continue
        if character == "\\":
            escaped = True
            continue
        if character == opener:
            depth += 1
        elif character == closer:
            depth -= 1
            if depth == 0:
                return text[start + 1:index], index + 1
    raise ValueError("unterminated BibTeX value")


def parse_bibliography(path: Path) -> dict[str, dict[str, object]]:
    """Parse the simple field subset needed for refmap identity resolution.

    Bibliography entries are identity metadata only. They never become registry rows.
    The parser intentionally supports braced and quoted values without depending on a
    third-party BibTeX package that is absent from the repository environment.
    """
    text = path.read_text()
    entries: dict[str, dict[str, object]] = {}
    cursor = 0
    header = re.compile(r"@[A-Za-z]+\s*\{\s*([^,\s]+)\s*,")
    while match := header.search(text, cursor):
        key = match.group(1)
        body_start = match.end()
        body, cursor = _balanced_value("{" + text[body_start:], 0, "{", "}")
        # _balanced_value sees the synthetic opening brace, so cursor is relative to
        # the sliced string and must be translated back to the full bibliography.
        cursor = body_start + cursor - 1
        fields: dict[str, object] = {"id": key}
        index = 0
        while index < len(body):
            while index < len(body) and (body[index].isspace() or body[index] == ","):
                index += 1
            name_match = re.match(r"([A-Za-z][A-Za-z0-9_-]*)\s*=\s*", body[index:])
            if not name_match:
                next_comma = body.find(",", index)
                index = len(body) if next_comma < 0 else next_comma + 1
                continue
            name = name_match.group(1).lower()
            index += name_match.end()
            if index < len(body) and body[index] == "{":
                value, index = _balanced_value(body, index, "{", "}")
            elif index < len(body) and body[index] == '"':
                value, index = _balanced_value(body, index, '"', '"')
            else:
                end = body.find(",", index)
                if end < 0:
                    end = len(body)
                value, index = body[index:end], end
            value = value.strip().replace("{", "").replace("}", "")
            fields[name] = value
        year = fields.get("year")
        if isinstance(year, str) and year.isdigit():
            fields["year"] = int(year)
        if "author" in fields:
            fields["authors"] = fields["author"]
        entries[key] = fields
    return entries


def normalize_title(value: object) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    ascii_value = (
        unicodedata.normalize("NFKD", value)
        .encode("ascii", "ignore")
        .decode("ascii")
        .lower()
    )
    normalized = re.sub(r"[^a-z0-9]+", " ", ascii_value).strip()
    return normalized or None


def normalize_url(value: object) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    parsed = urlsplit(value.strip())
    if parsed.scheme.lower() not in {"http", "https"} or not parsed.netloc:
        return None
    scheme = parsed.scheme.lower()
    host = parsed.netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    path = re.sub(r"/+", "/", unquote(parsed.path)).rstrip("/") or "/"
    if host == "doi.org":
        path = path.lower()
    query = [
        (key, item)
        for key, item in parse_qsl(parsed.query, keep_blank_values=True)
        if key.lower() not in TRACKING_QUERY_KEYS
        and not key.lower().startswith(TRACKING_QUERY_PREFIXES)
    ]
    if host == "arxiv.org":
        match = re.match(r"^/(?:abs|html|pdf)/([^/]+?)(?:\.pdf)?$", path, re.I)
        if match:
            arxiv_id = re.sub(r"v\d+$", "", match.group(1), flags=re.I)
            path = f"/abs/{arxiv_id}"
            query = []
    if host == "openreview.net":
        review_id = dict(query).get("id")
        if review_id and path.lower() in {"/forum", "/pdf", "/attachment"}:
            path = "/forum"
            query = [("id", review_id)]
    return urlunsplit((scheme, host, path, urlencode(sorted(query)), ""))


def extract_doi(record: dict[str, object]) -> str | None:
    value = record.get("doi")
    if isinstance(value, str):
        candidate = value.strip()
        if candidate and not candidate.lower().startswith("unassigned:"):
            candidate = re.sub(r"^https?://(?:www\.)?doi\.org/", "", candidate, flags=re.I)
            return candidate.rstrip("/.").lower()
    url = normalize_url(record.get("url") or record.get("canonical_url"))
    if url:
        parsed = urlsplit(url)
        if parsed.netloc == "doi.org":
            candidate = unquote(parsed.path).strip("/")
            return candidate.rstrip("/.").lower() or None
        if parsed.netloc == "arxiv.org" and parsed.path.startswith("/abs/"):
            arxiv_id = parsed.path.removeprefix("/abs/")
            return f"10.48550/arxiv.{arxiv_id}".lower()
    return None


def output_doi(record: dict[str, object]) -> str | None:
    """Return citable DOI metadata without filling frozen migration nulls."""
    if (
        record.get("_origin") == "bibliography-migration-sources.json"
        and record.get("doi") is None
    ):
        return None
    return extract_doi(record)


def is_arxiv_doi(value: str) -> bool:
    return value.lower().startswith("10.48550/arxiv.")


def publication_version_dois(dois: set[str]) -> tuple[str | None, set[str]]:
    """Return a unique version-of-record DOI and its arXiv aliases, if supported.

    This rule is deliberately narrow. It applies only when a title match has already
    passed the year and author checks, the DOI set contains at least one arXiv DOI,
    and exactly one non-arXiv DOI remains. Two different publisher DOIs are never
    collapsed by this rule.
    """
    arxiv_dois = {doi for doi in dois if is_arxiv_doi(doi)}
    publisher_dois = dois - arxiv_dois
    if arxiv_dois and len(publisher_dois) == 1:
        return next(iter(publisher_dois)), arxiv_dois
    return None, set()


def stable_record_key(record: dict[str, object]) -> tuple[object, ...]:
    """Order source records by content, never by their position in an input array."""
    year = record.get("year")
    return (
        int(record.get("_rank", 99)),
        str(record.get("id") or ""),
        normalize_title(record.get("title")) or "",
        normalize_title(record.get("authors")) or "",
        int(year) if isinstance(year, int) and not isinstance(year, bool) else -1,
        extract_doi(record) or "",
        normalize_url(record.get("url") or record.get("canonical_url")) or "",
        str(record.get("_origin") or ""),
    )


def source_type(record: dict[str, object]) -> str:
    existing = record.get("source_type")
    if isinstance(existing, str) and existing in VALID_SOURCE_TYPES:
        return existing
    if isinstance(existing, str) and existing in PRIOR_SOURCE_TYPE_MAP:
        return PRIOR_SOURCE_TYPE_MAP[existing]
    raw = str(record.get("type") or "").lower()
    url = normalize_url(record.get("url")) or ""
    host = urlsplit(url).netloc
    if raw == "peer-reviewed":
        return "peer_reviewed"
    if raw == "preprint":
        return "preprint"
    if raw == "vendor-material":
        return "marketing_material"
    if raw == "repository-state":
        return "official_repository"
    if raw == "community-commentary":
        return "secondary_material"
    if raw == "official-documentation":
        if host in {"github.com", "gitlab.com"}:
            return "official_repository"
        if any(name in host for name in ("intel.com", "synsense.ai", "brainchip.com")):
            return "official_manufacturer_documentation"
        return "official_sdk_documentation"
    if host == "doi.org":
        return "peer_reviewed"
    if host == "arxiv.org":
        return "preprint"
    if host == "openreview.net":
        return "peer_reviewed"
    if host in {"github.com", "gitlab.com"}:
        return "official_repository"
    if any(
        marker in host
        for marker in (
            "readthedocs.io",
            "lava-nc.org",
            "nengo.ai",
            "neuroir.org",
            "electronicvisions.github.io",
            "spinnaker2.gitlab.io",
            "isn.ucsd.edu",
        )
    ):
        return "official_sdk_documentation"
    return "general_web"


class UnionFind:
    def __init__(self, size: int) -> None:
        self.parent = list(range(size))

    def find(self, item: int) -> int:
        if self.parent[item] != item:
            self.parent[item] = self.find(self.parent[item])
        return self.parent[item]

    def union(self, first: int, second: int) -> None:
        first_root, second_root = self.find(first), self.find(second)
        if first_root == second_root:
            return
        self.parent[max(first_root, second_root)] = min(first_root, second_root)


def load_input_records(root: Path) -> tuple[list[dict[str, object]], dict[str, str], dict[str, int]]:
    records: list[dict[str, object]] = []
    counts: dict[str, int] = {}
    prior_count = 0
    for letter in "ABCD":
        filename = f"batch-{letter}.json"
        batch = read_json(root / "research/prior-surveys" / filename)
        candidates = batch.get("source_candidates")
        if not isinstance(candidates, list):
            raise ValueError(f"{filename} does not contain source_candidates")
        for index, candidate in enumerate(candidates):
            if not isinstance(candidate, dict):
                raise ValueError(f"{filename} source candidate {index} is not an object")
            record = dict(candidate)
            source_id = record.get("id") or record.get("source_id")
            if not isinstance(source_id, str) or not source_id:
                raise ValueError(f"{filename} source candidate {index} lacks an id")
            record["id"] = source_id
            record["url"] = record.get("canonical_url") or record.get("url")
            raw_retrieval = str(record.get("retrieval_status") or "metadata_only")
            record["retrieval_status"] = PRIOR_RETRIEVAL_MAP.get(
                raw_retrieval, raw_retrieval
            )
            record["verification_status"] = (
                "verified" if record["retrieval_status"] == "full_text" else "provisional"
            )
            record["retrieved_on"] = str(record.get("retrieved_on") or AUDIT_DATE)
            record["_origin"] = f"research/prior-surveys/{filename}"
            record["_rank"] = 0
            record["_index"] = index
            records.append(record)
            prior_count += 1
    counts["prior-survey batches A-D"] = prior_count
    for filename, collection, rank in INPUTS:
        document = read_json(root / "data" / filename)
        rows = document if collection is None else document[collection]
        if not isinstance(rows, list):
            raise ValueError(f"{filename} does not contain the expected source array")
        counts[filename] = len(rows)
        for index, row in enumerate(rows):
            if not isinstance(row, dict):
                raise ValueError(f"{filename} source {index} is not an object")
            record = dict(row)
            record["_origin"] = filename
            record["_rank"] = rank
            record["_index"] = index
            records.append(record)

    # Claim audits carry source-specific review states and locators. Add one rank-zero
    # overlay per inspected source. Metadata continues to come from the structured
    # source inputs, so an audit cannot invent or overwrite bibliographic identity.
    audited_locators: dict[str, set[str]] = defaultdict(set)
    audited_origins: dict[str, set[str]] = defaultdict(set)
    audited_retrieval_states: dict[str, set[str]] = defaultdict(set)
    audited_verification_states: dict[str, set[str]] = defaultdict(set)
    for audit_path in sorted((root / "research/claim-audits").glob("audit-*.json")):
        audit = read_json(audit_path)
        for section_name in ("claims", "route_edges"):
            section_records = audit.get(section_name, [])
            if not isinstance(section_records, list):
                raise ValueError(
                    f"{audit_path.name} does not contain a {section_name} array"
                )
            if section_name == "claims" and not section_records:
                raise ValueError(f"{audit_path.name} does not contain a claims array")
            for record_index, record in enumerate(section_records):
                label = f"{section_name}[{record_index}]"
                if not isinstance(record, dict):
                    raise ValueError(
                        f"{audit_path.name} {label} is not an object"
                    )
                source_refs = record.get("source_refs")
                if not isinstance(source_refs, list) or not source_refs:
                    raise ValueError(
                        f"{audit_path.name} {label} has invalid source_refs"
                    )
                for ref_index, source_ref in enumerate(source_refs):
                    if not isinstance(source_ref, dict):
                        raise ValueError(
                            f"{audit_path.name} {label} source ref "
                            f"{ref_index} is not an object"
                        )
                    source_id = source_ref.get("source_id")
                    locators = source_ref.get("locators")
                    retrieval_status = source_ref.get("retrieval_status")
                    verification_status = source_ref.get("verification_status")
                    if not isinstance(source_id, str) or not source_id:
                        raise ValueError(
                            f"{audit_path.name} {label} source ref "
                            f"{ref_index} has invalid source_id"
                        )
                    if not isinstance(locators, list) or not locators or not all(
                        isinstance(locator, str) and locator for locator in locators
                    ):
                        raise ValueError(
                            f"{audit_path.name} {label} source ref "
                            f"{source_id!r} has invalid locators"
                        )
                    if retrieval_status not in {
                        "full_text", "partial_text", "metadata_only", "not_retrieved"
                    }:
                        raise ValueError(
                            f"{audit_path.name} {label} source ref "
                            f"{source_id!r} has invalid retrieval_status"
                        )
                    if verification_status not in {
                        "verified", "provisional", "conflicted", "rejected"
                    }:
                        raise ValueError(
                            f"{audit_path.name} {label} source ref "
                            f"{source_id!r} has invalid verification_status"
                        )
                    audited_locators[source_id].update(locators)
                    audited_origins[source_id].add(audit_path.name)
                    audited_retrieval_states[source_id].add(str(retrieval_status))
                    audited_verification_states[source_id].add(str(verification_status))

    metadata_by_id: dict[str, list[dict[str, object]]] = defaultdict(list)
    for record in records:
        metadata_by_id[str(record["id"])].append(record)
    audit_count = 0
    for source_id in sorted(audited_locators):
        if len(audited_retrieval_states[source_id]) != 1:
            raise ValueError(
                f"claim-audited source {source_id!r} has inconsistent retrieval states: "
                f"{sorted(audited_retrieval_states[source_id])}"
            )
        if len(audited_verification_states[source_id]) != 1:
            raise ValueError(
                f"claim-audited source {source_id!r} has inconsistent verification states: "
                f"{sorted(audited_verification_states[source_id])}"
            )
        candidates = metadata_by_id.get(source_id, [])
        if not candidates:
            raise ValueError(
                f"claim-audited source {source_id!r} has no structured metadata input"
            )
        base = min(candidates, key=stable_record_key)
        overlay = {
            key: value
            for key, value in base.items()
            if not key.startswith("_")
        }
        overlay.update({
            "id": source_id,
            "retrieval_status": next(iter(audited_retrieval_states[source_id])),
            "verification_status": next(iter(audited_verification_states[source_id])),
            "retrieved_on": AUDIT_DATE,
            "locators": sorted(audited_locators[source_id]),
            "notes": (
                (
                    "Full text, official documentation, or released source was inspected in "
                    if next(iter(audited_retrieval_states[source_id])) == "full_text"
                    else "Partial text or an abstract was inspected in "
                    if next(iter(audited_retrieval_states[source_id])) == "partial_text"
                    else "Source metadata was inspected in "
                )
                + ", ".join(sorted(audited_origins[source_id])) + "."
            ),
            "_origin": "research/claim-audits",
            "_rank": 0,
            "_index": audit_count,
        })
        records.append(overlay)
        audit_count += 1
    counts["claim-audit reviewed sources"] = audit_count
    refmap = read_json(root / "data/refmap.json")
    if not isinstance(refmap, dict) or not all(
        isinstance(key, str) and isinstance(value, str)
        for key, value in refmap.items()
    ):
        raise ValueError("refmap.json must contain a string-to-string object")
    return records, refmap, counts


def member_ids(records: list[dict[str, object]]) -> set[str]:
    return {str(record["id"]) for record in records}


def author_tokens(record: dict[str, object]) -> set[str]:
    normalized = normalize_title(record.get("authors")) or ""
    return {
        token for token in normalized.split()
        if len(token) > 2 and token not in {"and", "the", "etal", "team", "group"}
    }


def cluster_records(
    records: list[dict[str, object]], refmap: dict[str, str],
) -> tuple[list[list[dict[str, object]]], list[dict[str, object]]]:
    union_find = UnionFind(len(records))
    unresolved: list[dict[str, object]] = []

    def component_dois(index: int) -> set[str]:
        root = union_find.find(index)
        return {
            doi
            for item, record in enumerate(records)
            if union_find.find(item) == root
            for doi in [extract_doi(record)]
            if doi
        }

    def merge_group(kind: str, key: str, indices: list[int]) -> None:
        anchor = indices[0]
        for candidate in indices[1:]:
            if union_find.find(anchor) == union_find.find(candidate):
                continue
            if kind == "title":
                first_year = records[anchor].get("year")
                second_year = records[candidate].get("year")
                first_authors = author_tokens(records[anchor])
                second_authors = author_tokens(records[candidate])
                incompatible_years = (
                    isinstance(first_year, int)
                    and isinstance(second_year, int)
                    and abs(first_year - second_year) > 1
                )
                incompatible_authors = (
                    bool(first_authors)
                    and bool(second_authors)
                    and not first_authors.intersection(second_authors)
                )
                if incompatible_years or incompatible_authors:
                    unresolved.append({
                        "kind": kind,
                        "key": key,
                        "record_ids": sorted(
                            member_ids([records[anchor], records[candidate]])
                        ),
                        "reason": (
                            "title-only match has incompatible year or author metadata"
                        ),
                    })
                    continue
            first_dois = component_dois(anchor)
            second_dois = component_dois(candidate)
            if first_dois and second_dois and first_dois != second_dois:
                version_doi, _ = publication_version_dois(first_dois | second_dois)
                if version_doi:
                    union_find.union(anchor, candidate)
                    continue
                unresolved.append({
                    "kind": kind,
                    "key": key,
                    "record_ids": sorted(
                        member_ids([records[anchor], records[candidate]])
                    ),
                    "reason": "identity match carries incompatible non-null DOIs",
                    "dois": sorted(first_dois | second_dois),
                })
                continue
            union_find.union(anchor, candidate)

    identity_functions = (
        ("doi", extract_doi),
        ("url", lambda record: normalize_url(record.get("url") or record.get("canonical_url"))),
        ("title", lambda record: normalize_title(record.get("title"))),
    )
    for kind, identity in identity_functions:
        groups: dict[str, list[int]] = defaultdict(list)
        for index, record in enumerate(records):
            key = identity(record)
            if key:
                groups[key].append(index)
        for key in sorted(groups):
            if len(groups[key]) > 1:
                merge_group(kind, key, groups[key])

    ids_to_indices: dict[str, list[int]] = defaultdict(list)
    for index, record in enumerate(records):
        ids_to_indices[str(record["id"])].append(index)
    for source_id, indices in sorted(ids_to_indices.items()):
        if len(indices) > 1 and any(
            records[index].get("_origin") == "bibliography-migration-sources.json"
            for index in indices
        ):
            merge_group("migration_id", source_id, indices)
    for first_id, second_id in REVIEWED_IDENTITY_MERGES:
        if first_id in ids_to_indices and second_id in ids_to_indices:
            merge_group(
                "reviewed_identity",
                f"{first_id}->{second_id}",
                [ids_to_indices[first_id][0], ids_to_indices[second_id][0]],
            )
    for alias, target in sorted(refmap.items()):
        if alias not in ids_to_indices or target not in ids_to_indices:
            continue
        merge_group("refmap", f"{alias}->{target}", [ids_to_indices[alias][0], ids_to_indices[target][0]])

    clusters: dict[int, list[dict[str, object]]] = defaultdict(list)
    for index, record in enumerate(records):
        clusters[union_find.find(index)].append(record)

    # Explicit legacy aliases are addresses, not fuzzy identity evidence. They may
    # repeat only within one already-resolved semantic cluster. An alias that also
    # names a different record ID is equally ambiguous and therefore fails closed.
    id_roots: dict[str, set[int]] = defaultdict(set)
    explicit_alias_roots: dict[str, set[int]] = defaultdict(set)
    for index, record in enumerate(records):
        root = union_find.find(index)
        id_roots[str(record["id"])].add(root)
        aliases = record.get("aliases") or []
        if not isinstance(aliases, list):
            unresolved.append({
                "kind": "alias_collision",
                "key": str(record["id"]),
                "record_ids": [str(record["id"])],
                "reason": "explicit aliases must be a list",
            })
            continue
        for alias in aliases:
            if isinstance(alias, str) and alias:
                explicit_alias_roots[alias].add(root)
    for address, alias_roots in sorted(explicit_alias_roots.items()):
        roots = alias_roots | id_roots.get(address, set())
        if len(roots) > 1:
            unresolved.append({
                "kind": "alias_collision",
                "key": address,
                "record_ids": sorted({
                    str(record["id"])
                    for index, record in enumerate(records)
                    if union_find.find(index) in roots
                }),
                "reason": "canonical ID or explicit alias addresses multiple works",
            })

    ordered = sorted(
        clusters.values(),
        key=lambda group: min((int(record["_rank"]), str(record["id"])) for record in group),
    )
    return ordered, sorted(unresolved, key=lambda item: (str(item["kind"]), str(item["key"])))


def bibliography_aliases_for_clusters(
    clusters: list[list[dict[str, object]]],
    refmap: dict[str, str],
    bibliography: dict[str, dict[str, object]],
) -> tuple[dict[int, set[str]], list[str], list[dict[str, object]]]:
    """Match refmap targets to structured clusters without importing BibTeX-only works."""
    aliases_by_cluster: dict[int, set[str]] = defaultdict(set)
    unmatched: list[str] = []
    conflicts: list[dict[str, object]] = []

    def unique_match(
        alias: str, target: str, kind: str, candidates: set[int]
    ) -> int | None:
        if len(candidates) == 1:
            return next(iter(candidates))
        if len(candidates) > 1:
            conflicts.append({
                "kind": "bibliography_identity",
                "key": f"{alias}->{target}",
                "record_ids": sorted({
                    record_id
                    for index in candidates
                    for record_id in member_ids(clusters[index])
                }),
                "reason": f"bibliography {kind} identity matched multiple clusters",
            })
        return None

    ids_to_clusters: dict[str, set[int]] = defaultdict(set)
    doi_to_clusters: dict[str, set[int]] = defaultdict(set)
    url_to_clusters: dict[str, set[int]] = defaultdict(set)
    for cluster_index, cluster in enumerate(clusters):
        for record in cluster:
            ids_to_clusters[str(record["id"])].add(cluster_index)
            doi = extract_doi(record)
            if doi:
                doi_to_clusters[doi].add(cluster_index)
            url = normalize_url(record.get("url") or record.get("canonical_url"))
            if url:
                url_to_clusters[url].add(cluster_index)

    for alias, target in sorted(refmap.items()):
        match_index: int | None = None
        direct = ids_to_clusters.get(target, set())
        if len(direct) == 1:
            match_index = next(iter(direct))
        elif len(direct) > 1:
            unique_match(alias, target, "structured-ID", direct)
        metadata = bibliography.get(target)
        if match_index is None and metadata:
            doi = extract_doi(metadata)
            if doi:
                match_index = unique_match(
                    alias, target, "DOI", doi_to_clusters.get(doi, set())
                )
            if match_index is None:
                url = normalize_url(metadata.get("url"))
                if url:
                    match_index = unique_match(
                        alias, target, "URL", url_to_clusters.get(url, set())
                    )
            if match_index is None:
                title = normalize_title(metadata.get("title"))
                year = metadata.get("year")
                bib_authors = author_tokens(metadata)
                if title and isinstance(year, int) and bib_authors:
                    bibliography_doi = extract_doi(metadata)

                    def guarded_match(record: dict[str, object]) -> bool:
                        record_year = record.get("year")
                        record_doi = extract_doi(record)
                        same_year = record_year == year
                        preprint_publication_year = (
                            isinstance(record_year, int)
                            and abs(record_year - year) == 1
                            and bibliography_doi is not None
                            and record_doi is not None
                            and publication_version_dois(
                                {bibliography_doi, record_doi}
                            )[0] is not None
                        )
                        return (
                            normalize_title(record.get("title")) == title
                            and (same_year or preprint_publication_year)
                            and bool(author_tokens(record) & bib_authors)
                        )

                    guarded_candidates = {
                        index
                        for index, cluster in enumerate(clusters)
                        if any(guarded_match(record) for record in cluster)
                    }
                    match_index = unique_match(
                        alias, target, "guarded title/author/year", guarded_candidates
                    )
        if match_index is None:
            unmatched.append(f"{alias}->{target}")
            continue
        aliases_by_cluster[match_index].add(alias)
    return aliases_by_cluster, sorted(unmatched), conflicts


def choose_canonical_id(records: list[dict[str, object]]) -> str:
    ids = member_ids(records)
    for marker, resolved in CANONICAL_ID_RESOLUTIONS.items():
        if marker in ids:
            return resolved
    selected = min(
        records,
        key=stable_record_key,
    )
    return str(selected["id"])


def find_override(records: list[dict[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for record_id in sorted(member_ids(records)):
        result.update(METADATA_OVERRIDES.get(record_id, {}))
    return result


def pick_text(records: list[dict[str, object]], field: str) -> str | None:
    values = [
        (str(record[field]).strip(), stable_record_key(record))
        for record in records
        if isinstance(record.get(field), str) and str(record[field]).strip()
    ]
    if not values:
        return None
    return min(values, key=lambda item: (item[1], item[0]))[0]


def resolution_for_year(records: list[dict[str, object]]) -> tuple[int | None, str | None]:
    override = find_override(records)
    if isinstance(override.get("year"), int):
        return int(override["year"]), str(override.get("note") or "Manual primary-source resolution.")
    for record_id in sorted(member_ids(records)):
        if record_id in YEAR_RESOLUTIONS:
            return YEAR_RESOLUTIONS[record_id]
    all_dois = {
        doi for record in records for doi in [extract_doi(record)] if doi
    }
    version_doi, _ = publication_version_dois(all_dois)
    if version_doi:
        publication_years = sorted({
            int(record["year"])
            for record in records
            if extract_doi(record) == version_doi
            and isinstance(record.get("year"), int)
            and not isinstance(record.get("year"), bool)
        })
        if len(publication_years) == 1:
            return (
                publication_years[0],
                "Year resolved to the version-of-record publication year; the other "
                "value describes the matching arXiv preprint.",
            )
    reviewed_years = [
        record.get("year")
        for record in records
        if int(record["_rank"]) == 0 and isinstance(record.get("year"), int)
    ]
    if reviewed_years:
        return int(reviewed_years[0]), None
    years = sorted({
        int(record["year"])
        for record in records
        if isinstance(record.get("year"), int) and not isinstance(record.get("year"), bool)
    })
    if len(years) == 1:
        return years[0], None
    return None, None


def resolve_cluster(
    records: list[dict[str, object]],
    refmap: dict[str, str],
    ambiguous_ids: set[str],
    bibliography_aliases: set[str] | None = None,
) -> tuple[dict[str, object], list[dict[str, object]], list[str]]:
    canonical_id = choose_canonical_id(records)
    ids = member_ids(records)
    override = find_override(records)
    conflicts: list[dict[str, object]] = []
    resolution_notes: list[str] = []

    titles = sorted({
        str(record["title"]).strip()
        for record in records
        if isinstance(record.get("title"), str) and str(record["title"]).strip()
    })
    normalized_titles = {
        normalized for title_value in titles
        for normalized in [normalize_title(title_value)] if normalized
    }
    title = str(override.get("title") or pick_text(records, "title") or "")
    if len(normalized_titles) > 1:
        if isinstance(override.get("title"), str):
            resolution_notes.append(
                "Title variants resolved through an explicit primary-source metadata override."
            )
        else:
            conflicts.append({
                "id": canonical_id,
                "field": "title",
                "values": titles,
                "reason": "material title variants lack an explicit metadata resolution",
            })

    author_values = sorted({
        str(record["authors"]).strip()
        for record in records
        if isinstance(record.get("authors"), str) and str(record["authors"]).strip()
    })
    author_sets = [author_tokens({"authors": value}) for value in author_values]
    material_author_difference = any(
        first and second and not first.intersection(second)
        for index, first in enumerate(author_sets)
        for second in author_sets[index + 1:]
    )
    authors = override.get("authors") or pick_text(records, "authors")
    if material_author_difference:
        if isinstance(override.get("authors"), str):
            resolution_notes.append(
                "Author variants resolved through an explicit primary-source metadata override."
            )
        else:
            conflicts.append({
                "id": canonical_id,
                "field": "authors",
                "values": author_values,
                "reason": "material author variants lack an explicit metadata resolution",
            })
    venue = override.get("venue") or pick_text(records, "venue")
    year, year_note = resolution_for_year(records)
    years = sorted({
        int(record["year"])
        for record in records
        if isinstance(record.get("year"), int) and not isinstance(record.get("year"), bool)
    })
    if year is None and years:
        conflicts.append({
            "id": canonical_id,
            "field": "year",
            "values": years,
            "reason": "missing or conflicting year lacks a primary-source resolution",
        })
        year = max(years)
    elif year is not None and len(years) > 1:
        resolution_notes.append(year_note or "Year resolved from reviewed canonical metadata.")

    dois = sorted({doi for record in records for doi in [output_doi(record)] if doi})
    override_doi = override.get("doi")
    if isinstance(override_doi, str) and override_doi.strip():
        doi = override_doi.strip()
        if doi.lower() not in {value.lower() for value in dois}:
            dois.append(doi)
    elif len(dois) == 1:
        doi = dois[0]
    elif not dois:
        doi = None
    else:
        version_doi, _ = publication_version_dois(set(dois))
        if version_doi:
            doi = version_doi
            resolution_notes.append(
                "The publisher DOI is canonical; the matching arXiv DOI identifies "
                "the preprint version of the same work."
            )
        else:
            doi = dois[0]
            conflicts.append({
                "id": canonical_id,
                "field": "doi",
                "values": dois,
                "reason": "multiple non-null DOIs lack an explicit resolution",
            })

    valid_urls = sorted({
        normalized
        for record in records
        for normalized in [normalize_url(record.get("url") or record.get("canonical_url"))]
        if normalized
    })
    override_url = normalize_url(override.get("url"))
    reviewed_urls = [
        normalize_url(record.get("url") or record.get("canonical_url"))
        for record in sorted(records, key=stable_record_key)
        if int(record["_rank"]) == 0
    ]
    reviewed_urls = [url for url in reviewed_urls if url]
    canonical_doi_url = normalize_url(f"https://doi.org/{doi}") if doi else None
    recorded_canonical_doi_url = (
        canonical_doi_url if canonical_doi_url in valid_urls else None
    )
    url = (
        override_url
        or recorded_canonical_doi_url
        or (reviewed_urls[0] if reviewed_urls else None)
    )
    if url is None and valid_urls:
        url = valid_urls[0]

    purpose_values = sorted({
        str(record["purpose"])
        for record in records
        if record.get("purpose") in {"external", "internal_analysis"}
    })
    purpose = purpose_values[0] if len(purpose_values) == 1 else "external"
    if len(purpose_values) > 1:
        conflicts.append({
            "id": canonical_id,
            "field": "purpose",
            "values": purpose_values,
            "reason": "external and internal-analysis identities cannot be merged",
        })

    reviewed_types = [
        source_type(record) for record in records if int(record["_rank"]) == 0
    ]
    resolved_type = (
        "internal_analysis"
        if purpose == "internal_analysis"
        else reviewed_types[0]
        if reviewed_types
        else source_type(min(records, key=stable_record_key))
    )
    reviewed = sorted(
        (record for record in records if int(record["_rank"]) == 0),
        key=stable_record_key,
    )
    status_records = reviewed or sorted(
        (
            record for record in records
            if record.get("retrieval_status")
            or record.get("verification_status")
            or record.get("locators")
        ),
        key=stable_record_key,
    )
    if status_records:
        status_record = status_records[0]
        retrieval_status = str(status_record.get("retrieval_status") or "metadata_only")
        verification_status = str(
            override.get("verification_status")
            or status_record.get("verification_status")
            or "provisional"
        )
        retrieved_on = str(status_record.get("retrieved_on") or AUDIT_DATE)
        locators = list(status_record.get("locators") or [])
        existing_notes = str(status_record.get("notes") or "").strip()
    else:
        retrieval_status = "metadata_only"
        verification_status = str(override.get("verification_status") or "provisional")
        retrieved_on = AUDIT_DATE
        locators = [
            "Structured metadata from "
            + ", ".join(sorted({str(record["_origin"]) for record in records}))
        ]
        existing_notes = ""

    if purpose == "internal_analysis":
        locators = sorted({
            str(locator)
            for record in records
            for locator in (record.get("locators") or [])
            if isinstance(locator, str) and locator
        })

    bibliography_aliases = bibliography_aliases or set()
    qualified_aliases = {
        f"{record['_origin']}:{record['id']}" for record in records
    }
    explicit_aliases = {
        alias
        for record in records
        for alias in (record.get("aliases") or [])
        if isinstance(alias, str) and alias
    }
    plain_aliases = {record_id for record_id in ids if record_id not in ambiguous_ids}
    aliases = sorted(
        (
            plain_aliases
            | qualified_aliases
            | explicit_aliases
            | bibliography_aliases
        )
        - {canonical_id}
    )
    origin_note = (
        "Canonicalized from structured inputs: "
        + ", ".join(sorted({str(record["_origin"]) for record in records}))
        + "."
    )
    override_note = str(override.get("note") or "").strip()
    note_parts = [existing_notes, origin_note, override_note, *resolution_notes]
    notes = " ".join(dict.fromkeys(part for part in note_parts if part)).strip()
    return {
        "id": canonical_id,
        "canonical_key": canonical_id,
        "title": title,
        "authors": authors,
        "year": year,
        "venue": venue,
        "doi": doi,
        "url": url,
        "source_type": resolved_type,
        "retrieval_status": retrieval_status,
        "verification_status": verification_status,
        "retrieved_on": retrieved_on,
        "locators": [str(locator) for locator in locators],
        "aliases": aliases,
        "notes": notes,
        "purpose": purpose,
    }, conflicts, resolution_notes


def render_log(diagnostics: dict[str, object]) -> str:
    lines = [
        "# Source validation log",
        "",
        f"Audit date: {AUDIT_DATE}",
        "",
        "## Inventory",
        "",
    ]
    for filename, count in sorted(diagnostics["input_counts"].items()):
        lines.append(f"- `{filename}`: {count} structured source records")
    lines.extend([
        f"- Canonical records: {diagnostics['canonical_count']}",
        f"- Input records merged as aliases: {diagnostics['merged_input_count']}",
        f"- Bibliography aliases attached: {diagnostics['bibliography_alias_count']}",
        "",
        "## Resolved duplicate groups",
        "",
    ])
    merged_groups = diagnostics["merged_groups"]
    if merged_groups:
        for group in merged_groups:
            lines.append(
                f"- `{group['id']}` retains aliases "
                + ", ".join(f"`{alias}`" for alias in group["aliases"])
                + "."
            )
    else:
        lines.append("- None.")
    lines.extend(["", "## Resolved metadata conflicts", ""])
    resolved = diagnostics["resolved_conflicts"]
    if resolved:
        for item in resolved:
            lines.append(f"- `{item['id']}`. {item['note']}")
    else:
        lines.append("- None.")
    lines.extend(["", "## Unresolved conflicts", ""])
    unresolved = diagnostics["unresolved_conflicts"]
    if unresolved:
        for item in unresolved:
            lines.append(
                f"- `{item.get('id', item.get('key', 'unknown'))}` "
                f"({item.get('field', item.get('kind', 'identity'))}). "
                f"{item['reason']}"
            )
    else:
        lines.append("- None.")
    lines.extend(["", "## Retrieval limits", ""])
    metadata_only = diagnostics["metadata_only_ids"]
    lines.append(
        f"- {len(metadata_only)} records remain metadata-only and require claim-level "
        "inspection before they can support substantive prose."
    )
    lines.append(
        "- Metadata-only IDs: "
        + (", ".join(f"`{item}`" for item in metadata_only) if metadata_only else "none")
        + "."
    )
    not_retrieved = diagnostics["not_retrieved_ids"]
    lines.append(
        f"- {len(not_retrieved)} records are explicitly not retrieved: "
        + (", ".join(f"`{item}`" for item in not_retrieved) if not_retrieved else "none")
        + "."
    )
    missing_metadata = diagnostics["missing_metadata"]
    lines.extend(["", "## Unresolved metadata", ""])
    if missing_metadata:
        for item in missing_metadata:
            lines.append(
                f"- `{item['id']}`: "
                + ", ".join(f"`{field}`" for field in item["fields"])
                + "."
            )
    else:
        lines.append("- None.")
    unmatched = diagnostics["unmatched_refmap_targets"]
    lines.extend(["", "## Bibliography migration coverage", ""])
    lines.append(
        "- The frozen bibliography migration is a lowest-priority structured input. "
        "Unknown metadata remains null and cannot override stronger reviewed evidence."
    )
    lines.append(
        f"- All {diagnostics['migration_alias_count']} frozen legacy aliases resolve "
        "exactly once through canonical IDs or aliases."
    )
    lines.append(
        f"- {len(unmatched)} pre-existing uncited reference-map targets outside the "
        "frozen migration set do not identify a canonical source record."
    )
    lines.append(
        "- Unmatched mappings: "
        + (", ".join(f"`{item}`" for item in unmatched) if unmatched else "none")
        + "."
    )
    return "\n".join(lines) + "\n"


def build_outputs(root: Path = ROOT) -> tuple[dict[str, object], str, dict[str, object]]:
    records, refmap, input_counts = load_input_records(root)
    clusters, identity_conflicts = cluster_records(records, refmap)
    bibliography = parse_bibliography(root / "assets/bibliography/references.bib")
    (
        bibliography_aliases,
        unmatched_refmap_targets,
        bibliography_conflicts,
    ) = bibliography_aliases_for_clusters(clusters, refmap, bibliography)
    identity_conflicts.extend(bibliography_conflicts)
    id_cluster_counts: Counter[str] = Counter()
    for cluster in clusters:
        id_cluster_counts.update(member_ids(cluster))
    ambiguous_ids = {
        record_id for record_id, count in id_cluster_counts.items() if count > 1
    }
    canonical: list[dict[str, object]] = []
    field_conflicts: list[dict[str, object]] = []
    resolved_conflicts: list[dict[str, str]] = []
    duplicate_records: list[dict[str, object]] = []
    for cluster_index, cluster in enumerate(clusters):
        record, conflicts, resolution_notes = resolve_cluster(
            cluster,
            refmap,
            ambiguous_ids,
            bibliography_aliases.get(cluster_index, set()),
        )
        canonical.append(record)
        if len(cluster) > 1:
            duplicate_records.append(record)
        field_conflicts.extend(conflicts)
        for note in resolution_notes:
            resolved_conflicts.append({"id": str(record["id"]), "note": note})
    canonical.sort(key=lambda record: str(record["id"]))

    canonical_id_counts = Counter(str(record["id"]) for record in canonical)
    duplicate_canonical_ids = sorted(
        record_id for record_id, count in canonical_id_counts.items() if count > 1
    )
    for record_id in duplicate_canonical_ids:
        field_conflicts.append({
            "id": record_id,
            "field": "canonical_id",
            "values": [record_id],
            "reason": "multiple semantic clusters selected the same canonical ID",
        })

    address_owners: dict[str, set[str]] = defaultdict(set)
    for record in canonical:
        source_id = str(record["id"])
        for address in [source_id, *map(str, record.get("aliases", []))]:
            address_owners[address].add(source_id)
    for address, owners in sorted(address_owners.items()):
        if len(owners) > 1:
            field_conflicts.append({
                "id": address,
                "field": "alias",
                "values": sorted(owners),
                "reason": "canonical ID or alias addresses multiple works",
            })

    canonical_ids = {str(record["id"]) for record in canonical}
    migration_aliases = {
        alias
        for record in records
        if record.get("_origin") == "bibliography-migration-sources.json"
        for alias in (record.get("aliases") or [])
        if isinstance(alias, str) and alias
    }
    bibliography_alias_count = sum(len(aliases) for aliases in bibliography_aliases.values())
    diagnostics: dict[str, object] = {
        "input_counts": input_counts,
        "canonical_count": len(canonical),
        "merged_input_count": len(records) - len(canonical),
        "bibliography_alias_count": bibliography_alias_count,
        "migration_alias_count": len(migration_aliases),
        "true_duplicate_count": len(duplicate_records),
        "merged_groups": [
            {"id": record["id"], "aliases": record["aliases"]}
            for record in sorted(duplicate_records, key=lambda item: str(item["id"]))
        ],
        "resolved_conflicts": sorted(
            resolved_conflicts, key=lambda item: (item["id"], item["note"])
        ),
        "unresolved_conflicts": sorted(
            [*identity_conflicts, *field_conflicts],
            key=lambda item: (
                str(item.get("id", item.get("key", ""))),
                str(item.get("field", item.get("kind", ""))),
            ),
        ),
        "metadata_only_ids": [
            record["id"] for record in canonical if record["retrieval_status"] == "metadata_only"
        ],
        "not_retrieved_ids": [
            record["id"] for record in canonical if record["retrieval_status"] == "not_retrieved"
        ],
        "missing_metadata": [
            {
                "id": record["id"],
                "fields": [
                    field
                    for field in ("authors", "year", "venue", "doi", "url")
                    if record.get(field) is None
                ],
            }
            for record in canonical
            if any(
                record.get(field) is None
                for field in ("authors", "year", "venue", "doi", "url")
            )
        ],
        "unmatched_refmap_targets": unmatched_refmap_targets,
        "canonical_ids": sorted(canonical_ids),
        "ambiguous_plain_ids": sorted(ambiguous_ids),
    }
    registry = {"schema_version": 1, "sources": canonical}
    return registry, render_log(diagnostics), diagnostics


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check", action="store_true",
        help="verify that generated registry and log match the committed files",
    )
    args = parser.parse_args()
    registry, log_text, diagnostics = build_outputs(ROOT)
    unresolved = diagnostics["unresolved_conflicts"]
    if unresolved:
        print("build-source-registry: unresolved conflicts", file=sys.stderr)
        for conflict in unresolved:
            print(f"- {conflict}", file=sys.stderr)
        return 1
    registry_text = json.dumps(registry, indent=2, ensure_ascii=False) + "\n"
    registry_path = ROOT / "data/source-registry.json"
    log_path = ROOT / "research/source-validation-log.md"
    if args.check:
        errors = []
        if not registry_path.exists() or registry_path.read_text() != registry_text:
            errors.append("data/source-registry.json is stale")
        if not log_path.exists() or log_path.read_text() != log_text:
            errors.append("research/source-validation-log.md is stale")
        if errors:
            print("build-source-registry: FAILED", file=sys.stderr)
            print("\n".join(f"- {error}" for error in errors), file=sys.stderr)
            return 1
        print(f"build-source-registry: {len(registry['sources'])} canonical records current")
        return 0
    write_text(registry_path, registry_text)
    write_text(log_path, log_text)
    print(f"build-source-registry: wrote {len(registry['sources'])} canonical records")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
