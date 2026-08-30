"""Shared filesystem paths for the MapToPoster project."""

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_DIR = Path(__file__).resolve().parent
RESOURCES_DIR = PACKAGE_DIR / "resources"
THEMES_DIR = Path(os.getenv("MAPTOPOSTER_THEMES_DIR", RESOURCES_DIR / "themes"))
FONTS_DIR = Path(os.getenv("MAPTOPOSTER_FONTS_DIR", PROJECT_ROOT / "fonts"))
POSTERS_DIR = Path(os.getenv("MAPTOPOSTER_OUTPUT_DIR", PROJECT_ROOT / "posters"))
CACHE_DIR = Path(os.getenv("MAPTOPOSTER_CACHE_DIR", PROJECT_ROOT / "cache"))
CHINA_DATA_DIR = Path(os.getenv("MAPTOPOSTER_CHINA_DATA_DIR", RESOURCES_DIR / "china"))
