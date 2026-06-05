# Project: Personal AI Brain

## What this is
A local-first AI second brain running on Ubuntu 22.04,
Ryzen 5 5600H, RTX 3060 6GB. Owner: Omar.

## Rules the agent MUST follow
1. Read STATUS.md before every session. Start exactly where it says.
2. Read the relevant spec in /specs/ before touching any code.
3. After completing a task, update STATUS.md immediately.
4. If you hit an error you cannot fix in 3 attempts, write it to ERRORS.md
   and STOP. Do not try a 4th workaround.
5. Never install a new library not listed in the current phase spec.
6. Never touch files outside the current phase's scope.
7. Every function must have a docstring. Every module must have a README.
8. Run tests before marking any task done.

## Hardware constraints
- Max VRAM for local models: 5.5GB (leave 0.5GB headroom)
- Preferred local model: mistral-7b-instruct via Ollama
- Cloud model for complex reasoning: Claude Sonnet 4 via API

## Tech stack (locked)
- Runtime: Python 3.11
- Memory: Letta (MemGPT) + LanceDB + pgvector
- Voice: Whisper.cpp (STT) + Kokoro ONNX (TTS)
- Agency: Claude Code as the orchestrator
- Sandbox: Docker + Bytebot
- API layer: FastAPI
- Notes: Obsidian-compatible markdown

## Current phase
See STATUS.md
