# Rule promotion — pattern feedback → permanent rules

When user picks **Other…** and feedback sounds like a **reusable pattern**, ask whether to persist it in `docs/rules/` before revising the step.

Config: [`agentic-flow.yaml`](../../agentic-flow.yaml) → `feedback.promote_*`

## When to ask

Only when feedback matches **pattern language** (`feedback.promote_triggers`):

- *always*, *never*, *from now on*, *convention*, *standard*, *new rule*, *every time*, *add to rules*

**Do not ask** for task-only tweaks (e.g. "make the button bigger", "rename this variable").

## Flow (same session, two AskQuestions)

1. User: **Other…** + feedback text
2. Append row to `docs/working/<TASK-ID>/feedback.md`
3. **If pattern-like** → **AskQuestion** (promotion — not the step carousel):

| id | label |
|----|-------|
| `add_rules` | Yes, add to rules |
| `task_only` | No, task only |

4. **If Yes** → edit target rules file + log row in [`feedback-log.md`](feedback-log.md); set feedback column to `yes → <file>`
5. **If No** or not pattern-like → set feedback column to `no task-only`; no rules edit
6. Revise current step (plan or specialist output)
7. **AskQuestion** — Proceed | Other… — **last action** ([review-carousel.md](review-carousel.md))

The step carousel stays **2 options only**. Promotion question runs **before** revise, never as a third carousel option.

## Target file routing

| Topic | File |
|-------|------|
| FE components, hooks, pages | [`rules-frontend.md`](../rules/rules-frontend.md) |
| FastAPI, routes, services | [`rules-backend.md`](../rules/rules-backend.md) |
| Tests, coverage policy | [`rules-testing.md`](../rules/rules-testing.md) |
| Theme, CSS tokens | [`rules-theming.md`](../rules/rules-theming.md) |
| i18n, copy, locales | [`rules-i18n.md`](../rules/rules-i18n.md) |
| Workflow, agents, scope | [`agent-decisions.md`](../rules/agent-decisions.md) |

On **Yes**: append one concise bullet under the right section. Do not duplicate an existing rule.

## Logging

| Where | What |
|-------|------|
| `feedback.md` | User text + promotion result (`yes → rules-*.md` / `no task-only` / `pending`) |
| `feedback-log.md` | Cross-task row: date, task, checkpoint, summary, updated file |

`feedback.confirm_writes: true` — the promotion AskQuestion **is** the confirm step.

## Who runs this

- **plan-agent** — on Other during plan review
- **orchestrator** — on Other during step checkpoints

Specialists do not edit rules; orchestrator handles promotion when user feedback arrives at a checkpoint.
