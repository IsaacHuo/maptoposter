"""Font loading for poster rendering."""

from __future__ import annotations

from functools import lru_cache

from .paths import FONTS_DIR


@lru_cache(maxsize=1)
def load_fonts() -> dict[str, str] | None:
    """Load known project fonts and return available paths by role."""
    fonts = {
        "en_bold": FONTS_DIR / "GoudyOldStyle-Bold.ttf",
        "en_regular": FONTS_DIR / "GoudyOldStyle-Regular.ttf",
        "cn": FONTS_DIR / "HYWenRunSongYunU.ttf",
    }

    available_fonts: dict[str, str] = {}
    for key, path in fonts.items():
        if path.exists():
            available_fonts[key] = str(path)
        else:
            print(f"⚠ Font not found: {path}")

    return available_fonts or None
