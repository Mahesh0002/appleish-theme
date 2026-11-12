#!/usr/bin/env python3
"""Design-token loader for Appleish.

Every number that ever reaches generated CSS comes from ``tokens.json``.
This module is the single source of truth; generators import *only* from
here and never inline magic numbers.

Structure returned by :func:`load`:

    {
        "spacing":   { "xs": 4, "sm": 8, ... },
        "radius":    { "sm": 4, "md": 8, ... },
        "typography":{ "body": { "size": 15, ... }, ... },
        "colors":    { "canvas": "#16161a", ... },
        "motion":    { "fast": "120ms ease-out", ... },
        "shadows":   { "card": "0px 2px 8px rgba(0,0,0,0.35)", ... },
        "font_families": [ "SF Pro Text", ... ],
        "meta": { "name": "...", "version": "..." }
    }

:func:`ctx` returns short aliases ``s, r, t, c, m, sh, ff`` for use inside
generator f-strings::

    from tools.tokens import ctx
    c = ctx("dark")
    # c["c"]["label"]   -> "#ffffff"
    # c["s"]["lg"]      -> 16
    # c["r"]["md"]      -> 8
"""

from __future__ import annotations

import json
from pathlib import Path

_TOKENS_PATH = Path(__file__).resolve().parent.parent / "tokens.json"


def _load_raw() -> dict:
    with open(_TOKENS_PATH, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _resolve_shadows(elevation: dict, colors: dict) -> dict:
    """Replace ``{shadow}`` / ``{shadow_strong}`` placeholders in elevation
    strings with the actual shadow colour for the active mode."""
    shadow = colors["shadow"]
    shadow_strong = colors["shadow_strong"]
    return {name: value.replace("{shadow}", shadow).replace("{shadow_strong}", shadow_strong)
            for name, value in elevation.items()}


def load(mode: str = "dark") -> dict:
    """Return every token resolved for ``mode`` (``"dark"`` or ``"light"``).

    Raises ``ValueError`` for any other mode, ``KeyError`` (via
    :func:`require_keys`) if a required key is missing from ``tokens.json``.
    """
    if mode not in ("dark", "light"):
        raise ValueError(f"mode must be 'dark' or 'light', got {mode!r}")

    raw = _load_raw()
    colors = raw["colors"][mode]
    elevation = raw["elevation"]

    result = {
        "spacing": raw["spacing"],
        "radius": raw["radius"],
        "typography": raw["typography"],
        "colors": colors,
        "motion": raw["motion"],
        "shadows": _resolve_shadows(elevation, colors),
        "font_families": raw["font_families"],
        "meta": raw["meta"],
    }
    return result


def ctx(mode: str = "dark") -> dict:
    """Short aliases for generator f-strings: ``s, r, t, c, m, sh, ff``."""
    d = load(mode)
    return {
        "s": d["spacing"],
        "r": d["radius"],
        "t": d["typography"],
        "c": d["colors"],
        "m": d["motion"],
        "sh": d["shadows"],
        "ff": d["font_families"],
    }


def font_rule() -> str:
    """Return the ``* { font-family: ...; }`` rule built from ``font_families``."""
    families = ", ".join(f'"{f}"' for f in load()["font_families"])
    return f"* {{ font-family: {families}; }}"


def require_keys(d: dict, keys: list, where: str) -> None:
    """Raise ``KeyError`` listing any key missing from ``d``."""
    missing = [k for k in keys if k not in d]
    if missing:
        raise KeyError(f"{where}: missing keys {missing}")  # noqa: TRY003


if __name__ == "__main__":  # pragma: no cover - smoke test
    d = load("dark")
    l = load("light")
    assert d["colors"]["label"] == "#ffffff"
    assert l["colors"]["label"] == "#1d1d1f"
    assert ctx("dark")["s"]["lg"] == 16
    assert "Adwaita Sans" in font_rule()
    assert d["shadows"]["card"] == "0px 2px 8px rgba(0,0,0,0.35)"
    assert d["shadows"]["popover"] == "0px 8px 24px rgba(0,0,0,0.55)"
    assert d["shadows"]["floating"] == "0px 4px 14px rgba(0,0,0,0.35)"
    print("tokens.py smoke test OK")
