# Personal AI Brain 🧠

> A local-first personal AI operating system with memory, retrieval, voice, and safe agent execution.

**Personal AI Brain** is not just a chatbot. It is a persistent digital twin designed to run entirely on your local hardware (optimized for 6GB+ VRAM like the RTX 3060). It features ultra-low latency voice interaction (~800ms), long-term Letta-backed memory, a LanceDB knowledge vault, and a ReAct task planner capable of executing local system commands.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Status: Beta](https://img.shields.io/badge/Status-Beta-green.svg)]()

## 🌟 What Works Today (v0.1.0)

- **The Vault:** Automated ingestion pipeline watching local folders. Extracts text from PDFs (with OCR fallback), auto-tags domains, and embeds them into a local LanceDB vector store.
- **The Voice:** Sub-second voice interaction. Wake-word detection ("Hey Jarvis") via OpenWakeWord, lightning-fast STT via faster-whisper, and true streaming TTS via Kokoro-ONNX.
- **The Memory:** Persistent agent identity using Letta. It remembers past conversations, tracks your mistakes, and updates its core memory blocks dynamically.
- **The Agency:** A ReAct Task Planner that can safely browse the web, search your vault, and execute system commands (with human-in-the-loop confirmation gates).
- **The Speed:** "Turbo Mode" integration allowing seamless fallback to cloud models (OpenClaw/Codex/Gemini) for high-speed reasoning, while enforcing strict local-only routing for "Personal" or "Religion" domains.
- **The Dashboard:** A modern, Glassmorphism-styled web dashboard (`http://localhost:8001`) to monitor system pulse, intelligence streams, and manage OAuth-style app authorizations.

## 🚀 Quickstart

We provide a single bootstrap script to create the environment, install dependencies, and verify your system.

```bash
# 1. Clone the repository
git clone https://github.com/omaroped/personal_ai_brain_project.git
cd personal_ai_brain_project

# 2. Run the bootstrap/startup script
chmod +x scripts/bootstrap.sh
./scripts/bootstrap.sh
```

Once the environment is verified, start the brain:

```bash
./scripts/start_brain.sh
```

When you see `Voice Pipeline active`, you can:
1. Open **`http://localhost:8001`** to view the dashboard.
2. Say **"Hey Jarvis, what is my core identity?"** to test the voice pipeline and memory.

## 🏗️ Architecture

The system is strictly separated into modular concerns:

1. **Ingestion (`src/ingestion/`)**: OS-level file watcher → PDF Extractor → Recursive Chunker → Ollama Embedder → LanceDB.
2. **Memory (`src/memory/`)**: Letta Agent (Identity & Conversation) + Mistake Tracker (Vector-backed error prevention) + Daily Review (Nightly JSONL log compression).
3. **Voice (`src/voice/`)**: VAD (Silero) + STT (Whisper) + TTS (Kokoro) + OpenWakeWord. Operates on an event loop independent of the heavy LLM reasoning.
4. **Agency (`src/agents/`)**: ReAct Planner loop delegating to a strict Tool Registry (`search_vault`, `execute_command`, `browse_url`).
5. **API (`src/api/`)**: FastAPI routing layer enforcing `PrivacyDecision` policies before allowing data to hit cloud endpoints.

*(For a deep dive into the exact architectural decisions and future roadmap, see `specs/UPDATED_PLAN_V6.md` and `specs/PROJECT_REFERENCE_GUIDE.md`)*.

## 🔒 The Privacy Contract
Your data is yours. The `PrivacyRouter` ensures that any document or query tagged with sensitive domains (e.g., `personal`, `finance`, `religion`) is **hard-blocked** from leaving your machine. Only "public" domain queries are allowed to use the Turbo Mode (Gemini/Codex) bypass.

## 🛣️ Roadmap (Phase 6)
- **Decoupled Audio Engine:** Moving VAD/TTS to a dedicated WebSocket daemon.
- **True Barge-in:** Continuous audio buffering to interrupt the Brain while it speaks.
- **Visual Grounding:** Desktop screenshot tool for multimodal reasoning.

## 🤝 Contributing
Contributions are welcome. Please ensure you run the test suite (`pytest tests/`) before submitting PRs. See `docs/TESTING.md` for our testing philosophy.
