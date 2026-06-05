# Unclaimed Support Tasks

## Priority P0: High Value Tests & Foundation

- [ ] **Task 1:** Create `tests/test_pdf_extractor_real_fixture.py` using `tests/fixtures/sample_textual.pdf`.
- [ ] **Task 2:** Create `tests/test_chunker.py` for section splitting, overlap behavior, and domain detection.
- [ ] **Task 3:** Create `tests/test_embedder.py` for retry logic, warmup behavior, blank input, and batch fallback.
- [ ] **Task 4:** Create `tests/test_pipeline.py` for directory ingest, error append behavior, private/public routing, and skip cases.
- [ ] **Task 5:** Create `tests/test_watcher.py` for pending clearing, duplicate handling, and extension filtering.
- [ ] **Task 6:** Create `tests/test_dashboard.py` for JSON health output and placeholder endpoints.
- [ ] **Task 7:** Create `tests/test_file_types.py` for `is_allowed_file()` and `get_file_type_label()`.
- [ ] **Task 8:** Create `tests/test_text_normalization.py` for whitespace cleanup, newline normalization, and printable filtering.

## Priority P1: Environment & Testing Utils

- [ ] **Task 11:** Create `scripts/run_phase1_checks.sh` to run static checks, compile passes, and any safe local validations.
- [ ] **Task 12:** Create `scripts/run_unit_subset.sh` that runs only tests that do not require Ollama or Docker.
- [ ] **Task 13:** Improve `docs/TESTING.md` with a table of test categories: offline, Ollama-required, Docker-required.
- [ ] **Task 14:** Create `docs/ENVIRONMENT_MATRIX.md` comparing current broken venv, system python3, and intended runtime.
- [ ] **Task 15:** Create `scripts/print_python_env.py` to print interpreter path, version, site-packages, and env vars.

## Priority P2: CLI & Documentation

- [ ] **Task 21:** Create `tests/test_query_legacy_mode.py` for `python query.py "question"` argument parsing behavior.
- [ ] **Task 22:** Create `tests/test_query_count_command.py` for `count --table ...`.
- [ ] **Task 23:** Create `tests/test_query_route_command.py` for route output and validation.
- [ ] **Task 39:** Create `docs/INGESTION_FLOW.md` with the exact step order and failure points.
- [ ] **Task 40:** Create `docs/PRIVACY_MODEL.md` documenting public vs private table routing.
- [ ] **Task 41:** Create `docs/VECTOR_STORE_NOTES.md` explaining schema, FTS, RRF, and scoring.
- [ ] **Task 42:** Create `docs/WATCHER_BEHAVIOR.md` covering debounce, duplicate hashes, and retry semantics.

## Priority P3: Hygiene & Catalogs

- [ ] **Task 69:** Create `scripts/list_project_modules.py` to enumerate project-owned Python modules excluding `venv/`.
- [ ] **Task 70:** Create `scripts/check_module_headers.py` to enforce `# MODULE:` headers.
- [ ] **Task 71:** Create `scripts/check_docstrings.py` to enforce function docstrings.
- [ ] **Task 77:** Create `codex/RUNTIME_BLOCKERS.md` with current blockers and status.
- [ ] **Task 78:** Create `codex/FIXTURE_CATALOG.md` listing all current fixtures and intended tests.
- [ ] **Task 79:** Create `codex/COMMAND_CATALOG.md` listing useful project scripts and CLI commands.
- [ ] **Task 80:** Create `codex/VERIFICATION_GAPS.md` listing what still cannot be proven until the environment runs.
