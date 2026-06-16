# Rules index

| File | Applies to |
|------|------------|
| [agent-decisions.md](agent-decisions.md) | **AI only** — plan-agent, orchestrator, specialists (reuse, tests, scope; user never sees this) |
| [rules-frontend.md](rules-frontend.md) | `apps/web-react/**` |
| [rules-backend.md](rules-backend.md) | `apps/api/**` |
| [rules-testing.md](rules-testing.md) | All tests — policy; see also [test-writing.md](../context/test-writing.md) |
| [rules-theming.md](rules-theming.md) | `apps/web-react/**` CSS — tokens in `theme.css` only |
| [rules-i18n.md](rules-i18n.md) | `apps/web-react/**` — react-i18next, no string literals |

Index checker (`code_index_build.py`) reports violations against these files.
