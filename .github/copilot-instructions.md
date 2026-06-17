# Project instructions

1. Read [`agentic-flow.yaml`](agentic-flow.yaml) — `workspace` (this repo) + `app` (React/FastAPI target).
2. Read `docs/context/INDEX.md` before new code.
3. Read `docs/rules/agent-decisions.md` — reuse, tests, scope are AI decisions.
4. After exports: run command in `workspace.index_refresh` (exit 0).
5. UI: `app.theme` + react-i18next (`app.locales`) — see rules-theming, rules-i18n.
6. Carousel-only: Proceed chains steps — `docs/flow/carousel-chain.md`.
7. Build gate: `python scripts/app_build_verify.py --repo .` after every step — exit 0.
8. Rule promotion: on Other + pattern feedback → `docs/flow/rule-promotion.md` (AskQuestion: Yes add to rules | No task only).
9. Bug-fix: debugger → `test-gap.md` → testing agent → `flow-end-validator`.
10. Never `git commit` on final step — user commits when ready.
