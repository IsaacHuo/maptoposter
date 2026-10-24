"""Regression tests for the documented command-line usage.

The README and AGENTS docs publish runnable commands. Previously the docs used
``--output-format``, which no parser defined, so argparse rejected the command with
``unrecognized arguments`` before any poster could be generated. These tests pin the
documented argv, the ``--output-format`` alias and the original ``--format``/``-f`` flags.
"""

from __future__ import annotations

import shlex
from pathlib import Path

from create_map_poster import build_parser as build_legacy_parser
from maptoposter.cli import build_parser

ROOT = Path(__file__).resolve().parents[1]


def _documented_argv(command: str, prefix_length: int) -> list[str]:
    """Split a documented command and drop the ``uv run ...`` prefix."""
    argv = shlex.split(command)
    return argv[prefix_length:]


def test_readme_documented_command_parses() -> None:
    """README.md's CLI example must parse verbatim and select the png format."""
    readme = (ROOT / "README.md").read_text(encoding="utf-8-sig")
    command = 'uv run maptoposter --city "Beijing" --theme japanese_ink --output-format png'
    assert command in readme

    args = build_parser().parse_args(_documented_argv(command, 3))
    assert args.city == "Beijing"
    assert args.theme == "japanese_ink"
    assert args.format == "png"


def test_agents_documented_legacy_command_parses() -> None:
    """AGENTS.md's legacy example must parse verbatim, including --city/--country."""
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    command = (
        "uv run python create_map_poster.py --city \"Beijing\" --country \"China\" "
        "--theme japanese_ink --output-format png"
    )
    assert command in agents

    args = build_legacy_parser().parse_args(_documented_argv(command, 4))
    assert args.city == "Beijing"
    assert args.country == "China"
    assert args.theme == "japanese_ink"
    assert args.format == "png"


def test_output_format_alias_maps_to_format_dest() -> None:
    """The alias resolves to the same ``format`` destination for both parsers."""
    assert build_parser().parse_args(["--city", "Paris", "--output-format", "svg"]).format == "svg"
    legacy = build_legacy_parser().parse_args(["--city", "Paris", "-C", "France", "--output-format", "pdf"])
    assert legacy.format == "pdf"


def test_format_flags_remain_available() -> None:
    """Existing --format and -f usage must keep working."""
    assert build_parser().parse_args(["--city", "Paris", "--format", "svg"]).format == "svg"
    assert build_parser().parse_args(["--city", "Paris", "-f", "pdf"]).format == "pdf"
    assert build_legacy_parser().parse_args(["--city", "Paris", "-C", "France", "--format", "svg"]).format == "svg"


def test_help_advertises_output_format_alias() -> None:
    """``--help`` must advertise the documented alias so users can discover it."""
    assert "--output-format" in build_parser().format_help()
    assert "--output-format" in build_legacy_parser().format_help()
