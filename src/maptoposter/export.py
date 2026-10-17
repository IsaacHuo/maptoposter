"""Export naming and artifact helpers."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from .models import OutputFormat
from .paths import POSTERS_DIR
from .typography import safe_ascii_slug, safe_slug


def ascii_download_filename(filename: str, fallback: str = "map-poster") -> str:
    """Return an ASCII-only filename that preserves the original extension.

    HTTP header values must be Latin-1 encodable; non-ASCII poster names are
    reduced to their ASCII parts for the ``filename=`` fallback.
    """
    path = Path(filename)
    return f"{safe_ascii_slug(path.stem, fallback=fallback)}{path.suffix}"


def generate_output_filename(
    place: str,
    style_id: str,
    output_format: OutputFormat | str,
    directory: str | Path = POSTERS_DIR,
    *,
    include_time: bool = True,
) -> str:
    """Return a readable, collision-resistant poster filename."""
    output_dir = Path(directory)
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S" if include_time else "%Y%m%d")
    extension = OutputFormat(output_format).value
    filename = f"{safe_slug(place)}-{safe_slug(style_id)}-{timestamp}.{extension}"
    return str(output_dir / filename)
