# Appleish Spacing & Radius Scale

## 8pt Grid

All spacing in Appleish derives from a single 8pt base unit. The allowed
spacing values (px) are:

| Token | Value | Use |
|-------|-------|-----|
| xs | 4px | Tight internal padding (buttons, entries, tooltips) |
| sm | 8px | Standard small padding (flowbox children, checkbutton) |
| md | 12px | Standard padding (button horizontal, menu separator) |
| lg | 16px | Standard list row padding, section padding |
| xl | 24px | Larger padding (suggested buttons, entry horizontal) |
| xxl | 32px | Extra padding |
| xxxl | 40px | |
| huge | 48px | |
| section | 64px | Section-level gaps |

The only sub-8px value is **4px (xs)**, used for tight internal gaps. Every
padding/margin/gap declaration in the generated CSS uses one of:
`0, 4, 8, 12, 16, 20, 24, 32, 40, 48, 56, 64`.

## Element Spacing Table

| Element | Padding | Margin | Gap | Min-height |
|---------|---------|--------|-----|------------|
| headerbar | 4px 8px | – | – | 44px |
| button (base) | 4px 16px | – | – | 32px |
| button (suggested/pill) | 8px 24px | – | – | 36px |
| entry / combobox / spinbutton | 4px 12px | – | – | 32px |
| list row / FlowBox row | 8px 16px | – | – | 36px |
| flowboxchild | 8px | – | – | – |
| menuitem | 4px 16px | – | – | 28px |
| notebook tab | 8px 16px | – | – | – |
| popover contents | 4px | – | – | – |
| tooltip | 4px 8px | – | – | – |
| separator | – | 4px 8px | – | 1px |
| checkbutton / radiobutton | 4px 8px | – | – | – |

## Corner Radius Scale

| Token | Value | Used for |
|-------|-------|----------|
| sm | 4px | Check/radio boxes |
| md | 8px | Buttons, entries, list rows, tabs |
| lg | 12px | Cards, popovers, frames |
| xl | 16px | Sheets, large cards |
| xxl | 24px | |
| pill | 9999px | Switches, sliders, scale thumbs, suggested-action buttons |

## Type Scale

| Token | Size | Weight | Apple HIG mapping |
|-------|------|--------|-------------------|
| caption | 11px | 400 | Caption 1 |
| footnote | 13px | 400 | Footnote |
| body | 15px | 400 | Body |
| body_emphasis | 15px | 600 | Body (emphasised) |
| callout | 17px | 500 | Callout |
| title3 | 20px | 600 | Title 3 |
| title2 | 24px | 600 | Title 2 |
| title1 | 28px | 700 | Title 1 |
| large_title | 34px | 700 | Large Title |
| control | 13px | 500 | Button/control text |
| tabular | 13px | 400 | Tabular numerals (tnum) |

All font sizes are set in `px` for pixel-perfect consistency across GTK3
and GTK4 applications. Font family stack:
`SF Pro Text`, `SF Pro Display`, `Inter`, `Adwaita Sans`, `Noto Sans`,
`sans-serif`.
