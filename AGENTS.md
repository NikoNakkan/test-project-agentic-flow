# Agents — Cursor & Copilot

| Agent | File | Cursor usage |
|-------|------|----------------|
| plan-agent | `.github/agents/plan-agent.agent.md` | **Plan mode** or @plan-agent — writes `plan.md` |
| orchestrator | `.github/agents/orchestrator.agent.md` | **Agent mode** — runs steps, updates `state.yaml` |
| navigator | `.github/agents/navigator.agent.md` | Always step 1 — `findings.md` |
| fe-design-navigator | `.github/agents/fe-design-navigator.agent.md` | UI tasks — design section in `findings.md` |
| be-api-contract | `.github/agents/be-api-contract.agent.md` | `packages/contract/` |
| be-dev / fe-dev | `.github/agents/be-dev.agent.md` | App code + test handoffs |
| be-testing-agent / fe-testing-agent | `.github/agents/*-testing-agent.agent.md` | Tests only |
| flow-end-validator | `.github/agents/flow-end-validator.agent.md` | Final step — index refresh |

**Config:** `agentic-flow.yaml` · **Cursor walkthrough:** `docs/flow/CURSOR-FLOW.md`

**Checkpoint tool:** Cursor → `AskQuestion` · Copilot → `vscode/askQuestions`
