#!/usr/bin/env python3
"""Sync graph.db → docs/context/*.md — strict symbol_id join; prune deleted; add new."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from code_index_lib import (
    AUTO_PURPOSE,
    CONTEXT_SYMBOL_FILES,
    CONTEXT_TEST_FILES,
    all_catalog_symbols,
    connect,
    context_file_for_symbol,
    dependents_of,
    format_row,
    lookup_column_for_context,
    section_header_map,
    split_sections,
    users_of,
)


def default_row_for_context(
    filename: str, symbol_id: int, name: str, tests: str, depends_on: str
) -> list[str]:
    if filename == "api-list.md":
        return [str(symbol_id), "", "", name, "", "", tests]
    if filename == "fe-services.md":
        return [str(symbol_id), name, AUTO_PURPOSE, tests, ""]
    if filename == "types.md":
        return [str(symbol_id), name, "function", ""]
    return [str(symbol_id), name, AUTO_PURPOSE, tests, depends_on]


def sync_section_body(
    conn, file_path: str, body: str, filename: str, valid_ids: set[int]
) -> tuple[str, int, set[int]]:
    col_map = section_header_map(body)
    if not col_map:
        return body, 0, set()

    lookup_col = lookup_column_for_context(filename)
    name_idx = col_map.get(lookup_col)
    if name_idx is None:
        return body, 0, set()

    updated = 0
    matched_ids: set[int] = set()
    new_lines: list[str] = []
    header_seen = False

    for line in body.splitlines():
        if not line.startswith("|") or line.startswith("|---"):
            new_lines.append(line)
            continue

        cells = [c.strip() for c in line.strip("|").split("|")]
        if not header_seen and cells and cells[0].lower() in ("symbol_id", "key"):
            new_lines.append(line)
            header_seen = True
            continue

        if not header_seen or not cells or cells[0].lower() in ("symbol_id", "key"):
            new_lines.append(line)
            continue

        while len(cells) < len(col_map):
            cells.append("")

        if name_idx >= len(cells):
            continue

        name = cells[name_idx]
        row = conn.execute(
            """
            SELECT s.id, s.tests, s.kind
            FROM symbols s JOIN files f ON f.id = s.file_id
            WHERE f.path = ? AND s.name = ?
            """,
            (file_path, name),
        ).fetchone()

        if not row:
            continue  # prune — symbol removed from graph

        sid = row["id"]
        matched_ids.add(sid)
        valid_ids.discard(sid)

        if "symbol_id" in col_map:
            cells[col_map["symbol_id"]] = str(sid)
        if "tests" in col_map:
            cells[col_map["tests"]] = row["tests"] or ""
        if "depends_on" in col_map:
            cells[col_map["depends_on"]] = ", ".join(dependents_of(conn, sid))
        if "api_calls" in col_map:
            cells[col_map["api_calls"]] = name.replace("_", " ")
        if "used_by" in col_map:
            cells[col_map["used_by"]] = ", ".join(
                u.split(":")[-1] for u in users_of(conn, sid)
            )
        new_lines.append(format_row(cells[: len(col_map)]))
        updated += 1

    return "\n".join(new_lines), updated, matched_ids


def ensure_symbol_row(
    conn,
    repo: Path,
    filename: str,
    file_path: str,
    symbol_id: int,
    name: str,
) -> bool:
    """Append catalog row if symbol_id not yet present in section."""
    path = repo / "docs" / "context" / filename
    preamble, sections = split_sections(path.read_text(encoding="utf-8"))
    col_map = None
    section_idx = None
    for i, (heading, body) in enumerate(sections):
        if heading == file_path:
            section_idx = i
            col_map = section_header_map(body)
            break

    if section_idx is None:
        sections.append((file_path, _empty_table_body(filename)))
        section_idx = len(sections) - 1
        col_map = section_header_map(sections[section_idx][1])

    if not col_map:
        return False

    lookup_col = lookup_column_for_context(filename)
    name_idx = col_map.get(lookup_col)
    body = sections[section_idx][1]

    for line in body.splitlines():
        if not line.startswith("|") or line.startswith("|---"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if cells and cells[0].isdigit() and int(cells[0]) == symbol_id:
            return False
        if name_idx is not None and len(cells) > name_idx and cells[name_idx] == name:
            return False

    sym = conn.execute("SELECT tests FROM symbols WHERE id = ?", (symbol_id,)).fetchone()
    tests = sym["tests"] if sym else ""
    deps = ", ".join(dependents_of(conn, symbol_id))
    row_cells = default_row_for_context(filename, symbol_id, name, tests, deps)

    lines = body.splitlines()
    lines.append(format_row(row_cells))
    sections[section_idx] = (file_path, "\n".join(lines))

    out = [preamble.rstrip(), ""]
    for heading, sec_body in sections:
        out.append(f"## {heading}")
        out.append(sec_body.rstrip())
        out.append("")
    path.write_text("\n".join(out).rstrip() + "\n", encoding="utf-8")
    return True


def _empty_table_body(filename: str) -> str:
    if filename == "api-list.md":
        header = "| symbol_id | method | path | handler | request_type | response_type | tests |"
        sep = "|-----------|--------|------|---------|--------------|---------------|-------|"
    elif filename == "fe-services.md":
        header = "| symbol_id | name | purpose | tests | api_calls |"
        sep = "|-----------|------|---------|-------|-----------|"
    elif filename == "types.md":
        header = "| symbol_id | name | kind | used_by |"
        sep = "|-----------|------|------|---------|"
    else:
        header = "| symbol_id | name | purpose | tests | depends_on |"
        sep = "|-----------|------|---------|-------|------------|"
    return f"{header}\n{sep}\n"


def sync_symbol_file(repo: Path, conn, filename: str, pending_ids: set[int]) -> int:
    path = repo / "docs" / "context" / filename
    if not path.is_file():
        return 0

    preamble, sections = split_sections(path.read_text(encoding="utf-8"))
    if not sections:
        return 0

    out = [preamble.rstrip(), ""]
    total = 0
    for heading, body in sections:
        new_body, n, _ = sync_section_body(conn, heading, body, filename, pending_ids)
        total += n
        out.append(f"## {heading}")
        out.append(new_body.rstrip())
        out.append("")

    path.write_text("\n".join(out).rstrip() + "\n", encoding="utf-8")
    return total


def sync_test_file(repo: Path, conn, filename: str, stack: str) -> int:
    path = repo / "docs" / "context" / filename
    path.parent.mkdir(parents=True, exist_ok=True)

    test_entries: dict[str, list] = {}
    symbols = conn.execute(
        """
        SELECT s.id, s.name, s.tests, f.path AS covers_file
        FROM symbols s JOIN files f ON f.id = s.file_id
        WHERE f.stack = ? AND s.tests != ''
        """,
        (stack,),
    ).fetchall()

    for sym in symbols:
        for test_path in sym["tests"].split(","):
            test_path = test_path.strip()
            if test_path:
                test_entries.setdefault(test_path, []).append(sym)

    lines = [
        f"# {'Frontend' if stack == 'react' else 'Backend'} tests",
        "",
        "Auto-synced by index. Top node = test file path.",
        "",
    ]

    count = 0
    for test_path in sorted(test_entries):
        lines.append(f"## {test_path}")
        lines.append("")
        lines.append("| symbol_id | covers_symbol | covers_file | kind |")
        lines.append("|-----------|---------------|-------------|------|")
        for sym in test_entries[test_path]:
            lines.append(
                format_row([str(sym["id"]), sym["name"], sym["covers_file"], "unit"])
            )
            count += 1
        lines.append("")

    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return count


def sync_all(repo: Path) -> dict:
    conn = connect(repo)
    pending_ids = {r["id"] for r in all_catalog_symbols(conn)}
    total = 0

    for filename in CONTEXT_SYMBOL_FILES:
        total += sync_symbol_file(repo, conn, filename, pending_ids)

    added = 0
    for sym in all_catalog_symbols(conn):
        ctx_file = context_file_for_symbol(sym["path"], sym["kind"], sym["stack"])
        if ensure_symbol_row(conn, repo, ctx_file, sym["path"], sym["id"], sym["name"]):
            added += 1
            pending_ids.discard(sym["id"])

    # Re-run sync after inserts so auto columns are fresh
    pending_ids = set()
    for filename in CONTEXT_SYMBOL_FILES:
        total += sync_symbol_file(repo, conn, filename, pending_ids)

    for filename, stack in CONTEXT_TEST_FILES.items():
        total += sync_test_file(repo, conn, filename, stack)

    conn.close()
    return {"rows_synced": total, "rows_added": added}


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync graph.db into docs/context/")
    parser.add_argument("--repo", type=Path, default=Path("."))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = sync_all(args.repo.resolve())
    if args.json:
        import json

        print(json.dumps(result, indent=2))
    else:
        print(
            f"Synced {result['rows_synced']} rows; added {result['rows_added']} new catalog rows"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
