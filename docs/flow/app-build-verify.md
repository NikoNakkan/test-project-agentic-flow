# App build verify (every step)

After **every** plan step, the app must still **build** before the carousel appears.

## Command

From repo root (`agentic-flow.yaml` → `app.verify`):

```bash
python scripts/app_build_verify.py --repo .
```

Exit code **must be 0** before marking a step done or posting AskQuestion.

## What it checks

| Layer | When | Checks |
|-------|------|--------|
| **Contract** | `packages/contract/openapi.yaml` exists | Valid OpenAPI header; `types.ts` non-empty if present |
| **Backend** | `apps/api/app/` exists | `compileall` + `from app.main import app` |
| **Frontend** | `apps/web-react/package.json` with `build` script | `npm install` if needed, then `npm run build` |

Layers not scaffolded yet are **skipped** (e.g. navigator on a greenfield task).

## Who runs it

1. **Specialist** — before AskQuestion; fix until green
2. **Orchestrator** — after specialist returns, before updating `state.yaml`

## Never

- Mark step `done` while verify fails
- Skip verify because "only docs changed" when app code exists in scope
