# Appleish — Design System

Appleish is a GTK 3 + GTK 4 theme that applies Apple HIG conventions —
an 8pt spacing grid, a fixed type scale, a small radius vocabulary and
semantic colour roles — to every GTK application on the system.

> See [`spacing.md`](spacing.md) for the element-by-element spacing table
> and the type/radius scales.

## Single source of truth: `tokens.json`

Every number and colour in the generated CSS comes from `tokens.json`.
Generators never inline magic numbers:

```
tokens.json ─┬─> tools/generate_gtk3.py ─> theme/gtk-3.0/gtk.css (+ gtk-light.css)
             └─> tools/generate_gtk4.py ─> theme/gtk-4.0/gtk.css (+ gtk-light.css)
```

Edit tokens, run `make build`, run `make install`. Never hand-edit the
generated CSS.

## Spacing

8pt grid. Allowed values (px): `4, 8, 12, 16, 20, 24, 32, 40, 48, 56, 64`.
The only sub-unit value is 4px for tight internal gaps. Full table in
[`spacing.md`](spacing.md).

## Radius scale

| Token | Value | Use |
|-------|-------|-----|
| sm | 4px | check / radio boxes |
| md | 8px | buttons, entries, list rows, tabs |
| lg | 12px | cards, popovers, frames |
| xl | 16px | sheets, large cards |
| xxl | 24px | — |
| pill | 9999px | switches, sliders, pill buttons |

## Typography scale + Apple HIG mapping

| Token | Size | Weight | HIG name |
|-------|------|--------|----------|
| caption | 11px | 400 | Caption 1 |
| footnote | 13px | 400 | Footnote |
| body | 15px | 400 | Body |
| body_emphasis | 15px | 600 | Body (emphasised) |
| callout | 17px | 500 | Callout |
| title3 | 20px | 600 | Title 3 |
| title2 | 24px | 600 | Title 2 |
| title1 | 28px | 700 | Title 1 |
| large_title | 34px | 700 | Large Title |
| control | 13px | 500 | Control / button label |
| tabular | 13px | 400 | Tabular numerals (tnum) |

Font stack: `SF Pro Text`, `SF Pro Display`, `Inter`, `Adwaita Sans`,
`Noto Sans`, `sans-serif`. If SF Pro is not installed the browser/GTK
falls back in that order.

## Colour roles

Roles are semantic, so components never name raw colours. Both modes carry
the same key set (enforced by `make verify`).

| Role | Dark | Light | Used for |
|------|------|-------|----------|
| canvas | `#16161a` | `#f5f5f7` | window background |
| card | `#1f1f24` | `#ffffff` | frames, cards, headerbar |
| card_elevated | `#2a2a31` | `#ffffff` | popovers, tooltips, menus |
| control | rgba(255,255,255,.06) | rgba(0,0,0,.05) | button/entry rest |
| control_hover | rgba(255,255,255,.12) | rgba(0,0,0,.08) | hover |
| control_pressed | rgba(255,255,255,.18) | rgba(0,0,0,.13) | active, trough |
| separator | rgba(255,255,255,.08) | rgba(0,0,0,.10) | hairlines, borders |
| focus_ring | `#0a84ff` | `#007aff` | focus outline |
| label | `#ffffff` | `#1d1d1f` | primary text |
| label_secondary | 0.78 alpha | 0.72 alpha | dim labels |
| label_tertiary | 0.55 alpha | 0.50 alpha | muted metadata |
| label_quaternary | 0.38 alpha | 0.35 alpha | disabled-ish text |
| link | `#0088ff` | `#0060cc` | hyperlinks |
| accent | `#0077cc` | `#0060cc` | primary action fill |
| accent_hover | `#3f97ff` | `#0052a3` | primary action hover |
| destructive | `#d93025` | `#d70015` | destructive action |
| success | `#32d74b` | `#28a745` | success |
| warning | `#ff9f0a` | `#c9740a` | warning |
| selection_wash | accent @ 0.16 | accent @ 0.14 | selected rows |
| shadow | rgba(0,0,0,.35) | rgba(0,0,0,.14) | card shadow |
| shadow_strong | rgba(0,0,0,.55) | rgba(0,0,0,.22) | popover shadow |

