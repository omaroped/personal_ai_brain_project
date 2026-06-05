# Restructure Plan

## Goal

Keep the original repository intact, but define a cleaner working structure for active development.

## Recommended Working Structure

```text
personal_ai_brain_project/
├── codex/
│   ├── README.md
│   ├── PROJECT_AUDIT.md
│   ├── RESTRUCTURE_PLAN.md
│   └── IMPLEMENTATION_START.md
├── docs/
│   ├── governance/
│   │   ├── CLAUDE.md
│   │   ├── STATUS.md
│   │   └── ERRORS.md
│   ├── architecture/
│   │   ├── MASTER_PLAN.md
│   │   ├── ARCHITECTURE.md
│   │   └── personal_ai_brain_architecture.svg
│   ├── specs/
│   │   ├── phase1_vault.md
│   │   ├── phase2_memory.md
│   │   ├── phase3_ingestion.md
│   │   ├── phase4_voice.md
│   │   └── phase5_agency.md
│   ├── research/
│   │   └── opinions/
│   └── context/
│       ├── USER_PROFILE.md
│       └── SYSTEM_RESOURCES.md
├── src/
│   ├── ingestion/
│   ├── memory/
│   ├── voice/
│   ├── agents/
│   └── api/
├── tests/
├── data/
├── docker/
├── requirements.txt
├── .env.example
├── config.py
└── query.py
```

## Why This Structure Is Better

- Separates documentation from implementation.
- Makes governance docs easy to find.
- Prevents root-level file sprawl.
- Keeps strategic opinion documents available without letting them dominate execution.
- Makes the codebase feel like a software project instead of a notes collection.

## Minimal Non-Destructive Version

If you do not want to move files yet, use this as a logical structure only:

- Keep current files where they are.
- Treat `codex/` as the working interpretation layer.
- Later, migrate documents into `docs/` once implementation is underway.

## Suggested Cleanup Items

### Keep

- `CLAUDE.md`
- `STATUS.md`
- `ERRORS.md`
- `specs/`
- `plan/MASTER_PLAN.md`
- `opinions/`
- `memory/`

### Review and likely remove or archive later

- `CLAUDE (1).md`
- root `phase1_vault.md` if `specs/phase1_vault.md` is the canonical version

### Fill immediately

- `plan/ARCHITECTURE.md`
- `requirements.txt`
- `.env.example`
- `config.py`

## Architecture Document Recommendation

`plan/ARCHITECTURE.md` should become the shortest technical source of truth for:
- module boundaries,
- data flow,
- storage layout,
- service dependencies,
- privacy routing,
- phase ownership of each subsystem.

It should not repeat all reasoning from the deep plan. It should only answer:
- what components exist,
- how they talk to each other,
- where data lives,
- what gets built first.
