# AGENTS.md - City Map Poster Generator

This file provides essential information for agentic coding agents working in the maptoposter repository.

## Project Overview

A Python-based web application that generates beautiful, minimalist map posters for any city in the world. Built with Gradio for the web interface, OSMnx for mapping data, and Matplotlib for rendering.

**Tech Stack:**
- Python 3.12+
- Gradio (web UI)
- OSMnx (street network analysis)
- Matplotlib (map rendering)
- GeoPandas (geospatial data)
- Nominatim (geocoding)

## Build/Test/Lint Commands

### Environment Setup
```bash
# Install dependencies with uv (recommended)
uv sync

# Alternative: with pip
pip install -r requirements.txt  # (if available)
```

### Running the Application
```bash
# Start the web interface
uv run python app.py

# Or use the restart script (handles port conflicts)
bash restart.sh

# The application runs on http://localhost:7860
```

### Running Tests
```bash
# Run the main test file
python test_logic.py

# Run individual test functions
python -c "from test_logic import test_china_hierarchy; test_china_hierarchy()"
python -c "from test_logic import test_manual_coordinates; test_manual_coordinates()"
```

### Development Utilities
```bash
# Verify city data integrity
python verify_data.py

# Create map poster directly (CLI)
python create_map_poster.py --city "Beijing" --theme japanese_ink --output-format png
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
import gradio as gr
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
├── app.py                 # Main Gradio web interface
├── create_map_poster.py   # Core poster generation logic
├── cities_data.py         # City/province/district data management
├── test_logic.py          # Test suite for data logic
├── verify_data.py         # Data integrity verification
├── src/maptoposter/       # Package structure (minimal)
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

### Gradio Interface Patterns
```python
def create_interface():
    with gr.Blocks() as interface:
        gr.Markdown("# City Map Poster Generator")
        
        with gr.Row():
            city_dropdown = gr.Dropdown(label="City", choices=[])
            theme_dropdown = gr.Dropdown(label="Theme", choices=[])
        
        generate_btn = gr.Button("Generate Poster")
        output_gallery = gr.Gallery()
        
        # Event handlers
        generate_btn.click(
            fn=generate_poster,
            inputs=[city_dropdown, theme_dropdown],
            outputs=output_gallery
        )
    
    return interface
```

## Testing Guidelines

### Test Structure
- Use simple assertion-based testing (no external testing framework)
- Group related tests in functions (e.g., `test_china_hierarchy()`)
- Test both data integrity and coordinate retrieval
- Include Chinese characters in test data

### Test Execution
```bash
# Run all tests
python test_logic.py

# Expected output for passing tests:
# ✅ Data logic tests passed!
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
- **Code Organization**: Keep the main Gradio interface in `app.py`, core logic in separate modules
- **Dependencies**: The project uses `uv` for dependency management. Lock file is `uv.lock`