# Code index — graph.db ↔ context MD contract

> **Location:** co-located with context files so agents edit `purpose` here and refresh in one place.  
> **Catalog DB:** `.code-index/graph.db` (run build if missing)

## Two databases

| DB | Path | Role |
|----|------|------|
| **Code catalog** | `.code-index/graph.db` | Symbols + `uses` edges — query with scripts |
| **App data** | `apps/api/data/app.db` | Runtime feature state (e.g. toggle) — not the catalog |

## Join key: `symbol_id`

```
graph.db symbols.id  ═══  docs/context/*.md  symbol_id column
graph.db files.path  ═══  ## file-path heading in MD
graph.db edges       ═══  depends_on column (synced, read-only)
```

- **Human writes:** `purpose` only (and `## file` section when adding exports)
- **Scripts write:** `symbol_id`, `tests`, `depends_on`, `used_by`, test MD files
- **Never hand-edit** `symbol_id` — run refresh after code changes

## After every code change (required)

Run **once** when you add, change, or remove exports:

```bash
python scripts/code_index_refresh.py --repo .
```

This runs **build → sync → validate**. Exit code **must be 0**.

| Step | Script | What it does |
|------|--------|--------------|
| Build | `code_index_build.py` | Rebuild `.code-index/graph.db` from source |
| Sync | `code_index_sync_context.py` | Update context MD rows (`symbol_id`, `tests`, `depends_on`) |
| Validate | `code_index_validate.py` | 1:1 graph ↔ context; every row has human `purpose` |

**If validate fails with `missing human purpose`:** edit the `purpose` column in the matching file below, then re-run refresh.

| Symbol kind | Context file |
|-------------|--------------|
| React components | [fe-components.md](fe-components.md) |
| React hooks | [fe-utils.md](fe-utils.md) |
| FE API clients | [fe-services.md](fe-services.md) |
| i18n keys (human catalog) | [fe-i18n.md](fe-i18n.md) |
| BE route handlers | [api-list.md](api-list.md) |
| BE services | [be-services.md](be-services.md) |

Then confirm tests:

```bash
python scripts/code_index_query.py --repo . missing_tests
```

Must return `[]`.

## Deterministic add / delete

| Event | graph.db | context MD |
|-------|----------|------------|
| New export in code | New symbol (stable id if same path+name) | Sync adds row with `(sync — add purpose)` |
| Remove export | Symbol deleted on rebuild | Sync **prunes** row |
| Rename symbol | New id (old pruned) | Old row pruned; add new row + purpose |

Symbol IDs are **stable across rebuilds** when path+name unchanged.

## Queries (navigator)

```bash
python scripts/code_index_query.py --repo . find_symbol BaseButton
python scripts/code_index_query.py --repo . symbol_deps App
python scripts/code_index_query.py --repo . who_uses FlowDialog
python scripts/code_index_query.py --repo . missing_tests
python scripts/dump_graph.py
```
