FROM node:22-bookworm-slim AS frontend-builder

WORKDIR /build/frontend
RUN corepack enable

COPY frontend/package.json frontend/pnpm-lock.yaml ./
RUN corepack pnpm install --frozen-lockfile

COPY frontend/ ./
RUN corepack pnpm build


FROM python:3.12-slim-bookworm AS runtime

COPY --from=ghcr.io/astral-sh/uv:0.12.7 /uv /uvx /bin/

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH" \
    MPLCONFIGDIR=/tmp/matplotlib \
    XDG_CACHE_HOME=/data/.cache \
    MAPTOPOSTER_PROJECT_ROOT=/app \
    MAPTOPOSTER_FONTS_DIR=/app/fonts \
    MAPTOPOSTER_CACHE_DIR=/data/cache \
    MAPTOPOSTER_OUTPUT_DIR=/data/posters \
    MAPTOPOSTER_USER_AGENT="MapToPoster/0.2 (+https://huggingface.co/spaces/isaachwf/MapToPoster)"

WORKDIR /app

COPY pyproject.toml uv.lock README.md ./
COPY src/ ./src/
COPY backend/ ./backend/
COPY app.py create_map_poster.py cities_data.py ./
COPY themes/ ./themes/
COPY fonts/ ./fonts/

RUN uv sync --frozen --no-dev --no-editable \
    && mkdir -p /data/cache /data/posters /data/.cache /tmp/matplotlib \
    && chown -R 1000:1000 /app /data /tmp/matplotlib

COPY --from=frontend-builder --chown=1000:1000 /build/frontend/dist ./frontend/dist

USER 1000:1000
EXPOSE 7860

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "7860", "--workers", "1", "--proxy-headers", "--forwarded-allow-ips", "*"]
