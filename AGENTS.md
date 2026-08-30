# AGENTS.md - City Map Poster Generator

This file provides essential information for agentic coding agents working in the maptoposter repository.

## Project Overview

A Python-based web application that generates beautiful, minimalist map posters for any place in the world. The product UI is React/Vite over FastAPI, while OSMnx and Matplotlib power the map pipeline.

**Tech Stack:**
- Python 3.12+
- React + Vite (primary web UI)
- FastAPI (application/API layer)
- OSMnx (street network analysis)
- Matplotlib (map rendering)
- GeoPandas (geospatial data)
- Nominatim (geocoding)

## Build/Test/Lint Commands

### Environment Setup
```bash
# Install dependencies with uv
uv sync --all-groups
corepack pnpm --dir frontend install --frozen-lockfile
```

### Running the Application
```bash
# Start the API
uv run python app.py

# Start the frontend dev server in another terminal
corepack pnpm --dir frontend dev

# Or use the restart script (handles port conflicts)
bash restart.sh

# Development UI: http://localhost:5173
# Production-style UI/API: http://localhost:7860 after building frontend
```

### Running Tests
```bash
# Run the full pytest suite
uv run pytest

# Run individual test functions
uv run pytest test_logic.py -k "china_hierarchy or manual_coordinates"
```

### Development Utilities
```bash
# Verify city data integrity
uv run python verify_data.py

# Create map poster directly (CLI)
uv run python create_map_poster.py --city "Beijing" --theme japanese_ink --output-format png
```

## Code Style Guidelines

### General Principles
- **Bilingual Support**: All user-facing text should support both English (en) and Chinese (cn)
- **File Encoding**: Use UTF-8 encoding with BOM for Chinese characters: `# -*- coding: utf-8 -*-`
- **Function Documentation**: Use docstrings for all public functions
- **Error Handling**: Provide meaningful error messages in both languages when possible

### Import Organization
```python
# Standard library imports first
import os
import json
import sys
from datetime import datetime

# Third-party imports next
from fastapi import FastAPI
import osmnx as ox
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim

# Local imports last
from cities_data import get_countries, get_provinces, get_cities
from create_map_poster import generate_map_poster
```

### Naming Conventions
- **Files**: `snake_case.py` (e.g., `cities_data.py`, `test_logic.py`)
- **Variables/Functions**: `snake_case` (e.g., `get_available_themes()`, `motorway_color`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `THEMES_DIR`, `LAYER_KEYS`)
- **Classes**: `PascalCase` (rare in this codebase, but follow convention if used)

### Type Hints
```python
def generate_output_filename(city: str, theme_name: str, output_format: str) -> str:
    """Generate unique output filename with city, theme, and datetime."""
    pass

def get_theme_choices(lang: str = "en") -> list[tuple[str, str]]:
    """Return a list of (Display Name, Internal Name) tuples for themes."""
    pass
```

### String Patterns
- **Language Keys**: Use `lang="en"` or `lang="cn"` parameters
- **Layer Constants**: Define parallel arrays for different languages
```python
LAYERS_EN = ["Motorway", "Primary Roads", "Secondary Roads", "Water", "Parks"]
LAYERS_CN = ["高速公路", "主干道", "次干道", "水域", "公园"]
LAYER_KEYS = ["motorway", "primary", "secondary", "water", "parks"]
```

### Data Structures
- **City Hierarchy**: Use tuples for display/internal name pairs: `[("Display Name", "internal_name"), ...]`
- **Theme Files**: JSON format with descriptive names: `{"name": "Theme Name", "bg": "#FFFFFF", ...}`
- **Coordinates**: Use `(lat, lon)` tuple format

## Directory Structure

