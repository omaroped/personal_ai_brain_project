#!/bin/bash
# Run static Phase 1 checks that are safe even when the local runtime is incomplete.

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "== Phase 1 static checks =="

echo "-- Python compile pass"
python3 -m py_compile \
  query.py \
  config.py \
  src/common/*.py \
  src/api/*.py \
  src/ingestion/*.py \
  src/memory/*.py \
  tests/test_foundation.py \
  tests/test_parallel_foundations.py \
  tests/test_phase1.py \
  tests/test_chunker.py \
  tests/test_ingestion_state.py \
  tests/test_privacy_router.py \
  tests/test_vector_store.py \
  tests/test_query_cli.py \
  tests/test_query_count_command.py \
  tests/test_query_legacy_mode.py \
  tests/test_query_route_command.py \
  tests/test_health_checks.py \
  tests/test_logging_utils.py \
  tests/test_cli_foundation.py

echo "-- Module header check"
python3 scripts/check_module_headers.py

echo "-- Function docstring check"
python3 scripts/check_docstrings.py

if command -v pytest >/dev/null 2>&1; then
  echo "-- Offline pytest subset"
  ./scripts/run_unit_subset.sh
else
  echo "-- Offline pytest subset skipped: pytest not installed in current interpreter"
fi

echo "Phase 1 static checks completed."