Contrast is enforced by `tools/check_contrast.py` (WCAG 2.1):
text pairs ≥ 4.5:1, muted text ≥ 3.0:1, white-on-accent ≥ 4.5:1.

## Motion tokens

| Token | Value | Use |
|-------|-------|-----|
| fast | 120ms ease-out | hover/press feedback |
| base | 180ms ease-in-out | selection, tabs |
| slow | 260ms ease-in-out | elevation changes |
| retint | 350ms ease-in-out | accent retint (runtime layer) |

GTK CSS `transition` supports colour, background, box-shadow, opacity and
min/max sizes. It does **not** support `transform`, so no scale/slide
animations are used.

## Elevation

| Token | Value |
|-------|-------|
| card | `0px 2px 8px <shadow>` |
| floating | `0px 4px 14px <shadow>` |
| popover | `0px 8px 24px <shadow_strong>` |

`<shadow>` / `<shadow_strong>` are substituted per mode by the token loader.

## GTK3 vs GTK4 implementation

| Aspect | GTK3 | GTK4 |
|--------|------|------|
| Tokens | inlined literal values | `--*` custom properties in `:root` |
| Light mode | separate `gtk-light.css` | `@media (prefers-color-scheme: light)` block + `gtk-light.css` |
| Tabs | `notebook header tab` | `notebook > header > tabs > tab` |
| Popover | `popover, popover.background` | `popover > contents`, `popover.background` |
| Lists | `list row`, `treeview` | + `columnview`, `gridview`, `listview` |
| Menus | `menuitem` | `modelbutton`, `button.model` |
| Window buttons | — | `windowcontrols button` |
| Forbidden | `var()`, `@media` | `transform`/`filter`/`overflow` (unimplemented) |

The GTK3 generator cannot emit custom properties (GTK 3.24 does not
support them), which is why its file repeats literal values.

## Customising

1. Edit `tokens.json` (colours, spacing, radius, typography, motion).
2. `make build` — regenerate all four CSS files.
3. `make verify` — structural, spacing, typography, contrast and runtime
   parse checks.
4. `make install` — copy into `~/.local/share/themes/Appleish/`.

Optional per-app runtime accent (GTK3 only):

```
python3 tools/ambient_accent.py '#0077cc' --print   # inspect CSS
python3 tools/ambient_accent.py '#0077cc' --apply   # 2s demo window
```

The ambient layer tints selection, focus, primary buttons, progress and
the active tab underline. It never changes window/card backgrounds.

## Known limits

- **No blur.** GTK CSS has no `backdrop-filter`; translucency/blur is a
  compositor concern (e.g. Hyprland blur rules).
- **No transforms.** No scale/slide/spring animations — only colour,
  shadow, opacity and size transitions.
- **Qt/Electron apps are unaffected.** They do not read GTK CSS; use
  `qt5ct`/`qt6ct` + Kvantum, or app-level overrides.
- **Icon and cursor themes are out of scope.** `index.theme` points at
  `Adwaita` icons/cursors; pair with your preferred icon set separately.
- **Apps with hardcoded CSS** (some Electron/Flutter apps) may ignore
  parts of the theme; no theme can override those.
- **High-contrast / a11y modes** are inherited from Adwaita and not
  re-implemented here.
- **GTK3 font rendering** of variable fonts may differ slightly from GTK4;
  sizes are fixed in px so layouts stay aligned.

## Repository layout

```
tokens.json               design tokens (only source of truth)
tools/tokens.py           token loader + font stack + shadows
tools/generate_gtk3.py    GTK3 CSS generator
tools/generate_gtk4.py    GTK4 CSS generator
tools/check_contrast.py   WCAG 2.1 contrast checker
tools/ambient_accent.py   optional runtime accent layer (GTK3)
theme/index.theme         metatheme metadata
theme/gtk-3.0/            gtk.css (dark) + gtk-light.css
theme/gtk-4.0/            gtk.css (dark + @media light) + gtk-light.css
scripts/verify.py         make verify
install.sh / uninstall.sh user-theme install / removal
docs/                     this file + spacing.md
```
