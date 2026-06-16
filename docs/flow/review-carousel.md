# Review checkpoint

**Every agent turn ends here.** User only uses the carousel — see [carousel-chain.md](carousel-chain.md).

## Cursor — `AskQuestion` (2 options only)

| id | label |
|----|-------|
| `proceed` | Proceed |
| `other` | Other… |

```
prompt: |
  <step summary + files to skim>

  Proceed to continue, or pick Other and write feedback.
options:
  - id: proceed
    label: Proceed
  - id: other
    label: Other…
```

**Last tool call of the turn.** No text after it asking the user to run another agent.

## On Proceed — chain (do not ask user to type)

| Agent | Next action |
|-------|-------------|
| plan-agent | Handoff **orchestrator** `send: true` |
| orchestrator | Handoff **next specialist** from `plan.md` `send: true` |
| specialist | Handoff **orchestrator** `send: true` |
| orchestrator (final) | `phase: done` |

## Copilot — `vscode/askQuestions`

Same 2 options; `allowFreeformInput: true`. Chain via handoffs or next dispatch — never chat instructions.

## Interpret

| Result | Action |
|--------|--------|
| Proceed | Chain per table above |
| Other + feedback | `feedback.md` → revise → AskQuestion again |

## When

Every item in `review.pause`: `spec`, `plan`, `step`, `code`, `done`.
