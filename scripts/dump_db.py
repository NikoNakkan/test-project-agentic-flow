#!/usr/bin/env python3
import json
import sqlite3
from pathlib import Path

db = Path(__file__).resolve().parent.parent / "apps" / "api" / "data" / "app.db"
if not db.exists():
    print(json.dumps({"error": "not found", "path": str(db)}, indent=2))
    raise SystemExit(1)

conn = sqlite3.connect(db)
conn.row_factory = sqlite3.Row
tables = [
    r[0]
    for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    )
]
out = {"path": str(db), "tables": {}}
for table in tables:
    cols = [d[1] for d in conn.execute(f"PRAGMA table_info({table})")]
    rows = [dict(r) for r in conn.execute(f"SELECT * FROM {table}")]
    out["tables"][table] = {"columns": cols, "row_count": len(rows), "rows": rows}
print(json.dumps(out, indent=2))
