# Implementation Start

## Practical Reading

If starting development now, the smallest authoritative reading set should be:

1. `CLAUDE.md`
2. `STATUS.md`
3. `specs/phase1_vault.md`
4. `ERRORS.md`

Everything else is supporting material.

## What Phase 1 Really Needs First

Before watcher, extractor, or embeddings, create the project foundation:

1. `requirements.txt`
2. `.env.example`
3. `config.py`
4. package/module init structure if needed
5. test scaffold

Without those, the phase tasks are conceptually ordered but operationally blocked.

## Recommended Build Order

### Step 0: Bootstrap

- Create `requirements.txt` with only Phase 1 dependencies.
- Create `.env.example` for configurable paths and local services.
- Create `config.py` for all path constants and runtime settings.
- Decide whether this is a package-based project or a loose-script project.

Recommended direction:
- package-based Python project with `src/` as the implementation root.

### Step 1: Deduplication and state

Build:
- file hashing utility
- SQLite ingestion state store

Reason:
- watcher behavior depends on deduplication and event suppression.

### Step 2: Extraction

Build:
- PDF extractor
- text/markdown/docx readers
- scanned PDF detector

### Step 3: Chunking

Build:
- structural splitting
- recursive splitting
- metadata shaping
- domain tagging

### Step 4: Embeddings and storage

Build:
- Ollama embedding client
- LanceDB schema setup
- writer lock
- hybrid retrieval

### Step 5: Pipeline and CLI

Build:
- ingestion pipeline
- file watcher worker integration
- `query.py`
- acceptance tests

## Codex Corrections

### Correction 1

Do not start by writing watcher code first.

Reason:
- watcher code is only the trigger layer.
- the actual foundation is config, state tracking, extraction, and storage contracts.

### Correction 2

Keep Phase 1 narrowly focused.

Do not mix in:
- Letta runtime,
- cloud model routing,
- voice loop concerns,
- proactive agent logic.

Those belong to later phases and will distract from validating the vault.

### Correction 3

Turn acceptance criteria into real tests early.

The current repo mentions tests, but the test files do not exist yet. That should change as soon as the first implementation files appear.

## Recommended Immediate Deliverables

The first coding session should ideally produce:

- `requirements.txt`
- `.env.example`
- `config.py`
- `src/ingestion/__init__.py`
- `src/ingestion/state.py`
- `tests/test_phase1.py`

That would convert the repository from planning-only to implementation-started.

## Final Recommendation

Yes, this project is buildable.

The right approach is:
- preserve the existing vision,
- reduce the number of active source documents during implementation,
- start with Phase 1 infrastructure,
- use `codex/` as the clean execution planning layer until the main repo is ready to be consolidated.
