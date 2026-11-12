#!/usr/bin/env python3
"""WCAG 2.1 contrast checker for Appleish tokens.

Loads ``tokens.json``, asserts dark/light key parity, then checks that every
semantic text/background colour pair passes WCAG contrast thresholds.

Exits 0 printing ``contrast OK (n pairs)``; exits 1 listing failing pairs.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.tokens import load  # noqa: E402


# ---------------------------------------------------------------------- colour math

_HEX = re.compile(r"^#([0-9a-fA-F]{2})([0-9a-fA-F]{2})([0-9a-fA-F]{2})$")
_RGBA = re.compile(
    r"rgba\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*([0-9.]+)\s*\)"
)


def _parse_rgb(value: str) -> tuple[float, float, float, float]:
    """Return (r, g, b, a) in 0..1 from a hex or rgba() string."""
    m = _HEX.match(value)
    if m:
        return tuple(int(g, 16) / 255.0 for g in m.groups()) + (1.0,)
    m = _RGBA.match(value)
    if m:
        r, g, b = (int(x) / 255.0 for x in m.groups()[:3])
        a = float(m.group(4))
        return r, g, b, a
    raise ValueError(f"Cannot parse colour: {value!r}")


def _composite(fg: tuple[float, float, float, float],
               bg: tuple[float, float, float, float]) -> tuple[float, float, float]:
    """Composite foreground colour (with alpha) over background (with alpha)."""
    fr, fg_, fb, fa = fg
    br, bg_, bb, ba = bg
    # Result alpha
    out_a = fa + ba * (1.0 - fa)
    if out_a <= 0:
        return 0.0, 0.0, 0.0
    out_r = (fr * fa + br * ba * (1.0 - fa)) / out_a
    out_g = (fg_ * fa + bg_ * ba * (1.0 - fa)) / out_a
    out_b = (fb * fa + bb * ba * (1.0 - fa)) / out_a
    return out_r, out_g, out_b


def _linearise(c: float) -> float:
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def _luminance(rgb: tuple[float, float, float]) -> float:
    r, g, b = rgb
    return 0.2126 * _linearise(r) + 0.7152 * _linearise(g) + 0.0722 * _linearise(b)


def _contrast(fg_rgb: tuple[float, float, float],
              bg_rgb: tuple[float, float, float]) -> float:
    l1 = _luminance(fg_rgb)
    l2 = _luminance(bg_rgb)
    light, dark = max(l1, l2), min(l1, l2)
    return (light + 0.05) / (dark + 0.05)


# ---------------------------------------------------------------------- check pairs

# (foreground_role, background_role, min_ratio, warn_only)
PAIRS = [
    ("label", "canvas", 4.5, False),
    ("label", "card", 4.5, False),
    ("label_secondary", "canvas", 4.5, False),
    ("label_tertiary", "canvas", 3.0, False),
    ("label_quaternary", "card", 3.0, True),
    ("link", "canvas", 4.5, False),
    ("#ffffff", "accent", 4.5, False),
    ("#ffffff", "destructive", 4.5, False),
    # label over selection_wash composited over canvas
    ("label", None, 4.5, False, "selection_over_canvas"),
]


def check(mode: str) -> list[tuple[str, float, float, bool]]:
    """Return list of (pair_name, ratio, threshold, passed) for one mode."""
    tokens = load(mode)
    colors = tokens["colors"]

    results: list[tuple[str, float, float, bool]] = []

    def resolve(role_or_hex: str, backdrop: tuple[float, float, float] | None = None):
        if role_or_hex.startswith("#"):
            fg = _parse_rgb(role_or_hex)
        else:
            fg = _parse_rgb(colors[role_or_hex])
        if backdrop is None:
            return fg[:3]
        return _composite(fg, (*backdrop, 1.0))

    canvas = _parse_rgb(colors["canvas"])
    card = _parse_rgb(colors["card"])
    accent = _parse_rgb(colors["accent"])
    destructive = _parse_rgb(colors["destructive"])

    for pair in PAIRS:
        fg_role, bg_role, threshold, warn_only = pair[:4]
        special = pair[4] if len(pair) > 4 else None

        if special == "selection_over_canvas":
            sw = _parse_rgb(colors["selection_wash"])
            wash_over_canvas = _composite(sw, canvas)  # canvas is already (r,g,b,a)
            fg_rgb = _parse_rgb(colors["label"])
            # Composite label over the wash-over-canvas
            final = _composite(fg_rgb, (*wash_over_canvas, 1.0))
            ratio = _contrast(final, canvas[:3])
            name = f"{mode}: label on selection_wash over canvas"
        else:
            bg = _parse_rgb(colors[bg_role])
            fg_rgb = resolve(fg_role, bg[:3])
            ratio = _contrast(fg_rgb, bg[:3])
            name = f"{mode}: {fg_role} on {bg_role}"

        passed = ratio >= threshold
        results.append((name, ratio, threshold, passed))

    return results


def main() -> int:
    dark_results = check("dark")
    light_results = check("light")

    # Key parity check
    dark_keys = set(load("dark")["colors"].keys())
    light_keys = set(load("light")["colors"].keys())
    if dark_keys != light_keys:
        missing_in_light = dark_keys - light_keys
        missing_in_dark = light_keys - dark_keys
        print(f"FAIL: colour key mismatch between modes")
        if missing_in_light:
            print(f"  missing in light: {sorted(missing_in_light)}")
        if missing_in_dark:
            print(f"  missing in dark: {sorted(missing_in_dark)}")
        return 1

    all_results = dark_results + light_results
    failures = [r for r in all_results if not r[3] and not _warn_only(r[0])]
    warnings = [r for r in all_results if not r[3] and _warn_only(r[0])]

    for name, ratio, threshold, passed in all_results:
        status = "PASS" if passed else ("WARN" if _warn_only(name) else "FAIL")
        tag = " (warn-only)" if _warn_only(name) else ""
        print(f"  [{status}] {name}: {ratio:.2f}:1 (need {threshold:.1f}:1){tag}")

    if failures:
        print(f"\nFAIL: {len(failures)} contrast pair(s) below threshold")
        return 1

    if warnings:
        print(f"\nWARN: {len(warnings)} pair(s) below threshold (warn-only, acceptable)")

    print(f"\ncontrast OK ({len(all_results)} pairs)")
    return 0


def _warn_only(name: str) -> bool:
    return "label_quaternary" in name


if __name__ == "__main__":
    sys.exit(main())
