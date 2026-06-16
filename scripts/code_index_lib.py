"""Shared helpers for code index build, sync, and query."""

from __future__ import annotations

import re
import sqlite3
from pathlib import Path

SCHEMA_PATH = Path(__file__).resolve().parent / "code_index_schema.sql"

TS_EXPORT_PATTERNS = [
    (re.compile(r"^export\s+(?:async\s+)?function\s+(\w+)", re.M), "function"),
    (re.compile(r"^export\s+const\s+(\w+)\s*=", re.M), "const"),
    (re.compile(r"^export\s+default\s+function\s+(\w+)", re.M), "function"),
    (re.compile(r"^export\s+default\s+class\s+(\w+)", re.M), "class"),
    (re.compile(r"^export\s+default\s+(\w+)\s*;?\s*$", re.M), "export"),
]

# Types, Props, infra helpers — readable in-file; not indexed for AI graph
SKIP_SYMBOL_NAMES = frozenset({"get_connection", "get_database_path", "init_db"})
SKIP_NAME_SUFFIXES = ("Props", "Body", "Request", "Response")

TS_IMPORT_RE = re.compile(
    r"""import\s+(?:(\w+)|\{([^}]+)\}|(\w+)\s*,\s*\{([^}]+)\})\s+from\s+['"]([^'"]+)['"]"""
)
TS_CALL_RE = re.compile(r"\b([a-zA-Z_]\w*)\s*\(")

PY_DEF_RE = re.compile(r"^def\s+(\w+)\s*\(", re.M)
PY_CLASS_RE = re.compile(r"^class\s+(\w+)", re.M)
PY_ROUTE_RE = re.compile(
    r"@\w+\.(get|post|put|patch|delete)\s*\(\s*['\"]([^'\"]+)['\"]", re.I
)
PY_IMPORT_RE = re.compile(r"^(?:from\s+(\S+)\s+)?import\s+(.+)$", re.M)

CONTEXT_SYMBOL_FILES = {
    "fe-utils.md": ("fe-utils", {"symbol_id", "name", "purpose", "tests", "depends_on"}),
    "fe-components.md": ("fe-components", {"symbol_id", "name", "purpose", "tests", "depends_on"}),
    "fe-services.md": ("fe-services", {"symbol_id", "name", "purpose", "tests", "api_calls"}),
    "be-services.md": ("be-services", {"symbol_id", "name", "purpose", "tests", "depends_on"}),
    "api-list.md": ("api-list", {"symbol_id", "method", "path", "handler", "request_type", "response_type", "tests"}),
    "types.md": ("types", {"symbol_id", "name", "kind", "used_by"}),
}

AUTO_PURPOSE = "(sync — add purpose)"


def format_row(cells: list[str]) -> str:
    return "| " + " | ".join(cells) + " |"


def split_sections(text: str) -> tuple[str, list[tuple[str, str]]]:
    text = text.replace("\r\n", "\n")
    if "\n## " not in text:
        return text, []
    preamble, rest = text.split("\n## ", 1)
    sections: list[tuple[str, str]] = []
    for chunk in rest.split("\n## "):
        first_nl = chunk.find("\n")
        if first_nl == -1:
            sections.append((chunk.strip(), ""))
        else:
            heading = chunk[:first_nl].strip()
            body = chunk[first_nl + 1 :]
            sections.append((heading, body))
    return preamble, sections


def section_header_map(body: str) -> dict[str, int]:
    for line in body.splitlines():
        if not line.startswith("|") or line.startswith("|---"):
            continue
        cells = [c.strip().lower() for c in line.strip("|").split("|")]
        if "symbol_id" in cells or "key" in cells:
            return {c: i for i, c in enumerate(cells)}
    return {}


def context_file_for_symbol(file_path: str, kind: str, stack: str) -> str:
    norm = file_path.replace("\\", "/")
    if stack == "python":
        if "/routes/" in norm:
            return "api-list.md"
        if "/services/" in norm:
            return "be-services.md"
        return "be-services.md"
    if "/api/" in norm:
        return "fe-services.md"
    if "/hooks/" in norm or kind == "hook":
        return "fe-utils.md"
    if "/components/" in norm or norm.endswith("App.tsx"):
        return "fe-components.md"
    return "fe-utils.md"


