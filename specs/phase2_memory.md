# Phase 2 Spec: The Memory Engine

## Goal
Establish a persistent, tiered memory system that tracks user identity, learning progress, and past mistakes.

## Components
- **Letta (MemGPT) Runtime:** Manages agent state and memory paging.
- **User Profile (Core Memory):** Structured JSON tracking domains (Psychology, Religion, etc.).
- **Daily Review System:** Nightly consolidation of learning and logs.

## Tasks
1. [ ] Install and configure Letta with local Ollama.
2. [ ] Define `omar_brain` agent with persistent core memory.
3. [ ] Create `core_memory.json` template.
4. [ ] Build `daily_review.py` for evening reflection.
5. [ ] Implement background extraction (log -> profile update).
6. [ ] Establish "Mistake Log" memory namespace.

## Validation
- The system correctly recalls a personal fact or a past mistake mentioned in a previous session.
