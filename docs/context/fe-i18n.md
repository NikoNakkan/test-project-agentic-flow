# Frontend i18n (react-i18next)

**Human-maintained.** Namespace keys and purpose. Locale files live under `apps/web-react/src/i18n/locales/`.

| namespace | key | purpose | used_in |
|-----------|-----|---------|---------|

**Adding a key:** update `en.json` + stub in `el.json` → add row here with `purpose`.

## Locale files

| File | Role |
|------|------|
| `apps/web-react/src/i18n/locales/en.json` | Source |
| `apps/web-react/src/i18n/locales/el.json` | Greek stub |

## Namespace layout (`en.json`)

```json
{
  "app": { "preferences": { "title": "..." }, "toggle": { "on": "...", "off": "..." } },
  "time": { "now": "...", "saveButton": "..." },
  "common": { "toggle": { "true": "...", "false": "..." } }
}
```
