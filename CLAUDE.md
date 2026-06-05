# Project: Personal AI Brain (v5.1 - Deep Engineering)

## What this is
A local-first AI second brain running on Ubuntu 22.04,
Ryzen 5 5600H, RTX 3060 6GB. Owner: Omar.

## 1. THE CONSTITUTION (Rules for Agents)
1. **Read STATUS.md first:** Never start a session without checking the progress.
2. **Read the SPEC:** Before writing code, read the relevant file in `/specs/`.
3. **Spec-Driven Development:** Write a plan, implement, then validate (tests/).
4. **Error Protocol:** If a fix fails 3 times, write to `ERRORS.md` and STOP.
5. **No Version Drift:** Follow the version lock in `MASTER_PLAN.md`.
6. **Privacy Shield:** Never send `personal` or `religion` domain data to cloud APIs.

## 2. Hardware Constraints & Routing
- **Local (Ollama/Faster-Whisper):** Default for 90% of tasks.
- **VRAM Budget:** 6GB total. Target: 5.5GB used, 0.5GB headroom.
- **Cloud (Claude 3.7):** Only for complex reasoning and synthesis.

## 3. Technology Version Lock
- Runtime: Python 3.11
- Memory: Letta (MemGPT) + LanceDB (0.8.x) + pgvector
- Voice: Faster-Whisper (1.1.0) + Kokoro ONNX (0.4.x) + Silero VAD (5.1.x)
- Agency: Agent S + Bytebot (Docker)
- Library: watchdog, pymupdf, fastapi, torch (2.3.x)

## 4. Source of Truth
- MASTER_PLAN.md: The overarching engineering blueprint.
- STATUS.md: The current execution state.
- ERRORS.md: The institutional memory of failures.
