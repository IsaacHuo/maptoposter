#!/bin/bash

# Port to check
PORT=7860

echo "Checking for processes on port $PORT..."

# Find and kill processes using the port
PIDS=$(lsof -t -i:$PORT)

if [ -n "$PIDS" ]; then
    echo "Killing processes on port $PORT: $PIDS"
    kill -9 $PIDS
    sleep 1
else
    echo "No processes found on port $PORT."
fi

if ! command -v uv >/dev/null 2>&1; then
    echo "uv is required. Install it from https://docs.astral.sh/uv/"
    exit 1
fi

echo "Starting application with uv..."
uv run python app.py
