# SPEC: Phase 2 — The Memory Engine
# Agent reads this before writing any Phase 2 code.
# This file is the contract. Code must match this spec exactly.

---

## Scope

**What this phase builds:** A persistent memory layer that gives the system continuity
across sessions using Letta, structured core memory, daily review consolidation,
and a mistake-tracking loop.

**Files the agent may create or modify in this phase:**
```
src/memory/core_memory.py
src/memory/daily_review.py
src/memory/extractor.py
src/memory/mistake_tracker.py
data/logs/                (only to add generated daily review logs)
tests/test_phase2.py
requirements.txt          (only to add Phase 2 libraries)
docker/docker-compose.yml (only if Letta runtime wiring is incomplete)
```

**Files the agent must NOT touch in this phase:**
- Anything in `src/voice/`
- Anything in `src/agents/`
- Anything in `src/api/` except a future import fix required by tests
- `CLAUDE.md`

---

## Task 2.1 — Letta Runtime Setup

### What to build
A reliable local Letta runtime connected to Ollama and persisted through Docker volumes.

### Behaviour rules
- Letta must run through Docker Compose
- Memory must survive container restarts
- Agent name must be `omar_brain`
- Letta health must be checked before any memory task executes
- If Letta is unavailable, the code must fail clearly with logging, not hang silently

### Done when
- `curl http://localhost:8283/health` returns 200
- A Letta agent named `omar_brain` exists or is created automatically
- Restarting the container does not erase previously stored state

---

## Task 2.2 — src/memory/core_memory.py

### What to build
A structured loader/updater for long-lived memory stored locally in JSON and synchronized
with Letta as the active system identity layer.

### Interface
```python
class CoreMemoryManager:
    def __init__(self, memory_path: Path): ...
    def load(self) -> dict: ...
    def save(self, payload: dict) -> None: ...
    def ensure_schema(self) -> dict: ...
    def update_section(self, section: str, value: dict | list | str) -> None: ...
    def sync_to_letta(self) -> None: ...
```

### Required schema
```json
{
  "identity": {},
  "domains": [],
  "goals": [],
  "mistakes": [],
  "preferences": {},
  "active_projects": [],
  "last_reviewed_at": ""
}
```

### Behaviour rules
- If the file does not exist, create it with the required schema
- Every update must preserve unknown keys instead of dropping them
- Writes must be atomic to avoid partial corruption
- Invalid JSON must be logged and repaired via schema reset only after creating a backup
- `sync_to_letta()` should push a concise representation, not the entire raw JSON dump

---

## Task 2.3 — src/memory/daily_review.py

### What to build
A nightly review generator that summarizes new activity and stores a dated review in `data/logs/`.

### Interface
```python
class DailyReviewRunner:
    def run(self, review_date: date | None = None) -> Path: ...
    def collect_inputs(self) -> dict: ...
    def summarize_day(self, inputs: dict) -> str: ...
    def write_review(self, review_date: date, content: str) -> Path: ...
```

### Review contents
- what changed today
- what was learned
- unresolved blockers
- repeated mistakes
- next priorities

### Behaviour rules
- Output file format: `data/logs/YYYY-MM-DD.md`
- If there is little data, still write a minimal review instead of skipping the day
- Reviews must be deterministic enough to test
- If cloud synthesis is ever used later, data tagged `personal` or `religion` must not leave local routing

---

## Task 2.4 — src/memory/extractor.py

### What to build
A parser that reads daily reviews and turns them into updates for core memory.

### Interface
```python
class DailyReviewExtractor:
    def extract_updates(self, review_path: Path) -> dict: ...
    def detect_goals(self, text: str) -> list[str]: ...
    def detect_mistakes(self, text: str) -> list[dict]: ...
    def detect_domain_changes(self, text: str) -> list[str]: ...
```

### Behaviour rules
- Extract only durable information, not every transient sentence
- New goals should be deduplicated against existing memory
- Mistakes should include context and correction if available
- The extractor must prefer precision over volume

### Done when
- A generated daily review produces structured updates
- Re-running extraction on the same review does not create duplicate entries

---

## Task 2.5 — src/memory/mistake_tracker.py

### What to build
A searchable mistake tracker that logs errors, stores fixes, and can be queried before work begins.

### Interface
```python
class MistakeTracker:
    def log_mistake(self, title: str, context: str, fix: str, tags: list[str]) -> None: ...
    def search(self, query: str, limit: int = 5) -> list[dict]: ...
    def pre_task_check(self, task_description: str) -> list[dict]: ...
```

### Behaviour rules
- Store mistakes in a machine-readable format
- Make `pre_task_check()` lightweight enough to run before each major task
- Search should work even before Phase 3 APIs exist
- Duplicate mistakes should be merged or linked, not endlessly appended

---

## Task 2.6 — tests/test_phase2.py

### Required acceptance tests
- Core memory file is created with the correct schema
- Updating one section does not delete unrelated sections
- Daily review writes a dated markdown file
- Extractor turns a review into structured updates
- Mistake tracker returns relevant prior mistakes for a task query
- Letta sync path fails clearly when Letta is down

---

## Definition of Done for Phase 2

- Local core memory exists and survives multiple runs
- Daily reviews are generated into `data/logs/`
- Durable items are extracted back into memory
- Mistake tracking is queryable before new tasks
- All Phase 2 tests pass
