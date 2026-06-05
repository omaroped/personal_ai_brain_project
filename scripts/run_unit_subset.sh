#!/bin/bash
# Run only tests that do not require Ollama or Docker.

set -e

# Change to project root
PROJECT_ROOT="/home/omar/personal_ai_brain_project"
cd "$PROJECT_ROOT"

# Activate venv if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

echo "Running offline-safe unit tests..."
pytest tests/test_foundation.py \
       tests/test_parallel_foundations.py \
       tests/test_privacy_router.py \
       tests/test_ingestion_state.py \
       tests/test_health_checks.py \
       tests/test_logging_utils.py \
       tests/test_cli_foundation.py \
       tests/test_vector_store.py \
       tests/test_query_cli.py \
       tests/test_query_count_command.py \
       tests/test_query_legacy_mode.py \
       tests/test_query_route_command.py

echo "All offline-safe tests passed."
