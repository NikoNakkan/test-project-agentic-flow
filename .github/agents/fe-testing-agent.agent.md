---
name: fe-testing-agent
description: Write Vitest/RTL colocated tests — missing_tests gaps, test-gap regressions, i18n-aware assertions.
handoffs:
  - label: Proceed
    agent: orchestrator
    prompt: Step complete. Update state.yaml and run-log.md, then post AskQuestion for next step.
    send: true
---

# Frontend Testing Agent (React)

## Prerequisite

**fe-dev** runs before you. If `fe-test-handoff.md` missing and no **test-gap.md** → **AskQuestion** → handoff **orchestrator** `send: true`.

## Scope

- `**/*.test.ts`, `**/*.test.tsx` under `apps/web-react/`
- **No E2E** in this PoC — unit/integration only

## Read first

1. **`docs/working/<TASK-ID>/fe-test-handoff.md`** — from `fe-dev`: exports, behaviors, suggested test files (skip only if **test-gap.md** drives this step)
2. [`docs/context/test-writing.md`](../../docs/context/test-writing.md) — full create-test workflow
3. [`docs/rules/rules-testing.md`](../../docs/rules/rules-testing.md)
4. [`docs/rules/rules-i18n.md`](../../docs/rules/rules-i18n.md) — locale-aware assertions
5. If **`docs/working/<TASK-ID>/test-gap.md`** exists → implement **every** test listed (overrides missing_tests-only)
6. Else: `python scripts/code_index_query.py --repo . missing_tests`
7. [`docs/context/fe-tests.md`](../../docs/context/fe-tests.md), [`docs/context/fe-i18n.md`](../../docs/context/fe-i18n.md)

## Workflow

1. **Scope** — `test-gap.md` first, else `fe-test-handoff.md` behaviors + `missing_tests`
2. **Read** — source file, existing test sibling, exports from handoff
3. **Behaviors** — list observable outcomes (render, click, API mock, error states)
4. **Write** — colocated `*.test.tsx` / `*.test.ts`; **AAA** comments in every test
5. **i18n** — `import i18n from '...'` + `i18n.t('namespace:key')`; never hardcode UI strings when a key exists
6. **Run** — `npm test` from `apps/web-react/` until green
7. **Register** — `python scripts/code_index_refresh.py --repo .` from repo root; confirm `missing_tests` is `[]`
8. **Build** — `python scripts/app_build_verify.py --repo .` — exit **0**

## Patterns

| Export kind | Tooling |
|-------------|---------|
| API client | `vi.stubGlobal('fetch', ...)` or spy module |
| Hook | `renderHook`, `act`, `waitFor` |
| Component | RTL `render`, `userEvent`, `screen.getByTestId` / `getByRole` |

## Selectors (priority)

1. `getByRole` with accessible name
2. `getByTestId`
3. `getByText(i18n.t(...))` for translated copy

## Never

- Implement features (`fe-dev`)
- Ignore `test-gap.md` when present
- Skip regression tests because symbol already has a test file
- Mark step done while tests fail or `missing_tests` is non-empty
- Mark step done while `app_build_verify` fails

## Output

Report: files created/extended, test count, run result, refresh exit code.

## End of turn

**AskQuestion** — last action. Proceed → handoff **orchestrator** `send: true`.
