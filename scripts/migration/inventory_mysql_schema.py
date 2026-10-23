#!/usr/bin/env python3
"""Extract a reviewable inventory from MySQL CREATE TABLE statements.

This is an inventory parser, not a MySQL-to-PostgreSQL translator. Original
column and constraint clauses are preserved for explicit review.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

BT = chr(96)
CREATE_TABLE = re.compile(
    r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?"
    + r"(?:" + BT + r"([^" + BT + r"]+)" + BT + r"|([A-Za-z0-9_$]+))\s*\(",
    re.IGNORECASE,
)


def _scan(sql: str, opening: int) -> int:
    depth = 0
    quote = None
    line_comment = False
    block_comment = False
    i = opening
    while i < len(sql):
        ch = sql[i]
        nxt = sql[i + 1] if i + 1 < len(sql) else ""
        if line_comment:
            if ch == "\n":
                line_comment = False
            i += 1
            continue
        if block_comment:
            if ch == "*" and nxt == "/":
                block_comment = False
                i += 2
            else:
                i += 1
            continue
        if quote:
            if ch == "\\" and quote in ("'", '"'):
                i += 2
                continue
            if ch == quote:
                # SQL permits doubled quote delimiters inside quoted values/identifiers.
                if nxt == quote:
                    i += 2
                    continue
                quote = None
            i += 1
            continue
        if ch == "/" and nxt == "*":
            block_comment = True
            i += 2
            continue
        if ch == "-" and nxt == "-" and (i + 2 == len(sql) or sql[i + 2].isspace()):
            line_comment = True
            i += 2
            continue
        if ch == "#":
            line_comment = True
            i += 1
            continue
        if ch in ("'", '"', BT):
            quote = ch
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    raise ValueError(f"Unclosed CREATE TABLE parentheses at offset {opening}")


def _split_top_level(body: str) -> list[str]:
    parts = []
    start = 0
    depth = 0
    quote = None
    line_comment = False
    block_comment = False
    i = 0
    while i < len(body):
        ch = body[i]
        nxt = body[i + 1] if i + 1 < len(body) else ""
        if line_comment:
            if ch == "\n":
                line_comment = False
            i += 1
            continue
        if block_comment:
            if ch == "*" and nxt == "/":
                block_comment = False
                i += 2
            else:
                i += 1
            continue
        if quote:
            if ch == "\\" and quote in ("'", '"'):
                i += 2
                continue
            if ch == quote:
                # SQL permits doubled quote delimiters inside quoted values/identifiers.
                if nxt == quote:
                    i += 2
                    continue
                quote = None
            i += 1
            continue
        if ch == "/" and nxt == "*":
            block_comment = True
            i += 2
            continue
        if ch == "-" and nxt == "-" and (i + 2 == len(body) or body[i + 2].isspace()):
            line_comment = True
            i += 2
            continue
        if ch == "#":
            line_comment = True
            i += 1
            continue
        if ch in ("'", '"', BT):
            quote = ch
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        elif ch == "," and depth == 0:
            part = body[start:i].strip()
            if part:
                parts.append(part)
            start = i + 1
        i += 1
    tail = body[start:].strip()
    if tail:
        parts.append(tail)
    return parts


def _identifier(part: str) -> str:
    quoted = re.match("^" + BT + "([^" + BT + "]+)" + BT + r"\s*(.*)$", part, re.DOTALL)
    if quoted:
        return quoted.group(1)
    plain = re.match(r"^([A-Za-z0-9_$]+)\s*(.*)$", part, re.DOTALL)
    return plain.group(1) if plain else ""


def _classify(part: str) -> str:
    value = part.lstrip().upper()
    if value.startswith("CONSTRAINT "):
        return "foreign_key" if "FOREIGN KEY" in value else "constraint"
    if value.startswith("FOREIGN KEY"):
        return "foreign_key"
    if value.startswith("PRIMARY KEY"):
        return "primary_key"
    if value.startswith(("UNIQUE ", "UNIQUE KEY", "UNIQUE INDEX")):
        return "unique"
    if value.startswith(("KEY ", "INDEX ")):
        return "index"
    if value.startswith("CHECK"):
        return "check"
    return "column"


def inventory(sql: str) -> dict[str, Any]:
    tables = []
    for match in CREATE_TABLE.finditer(sql):
        table_name = match.group(1) or match.group(2)
        opening = match.end() - 1
        closing = _scan(sql, opening)
        entries = _split_top_level(sql[opening + 1:closing])
        columns = []
        constraints = []
        for entry in entries:
            kind = _classify(entry)
            name = _identifier(entry)
            if kind == "column":
                columns.append({
                    "name": name,
                    "declaration": entry,
                    "generated": bool(re.search(
                        r"\bGENERATED\s+ALWAYS\b|\bAS\s*\(.*\)\s*(?:STORED|VIRTUAL)",
                        entry, re.IGNORECASE | re.DOTALL
                    )),
                })
            else:
                constraints.append({"kind": kind, "name": name, "declaration": entry})
        tables.append({"name": table_name, "columns": columns, "constraints": constraints})
    counts = {
        "tables": len(tables),
        "columns": sum(len(t["columns"]) for t in tables),
        "primary_keys": sum(c["kind"] == "primary_key" for t in tables for c in t["constraints"]) + sum("PRIMARY KEY" in col["declaration"].upper() for t in tables for col in t["columns"]),
        "unique_constraints": sum(c["kind"] == "unique" for t in tables for c in t["constraints"]) + sum(re.search(r"\bUNIQUE\b", col["declaration"], re.IGNORECASE) is not None for t in tables for col in t["columns"]),
        "indexes": sum(c["kind"] == "index" for t in tables for c in t["constraints"]),
        "foreign_keys": sum(c["kind"] == "foreign_key" for t in tables for c in t["constraints"]),
        "checks": sum(c["kind"] == "check" for t in tables for c in t["constraints"]),
        "generated_columns": sum(col["generated"] for t in tables for col in t["columns"]),
    }
    return {"counts": counts, "tables": tables}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("schema", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = inventory(args.schema.read_text(encoding="utf-8"))
    payload = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload)


if __name__ == "__main__":
    main()
