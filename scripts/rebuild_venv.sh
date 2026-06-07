#!/bin/bash
# MODULE: Script to rebuild the Python virtual environment to fix library/path issues.

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="$PROJECT_ROOT/venv"

echo "Stopping services if running..."
# Add commands to stop watcher if applicable

echo "Removing old virtual environment at $VENV_DIR..."
rm -rf "$VENV_DIR"

echo "Creating new virtual environment with Python 3.10..."
python3 -m venv "$VENV_DIR"

echo "Activating venv and installing requirements..."
source "$VENV_DIR/bin/activate"

pip install --upgrade pip
if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
    pip install -r "$PROJECT_ROOT/requirements.txt"
else
    echo "Warning: requirements.txt not found at $PROJECT_ROOT"
fi

echo "Environment rebuild complete."
echo "Run 'source venv/bin/activate' to start."
