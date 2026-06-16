#!/usr/bin/env python3
"""Validate strict graph.db ↔ docs/context symbol_id linkage."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from code_index_lib import (
    AUTO_PURPOSE,
    CONTEXT_SYMBOL_FILES,
    all_catalog_symbols,
    connect,
    context_file_for_symbol,
    dependents_of,
    lookup_column_for_context,
    split_sections,
    symbol_by_id,
)


def parse_context_rows(repo: Path) -> list[dict]:
    rows: list[dict] = []
    for filename in CONTEXT_SYMBOL_FILES:
        path = repo / "docs" / "context" / filename
        if not path.is_file():
            continue
        _, sections = split_sections(path.read_text(encoding="utf-8"))
        lookup_col = lookup_column_for_context(filename)
        for file_path, body in sections:
            col_map: dict[str, int] = {}
            for line in body.splitlines():
                if not line.startswith("|") or line.startswith("|---"):
                    continue
                cells = [c.strip() for c in line.strip("|").split("|")]
                if not col_map and cells and cells[0].lower() in ("symbol_id", "key"):
                    col_map = {c.lower(): i for i, c in enumerate(cells)}
                    continue
                if not col_map or not cells[0].isdigit():
                    continue
                sid = int(cells[0])
                name_idx = col_map.get(lookup_col)
                name = cells[name_idx] if name_idx is not None and name_idx < len(cells) else ""
                purpose_idx = col_map.get("purpose")
                purpose = (
                    cells[purpose_idx]
                    if purpose_idx is not None and purpose_idx < len(cells)
                    else ""
                )
                rows.append(
                    {
                        "symbol_id": sid,
                        "name": name,
                        "file_path": file_path,
                        "context_file": filename,
                        "purpose": purpose,
                        "has_purpose_col": "purpose" in col_map,
                    }
                )
    return rows


def validate(repo: Path) -> dict:
    repo = repo.resolve()
    conn = connect(repo)
    errors: list[str] = []

    graph_symbols = {r["id"]: r for r in all_catalog_symbols(conn)}
    md_rows = parse_context_rows(repo)
    md_by_id: dict[int, dict] = {}

    for row in md_rows:
        sid = row["symbol_id"]
        if sid in md_by_id:
            errors.append(f"duplicate symbol_id {sid} in context MDs")
        md_by_id[sid] = row

        sym = symbol_by_id(conn, sid)
        if not sym:
            errors.append(f"context row symbol_id={sid} ({row['name']}) not in graph.db")
            continue
        if sym["name"] != row["name"]:
            errors.append(
                f"symbol_id {sid}: MD name '{row['name']}' != graph '{sym['name']}'"
            )
        if sym["path"] != row["file_path"]:
            errors.append(
                f"symbol_id {sid}: MD path '{row['file_path']}' != graph '{sym['path']}'"
            )
        expected_ctx = context_file_for_symbol(sym["path"], sym["kind"], sym["stack"])
        if row["context_file"] != expected_ctx:
            errors.append(
                f"symbol_id {sid}: in {row['context_file']} but should be {expected_ctx}"
            )
        if row.get("has_purpose_col") and (
            not row["purpose"] or row["purpose"] == AUTO_PURPOSE
        ):
            errors.append(f"symbol_id {sid} ({sym['name']}): missing human purpose")

    for sid, sym in graph_symbols.items():
        if sid not in md_by_id:
            errors.append(
                f"graph symbol id={sid} ({sym['name']} @ {sym['path']}) missing from context MDs"
            )

    conn.close()
    return {
        "ok": len(errors) == 0,
        "graph_symbols": len(graph_symbols),
        "context_rows": len(md_rows),
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate graph ↔ context linkage")
    parser.add_argument("--repo", type=Path, default=Path("."))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = validate(args.repo)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result["ok"]:
            print(
                f"OK — {result['graph_symbols']} graph symbols match "
                f"{result['context_rows']} context rows"
            )
        else:
            print(f"FAILED — {len(result['errors'])} error(s):")
            for err in result["errors"]:
                print(f"  - {err}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
