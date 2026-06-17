# Agent decisions (hard rules — plan-agent does not ask the user)

> **Audience:** plan-agent, orchestrator, and all specialists.  
> **Flow config:** [`agentic-flow.yaml`](../../agentic-flow.yaml) controls checkpoints, gate tiers, and feedback → rules/context.  
> **User says one thing:** e.g. *"Build a todo list"* or *"Add DELETE /todos/:id"*.  
> **Hard rules** below are **your** decisions from this file, index, and context.

## User input vs spec clarifications

| Layer | Who | What |
|-------|-----|------|
| **Goal** | User | One task in plain language |
| **Spec clarifications** | Plan-agent asks user | 1–3 product/UX questions after stating what was found — only when unclear whether/how to implement |
| **Hard rules** | AI only | Stack, reuse, tests, acceptance, index sync, agent routing |

### Plan-agent as spec agent

Before planning, plan-agent **scans** index + context, then messages the user like:

> *I found BaseButton and toggle-state API. Unclear: should emoji be on App or inside BaseButton?*

**Ask:** implement or not, behavior, visible UX, data meaning, extend vs replace.  
**Do not ask:** React vs Angular, pytest vs vitest, run index-curator, reuse policy, test policy.  
**Max 3 questions** per task. If clear → ask nothing, write plan.

---

## Defaults (when goal does not say otherwise)

| Topic | Default | Source |
|-------|---------|--------|
| Frontend | React in `app.frontend` | agentic-flow.yaml |
| Backend | FastAPI in `app.backend` | agentic-flow.yaml |
| Contract | OpenAPI in `app.contract` | agentic-flow.yaml |
| Persistence | In-memory unless goal says database | PoC default |
| Auth | Out of scope unless goal mentions it | PoC default |
| Tests | Vitest (FE) · pytest (BE) — see `app.tests` | agentic-flow.yaml |
| i18n | react-i18next, keys in `app.locales` | rules-i18n.md, fe-i18n.md |
| Theming | CSS variables in `app.theme` only | rules-theming.md |
| Reuse | Always prefer existing symbols | Index + context MDs |

---

## Design system (UI tasks — not user Q&A)

When the goal touches UI, styling, components, or layout:

1. Run **`fe-design-navigator`** (with or right after `navigator`)
2. Read `docs/context/fe-design-system.md` — theme tokens, **base** table, then **extending** table
3. Read `docs/context/fe-i18n.md` + `rules-i18n.md` for any user-facing copy
4. **No magic colors** — `rules-theming.md`; **no string literals in JSX** — `rules-i18n.md`
5. **No extending component without a registered base** — plan must create base first if missing

---

## Reuse (navigator + index — not user Q&A)

**Always** run `navigator` as plan step 1.

Before creating any file or export:

```bash
python scripts/code_index_query.py --repo . find_symbol <name>
python scripts/code_index_query.py --repo . who_uses <name>
python scripts/code_index_query.py --repo . context_pack "<keywords from goal>"
```

Read matching sections in `docs/context/`.

| Index / context signal | Action |
|------------------------|--------|
| `find_symbol` hit + row in context MD | **Extend** — read `purpose`, do not duplicate |
| `who_uses` shows callers | **Preserve** public shape; refactor agent if rename needed |
| No hits, empty repo | **Create new** — record in `findings.md` |
| Partial overlap | **Reuse** util/hook/service; add only missing pieces |

Write `docs/working/<TASK-ID>/findings.md` with: what exists, what to reuse, what to create.

---

## Tests (index-driven — not user Q&A)

Policy: every **exported** symbol should have a test file (`rules-testing.md`).

**Who writes tests:** `be-testing-agent` / `fe-testing-agent` — not feature dev agents.

**When to include a testing step in the plan:**

```bash
python scripts/code_index_query.py --repo . missing_tests
```

| Situation | Plan step |
|-----------|-----------|
| New exports expected (greenfield feature) | Include testing agent after implementation |
| Only editing existing covered symbols | Include testing agent with `done_when: no new missing_tests in scope` |
| `missing_tests` already empty for scope | Step may complete immediately — run query, mark done |

Testing agents **only** add tests for symbols with empty `symbols.tests` / `missing_tests` output — **except** when `docs/working/<TASK-ID>/test-gap.md` exists (debugger bug-fix); then implement every test listed in test-gap.

### Regression from debugger (bug-fix tasks)

When goal is fix / bug / broken:

| Step | Agent | done_when |
|------|-------|-----------|
| 1 | navigator | `findings.md` |
| 2 | fe-debugger or be-debugger | minimal fix + **`test-gap.md`** written |
| 3 | fe-testing-agent or be-testing-agent | all tests from test-gap added; suite green |
| 4 | flow-end-validator | `code_index_refresh.py` exit 0 |

Debugger **must** document why existing tests failed to catch the bug. Testing agent **must not** skip test-gap tests because symbol already has a test file.

---

## Scope inference from goal

| Goal signals | In scope | Out of scope |
|--------------|----------|--------------|
| "API", "endpoint", "route" | BE + contract if new surface | FE unless also mentioned |
| "page", "UI", "component", "screen" | FE | BE unless also mentioned |
| "full", "end-to-end", feature name without layer | FE + BE + contract | Deploy, CI, auth |
| "fix", "bug", "broken" | `fe-debugger` or `be-debugger` → testing agent | New features |
| "rename", "extract", "move" | `fe-refactorer` or `be-refactorer` | Behavior change |

When both FE and BE are implied, order: **contract → BE → BE tests → FE → FE tests → flow-end-validator**.

---

## Plan-agent output

1. `plan.md` — user goal + **what I found** + spec answers + **AI decisions** + **proposed tech & scope** + **user plan review** + steps + acceptance
2. Do **not** write application code

Every plan must:

1. Start with `navigator`
2. Put **contract before implementation** for new API surfaces
3. Put **implementation before testing agents**
4. End with `flow-end-validator` + `workspace.index_refresh` (must exit 0)
5. Every step `done_when` implies `app.verify` exit 0 when app layers exist
5. Map each acceptance checkbox to at least one `done_when`

---

## Orchestrator

- Read `agentic-flow.yaml` before every dispatch
- Proceed when `plan.md` approved (after plan dialog)
- **Review checkpoint** — **AskQuestion** with 2 options: Proceed | Other… ([review-carousel.md](../flow/review-carousel.md))
- Gate tier from `review.full` / `review.quick`
- Capture notes in `feedback.task_file`; on pattern-like Other feedback run promotion flow ([rule-promotion.md](../flow/rule-promotion.md)) — AskQuestion Yes add to rules | No task only before revise
- After `feedback.revise_threshold` same revises → propose rule/agent edit
- Skip testing only if `missing_tests` empty and no `test-gap.md`; never skip navigator step 1
- Never ask user to choose stack, reuse, or test policy in checkpoint dialog
- Final sign-off dialog after `flow-end-validator` before `phase: done`
- **Never `git commit` on final step** — `git.forbid_on_final_step` in agentic-flow.yaml; user commits when ready

---

## Specialists

Before writing code, read assigned context MDs and run `find_symbol` for names you plan to add.

After writing exports, add `## <file-path>` + `purpose` row in the correct context MD.

After each implementation batch: remind or run `python scripts/code_index_refresh.py --repo .`.

**When `done_when` is met:** stop — do not run the next agent. Orchestrator posts a human checkpoint; user replies **proceed** before the next step.