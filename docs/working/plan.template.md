# Plan — TASK-XXX

> Written by **plan-agent** from user goal + [agent-decisions.md](../rules/agent-decisions.md) + [agentic-flow.yaml](../../agentic-flow.yaml).  
> **User reviews via carousel** (Proceed | Other…) — plan-agent ends with AskQuestion; Proceed chains to orchestrator automatically.

## User goal (verbatim)

> <!-- Paste exactly what the user said -->

## What we found

<!-- plan-agent recon: index hits, existing symbols, gaps — 2–5 bullets -->

## Spec clarifications

<!-- User answers to 0–3 questions. "None" if clear. -->

## AI decisions

| Decision | Value | Basis |
|----------|-------|-------|
| Stack | | `app.*` in agentic-flow.yaml |
| In scope | | inferred from goal |
| Out of scope | | agent-decisions defaults |
| API surfaces | | goal + api-list.md / index |
| UI surfaces | | goal + context MDs / index |
| Data / env | | defaults or envs.md |
| Reuse strategy | | find_symbol / context_pack |
| Test strategy | | missing_tests + rules-testing |

## Proposed tech & scope (user reviews)

| Topic | Proposal | User notes |
|-------|----------|------------|
| Persistence | | |
| New API endpoints | | |
| New UI components | | |
| Other | | |

## User plan review

| Field | Value |
|-------|-------|
| **Status** | `pending` \| `approved` \| `revision_requested` |
| **Reviewed at** | |
| **User notes** | |

Orchestrator sets **approved** after dialog **proceed**. Do not start step 1 while **pending** or **revision_requested**.

---

## Acceptance

- [ ] ...

## Steps

| # | agent | gate | task | context_files | scope | done_when |
|---|-------|------|------|---------------|-------|-----------|
| 1 | navigator | full | Query index + context; write findings | INDEX.md | read-only | findings.md |
| 2 | be-api-contract | full | API contract (if new surfaces) | api-list.md, types.md | app.contract/** | openapi + contract-summary.md |
| 3 | be-dev | quick | Routes + service | api-list.md, envs.md | app.backend/** | routes work; be-test-handoff.md |
| 4 | be-testing-agent | quick | BE tests | be-tests.md | app.backend/tests/** | pytest pass |
| 4b | fe-design-navigator | full | Design findings | fe-design-system.md, fe-i18n.md | read-only | findings.md **Design findings** |
| 5 | fe-dev | full | UI per goal | findings.md, fe-components.md | app.frontend/** | ui-summary.md; fe-test-handoff.md |
| 6 | fe-testing-agent | quick | FE tests | fe-tests.md | app.frontend/** | vitest pass |
| 7 | flow-end-validator | full | Index refresh | CODE-INDEX.md | scripts/** | index_refresh exit 0 |

> Paths from `agentic-flow.yaml` → `app.*`. Gate from `review.full` / `review.quick`. Omit rows by scope.

**Human checkpoints:** AskQuestion — **Proceed** | **Other…** only (2 options, never 3).

**Build gate:** every step must pass `python scripts/app_build_verify.py --repo .` before done.

## Bug-fix variant

| # | agent | gate | task | scope | done_when |
|---|-------|------|------|-------|-----------|
| 1 | navigator | full | findings | read-only | findings.md |
| 2 | fe-debugger or be-debugger | full | fix + test-gap.md | app.*/** | test-gap.md; fix applied |
| 3 | fe-testing-agent or be-testing-agent | quick | regression tests | app.*/** | test-gap tests pass |
| 4 | flow-end-validator | full | index refresh | scripts/** | index_refresh exit 0 |

## Notes

<!-- reuse hits, skipped steps rationale -->
