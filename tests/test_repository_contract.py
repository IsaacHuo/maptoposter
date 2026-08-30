from __future__ import annotations

import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_gradio_product_path_is_removed() -> None:
    """The retired Gradio UI must not return as a runtime or optional dependency."""
    assert not (ROOT / "app_gradio.py").exists()
    assert not list((ROOT / "legacy").glob("*.py"))

    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    dependency_text = "\n".join(project["project"].get("dependencies", []))
    optional_text = repr(project["project"].get("optional-dependencies", {}))
    assert "gradio" not in dependency_text.lower()
    assert "gradio" not in optional_text.lower()


def test_hugging_face_docker_contract() -> None:
    """The repository must remain directly deployable as the production Docker Space."""
    readme = (ROOT / "README.md").read_text(encoding="utf-8-sig")
    assert readme.startswith("---\n")
    metadata = readme.split("---\n", 2)[1]
    assert "sdk: docker" in metadata
    assert "app_port: 7860" in metadata
    assert "python_version: 3.12" in metadata
    assert "sdk_version:" not in metadata
    assert "app_file:" not in metadata

    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")
    assert "node:22-bookworm-slim AS frontend-builder" in dockerfile
    assert "python:3.12-slim-bookworm AS runtime" in dockerfile
    assert "COPY --from=ghcr.io/astral-sh/uv:0.12.7 /uv /uvx /bin/" in dockerfile
    assert "MAPTOPOSTER_PROJECT_ROOT=/app" in dockerfile
    assert "MAPTOPOSTER_FONTS_DIR=/app/fonts" in dockerfile
    assert "USER 1000:1000" in dockerfile
    assert '"--port", "7860"' in dockerfile
    assert '"--workers", "1"' in dockerfile


def test_main_release_contract() -> None:
    """A validated main build must be the only path that publishes the Space."""
    attributes = (ROOT / ".gitattributes").read_text(encoding="utf-8")
    assert "fonts/HYWenRunSongYunU.ttf filter=lfs" in attributes

    workflow = (ROOT / ".github/workflows/publish-hugging-face.yml").read_text(encoding="utf-8")
    assert "branches: [main]" in workflow
    assert "needs: validate" in workflow
    assert "huggingface/hub-sync@v0.1.0" in workflow
    assert "huggingface_repo_id: isaachwf/MapToPoster" in workflow
    assert "hf_token: ${{ secrets.HF_TOKEN }}" in workflow
    assert "space_sdk: docker" in workflow
