#!/bin/bash
echo "Killing all Brain processes..."
fuser -k 8001/tcp &>/dev/null || true
pkill -f "python3 src/api/main.py" || true
pkill -f "python3 src/voice/pipeline.py" || true
echo "Done."
