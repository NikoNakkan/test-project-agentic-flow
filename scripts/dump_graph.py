#!/usr/bin/env python3
"""Human-readable dump of AI catalog graph (symbols + uses edges only)."""
import json
import sqlite3
from pathlib import Path

db = Path(__file__).resolve().parent.parent / ".code-index" / "graph.db"
if not db.exists():
    print(json.dumps({"error": "not found", "path": str(db)}, indent=2))
    raise SystemExit(1)

conn = sqlite3.connect(db)
conn.row_factory = sqlite3.Row

symbols = [
    dict(r)
    for r in conn.execute(
        """
        SELECT s.id, s.name, s.kind, s.tests, f.path
        FROM symbols s JOIN files f ON f.id = s.file_id
        ORDER BY f.path, s.name
        """
    )
]
edges = [
    dict(r)
    for r in conn.execute(
        """
        SELECT s1.name AS from_symbol, f1.path AS from_file,
               s2.name AS to_symbol, f2.path AS to_file, e.kind
        FROM edges e
        JOIN symbols s1 ON s1.id = e.from_symbol_id
        JOIN files f1 ON f1.id = s1.file_id
        JOIN symbols s2 ON s2.id = e.to_symbol_id
        JOIN files f2 ON f2.id = s2.file_id
        WHERE e.to_symbol_id IS NOT NULL
        ORDER BY from_file, from_symbol
        """
    )
]
print(
    json.dumps(
        {
            "path": str(db),
            "symbol_count": len(symbols),
            "uses_edge_count": len(edges),
            "symbols": symbols,
            "uses": edges,
        },
        indent=2,
    )
)
