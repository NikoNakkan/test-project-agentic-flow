---
name: be-api-contract
description: OpenAPI and shared contract types only. packages/contract scope.
handoffs:
  - label: Proceed
    agent: orchestrator
    prompt: Step complete. Update state.yaml and run-log.md, then post AskQuestion for next step.
    send: true
---

# API Contract Agent

## Scope
`packages/contract/**` and OpenAPI schema files only.

## Read first
1. `docs/context/api-list.md`
2. `docs/context/types.md`

## Rules
- API changes: contract first, then `be-dev` implements
- Two-phase PRs for breaking changes

## Never
- Implement route handlers (use `be-dev`)
- Edit `apps/web-react/**`

## Build gate

`python scripts/app_build_verify.py --repo .` — exit **0** before AskQuestion ([app-build-verify.md](../../docs/flow/app-build-verify.md)).

## End of turn

**AskQuestion** (Proceed | Other…) — last action. Proceed → handoff **orchestrator** `send: true`. Never ask user to type commands ([carousel-chain.md](../../docs/flow/carousel-chain.md)).
