# Phase 2 Spec: The Memory Engine (v5.1 Deep)

## Goal
Stateful continuity using the Letta (MemGPT) paradigm.

## 1. Letta Runtime
- **Setup:** Docker-based Letta with local Ollama/Mistral-7B.
- **Tiers:** Core (Active Persona), Recall (Postgres/pgvector), Archival (LanceDB).

## 2. Core Memory Architecture
- **Schema:** `core_memory.json` (Identity, Domains, Mistakes, Goals).
- **Auto-Update:** Agent uses `core_memory_replace` to evolve the profile.

## 3. Daily Review & Reflection
- **Systemd Timer:** Trigger at 9 PM (Persistent).
- **Consolidation:** Summarize day's activity into `data/logs/`.
- **Extraction:** Update `core_memory.json` with learning progress.

## 4. Mistake Tracker
- **Namespace:** Dedicated Letta segments for errors + corrections.
- **Pre-Task Check:** Automatic search for relevant past mistakes before new tasks.
