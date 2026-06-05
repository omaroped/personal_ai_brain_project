# Sub-Agent Operating Contract

## Purpose

This file is the working contract for all parallel AI agents contributing to this repository.

If you are a supporting agent, read this file before touching anything.

This file exists to:
- prevent file conflicts,
- keep implementation style consistent,
- keep work aligned with the main builder,
- reduce cleanup and merge friction.

## Authority

The main builder for this project is the lead agent working in the core ingestion path.

Lead agent ownership currently includes:
- `src/ingestion/watcher.py`
- `src/ingestion/pdf_extractor.py`
- `src/ingestion/chunker.py`
- `src/ingestion/embedder.py`
- `src/ingestion/pipeline.py`
- `tests/test_phase1.py`
- `STATUS.md`
- `CLAUDE.md`

Supporting agents must not edit those files unless explicitly reassigned.

## Source Of Truth

Supporting agents should treat these as the active authority stack:

1. `CLAUDE.md`
2. `STATUS.md`
3. `phase1_vault.md`
4. `ERRORS.md`
5. `codex/SUBAGENT_OPERATING_CONTRACT.md`
6. `codex/AGENT_ASSIGNMENTS.md`

If documents disagree:
- do not silently choose,
- do not invent a compromise in code,
- leave a note in `codex/MERGE_NOTES.md` or the relevant doc task output.

## Working Mode

You are not the orchestration lead.

Your job is to:
- complete a bounded sub-task,
- avoid touching core integration files,
- keep interfaces clean and predictable,
- leave work easy to merge.

Do not:
- refactor unrelated files,
- rename files without need,
- rewrite project strategy,
- “improve” lead-owned modules,
- add speculative framework complexity.

## Style Rules

All supporting agents must write in this style.

### General engineering style

- Be direct and minimal.
- Prefer clarity over cleverness.
- Keep functions small and composable.
- Use deterministic behavior when possible.
- Avoid hidden side effects.
- Keep interfaces explicit.

### Python code rules

- Use ASCII unless the file already requires otherwise.
- Add type hints everywhere practical.
- Every function must have a docstring.
- Every module must start with a `# MODULE:` header comment.
- Use the `logging` module, not `print()`.
- Catch specific exceptions, not bare `except:`.
- Reuse `config.py` constants instead of hardcoding paths or service URLs.
- Prefer simple data structures over abstraction-heavy designs.

### Test rules

- Tests should be narrow and deterministic.
- Prefer fixtures and temp paths over touching real project data.
- Do not depend on Ollama, Docker, or network access unless the task explicitly requires it.
- If a dependency is optional, test the fallback behavior.

### Documentation style

- Write short, high-signal sections.
- Avoid motivational or promotional language.
- State assumptions explicitly.
- Prefer operational instructions over vague guidance.

## Merge Safety Rules

Supporting agents should prefer adding new files over editing shared files.

Safe targets:
- new tests
- new fixtures
- new docs
- new scripts
- isolated helper modules

Avoid editing unless the assigned task explicitly requires it:
- `config.py`
- `requirements.txt`
- `README.md`
- `query.py`
- any file under `src/ingestion/` already owned by the lead

If you must touch a shared file:
- make the smallest change possible,
- document exactly why,
- note it in `codex/MERGE_NOTES.md`.

## Task Assignment Rules

A supporting agent should work on exactly one assigned task at a time.

Each task should define:
- target files,
- goal,
- done criteria,
- conflict boundaries.

If those are missing, do not guess. Use the nearest matching assignment in:
- `codex/AGENT_ASSIGNMENTS.md`
- `codex/SUBAGENT_BACKLOG.md`

## Current Reserved Areas

### Reserved for lead agent

- watcher implementation
- PDF extraction implementation
- chunking implementation
- embedding implementation
- pipeline integration
- main Phase 1 acceptance test file

### Safe for supporting agents

- fixture creation
- isolated tests
- CLI test support
- service verification scripts
- benchmark utilities
- architecture docs
- testing docs
- operations docs
- environment repair docs/scripts
- helper modules not yet integrated by the lead

## Delivery Format

When a supporting agent finishes a task, it should leave:

1. the code or document changes
2. a short note in `codex/MERGE_NOTES.md` with:
   - task completed
   - files added or changed
   - any assumptions
   - any follow-up needed

The note should be factual and short.

## Quality Bar

Supporting agent work is only acceptable if it is:
- mergeable without rework,
- consistent with the project rules,
- isolated from lead-owned files,
- not dependent on hidden context,
- easy for another engineer to understand quickly.

## Example Good Behavior

- add a new test file for an isolated module
- add a fixture file and explain its intended use
- add a service-check script using existing config values
- fill an empty architecture doc without touching runtime code

## Example Bad Behavior

- rewrite `watcher.py` because you think it can be cleaner
- change `CLAUDE.md`
- add a new dependency without reason
- mix multiple unrelated tasks into one patch
- add a complex abstraction layer nobody asked for

## Current Priority For Supporting Agents

Best current parallel tasks:
- testing support
- fixtures
- architecture documentation
- operations documentation
- service verification scripts
- benchmark harness support
- isolated helper modules

## Final Rule

If you are unsure whether a task conflicts with the lead agent’s work:
- do not touch the file,
- choose a safer isolated task,
- leave the integration point for the lead.
