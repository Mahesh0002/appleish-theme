# Appleish — an Apple HIG-inspired GTK 3/4 theme

A system-wide GTK theme that gives every GTK 3 and GTK 4 application the
same spacing rhythm, type scale, corner radii and semantic colours as
macOS — generated from a single `tokens.json`, so the two toolkits can
never drift apart.

Screenshots: _add `docs/screenshots/` captures of gtk3-demo and gtk4-demo
here._

## Requirements

- Linux with GTK 3.24 and/or GTK 4 (tested on Arch Linux + Hyprland/Wayland)
- Python 3.10+ (generators use only the standard library)
- Optional for live verification: `gtk3-demo`, `gtk4-demo`

## Install

```bash
git clone <this repo> ~/Projects/appleish-theme
cd ~/Projects/appleish-theme
make install
```

`make install` regenerates the CSS and copies the theme to
`${XDG_DATA_HOME:-~/.local/share}/themes/Appleish/`, backing up any previous
install. Then select it:

- **GUI:** choose `Appleish` in `nwg-look`, `gnome-tweaks` or
  `lxappearance` (GTK3) — GTK4 apps pick it up from the same theme name.
- **Per-app test:**

  ```bash
  GTK_THEME=Appleish gtk3-demo
  GTK_THEME=Appleish gtk4-demo
  ```

- **Force light mode:** `GTK_THEME=Appleish:light <app>`

## Uninstall

```bash
make uninstall            # removes ~/.local/share/themes/Appleish
bash uninstall.sh --restore   # restore the newest backup instead
```

## Customise

```bash
$EDITOR tokens.json      # colours, spacing, radius, typography, motion
make build               # regenerate all four CSS files
make verify              # structural + spacing + typography + WCAG checks
make install             # install the regenerated theme
```

Spacing lives on an 8pt grid (`4/8/12/16/24/32/40/48/64`), radii come from
`4/8/12/16/24/9999`, and the type scale is `11/13/15/20/24/34` px. See
[`docs/DESIGN.md`](docs/DESIGN.md) and [`docs/spacing.md`](docs/spacing.md).

## Verify

```bash
make verify     # alias: make doctor
make contrast   # WCAG 2.1 contrast report only
```

`make verify` checks: token parsing and dark/light key parity, generated
file markers, GTK3 forbidden constructs (`var()`, `@media`, `transform`,
…), GTK4 custom-property resolution, the spacing/radius grid, the type
scale ordering, WCAG contrast, `index.theme` metadata, an optional runtime
parse with the installed GTK versions, and the presence of the docs.

## Optional: runtime accent colour (GTK3)

```bash
python3 tools/ambient_accent.py '#0077cc' --print   # inspect the CSS
python3 tools/ambient_accent.py '#0077cc' --apply   # 2-second demo window
make accent
```

This tints selection, focus rings, primary buttons, progress and the active
tab underline at runtime without touching window/card backgrounds. GTK4
apps are not covered (they need `add_provider_for_display`).

## Notes

- **Qt and Electron applications are unaffected** — they do not read GTK
  CSS. Use `qt5ct`/`qt6ct` + Kvantum for Qt apps.
- Icon and cursor themes are **out of scope**; `index.theme` points at
  Adwaita icons/cursors. Pair with your preferred icon set separately.
- The theme assumes **no blur**; translucency/blur is handled by the
  compositor (e.g. Hyprland blur rules).
- After a GTK major-version update, re-run `make verify` — the runtime
  parse check will flag any newly rejected CSS.
