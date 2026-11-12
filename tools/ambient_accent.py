#!/usr/bin/env python3
"""Optional runtime accent override for Appleish GTK3 apps.

Injects a screen-level CssProvider at STYLE_PROVIDER_PRIORITY_USER + 1 that
tints only accent-sensitive widgets (selection, focus, primary buttons,
progress, tab underline).  It deliberately does NOT touch window/card
backgrounds — those stay neutral from the static gtk.css base.

GTK4 is intentionally not supported (needs add_provider_for_display).

Usage:
    python3 tools/ambient_accent.py '#0a84ff' --print   # print CSS to stdout
    python3 tools/ambient_accent.py '#0a84ff' --apply   # live demo window
"""

from __future__ import annotations

import re
import sys

_HEX_RE = re.compile(r"^#[0-9a-fA-F]{6}$")


def _parse_hex(hex_str: str) -> tuple[int, int, int]:
    if not _HEX_RE.match(hex_str):
        raise ValueError(f"Expected #RRGGBB, got {hex_str!r}")
    return tuple(int(hex_str[i : i + 2], 16) for i in (1, 3, 5))


def _lighten(color: tuple[int, int, int], amount: float) -> tuple[int, int, int]:
    """Blend ``color`` toward white by ``amount`` (0..1)."""
    return tuple(
        int(c + (255 - c) * amount) for c in color
    )


def _rgb(color: tuple[int, int, int]) -> str:
    return f"rgb({color[0]}, {color[1]}, {color[2]})"


def _rgba(color: tuple[int, int, int], alpha: float) -> str:
    return f"rgba({color[0]}, {color[1]}, {color[2]}, {alpha:.2f})"


def accent_css(accent_hex: str) -> str:
    """Build accent-only CSS rules for the given hex colour.

    Returns a CSS string that styles selection, focus rings, suggested
    actions, progress/scrollbar highlight, and tab underlines.  Does NOT
    style window, .background, card, or any surface colour.
    """
    rgb = _parse_hex(accent_hex)
    hover = _lighten(rgb, 0.14)
    wash = _rgba(rgb, 0.16)

    return f"""/* Ambient accent layer — Appleish ({accent_hex}) */
/* Applied in-process at STYLE_PROVIDER_PRIORITY_USER + 1.  Does not touch
   window/card backgrounds — those stay neutral from the static gtk.css. */

row:selected,
treeview:selected,
row:selected label,
treeview:selected label {{
    background-color: {wash};
    color: #fff;
}}

button:focus,
entry:focus,
scale:focus {{
    outline-color: {_rgb(rgb)};
}}

.suggested-action {{
    background-color: {_rgb(rgb)};
}}

.suggested-action:hover {{
    background-color: {_rgb(hover)};
}}

progressbar progress,
.scale highlight {{
    background-color: {_rgb(rgb)};
}}

notebook header tab:checked {{
    border-bottom-color: {_rgb(rgb)};
}}
"""


class AccentStyler:
    """Owns one screen-level CssProvider for the accent layer."""

    def __init__(self) -> None:
        self._provider = None
        self._screen = None

    def apply(self, accent_hex: str) -> bool:
        """Apply accent colour (GTK3 only). Main thread only."""
        from gi.repository import Gdk, Gtk  # deferred import

        css = accent_css(accent_hex)
        try:
            if self._provider is None:
                screen = Gdk.Screen.get_default()
                if screen is None:
                    return False
                self._provider = Gtk.CssProvider()
                Gtk.StyleContext.add_provider_for_screen(
                    screen, self._provider, Gtk.STYLE_PROVIDER_PRIORITY_USER + 1
                )
                self._screen = screen
            self._provider.load_from_data(css.encode("utf-8"))
            return True
        except Exception as exc:  # noqa: BLE001
            print(f"[Appleish] AccentStyler apply failed: {exc}")
            return False

    def remove(self) -> None:
        from gi.repository import Gdk, Gtk  # deferred import

        if self._provider is not None and self._screen is not None:
            try:
                Gtk.StyleContext.remove_provider_for_screen(
                    self._screen, self._provider
                )
            except Exception:
                pass
        self._provider = None
        self._screen = None


def _demo_window() -> None:
    from gi.repository import Gdk, Gtk  # deferred import

    Gtk.init([])
    styler = AccentStyler()
    styler.apply("#0077cc")

    win = Gtk.Window(title="Appleish Accent Demo")
    win.set_default_size(400, 300)
    win.connect("destroy", lambda *_: Gtk.main_quit())

    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
    box.set_margin_top(12)
    box.set_margin_bottom(12)
    box.set_margin_start(12)
    box.set_margin_end(12)

    label = Gtk.Label(label="Accent layer active — selection, focus, buttons tinted")
    btn = Gtk.Button(label="Suggested action")
    btn.get_style_context().add_class("suggested-action")
    plain = Gtk.Button(label="Plain button")
    entry = Gtk.Entry()
    entry.set_placeholder_text("Focused entry shows accent ring")

    scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
    scale.set_value(50)

    box.append(label)
    box.append(btn)
    box.append(plain)
    box.append(entry)
    box.append(scale)

    win.set_child(box)
    win.show()

    # Auto-destroy after 2 seconds
    GLib = __import__("gi.repository", fromlist=["GLib"]).GLib
    GLib.timeout_add_seconds(2, lambda: (Gtk.main_quit(), False)[0])

    Gtk.main()
    styler.remove()


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python3 tools/ambient_accent.py '#RRGGBB' [--print|--apply]")
        return 2

    accent_hex = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 else "--print"

    if mode == "--print":
        print(accent_css(accent_hex), end="")
        return 0
    if mode == "--apply":
        _demo_window()
        return 0

    print(f"Unknown mode: {mode} (use --print or --apply)", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
