# Cursor — test the full agentic flow

User gives **one goal**. After that, **only the carousel** — no typing commands.

See [carousel-chain.md](carousel-chain.md).

## Flow (chat)

1. **Plan mode** — paste your dumb goal (e.g. *"Add a hello note in docs"*).
2. Plan-agent writes `plan.md` → **AskQuestion** (Proceed | Other…).
3. **Proceed** → orchestrator starts automatically (`send: true` handoff).
4. Each step → specialist work → **AskQuestion** → **Proceed** → next step.
5. **Other** → type feedback → revise → carousel again.

You never type `run orchestrator` or `@agent`.

## Copilot vs Cursor

| | Cursor | Copilot |
|---|--------|---------|
| Tool | `AskQuestion` | `vscode/askQuestions` |
| Chain | handoffs `send: true` | same pattern |