```
maptoposter/
├── app.py                 # FastAPI + built frontend entry point
├── Dockerfile             # Hugging Face production container
├── create_map_poster.py   # Core poster generation logic
├── cities_data.py         # City/province/district data management
├── test_logic.py          # Test suite for data logic
├── verify_data.py         # Data integrity verification
├── backend/               # FastAPI schemas and endpoints
├── frontend/              # React/Vite editor
├── docs/                  # Deployment and maintenance guides
├── .github/workflows/     # Validation and Space publishing
├── src/maptoposter/       # Typed core, cache, renderer, resources
├── themes/                # JSON theme configuration files
├── fonts/                 # Font files (Chinese and English)
├── posters/               # Generated poster outputs
├── public/                # Static assets and demo images
└── restart.sh            # Development restart script
```

## Common Patterns

### Language Support
```python
def translate(text: str, lang: str = "en") -> str:
    """Simple translation wrapper."""
    translations = {
        "en": {"City": "City", "Theme": "Theme"},
        "cn": {"City": "城市", "Theme": "主题"}
    }
    return translations.get(lang, {}).get(text, text)
```

### File Path Handling
```python
THEMES_DIR = "themes"
FONTS_DIR = "fonts"
POSTERS_DIR = "posters"

# Always check existence
if not os.path.exists(THEMES_DIR):
    return []
```

### FastAPI Endpoint Patterns
```python
@app.get("/api/v1/health")
def health() -> dict[str, str]:
    """Return service readiness and version information."""
    return {"status": "ok", "version": __version__}
```

## Testing Guidelines

### Test Structure
- Use pytest tests with focused fixtures and mocks
- Group related tests in modules/functions (e.g., `test_china_hierarchy()`)
- Test both data integrity and coordinate retrieval
- Include Chinese characters in test data

### Test Execution
```bash
# Run all tests
uv run pytest

# The exact count grows with the maintained suite; require zero failures.
```

## Error Handling

### Common Patterns
```python
# File not found handling
if not os.path.exists(font_path):
    print(f"⚠ Font not found: {font_path}")
    continue

# API error handling
try:
    result = geocoder.geocode(city)
except Exception as e:
    print(f"⚠ Geocoding failed for {city}: {e}")
    return None

# Data validation
assert len(provinces) > 30, f"Expected >30 provinces, found {len(provinces)}"
```

## Performance Considerations

- **Caching**: OSMnx caching is enabled: `ox.settings.use_cache = True`
- **Large Cities**: Be aware that Beijing/Shanghai may have centering issues
- **Small Cities**: Some layers may be empty due to missing OSM data
- **Memory**: Clear matplotlib figures after generation to prevent memory leaks

## Font Management

The project supports both English and Chinese fonts:
- **English**: Goudy Old Style (Regular, Bold)
- **Chinese**: HYWenRunSongYunU.ttf

Always verify font availability before use:
```python
if os.path.exists(font_path):
    font = FontProperties(fname=font_path)
else:
    print(f"⚠ Font not found: {font_path}")
    font = None
```

## Theme Development

Themes are JSON files in the `themes/` directory with the following structure:
```json
{
  "name": "Theme Display Name",
  "description": "Brief description",
  "bg": "#FFFFFF",
  "text": "#000000",
  "water": "#E0E0E0",
  "parks": "#F0F0F0",
  "road_motorway": "#FF0000",
  "road_primary": "#333333",
  "road_secondary": "#666666",
  "road_tertiary": "#999999",
  "road_residential": "#CCCCCC",
  "road_default": "#888888"
}
```

## Development Notes

- **Port Management**: Default port is 7860. Use `restart.sh` to handle conflicts
- **Output Directory**: Generated posters go to `posters/` (auto-created if needed)
- **Debugging**: Use print statements with emoji indicators for important events
- **Code Organization**: Keep API routes in `backend/`, UI code in `frontend/`, and domain logic in `src/maptoposter/`
- **Deployment**: GitHub `main` is mirrored to the Docker Space only after CI validation
- **Dependencies**: The project uses `uv` for dependency management. Lock file is `uv.lock`
