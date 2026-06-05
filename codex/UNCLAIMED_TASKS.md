# Unclaimed Support Tasks

## Priority P0: High Value Tests & Foundation

- [ ] **Task 1:** Create `tests/test_pdf_extractor_real_fixture.py` using `tests/fixtures/sample_textual.pdf`. (Awaiting valid PDF fixture)
- [ ] **Task 6:** Create `tests/test_dashboard.py` for JSON health output and placeholder endpoints.

## Priority P1: Environment & Testing Utils

- [ ] **Task 16:** Create `scripts/check_venv_links.sh` to inspect venv/bin/python, pyvenv.cfg, and likely shared-lib issues.
- [ ] **Task 17:** Create `tests/test_environment_docs.py` only if done as a lightweight doc consistency check.
- [ ] **Task 18:** Create `docs/RECOVERY_PLAYBOOK.md` for broken venv, missing Ollama, missing Letta, and missing models.
- [ ] **Task 19:** Create `scripts/check_models.py` for Ollama model availability using configured model names.
- [ ] **Task 20:** Create `scripts/check_paths.py` for vault, vectordb, logs, and watcher directories.

## Priority P2: CLI & Documentation

- [ ] **Task 24:** Create `docs/CLI_USAGE.md` documenting query.py commands and direct legacy usage.
- [ ] **Task 25:** Create `scripts/demo_query_usage.md` or `docs/QUERY_EXAMPLES.md` with realistic search examples.
- [ ] **Task 26:** Create `tests/test_query_rendering.py` for output formatting assumptions using mocked results.
- [ ] **Task 27:** Create a small patch proposal in `codex/QUERY_IMPROVEMENTS.md` for future CLI enhancements.
- [ ] **Task 39:** Create `docs/INGESTION_FLOW.md` with the exact step order and failure points.
- [ ] **Task 40:** Create `docs/PRIVACY_MODEL.md` documenting public vs private table routing.
- [ ] **Task 41:** Create `docs/VECTOR_STORE_NOTES.md` explaining schema, FTS, RRF, and scoring.
- [ ] **Task 42:** Create `docs/WATCHER_BEHAVIOR.md` covering debounce, duplicate hashes, and retry semantics.

## Priority P3: Hygiene & Catalogs

- [ ] **Task 72:** Create `scripts/check_doc_links.py` to find broken internal markdown references.
- [ ] **Task 73:** Create `tests/test_repo_compliance.py` for module-header/docstring rules.
- [ ] **Task 74:** Create `docs/REPO_CONVENTIONS.md` summarizing style and structure.
