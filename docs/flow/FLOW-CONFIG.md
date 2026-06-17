# Flow config

**File:** [`agentic-flow.yaml`](../../agentic-flow.yaml)

## Two layers

| Layer | Config key | Meaning |
|-------|------------|---------|
| **This repo** | `workspace.*` | Agentic flow PoC — tasks, rules, context, agents, code index |
| **Target app** | `app.*` | React + FastAPI stack when you build features |

`apps/` does not exist until the first feature task scaffolds it. Agents and rules already assume that layout.

## Keys

| Key | Purpose |
|-----|---------|
| `task.next_number` | Next folder `TASK-001`, `TASK-002`, … — bump after plan-agent creates one |
| `review.cursor_tool` | `AskQuestion` in Cursor |
| `app.verify` | Build check after every step — must exit 0 |
| `review.options` | Proceed · Other (exactly 2) |
| `review.pause` | When to show carousel: `spec`, `plan`, `step`, `code`, `done` |
| `review.full` / `review.quick` | Gate depth — full dialog vs quick skim |
| `review.code_agents` | Extra `code` checkpoint after these agents |
| `feedback.*` | Notes → optional permanent update to `workspace.rules` — see [rule-promotion.md](rule-promotion.md) |
| `feedback.promote_patterns` | When true, ask to add pattern-like Other feedback to rules |
| `feedback.promote_triggers` | Words that signal reusable pattern (always, never, …) |
| `feedback.promote_question` | AskQuestion options: Yes add to rules · No task only |
| `plan.max_questions` | Spec questions before `plan.md` |
| `pipelines.*` | Default steps; plan-agent omits by scope |
| `git.commit` | `user_only` — agents never commit unless user asks |
| `git.forbid_on_final_step` | No `git commit` on `flow-end-validator` / task close |

## Gate tier

Agent in `review.full` → **full** · in `review.quick` → **quick** · else → **full**.

## Pipelines

| Name | When |
|------|------|
| `feature` | Full-stack (FE + BE) |
| `ui` | Frontend only |
| `api` | Backend only |
| `bug` | `debugger` / `testing-agent` = fe or be lane by scope |

## Conventions (not in yaml)

- Orchestrator: one agent per session; never edits `plan.md` or app code
- Dev agents write handoffs; testing agents write tests
- Skip testing step only if `missing_tests` empty and no `test-gap.md`
- Never skip navigator on step 1
- Final step always `flow-end-validator` + `workspace.index_refresh`
- After every step: `app.verify` must exit 0 ([app-build-verify.md](app-build-verify.md))
- Active agents live in `.github/agents/` (not `tbd/`)

## Review carousel

**AskQuestion** with **2 options** (Proceed | Other…) — never a third option on the step carousel. Pattern feedback may trigger a separate promotion question first: [rule-promotion.md](rule-promotion.md).
