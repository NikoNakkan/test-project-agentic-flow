#!/usr/bin/env python3
"""Named queries against .code-index/graph.db for navigator agent."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from code_index_lib import connect, dependents_of, users_of


def find_symbol(conn, name: str) -> list[dict]:
    rows = conn.execute(
        """
        SELECT s.id, s.name, s.kind, s.tests, f.path, f.stack
        FROM symbols s JOIN files f ON f.id = s.file_id
        WHERE s.name LIKE ?
        """,
        (f"%{name}%",),
    ).fetchall()
    return [dict(r) for r in rows]


def who_uses(conn, name: str) -> list[str]:
    rows = conn.execute(
        "SELECT id FROM symbols WHERE name = ?", (name,)
    ).fetchall()
    out: list[str] = []
    for r in rows:
        out.extend(users_of(conn, r["id"]))
    return sorted(set(out))


def missing_tests(conn, kind: str | None = None) -> list[dict]:
    q = """
        SELECT s.name, s.kind, f.path
        FROM symbols s JOIN files f ON f.id = s.file_id
        WHERE f.kind != 'test' AND (s.tests IS NULL OR s.tests = '')
    """
    params: tuple = ()
    if kind:
        q += " AND s.kind = ?"
        params = (kind,)
    rows = conn.execute(q, params).fetchall()
    return [dict(r) for r in rows]


def symbol_deps(conn, name: str) -> dict:
    rows = conn.execute(
        "SELECT id, name, kind FROM symbols WHERE name = ?", (name,)
    ).fetchall()
    if not rows:
        return {"name": name, "found": False, "uses": [], "used_by": []}
    sid = rows[0]["id"]
    uses = dependents_of(conn, sid)
    used_by = [u.split(":")[-1] for u in users_of(conn, sid)]
    return {
        "name": name,
        "found": True,
        "kind": rows[0]["kind"],
        "uses": uses,
        "used_by": sorted(set(used_by)),
    }


def context_pack(conn, keywords: str, limit: int = 20) -> list[dict]:
    terms = [t for t in keywords.split() if t]
    if not terms:
        return []
    clauses = " OR ".join(["f.path LIKE ? OR s.name LIKE ?"] * len(terms))
    params: list[str] = []
    for t in terms:
        params.extend([f"%{t}%", f"%{t}%"])
    rows = conn.execute(
        f"""
        SELECT DISTINCT s.name, s.kind, f.path, s.tests
        FROM symbols s JOIN files f ON f.id = s.file_id
        WHERE {clauses}
        LIMIT ?
        """,
        (*params, limit),
    ).fetchall()
    return [dict(r) for r in rows]


def main() -> int:
    parser = argparse.ArgumentParser(description="Query code index")
    parser.add_argument("--repo", type=Path, default=Path("."))
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_find = sub.add_parser("find_symbol")
    p_find.add_argument("name")

    p_who = sub.add_parser("who_uses")
    p_who.add_argument("name")

    p_miss = sub.add_parser("missing_tests")
    p_miss.add_argument("--kind", default=None)

    p_pack = sub.add_parser("context_pack")
    p_pack.add_argument("keywords")
    p_pack.add_argument("--limit", type=int, default=20)

    p_deps = sub.add_parser("symbol_deps")
    p_deps.add_argument("name")

    args = parser.parse_args()
    conn = connect(args.repo.resolve())

    if args.cmd == "find_symbol":
        result = find_symbol(conn, args.name)
    elif args.cmd == "who_uses":
        result = who_uses(conn, args.name)
    elif args.cmd == "missing_tests":
        result = missing_tests(conn, args.kind)
    elif args.cmd == "context_pack":
        result = context_pack(conn, args.keywords, args.limit)
    elif args.cmd == "symbol_deps":
        result = symbol_deps(conn, args.name)
    else:
        result = []

    conn.close()
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
