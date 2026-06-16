# Findings — TASK-001

> Written by **navigator** (step 1). Read-only recon for Hello World button + backend click counter.

## Index queries

| Query | Result |
|-------|--------|
| `context_pack "hello world button click counter"` | Error — `symbols` table missing (index not yet populated) |
| `find_symbol HelloWorld` | Error — `symbols` table missing |
| `missing_tests` | Error — `symbols` table missing |

**Conclusion:** Greenfield repo. No symbols to reuse or extend.

## What exists

| Area | Status |
|------|--------|
| `apps/api` | **Missing** — scaffold on be-dev step |
| `apps/web-react` | **Missing** — scaffold on fe-dev step |
| `packages/contract` | **Missing** — scaffold on be-api-contract step |
| `docs/context/api-list.md` | Empty shell |
| `docs/context/fe-design-system.md` | Empty — no base components registered |
| `docs/context/fe-components.md` | Empty |
| `docs/context/be-services.md` | Empty |
| `.code-index/graph.db` | Present but unpopulated |

## What to create

### Backend (`apps/api`)

| Item | Path / symbol | Notes |
|------|---------------|-------|
| In-memory counter service | `apps/api/app/services/hello_world.py` | Module-level integer; `get_count()`, `increment()` |
| Routes | `apps/api/app/routes/hello_world.py` | `GET /hello-world/count`, `POST /hello-world/click` |
| FastAPI app entry | `apps/api/app/main.py` | Mount router, CORS for FE dev |
| Tests | `apps/api/tests/` | pytest for service + routes |

### Contract (`packages/contract`)

| Item | Notes |
|------|-------|
| OpenAPI spec | Document both hello-world endpoints + `HelloWorldCount` schema |
| Shared types | Export count response type for FE consumption |

### Frontend (`apps/web-react`)

| Item | Path / symbol | Notes |
|------|---------------|-------|
| `BaseButton` | `apps/web-react/src/components/base/BaseButton.tsx` | **Must register in fe-design-system.md first** — no base exists yet |
| `HelloWorldButton` | `apps/web-react/src/components/HelloWorldButton.tsx` | Calls `POST /hello-world/click`, displays count |
| API client / hook | `apps/web-react/src/hooks/useHelloWorldCount.ts` or service | `GET` on mount, refresh after click |
| Home / demo page | `apps/web-react/src/App.tsx` | Single screen with button + count |
| i18n keys | `helloWorld.button`, `helloWorld.countLabel` | Per `fe-i18n.md` — no string literals in JSX |
| Theme | `apps/web-react/src/styles/theme.css` | CSS variables only per `rules-theming.md` |
| Tests | `apps/web-react/src/**/*.test.tsx` | vitest for button + hook |

## Reuse strategy

**Create new** — no index hits, no existing symbols. First feature task scaffolds the full `apps/` layout per `agentic-flow.yaml`.

## Context file routing

| Next agent | Read |
|------------|------|
| be-api-contract | `api-list.md`, `types.md` |
| be-dev | `api-list.md`, `envs.md`, `be-services.md` |
| fe-design-navigator | `fe-design-system.md`, `fe-i18n.md` |
| fe-dev | `findings.md` (this file), `fe-components.md`, design section when added |

## Risks / notes

- Counter is in-memory — document that server restart resets count.
- `VITE_API_URL` env var needed for FE → BE in dev (see `envs.md`).
- Index refresh (`flow-end-validator`) will populate `symbols` after first implementation.
