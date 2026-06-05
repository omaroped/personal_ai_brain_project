# Merge Notes

## Purpose

Short factual notes from supporting agents about completed bounded tasks.

Format:

```text
## YYYY-MM-DD — Task name
- Files: file1, file2
- Summary: one short sentence
- Assumptions: optional short sentence
- Follow-up: optional short sentence
```

---

## 2026-06-06 — Supporting Agent: Security, Backup, and Dashboard
- Files: `plan/SECURITY.md`, `plan/BACKUP_STRATEGY.md`, `src/api/dashboard.py`
- Summary: Completed remaining P2 supporting tasks including security policy definition, backup strategy design, and a minimal dashboard API skeleton.
- Assumptions: Dashboard and backup scripts will be fleshed out in later phases as core logic matures.
- Follow-up: Lead agent can integrate dashboard endpoints with real ingestion and search state when Phase 1 is complete.

## 2026-06-06 — Supporting Agent: Architecture Documentation
- Files: `plan/ARCHITECTURE.md`
- Summary: Populated the empty architecture document with a system overview, component breakdown, and initial ADRs based on the master plan.
- Assumptions: Architecture aligns with the current foundation implementation (Agent A-J).
- Follow-up: Review ARCHITECTURE.md for alignment as more Phase 1 modules are finalized by the lead.

## 2026-06-06 — Task 19: Create text_normalization.py
- Files: `src/common/text_normalization.py`
- Summary: Implemented reusable text cleaning helpers including whitespace consolidation, newline normalization, and non-printable character removal.
- Assumptions: None.
- Follow-up: Integrate these helpers into the `pdf_extractor` and `chunker` logic.

## 2026-06-06 — Task 18: Create file_types.py
- Files: `src/common/file_types.py`
- Summary: Defined shared constants for supported file extensions and provided validation helpers to ensure consistency across watcher and extractor modules.
- Assumptions: None.
- Follow-up: Refactor existing watcher/extractor code to use these constants during the next lead integration.

## 2026-06-06 — Task 17: Add scripts/benchmark_stub.py
- Files: `scripts/benchmark_stub.py`
- Summary: Created a demonstration script for the project's timing and latency tracking utilities, showing how to measure and summarize function execution time.
- Assumptions: None.
- Follow-up: None.

## 2026-06-06 — Task 16: Add scripts/verify_services.py
- Files: `scripts/verify_services.py`
- Summary: Created a pretty-printed CLI script to check the status of Ollama, Letta, and core data directories using existing health-check utilities.
- Assumptions: Requires `httpx` and `rich` to be installed in the environment.
- Follow-up: None.

## 2026-06-06 — Task 15: Create OPERATIONS.md
- Files: `docs/OPERATIONS.md`
- Summary: Documented local service endpoints, Docker management commands, log locations, and common failure modes with their respective fixes.
- Assumptions: None.
- Follow-up: None.

## 2026-06-06 — Task 14: Create TESTING.md
- Files: `docs/TESTING.md`
- Summary: Created a testing guide with instructions for running pytest, service-dependency breakdown, fixture policy, and environment repair procedures.
- Assumptions: None.
- Follow-up: None.

## 2026-06-06 — Task 13: Fill ARCHITECTURE.md
- Files: `plan/ARCHITECTURE.md`
- Summary: Refined the architecture document with detailed descriptions for configuration, ingestion modules, memory engine tiers, voice pipeline targets, and storage technologies.
- Assumptions: None.
- Follow-up: Review for consistency as implementation details evolve.

## 2026-06-06 — Task 12: Create references fixture
- Files: `tests/fixtures/sample_references_tail.txt`
- Summary: Created a fixture containing a 'References' section to test the extractor's ability to strip bibliographies from academic texts.
- Assumptions: None.
- Follow-up: None.

## 2026-06-06 — Task 11: Create transcript fixture
- Files: `tests/fixtures/sample_transcript.txt`
- Summary: Created a sample transcript fixture with timestamps and speaker labels to test future transcript-specific chunking and ingestion logic.
- Assumptions: None.
- Follow-up: None.

## 2026-06-06 — Task 10: Create scanned PDF fixture plan
- Files: `tests/fixtures/sample_scanned_fixture_plan.md`
- Summary: Documented the procedure for generating a valid scanned-image PDF fixture and defined the expected OCR detection and extraction behavior for the pipeline.
- Assumptions: OCR testing is optional based on system environment (Tesseract availability).
- Follow-up: Generate the binary PDF fixture when an image-processing environment is available.

## 2026-06-06 — Task 9: Create textual PDF fixture
- Files: `tests/fixtures/sample_textual.pdf`
- Summary: Created a minimal valid textual PDF fixture containing "Hello World" to support future extraction unit tests.
- Assumptions: None.
- Follow-up: None.

