# i18n rules (React)

## Stack

**react-i18next** — all user-facing copy in locale JSON files.

| Path | Role |
|------|------|
| `apps/web-react/src/i18n/index.ts` | `i18n.init`, resources, default namespace |
| `apps/web-react/src/i18n/locales/en.json` | Source locale (complete) |
| `apps/web-react/src/i18n/locales/el.json` | Additional locales (stub or translated) |

Wire `import './i18n'` in app entry (`main.tsx`) before render.

## Rules

- **No user-facing string literals** in JSX/TSX — use `useTranslation('namespace')` + `t('key')`
- Applies to: labels, titles, `aria-label`, `placeholder`, error messages, button text
- New copy: add key to `en.json` + stub in other locale files; register row in [`fe-i18n.md`](../context/fe-i18n.md)
- Key shape: `namespace.section.key` (e.g. `app.toggle.on`)

## Components

```tsx
const { t } = useTranslation('app');
<button>{t('toggle.on')}</button>
```

## Tests

- Prefer `i18n.t('namespace:key')` for expected text, or render with test i18n instance
- Avoid hardcoded locale strings in assertions when a key exists

## Agents

- `fe-dev` — read `fe-i18n.md` before adding UI copy
- `fe-testing-agent` — align test expectations with locale keys
