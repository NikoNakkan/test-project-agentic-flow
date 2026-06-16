# Theming rules (React)

## Single source of truth

| Asset | Path |
|-------|------|
| Theme tokens | `apps/web-react/src/styles/theme.css` |

**Only `theme.css` may contain** `#`, `rgb()`, `rgba()`, `hsl()`, `hsla()` literals.

Everywhere else (`*.css`, inline `style`, component class rules): use **`var(--token-name)`** only.

## Token layout (`theme.css`)

Organize `:root` in this order:

1. **Raw palette** — `--palette-neutral-*`, `--palette-primary-*`, `--palette-emerald-*`
2. **Semantic colors** — `--color-bg`, `--color-text`, `--color-error`, flow/button/dialog tokens
3. **Spacing** — `--space-1` … `--space-8`
4. **Typography** — `--font-family-sans`, `--font-size-*`, `--line-height-*`
5. **Radius, shadow, z-index** — `--radius-*`, `--shadow-*`, `--z-overlay`, `--z-modal`

## Adding a new color

1. Add palette step in `theme.css` if needed
2. Add semantic token referencing palette
3. Use semantic token in component CSS — never add a new hex in component files

## Agents

- `fe-dev`, `fe-design-navigator` — read [`fe-design-system.md`](../context/fe-design-system.md) for theme path
- Future CI: lint for hex outside `theme.css` (not automated in PoC)
