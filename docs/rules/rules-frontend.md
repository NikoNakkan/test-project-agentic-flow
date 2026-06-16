# Frontend rules (React)

- Exported hooks → row in `docs/context/fe-utils.md`, name `use*`
- Exported components → row in `docs/context/fe-components.md`
- API clients → row in `docs/context/fe-services.md`
- Every export → colocated test file in the same folder (see `rules-testing.md`)

## Design system

- Paths, theme, and tiers → `docs/context/fe-design-system.md`
- UI tasks: run **`fe-design-navigator`** before **`fe-dev`** (plan step or same findings pass)
- **Base components** — `Base<Name>` in `components/Base<Name>/`; listed in fe-design-system **base** table
- **Extending components** — listed in fe-design-system **extending** table with `extends_base` set
- **No extending component without a base** — create/register the base first
- Read order: theme/colors → i18n keys → base components → extending → page shell
- **No magic colors** — see [rules-theming.md](rules-theming.md); tokens only in `theme.css`
- **No UI string literals** — see [rules-i18n.md](rules-i18n.md); use `react-i18next` + `fe-i18n.md`
- **Tests** — fe/be-dev hand off to testing agents; see [test-writing.md](../context/test-writing.md)
