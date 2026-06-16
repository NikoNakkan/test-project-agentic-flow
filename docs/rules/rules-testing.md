# Testing rules

Policy details and examples: [`test-writing.md`](../context/test-writing.md)

## Placement (colocated)

**Every test file lives in the same directory as the source it covers** — component folder, hook file, API client, route module, or service module. No separate test trees for symbol-level tests.

| Source | Test file (same folder) |
|--------|------------------------|
| `components/Foo/Foo.tsx` | `components/Foo/Foo.test.tsx` |
| `hooks/useBar.ts` | `hooks/useBar.test.ts` |
| `api/toggleState.ts` | `api/toggleState.test.ts` |
| `App.tsx` | `App.test.tsx` |
| `routes/toggle_state.py` | `tests/test_toggle_state.py` |
| `services/toggle_state.py` | covered via route tests or `tests/test_*.py` |

**Do not** use `__tests__/`, repo-root test mirrors, or distant folders for per-symbol tests.

**Exception:** shared setup only (`test-setup.ts`, pytest `conftest.py`) at app config paths.

## Naming

- `Foo.tsx` → `Foo.test.tsx`
- `useBar.ts` → `useBar.test.ts`
- Route/service coverage → `tests/test_<feature>.py`

## Stack (this repo)

| Layer | Tool |
|-------|------|
| FE | Vitest + React Testing Library + jsdom |
| BE | pytest + FastAPI TestClient |
| E2E | **Out of scope** for this PoC |

## Required

- Every exported symbol → colocated test file linked in index (`symbols.tests`)
- After adding tests: `python scripts/code_index_refresh.py --repo .`
- `missing_tests` must be `[]` before task close

## When to write tests

| Situation | Agent | Action |
|-----------|-------|--------|
| Greenfield / new exports | fe-testing-agent / be-testing-agent | Cover all `missing_tests` in scope |
| Bug-fix task | fe/be-debugger → testing agent | **`test-gap.md`** — implement **every** listed test |
| Symbol already has tests + test-gap exists | testing agent | **Extend** file — do not skip |

Query gaps:

```bash
python scripts/code_index_query.py --repo . missing_tests
```

## AAA pattern (mandatory)

Every test uses **Arrange → Act → Assert** with comments.

## FE i18n in tests

- Import `./i18n` or rely on `test-setup.ts`
- Assert UI copy with `i18n.t('namespace:key')` when key exists in `fe-i18n.md`
- Do not hardcode user-facing strings in assertions

See [`rules-i18n.md`](rules-i18n.md).

## Handoff

fe-dev writes [`fe-test-handoff.template.md`](../working/fe-test-handoff.template.md); be-dev writes [`be-test-handoff.template.md`](../working/be-test-handoff.template.md) — one file per lane, before the matching testing step.

## Regression from debugger

When `docs/working/<TASK-ID>/test-gap.md` exists:

1. **fe-debugger** / **be-debugger** writes test-gap (why tests missed the bug + tests to add)
2. **fe-testing-agent** / **be-testing-agent** implements **every** listed test
3. Fix is not done until test-gap tests pass

Template: [`test-gap.template.md`](../working/test-gap.template.md)

## Commands

```powershell
# App build — from repo root (after every step)
python scripts/app_build_verify.py --repo .

# FE — from apps/web-react
npm test

# BE — from apps/api
python -m pytest tests/ -q

# Index — from repo root
python scripts/code_index_refresh.py --repo .
```

## Anti-patterns

- Hardcoded locale strings in FE test assertions
- Skipping test-gap tests because a test file already exists
- Testing implementation details instead of observable behavior
- Marking testing step done while `missing_tests` is non-empty


# BACKEND testing

## TDD Workflow
1. write Gherkin (GIVEN / WHEN / THEN)
2. write failing test
3. implement minimal code
4. pass test
5. refactor

## Mandatory validation
pytest tests/unit/ -x --tb=short

## Conventions
- no testing private methods
- naming:
  test_<action>_<condition>_<result>
- use GIVEN / WHEN / THEN docstrings
- Arrange–Act–Assert

## Markers
- @pytest.mark.unit
- @pytest.mark.asyncio

## Mocking
- AsyncMock for DB
- respx for httpx
- patch for services

## Fixtures
- use shared fixtures (conftest.py)
- avoid inline setup
