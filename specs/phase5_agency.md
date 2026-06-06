# Phase 5 Spec: Agency & Proactivity

## Goal
Transform the brain into an active agent that can operate the PC securely and provide proactive help.

## Components
- **Task Planner:** Breaks high-level goals into executable steps.
- **Expert Prompt Library:** A collection of 30+ high-signal templates (e.g., Code Review, Pareto Audit) used by sub-agents for specialized execution.
- **Bytebot Sandbox:** Isolated Docker container for running scripts/browsing.
- **Proactive Monitor:** Watches screen context to surface relevant notes.

## Tasks
1. [x] **Task 5.0.0** — Integrate Expert Prompt Library (`memory/PROMPT_LIBRARY.md` and `src/agents/prompts.py`).
2. [ ] Configure Bytebot Docker environment.
2. [ ] Build Hierarchical Agent Planner.
3. [ ] Develop "Dry Run" permission logic.
4. [ ] Build the proactive side-panel monitor.
5. [ ] Integrate Agent S for visual grounding.

## Validation
- The system can successfully execute a task like "Summarize these 3 PDFs and save the result to my vault" with minimal human intervention.