## 2026-06-06 — Task 8: Create DOCX fixture
- Files: `tests/fixtures/sample_docx.docx`, `tests/fixtures/README.md`
- Summary: Created a placeholder DOCX fixture and updated the README with descriptions for all current fixtures.
- Assumptions: The DOCX is a text-based placeholder for routing tests.
- Follow-up: Replace with a real binary DOCX if complex extraction tests are needed.

## 2026-06-06 — Task 7: Add tests/test_cli_foundation.py
- Files: `tests/test_cli_foundation.py`
- Summary: Added tests for the CLI commands in `query.py`, covering health checks, privacy routing, result counting, and search parameter validation using mocked dependencies.
- Assumptions: None.
- Follow-up: None.

## 2026-06-06 — Task 6: Add tests/test_vector_store.py
- Files: `tests/test_vector_store.py`
- Summary: Added unit tests for the vector store wrapper, covering table initialization, schema validation, search result shaping, and RRF merging logic.
- Assumptions: Mocking the embedder to avoid Ollama dependency.
- Follow-up: None.

## 2026-06-06 — Task 5: Add tests/test_privacy_router.py
- Files: `tests/test_privacy_router.py`
- Summary: Added unit tests for privacy routing logic, including domain normalization, cloud eligibility checks, and automatic fallback behaviors.
- Assumptions: Mocking config values for predictable testing.
- Follow-up: None.

## 2026-06-06 — Task 4: Add tests/test_ingestion_state.py
- Files: `tests/test_ingestion_state.py`
- Summary: Added comprehensive unit tests for the ingestion state module, covering hashing stability, record lifecycle, and duplicate detection.
- Assumptions: Isolated from real project database using pytest fixtures.
- Follow-up: None.

## 2026-06-06 — Task 3: Create tests/conftest.py
- Files: `tests/conftest.py`
- Summary: Added shared pytest fixtures for temporary data directories, SQLite database paths, and dummy file helpers to enable isolated module testing.
- Assumptions: None.
- Follow-up: None.

## 2026-06-06 — Task 2: Repair Python environment
- Files: `docs/ENVIRONMENT_FIX.md`, `scripts/rebuild_venv.sh`
- Summary: Documented the Python 3.11 library error root cause and provided a safe rebuild script to transition the environment to Python 3.10 as per CLAUDE.md.
- Assumptions: User has python3-venv installed on Ubuntu 22.04.
- Follow-up: User or orchestration agent should run `scripts/rebuild_venv.sh` to unblock tests.

## 2026-06-06 — Task 1: Create .gitignore
- Files: `.gitignore`
- Summary: Created a standard Python .gitignore file with project-specific exclusions for data/vectordb and ingestion indexes.
- Assumptions: None.
- Follow-up: None.

## 2026-06-06 — Lead agent Phase 1 foundation and ingestion start
- Files: `README.md`, `.env.example`, `config.py`, `docker/docker-compose.yml`, `src/common/*`, `src/api/privacy_router.py`, `src/ingestion/state.py`, `src/ingestion/vector_store.py`, `src/ingestion/watcher.py`, `src/ingestion/pdf_extractor.py`, `query.py`, `tests/test_foundation.py`, `tests/test_parallel_foundations.py`, `tests/test_phase1.py`
- Summary: Added shared foundation, privacy routing, vector bootstrap, watcher, and initial PDF extraction.
- Assumptions: Full pytest execution is blocked until the local Python environment is repaired.
- Follow-up: Lead agent continues with `src/ingestion/chunker.py`, `src/ingestion/embedder.py`, and `src/ingestion/pipeline.py`.

## 2026-06-06 — Lead agent Phase 1 integration hardening
- Files: `src/ingestion/chunker.py`, `src/ingestion/embedder.py`, `src/ingestion/vector_store.py`, `src/ingestion/pipeline.py`, `src/ingestion/watcher.py`, `query.py`, `requirements.txt`, `tests/test_foundation.py`, `tests/test_parallel_foundations.py`, `tests/test_phase1.py`, `docs/ENVIRONMENT_FIX.md`, `codex/AGENT_ASSIGNMENTS.md`
- Summary: Completed the core ingestion path, added named Phase 1 acceptance tests, fixed watcher pending-state cleanup, normalized retrieval scoring, added legacy-compatible CLI invocation, and cleaned project-owned Python compliance gaps.
- Assumptions: Full runtime validation still depends on repairing the local Python environment and reaching a live Ollama service.
- Follow-up: Run the actual pytest suite and live retrieval flow once the environment blocker is removed.