def lookup_column_for_context(filename: str) -> str:
    return "handler" if filename == "api-list.md" else "name"


def all_catalog_symbols(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute(
        """
        SELECT s.id, s.name, s.kind, s.tests, f.path, f.stack
        FROM symbols s JOIN files f ON f.id = s.file_id
        ORDER BY f.path, s.name
        """
    ).fetchall()


def symbol_by_id(conn: sqlite3.Connection, symbol_id: int) -> sqlite3.Row | None:
    return conn.execute(
        """
        SELECT s.id, s.name, s.kind, s.tests, f.path, f.stack
        FROM symbols s JOIN files f ON f.id = s.file_id
        WHERE s.id = ?
        """,
        (symbol_id,),
    ).fetchone()

CONTEXT_TEST_FILES = {
    "fe-tests.md": "react",
    "be-tests.md": "python",
}


def db_path(repo: Path) -> Path:
    return repo / ".code-index" / "graph.db"


def connect(repo: Path) -> sqlite3.Connection:
    path = db_path(repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    conn.commit()


def posix(p: Path, repo: Path) -> str:
    try:
        return p.resolve().relative_to(repo.resolve()).as_posix()
    except ValueError:
        return str(p).replace("\\", "/")


def infer_file_kind(rel: str, stack: str) -> str:
    low = rel.lower()
    if "test" in Path(rel).name.lower() or "/__tests__/" in low or low.startswith("tests/"):
        return "test"
    if stack == "react":
        if low.endswith("/app.tsx"):
            return "component"
        if "/components/" in low:
            return "component"
        if "/hooks/" in low or "/hook/" in low:
            return "hook"
        if "/api/" in low or "/services/" in low:
            return "service"
        return "util"
    if stack == "python":
        if "/routes/" in low:
            return "route"
        if "/services/" in low:
            return "service"
        if "/domain/" in low:
            return "domain"
        return "module"
    return "file"


def infer_symbol_kind(name: str, file_kind: str, sym_kind: str) -> str:
    if name.startswith("use") and len(name) > 3 and name[3].isupper():
        return "hook"
    if file_kind == "component":
        return "component"
    if file_kind == "route":
        return "route"
    if sym_kind in ("interface", "type"):
        return sym_kind
    if sym_kind == "class":
        return "class"
    return "function"


def scan_source_files(repo: Path) -> list[tuple[Path, str, str]]:
    """Return (path, stack, extension) for indexable sources (no test files)."""
    out: list[tuple[Path, str, str]] = []
    app_web = repo / "apps" / "web-react"
    app_api = repo / "apps" / "api"
    has_app_tree = app_web.is_dir() or app_api.is_dir()
    roots = [
        (app_web, "react", {".ts", ".tsx"}),
        (app_api, "python", {".py"}),
    ]
    if not has_app_tree:
        roots.extend(
            [
                (repo / "fixtures" / "code-index-poc" / "apps" / "web-react", "react", {".ts", ".tsx"}),
                (repo / "fixtures" / "code-index-poc" / "apps" / "api", "python", {".py"}),
            ]
        )
    for root, stack, exts in roots:
        if not root.is_dir():
            continue
        for p in root.rglob("*"):
            if p.suffix in exts and p.is_file():
                if "node_modules" in p.parts or "__pycache__" in p.parts:
                    continue
                rel = posix(p, repo)
                if infer_file_kind(rel, stack) == "test":
                    continue
                out.append((p, stack, p.suffix))
    return out


def should_index_symbol(name: str, sym_kind: str, file_kind: str, rel: str) -> bool:
    """Catalog entries only — cross-file navigation, not in-file trivia."""
    if name in SKIP_SYMBOL_NAMES:
        return False
    if name.startswith("test_"):
        return False
    if sym_kind in ("type", "interface", "class"):
        return False
    if any(name.endswith(s) for s in SKIP_NAME_SUFFIXES):
        return False
    if name.startswith(("GET_", "POST_", "PUT_", "PATCH_", "DELETE_")):
        return False
    if rel.endswith("main.py"):
        return False
    norm = rel.replace("\\", "/")
    if file_kind == "route":
        return True
    if "/services/" in norm:
        return True
    if "/api/" in norm:
        return name.startswith(("fetch", "save"))
    if file_kind == "hook" or (name.startswith("use") and len(name) > 3 and name[3].isupper()):
        return True
    if "/components/" in norm or norm.endswith("App.tsx"):
        return name[0].isupper()
    return False


def extract_ts_symbols(text: str) -> list[tuple[str, str]]:
    found: dict[str, str] = {}
    for pattern, kind in TS_EXPORT_PATTERNS:
        for m in pattern.finditer(text):
            name = m.group(1)
            if name and name not in found:
                found[name] = kind
    return list(found.items())


def extract_py_symbols(text: str, file_kind: str) -> list[tuple[str, str]]:
    found: dict[str, str] = {}
    for m in PY_DEF_RE.finditer(text):
        if not m.group(1).startswith("_"):
            found[m.group(1)] = "function"
    return list(found.items())


def extract_brace_body(text: str, open_pos: int) -> str:
    depth = 0
    for i in range(open_pos, len(text)):
        ch = text[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[open_pos : i + 1]
    return text[open_pos:]


def ts_symbol_bodies(text: str) -> dict[str, str]:
    """Map exported symbol name → its body text (for use-edge detection)."""
    bodies: dict[str, str] = {}
    patterns = [
        re.compile(r"^export\s+(?:async\s+)?function\s+(\w+)", re.M),
        re.compile(r"^export\s+const\s+(\w+)\s*=", re.M),
        re.compile(r"^export\s+default\s+function\s+(\w+)", re.M),
    ]
    for pat in patterns:
        for m in pat.finditer(text):
            name = m.group(1)
            brace = text.find("{", m.end())
            if brace != -1:
                bodies[name] = extract_brace_body(text, brace)
    for m in re.finditer(r"^export\s+default\s+(\w+)\s*;?\s*$", text, re.M):
        name = m.group(1)
        fn = re.search(rf"function\s+{re.escape(name)}\s*\([^)]*\)\s*\{{", text)
        if fn:
            bodies[name] = extract_brace_body(text, fn.end() - 1)
    return bodies


def py_symbol_bodies(text: str) -> dict[str, str]:
    bodies: dict[str, str] = {}
    matches = [m for m in PY_DEF_RE.finditer(text) if not m.group(1).startswith("_")]
    for i, m in enumerate(matches):
        name = m.group(1)
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        bodies[name] = text[start:end]
    return bodies


def symbol_used_in_text(name: str, text: str) -> bool:
    if name[0].isupper():
        if re.search(rf"<{re.escape(name)}\b", text):
            return True
    return bool(re.search(rf"\b{re.escape(name)}\b", text))


def find_tests_for_symbol(repo: Path, source_rel: str, symbol_name: str, stack: str) -> str:
    src = Path(source_rel)
    stem = src.stem
    parent = (repo / src.parent).resolve()
    candidates: list[str] = []

    if stack == "react":
        patterns = [
            parent / f"{stem}.test.ts",
            parent / f"{stem}.test.tsx",
            parent / f"{stem}.spec.ts",
            parent / f"{stem}.spec.tsx",
            parent / "__tests__" / f"{stem}.test.ts",
            parent / "__tests__" / f"{stem}.test.tsx",
            parent / f"{symbol_name}.test.ts",
            parent / f"{symbol_name}.test.tsx",
        ]
    else:
        patterns = [
            parent / f"test_{stem}.py",
            parent / f"{stem}_test.py",
            parent / "tests" / f"test_{stem}.py",
            parent.parent / "tests" / f"test_{stem}.py",
            parent.parent.parent / "tests" / f"test_{stem}.py",
            parent / "tests" / f"test_{symbol_name}.py",
        ]

    for pat in patterns:
        if pat.is_file():
            candidates.append(posix(pat, repo))

    if not candidates and stack == "python":
        for test_root in [parent / "tests", parent.parent / "tests", parent.parent.parent / "tests"]:
            if not test_root.is_dir():
                continue
            for tp in test_root.glob("test_*.py"):
                try:
                    if symbol_name in tp.read_text(encoding="utf-8", errors="replace"):
                        candidates.append(posix(tp, repo))
                        break
                except OSError:
                    pass

    return ",".join(dict.fromkeys(candidates))


def extract_ts_imports(text: str) -> list[tuple[str, list[str]]]:
    imports: list[tuple[str, list[str]]] = []
    for m in TS_IMPORT_RE.finditer(text):
        default = m.group(1)
        named1 = m.group(2)
        default2 = m.group(3)
        named2 = m.group(4)
        module = m.group(5)
        names: list[str] = []
        if default:
            names.append(default)
        if default2:
            names.append(default2)
        for block in (named1, named2):
            if block:
                for part in block.split(","):
                    n = part.strip().split(" as ")[0].strip()
                    if n:
                        names.append(n)
        imports.append((module, names))
    return imports


def extract_py_imports(text: str) -> list[tuple[str, list[str]]]:
    imports: list[tuple[str, list[str]]] = []
    for m in PY_IMPORT_RE.finditer(text):
        module = m.group(1) or ""
        rest = m.group(2)
        names = [n.strip().split(" as ")[0] for n in rest.split(",") if n.strip()]
        imports.append((module, names))
    return imports


def resolve_ts_module(repo: Path, source_file: Path, module: str) -> str | None:
    if module.startswith("."):
        base = (source_file.parent / module).resolve()
        for ext in (".ts", ".tsx", "/index.ts", "/index.tsx"):
            if ext.startswith("/"):
                candidate = Path(str(base) + ext)
            else:
                candidate = Path(str(base) + ext) if not str(base).endswith(ext) else base
            if candidate.is_file():
                return posix(candidate, repo)
        return None
    return None


def resolve_py_module(repo: Path, source_file: Path, module: str) -> str | None:
    if not module.startswith("src."):
        return None
    rel = module.replace(".", "/") + ".py"
    for base in (source_file.parent, repo / "apps" / "api"):
        candidate = (base / rel).resolve()
        if candidate.is_file():
            return posix(candidate, repo)
        init = candidate.parent / "__init__.py"
        if init.is_file():
            return posix(init, repo)
    api_candidate = repo / "apps" / "api" / rel
    if api_candidate.is_file():
        return posix(api_candidate, repo)
    return None


def internal_import_targets(
    repo: Path,
    path: Path,
    rel: str,
    stack: str,
    text: str,
    sym_map: dict[tuple[str, str], int],
) -> dict[str, int]:
    """Imported names → symbol id (repo-internal only)."""
    targets: dict[str, int] = {}
    if stack == "react":
        for module, names in extract_ts_imports(text):
            resolved = resolve_ts_module(repo, path, module) if module.startswith(".") else None
            if not resolved:
                continue
            for name in names:
                sid = sym_map.get((resolved, name))
                if sid:
                    targets[name] = sid
    else:
        for module, names in extract_py_imports(text):
            resolved = resolve_py_module(repo, path, module) if module else None
            for name in names:
                if resolved:
                    sid = sym_map.get((resolved, name))
                    if sid:
                        targets[name] = sid
    return targets


def symbol_id_map(conn: sqlite3.Connection) -> dict[tuple[str, str], int]:
    rows = conn.execute(
        """
        SELECT s.id, s.name, f.path
        FROM symbols s JOIN files f ON f.id = s.file_id
        """
    ).fetchall()
    return {(r["path"], r["name"]): r["id"] for r in rows}


def dependents_of(conn: sqlite3.Connection, symbol_id: int) -> list[str]:
    rows = conn.execute(
        """
        SELECT s.name AS dep
        FROM edges e
        JOIN symbols s ON s.id = e.to_symbol_id
        WHERE e.from_symbol_id = ? AND e.to_symbol_id IS NOT NULL
        """,
        (symbol_id,),
    ).fetchall()
    return sorted({r["dep"] for r in rows if r["dep"]})


def users_of(conn: sqlite3.Connection, symbol_id: int) -> list[str]:
    rows = conn.execute(
        """
        SELECT f.path, s.name
        FROM edges e
        JOIN symbols s ON s.id = e.from_symbol_id
        JOIN files f ON f.id = s.file_id
        WHERE e.to_symbol_id = ?
        """,
        (symbol_id,),
    ).fetchall()
    return [f"{r['path']}:{r['name']}" for r in rows]
