# Sub-Agent Backlog

## Goal

Define tasks that separate agents can start now so later implementation agents move faster.

These tasks are chosen to be:
- low-conflict,
- useful across multiple phases,
- mostly independent,
- safe to complete before the core build is finished.

## Priority Labels

- `P0`: can start now and will help immediately
- `P1`: useful soon, low risk
- `P2`: useful later, should not block early implementation

## P0: Best Tasks To Start Now

### 1. Environment bootstrap agent

**Deliverables**
- `requirements.txt`
- `.env.example`
- dependency grouping comments
- install verification notes

**Why now**
- every future agent depends on this
- no product logic decisions required

**Constraints**
- only include libraries already approved by the phase specs
- do not over-install future optional tools unless clearly needed

### 2. Config agent

**Deliverables**
- `config.py`
- path constants
- model names
- privacy constants
- phase-safe defaults

**Why now**
- removes hardcoded path risk
- almost all later modules will import this

### 3. Docker/runtime agent

**Deliverables**
- `docker/docker-compose.yml`
- Letta persistence volumes
- health checks
- environment wiring

**Why now**
- later agents should not waste time rebuilding runtime plumbing

### 4. README/setup agent

**Deliverables**
- root `README.md`
- setup instructions
- bootstrap commands
- service checks
- troubleshooting section

**Why now**
- improves reproducibility for every future session

### 5. Test fixtures agent

**Deliverables**
- `tests/fixtures/`
- small PDF sample
- markdown sample
- text note sample
- fake daily review sample
- safe transcript sample

**Why now**
- later code agents can write tests much faster if fixtures already exist

### 6. Logging foundation agent

**Deliverables**
- logging configuration module
- rotating file logging setup
- log format conventions

**Why now**
- every subsystem benefits
- avoids ad hoc logging styles later

## P1: Strong Early Parallel Tasks

### 7. Ingestion state agent

**Deliverables**
- SQLite schema for ingestion index
- file hash helpers
- deduplication utilities

**Why now**
- watcher and pipeline both depend on it
- isolated enough to build early

### 8. LanceDB schema agent

**Deliverables**
- vector schema definitions
- table bootstrap helpers
- locking strategy wrapper

**Why now**
- embedder and retrieval code will need stable schema contracts

### 9. Privacy routing agent

**Deliverables**
- `src/api/privacy_router.py`
- domain sensitivity rules
- local-only enforcement helpers

**Why now**
- touches multiple phases
- core product differentiator

### 10. CLI skeleton agent

**Deliverables**
- command structure for `query.py` or `brain` CLI
- placeholder commands
- argument parsing structure

**Why now**
- gives later feature agents a stable operational interface

### 11. Health-check agent

**Deliverables**
- service verification helpers for:
  - Ollama
  - Letta
  - vector DB path readiness
- human-readable diagnostics

**Why now**
- reduces future debugging overhead

### 12. Benchmark harness agent

**Deliverables**
- timing utilities
- benchmark script skeletons
- latency recording format

**Why now**
- useful for ingestion, retrieval, and voice phases

## P2: Useful But Should Not Distract Early Build

### 13. Local dashboard skeleton agent

**Deliverables**
- minimal FastAPI or web UI shell
- placeholder pages:
  - health
  - ingestion status
  - search
  - memory

**Why later**
- valuable, but not required to prove Phase 1

### 14. Backup/restore agent

**Deliverables**
- backup script design
- export/import structure for:
  - `data/vectordb`
  - `data/logs`
  - memory files

**Why later**
- important for professionalism, but not Phase 1 critical

### 15. ADR/documentation agent

**Deliverables**
- architecture decision records
- filled `plan/ARCHITECTURE.md`
- source-of-truth rules

**Why later**
- helps coherence, but should not stall bootstrapping

### 16. Security policy agent

**Deliverables**
- secret handling rules
- file access policy
- action confirmation policy

**Why later**
- critical before Phase 5, not blocking Phase 1 bootstrapping

## Tasks That Should Not Be Split Too Early

These are better kept with the main implementation agent because they are tightly coupled:

- full ingestion pipeline integration
- chunking logic plus retrieval tuning
- voice end-to-end loop
- proactive agent execution logic

Reason:
- too many moving parts
- high chance of interface mismatch if split too early

## Recommended Parallelization Set

If you want multiple agents working now, the best split is:

### Agent A
- environment bootstrap
- `requirements.txt`
- `.env.example`

### Agent B
- `config.py`
- logging foundation
- health checks

### Agent C
- Docker runtime
- Letta compose setup
- service persistence

### Agent D
- README/setup docs
- troubleshooting guide
- architecture summary

### Agent E
- test fixtures
- benchmark harness
- test scaffold

### Agent F
- ingestion state helpers
- file hashing
- SQLite dedup schema

## Highest-Leverage Deliverables

If only a few things get done now, make it these:

1. `config.py`
2. `requirements.txt`
3. `.env.example`
4. `docker/docker-compose.yml`
5. `tests/fixtures/`
6. logging setup
7. ingestion state schema

Those seven items will remove a lot of friction for every later phase.

## Final Recommendation

The best sub-task strategy is:
- build shared infrastructure first,
- avoid splitting tightly coupled feature logic too early,
- let later agents inherit ready-made foundations.

That will make the main implementation agent much faster in Phase 1 and cleaner in later phases.
