#!/usr/bin/env python3
"""Build Code Index (SQLite) — stable symbol IDs + catalog uses edges."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from code_index_lib import (
    connect,
    extract_py_symbols,
    extract_ts_symbols,
    find_tests_for_symbol,
    infer_file_kind,
    infer_symbol_kind,
    init_db,
    internal_import_targets,
    posix,
    py_symbol_bodies,
    scan_source_files,
    should_index_symbol,
    symbol_id_map,
    symbol_used_in_text,
    ts_symbol_bodies,
)


def rebuild(repo: Path) -> dict:
    repo = repo.resolve()
    conn = connect(repo)
    init_db(conn)

    old_files = {
        r["path"]: r["id"]
        for r in conn.execute("SELECT id, path FROM files").fetchall()
    }
    old_symbols = {
        (r["path"], r["name"]): r["id"]
        for r in conn.execute(
            """
            SELECT s.id, s.name, f.path
            FROM symbols s JOIN files f ON f.id = s.file_id
            """
        ).fetchall()
    }

    conn.execute("DELETE FROM edges")
    conn.commit()

    seen_files: set[str] = set()
    seen_symbols: set[tuple[str, str]] = set()
    indexed_symbols: list[tuple[str, str, str, str, str]] = []

    for path, stack, _ext in scan_source_files(repo):
        rel = posix(path, repo)
        kind = infer_file_kind(rel, stack)
        seen_files.add(rel)

        if rel in old_files:
            file_id = old_files[rel]
            conn.execute(
                "UPDATE files SET kind = ?, stack = ? WHERE id = ?",
                (kind, stack, file_id),
            )
        else:
            conn.execute(
                "INSERT INTO files (path, kind, stack) VALUES (?, ?, ?)",
                (rel, kind, stack),
            )
            file_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        symbols = (
            extract_ts_symbols(text) if stack == "react" else extract_py_symbols(text, kind)
        )

        for name, sym_kind in symbols:
            sk = infer_symbol_kind(name, kind, sym_kind)
            if not should_index_symbol(name, sym_kind, kind, rel):
                continue

            key = (rel, name)
            seen_symbols.add(key)
            tests = find_tests_for_symbol(repo, rel, name, stack)

            if key in old_symbols:
                conn.execute(
                    "UPDATE symbols SET file_id = ?, kind = ?, tests = ? WHERE id = ?",
                    (file_id, sk, tests, old_symbols[key]),
                )
            else:
                conn.execute(
                    "INSERT INTO symbols (file_id, name, kind, tests) VALUES (?, ?, ?, ?)",
                    (file_id, name, sk, tests),
                )
            indexed_symbols.append((rel, name, stack, kind, text))

    for key, sid in old_symbols.items():
        if key not in seen_symbols:
            conn.execute("DELETE FROM symbols WHERE id = ?", (sid,))

    for path, fid in old_files.items():
        if path not in seen_files:
            conn.execute("DELETE FROM files WHERE id = ?", (fid,))

    conn.commit()
    sym_map = symbol_id_map(conn)

    for rel, name, stack, kind, text in indexed_symbols:
        path = repo / rel
        src_id = sym_map.get((rel, name))
        if not src_id:
            continue

        bodies = ts_symbol_bodies(text) if stack == "react" else py_symbol_bodies(text)
        scope = bodies.get(name, text)
        targets = internal_import_targets(repo, path, rel, stack, text, sym_map)

        for imp_name, dst_id in targets.items():
            if symbol_used_in_text(imp_name, scope) and dst_id != src_id:
                conn.execute(
                    """
                    INSERT OR IGNORE INTO edges (from_symbol_id, to_symbol_id, to_name, kind)
                    VALUES (?, ?, NULL, 'uses')
                    """,
                    (src_id, dst_id),
                )

        if stack == "react":
            for (t_rel, t_name), dst_id in sym_map.items():
                if t_rel == rel and t_name == name:
                    continue
                if symbol_used_in_text(t_name, scope):
                    conn.execute(
                        """
                        INSERT OR IGNORE INTO edges (from_symbol_id, to_symbol_id, to_name, kind)
                        VALUES (?, ?, NULL, 'uses')
                        """,
                        (src_id, dst_id),
                    )

    conn.commit()

    stats = {
        "files": conn.execute("SELECT COUNT(*) FROM files").fetchone()[0],
        "symbols": conn.execute("SELECT COUNT(*) FROM symbols").fetchone()[0],
        "edges": conn.execute(
            "SELECT COUNT(*) FROM edges WHERE to_symbol_id IS NOT NULL"
        ).fetchone()[0],
        "missing_tests": conn.execute(
            """
            SELECT COUNT(*) FROM symbols s
            JOIN files f ON f.id = s.file_id
            WHERE f.kind != 'test' AND (s.tests IS NULL OR s.tests = '')
            """
        ).fetchone()[0],
    }
    conn.close()
    return stats


def main() -> int:
    parser = argparse.ArgumentParser(description="Build .code-index/graph.db")
    parser.add_argument("--repo", type=Path, default=Path("."), help="Repository root")
    parser.add_argument("--json", action="store_true", help="Print stats as JSON")
    args = parser.parse_args()

    stats = rebuild(args.repo)
    if args.json:
        print(json.dumps(stats, indent=2))
    else:
        print(
            f"Indexed {stats['files']} files, {stats['symbols']} catalog symbols, "
            f"{stats['edges']} uses edges"
        )
        print(f"Symbols missing tests: {stats['missing_tests']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
