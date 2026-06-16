# Task artifacts

Per-task folder: `docs/working/<TASK-ID>/`. Flow behavior: [`agentic-flow.yaml`](../../agentic-flow.yaml).

| File | Writer | Reader | Purpose |
|------|--------|--------|---------|
| `plan.md` | plan-agent | user, orchestrator | Goal, decisions, tech proposals, steps — **user approves before step 1** |
| `state.yaml` | orchestrator | orchestrator | Machine state, gate status, staleness |
| `run-log.md` | orchestrator | user, plan-agent | Human audit trail |
| `feedback.md` | orchestrator, plan-agent | user | Dialog review notes; drives rule/context updates |
| `findings.md` | navigator, fe-design-navigator | fe-dev, user | Reuse/create + design findings |
| `contract-summary.md` | be-api-contract | user | Readable API summary at checkpoints |
| `be-test-handoff.md` | be-dev | be-testing-agent | BE test brief |
| `fe-test-handoff.md` | fe-dev | fe-testing-agent | FE test brief |
| `ui-summary.md` | fe-dev | user | Readable UI summary at checkpoints |
| `test-gap.md` | debugger | testing agent | Bug-fix regression list |

Templates: `docs/working/*.template.md`, `state.template.yaml`.
