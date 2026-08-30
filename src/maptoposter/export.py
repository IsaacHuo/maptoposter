"""Export naming and artifact helpers."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from .models import OutputFormat
from .paths import POSTERS_DIR
from .typography import safe_slug


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
