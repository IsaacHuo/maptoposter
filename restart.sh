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

# Path to python in venv
VENV_PYTHON="./.venv/bin/python"

if [ -f "$VENV_PYTHON" ]; then
    echo "Starting application with virtual environment..."
    $VENV_PYTHON app.py
else
    echo "Virtual environment not found, trying system python..."
    python3 app.py
fi
