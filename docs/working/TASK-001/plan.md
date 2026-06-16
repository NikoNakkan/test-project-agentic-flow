# Plan — TASK-001

> Written by **plan-agent** from user goal + [agent-decisions.md](../../rules/agent-decisions.md) + [agentic-flow.yaml](../../../agentic-flow.yaml).  
> **User must review this entire file** and reply in dialog before orchestrator runs step 1.

## User goal (verbatim)

> add a hello world button that saves in a backend hello world click counter

## What we found

- **Greenfield:** `apps/` does not exist yet — first feature task will scaffold React (`apps/web-react`) and FastAPI (`apps/api`) per `agentic-flow.yaml`.
- **Index:** `.code-index/graph.db` has no `symbols` table yet — no reusable components, routes, or services to extend.
- **Context:** `api-list.md`, `fe-design-system.md`, and `fe-components.md` are empty shells — all surfaces are new.
- **Persistence default:** in-memory counter (PoC) unless user later requests a database.

## Spec clarifications

None — goal is clear: one button, backend persists click count, full-stack PoC.

## AI decisions

| Decision | Value | Basis |
|----------|-------|-------|
| Stack | React + FastAPI + OpenAPI contract | `app.*` in agentic-flow.yaml |
| In scope | FE button + BE counter API + contract + tests + index refresh | Full-stack feature goal |
| Out of scope | Auth, deploy, CI, persistent DB | agent-decisions defaults |
| API surfaces | `GET /hello-world/count`, `POST /hello-world/click` | Increment-on-click + read count for UI |
| UI surfaces | Home/demo page with Hello World button + displayed count | Single interactive PoC screen |
| Data / env | In-memory counter in BE; `VITE_API_URL` for FE | envs.md defaults |
| Reuse strategy | Create new — no index hits | Empty repo |
| Test strategy | pytest (BE) + vitest (FE) after implementation | `app.tests` + rules-testing |

## Proposed tech & scope (user reviews)

| Topic | Proposal | User notes |
|-------|----------|------------|
| Persistence | In-memory integer counter in FastAPI service module | Resets on server restart |
| New API endpoints | `GET /hello-world/count` → `{ "count": number }`; `POST /hello-world/click` → increment and return `{ "count": number }` | |
| New UI components | `BaseButton` (design-system base) + `HelloWorldButton` (feature) on app home | Theme tokens only; i18n keys for label |
| Scaffold | Minimal `apps/api`, `apps/web-react`, `packages/contract` on first implementation step | Standard PoC layout |

## User plan review

| Field | Value |
|-------|-------|
| **Status** | `approved` |
| **Reviewed at** | 2026-06-17 |
| **User notes** | Proceed |

Orchestrator sets **approved** after dialog **proceed**. Do not start step 1 while **pending** or **revision_requested**.

---

## Acceptance

- [ ] Clicking the Hello World button calls the backend and increments the stored counter.
- [ ] UI shows the current click count (loaded on mount, updated after each click).
- [ ] OpenAPI contract documents both endpoints; FE uses generated or shared types from `packages/contract`.
- [ ] BE pytest and FE vitest suites pass for new exports.
- [ ] Code index refresh exits 0 after implementation.

## Steps

| # | agent | gate | task | context_files | scope | done_when |
|---|-------|------|------|---------------|-------|-----------|
| 1 | navigator | full | Query index + context; write findings | INDEX.md, api-list.md, fe-design-system.md | read-only | `findings.md` with reuse/create list |
| 2 | be-api-contract | full | Define hello-world counter API | api-list.md, types.md | `packages/contract/**` | OpenAPI spec + `contract-summary.md` |
| 3 | be-dev | quick | Scaffold `apps/api` if missing; implement routes + in-memory service | api-list.md, envs.md, be-services.md | `apps/api/**` | Endpoints work; `be-test-handoff.md` |
| 4 | be-testing-agent | quick | BE tests for counter service and routes | be-tests.md | `apps/api/tests/**` | pytest pass |
| 5 | fe-design-navigator | full | Design findings for button + layout | fe-design-system.md, fe-i18n.md | read-only | `findings.md` **Design findings** section |
| 6 | fe-dev | full | Scaffold `apps/web-react` if missing; Hello World button + count display | findings.md, fe-components.md | `apps/web-react/**` | `ui-summary.md`; `fe-test-handoff.md` |
| 7 | fe-testing-agent | quick | FE tests for button and API hook/service | fe-tests.md | `apps/web-react/**` | vitest pass |
| 8 | flow-end-validator | full | Index refresh + artifact index update | CODE-INDEX.md | `scripts/**`, `docs/working/INDEX.md` | `code_index_refresh.py` exit 0 |

**Human checkpoints:** AskQuestion — **Proceed** | **Other…** (2 options, never 3).

## Notes

- First feature in repo — navigator will record scaffold requirements; be-dev and fe-dev may create initial app structure.
- Counter is process-local memory; document in `ui-summary.md` / API docs that restart resets count.
