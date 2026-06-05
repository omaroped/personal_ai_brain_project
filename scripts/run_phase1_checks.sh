#!/bin/bash
# MODULE: Script to run Phase 1 static checks, compile passes, and safe local validations.

set -e

PROJECT_ROOT="/home/omar/personal_ai_brain_project"
cd "$PROJECT_ROOT"

echo "Step 1: Compile Pass (src/)"
python3 -m compileall src/

echo "Step 2: Compile Pass (tests/)"
python3 -m compileall tests/

echo "Step 3: Syntax Check with flake8 (if available)"
if command -v flake8 >/dev/null 2>&1; then
    flake8 src/ tests/ --count --select=E9,F63,F7,F82 --show-source --statistics
else
    echo "flake8 not found, skipping syntax check."
fi

echo "Step 4: Running Offline-safe Unit Tests"
# Using the list from docs/TESTING.md
source venv/bin/activate
pytest tests/test_foundation.py \
       tests/test_parallel_foundations.py \
       tests/test_privacy_router.py \
       tests/test_ingestion_state.py \
       tests/test_health_checks.py \
       tests/test_logging_utils.py

echo "Phase 1 checks passed successfully."
