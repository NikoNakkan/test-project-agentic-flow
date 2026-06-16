-- Code Index — PoC schema (React + Python)
-- Generated DB: .code-index/graph.db

CREATE TABLE IF NOT EXISTS files (
    id    INTEGER PRIMARY KEY AUTOINCREMENT,
    path  TEXT NOT NULL UNIQUE,
    kind  TEXT NOT NULL,
    stack TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS symbols (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id INTEGER NOT NULL REFERENCES files(id) ON DELETE CASCADE,
    name    TEXT NOT NULL,
    kind    TEXT NOT NULL,
    tests   TEXT NOT NULL DEFAULT '',
    UNIQUE(file_id, name)
);

CREATE TABLE IF NOT EXISTS edges (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    from_symbol_id INTEGER NOT NULL REFERENCES symbols(id) ON DELETE CASCADE,
    to_symbol_id   INTEGER REFERENCES symbols(id) ON DELETE SET NULL,
    to_name        TEXT,
    kind           TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_symbols_name ON symbols(name);
CREATE INDEX IF NOT EXISTS idx_edges_from ON edges(from_symbol_id);
CREATE INDEX IF NOT EXISTS idx_edges_to ON edges(to_symbol_id);
