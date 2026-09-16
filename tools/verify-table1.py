#!/usr/bin/env python3
"""Verify the reader-facing contract of the generated prior-survey matrix."""
from __future__ import annotations

import runpy
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def fail(message: str) -> None:
    raise AssertionError(message)


def main() -> int:
    module = runpy.run_path(ROOT / "tools/build-table1.py")
    build_table = module.get("build_table")
    if not callable(build_table):
        fail("build-table1 does not expose build_table(root)")
    table = build_table(ROOT)
    if table.count("<tr><td>") != 37:
        fail("Table 1 no longer contains all 37 audited works")
    if "survey-tag" in table:
        fail("Table 1 still displays per-work category tags")
    print("verify-table1: PASS (37 audited works; no per-work category tags)")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, KeyError, OSError, TypeError, ValueError) as error:
        print(f"verify-table1: FAILED: {error}", file=sys.stderr)
        raise SystemExit(1)
