# SPEC: Phase 5 — Agency & Proactivity
# Agent reads this before writing any Phase 5 code.
# This file is the contract. Code must match this spec exactly.

---

## Scope

**What this phase builds:** A constrained action layer that can plan tasks,
execute them in isolation, and offer proactive help based on desktop context.

**Files the agent may create or modify in this phase:**
```
src/agents/planner.py
src/agents/sub_agent.py
src/agents/proactive.py
docker/bytebot/           (configuration and support files)
tests/test_phase5.py
requirements.txt          (only to add Phase 5 libraries)
```

**Files the agent must NOT touch in this phase:**
- `CLAUDE.md`

---

## Task 5.1 — src/agents/planner.py

### What to build
A planner that turns a high-level goal into bounded executable steps.

### Interface
```python
class TaskPlanner:
    def create_plan(self, goal: str) -> list[dict]: ...
    def validate_plan(self, plan: list[dict]) -> list[dict]: ...
```

### Behaviour rules
- Plans must be explicit, ordered, and inspectable
- Each step should have a clear action, input, and expected output
- Dangerous or ambiguous steps must be flagged before execution

---

## Task 5.2 — src/agents/sub_agent.py

### What to build
An isolated executor that can run one bounded task with limited context.

### Interface
```python
class SubAgentExecutor:
    def run_step(self, step: dict) -> dict: ...
    def dry_run(self, step: dict) -> dict: ...
```

### Behaviour rules
- Each execution should be sandboxed
- Results must include logs, outputs, and status
- A failing step should not corrupt the whole plan state

---

## Task 5.3 — Bytebot sandbox

### What to build
A Docker-based execution environment for agent actions.

### Behaviour rules
- The sandbox must isolate filesystem and network access as much as practical
- Mounts must be intentional and minimal
- The agent must be able to preview intended actions before executing them

### Done when
- A sample step can run in the sandbox and return logs safely

---

## Task 5.4 — src/agents/proactive.py

### What to build
A monitor that observes lightweight desktop context and surfaces relevant reminders or notes.

### Interface
```python
class ProactiveAssistant:
    def poll_context(self) -> dict: ...
    def suggest(self, context: dict) -> list[str]: ...
    def notify(self, suggestions: list[str]) -> None: ...
```

### Behaviour rules
- Context collection must be minimal and privacy-aware
- Suggestions must be relevant, not constant noise
- Notifications should be rate-limited

---

## Task 5.5 — Permission and dry-run logic

### What to build
A safety layer that distinguishes:
- observe
- suggest
- dry-run
- execute

### Behaviour rules
- Potentially destructive actions must require explicit approval
- The system should always be able to explain what it is about to do
- Dry-run mode must show intended commands or steps without performing them

---

## Task 5.6 — tests/test_phase5.py

### Required acceptance tests
- Planner produces a structured multi-step plan
- Invalid or risky steps are flagged by validation
- Sub-agent dry-run returns preview output without executing
- Sandbox executes a safe sample task and returns logs
- Proactive assistant suggestions are rate-limited and context-based

---

## Definition of Done for Phase 5

- High-level goals can be turned into bounded plans
- Individual steps can run in isolation
- Safety and dry-run controls work
- Proactive suggestions are useful and not spammy
- All Phase 5 tests pass
