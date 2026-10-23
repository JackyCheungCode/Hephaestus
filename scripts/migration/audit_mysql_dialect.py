#!/usr/bin/env python3
"""Inventory MySQL dialect coupling in a pinned source tree.

This is a review aid, not a SQL parser or an automatic SQL translator.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

PATTERNS: dict[str, re.Pattern[str]] = {
    "mysql_driver_import": re.compile(r"""from\s+["']mysql2(?:/promise)?["']|require\(["']mysql2(?:/promise)?["']\)""", re.I),
    "on_duplicate_key_update": re.compile(r"\bON\s+DUPLICATE\s+KEY\s+UPDATE\b", re.I),
    "insert_ignore": re.compile(r"\bINSERT\s+IGNORE\s+INTO\b", re.I),
    "now_millis": re.compile(r"\bNOW\s*\(\s*3\s*\)", re.I),
    "current_timestamp_millis": re.compile(r"\bCURRENT_TIMESTAMP\s*\(\s*3\s*\)", re.I),
    "database_function": re.compile(r"\bDATABASE\s*\(\s*\)", re.I),
    "information_schema": re.compile(r"\binformation_schema\s*\.\s*(?:columns|tables|statistics|key_column_usage)\b", re.I),
    "for_update_lock": re.compile(r"\bFOR\s+UPDATE\b", re.I),
    "json_array_function": re.compile(r"\bJSON_ARRAY\s*\(", re.I),
    "replace_into": re.compile(r"\bREPLACE\s+INTO\b", re.I),
    "mysql_engine": re.compile(r"\bENGINE\s*=\s*InnoDB\b", re.I),
    "mysql_datetime_precision": re.compile(r"\bDATETIME\s*\(\s*3\s*\)", re.I),
    "mysql_json_type": re.compile(r"\bJSON\b", re.I),
    "mysql_placeholder": re.compile(r"\?"),
}

SKIP_DIRS = {".git", "node_modules", "dist", "build", "coverage", ".next"}
TEXT_SUFFIXES = {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".sql", ".json", ".md", ".sh"}


def inventory(root: Path) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    files_scanned = 0
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (UnicodeDecodeError, OSError):
            continue
        files_scanned += 1
        for line_number, line in enumerate(lines, start=1):
            for name, pattern in PATTERNS.items():
                for match in pattern.finditer(line):
                    findings.append({
                        "pattern": name,
                        "path": path.relative_to(root).as_posix(),
                        "line": line_number,
                        "match": match.group(0),
                        "excerpt": line.strip()[:240],
                    })
    counts = {name: 0 for name in PATTERNS}
    for item in findings:
        counts[item["pattern"]] += 1
    return {
        "warning": "Static text matches only; counts are not proof of executable SQL and are not a SQL conversion.",
        "files_scanned": files_scanned,
        "finding_count": len(findings),
        "counts_by_pattern": counts,
        "findings": findings,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = inventory(args.root)
    payload = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload)


if __name__ == "__main__":
    main()
