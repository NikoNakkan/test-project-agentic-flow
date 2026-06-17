# Carousel chain — user only clicks Proceed | Other

After the user's **first goal**, they must **never** type commands (`run orchestrator`, `@agent`, etc.). **Only the carousel.**

## Rule

Every agent turn **ends** with **AskQuestion** (2 options: Proceed | Other…). **Nothing after** — no "next run X", no instructions to type.

## On Proceed

| Who | Do this (automatically) |
|-----|-------------------------|
| **plan-agent** | Set plan approved → **handoff orchestrator** `send: true` |
| **orchestrator** | Mark step done → **run next plan step** (handoff to specialist `send: true`, or execute inline) |
| **any specialist** | **handoff orchestrator** `send: true` — "Step N done; update state + checkpoint" |
| **orchestrator** (final) | Mark `phase: done` → AskQuestion once more → Proceed closes task — **no git commit** |

## On Other

Append `feedback.md` → if pattern-like ([rule-promotion.md](rule-promotion.md)) **AskQuestion** Yes add to rules | No task only → optional rules write → revise same step → **AskQuestion** again.

## Handoff template (Cursor)

```yaml
handoffs:
  - label: Proceed
    agent: orchestrator   # or next specialist from plan
    prompt: <auto — step context from plan.md / state.yaml>
    send: true
```

## Never say to the user

- "Run orchestrator"
- "@.github/agents/..."
- "Switch to Agent mode and type..."
- "Reply proceed in chat"

The carousel **is** the only control.
