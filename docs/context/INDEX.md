# Context files — index

Read **one** relevant file before opening source code.

| File | When to read |
|------|--------------|
| [CODE-INDEX.md](CODE-INDEX.md) | **After any export change** — refresh graph.db, fix `purpose`, validate |
| [test-writing.md](test-writing.md) | **How to create/run tests** — Vitest, pytest, test-gap flow |
| [fe-utils.md](fe-utils.md) | Helpers, hooks, pure functions (React) |
| [fe-components.md](fe-components.md) | UI components (index-synced) |
| [fe-design-system.md](fe-design-system.md) | **Theme paths, colors, base vs extending components** — read before UI work |
| [fe-i18n.md](fe-i18n.md) | **Locale keys and namespaces** — read before UI copy |
| [fe-services.md](fe-services.md) | API clients, stores, data services (FE) |
| [api-list.md](api-list.md) | HTTP routes, FastAPI handlers |
| [be-services.md](be-services.md) | Backend service/domain functions |
| [fe-tests.md](fe-tests.md) | All frontend tests (auto-synced) |
| [be-tests.md](be-tests.md) | All backend tests (auto-synced) |
| [envs.md](envs.md) | Environment variables |
| [types.md](types.md) | Shared types, DTOs, schemas |

**Format:** `## <source-file-path>` heading, table rows per export.  
**Human edits:** `purpose`, `description` only.  
**Auto-synced:** `symbol_id`, `tests`, `depends_on`, `api_calls`, `used_by` — run `python scripts/code_index_refresh.py --repo .`
