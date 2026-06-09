"""Shared filesystem paths for the MapToPoster project."""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
THEMES_DIR = PROJECT_ROOT / "themes"
FONTS_DIR = PROJECT_ROOT / "fonts"
POSTERS_DIR = PROJECT_ROOT / "posters"
CHINA_DATA_DIR = PROJECT_ROOT / "public" / "china-city-data"

