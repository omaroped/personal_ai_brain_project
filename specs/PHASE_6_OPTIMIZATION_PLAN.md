# Phase 6: Optimization & Jarvis-Tier Features
# The road to a flawless, open-source-ready Digital Twin

## 1. Current State Assessment
We have built a powerful local AI system with Voice (Wake-words + TTS), Agency (ReAct Planner + OpenClaw), and Memory (Letta + LanceDB). 

However, the architecture has grown organically and has technical debt:
- **Audio Feedback Loop:** The VAD sometimes clashes with TTS, requiring hardcoded `time.sleep()` patches.
- **Dependency Bloat:** We have PyTorch, ONNX, Letta, OpenWakeWord, and FastAPI all fighting for resources.
- **Agent Monolith:** The Voice Pipeline is trying to do too much (managing auth, routing to OpenClaw vs Letta vs Planner).

## 2. Optimization Goals (Refactoring before Features)
Before adding complex visual features, we must make the core bulletproof.

- [ ] **Decouple the Voice Engine:** Move VAD, STT, and TTS into a separate lightweight background daemon that communicates with the Master API via WebSockets. This isolates audio bugs from logic bugs.
- [ ] **Unify the Identity Provider:** Move the `OpenClawAgent` and `OmarBrainAgent` logic behind a single `IdentityManager` interface. The system should automatically handle fallback without messy `if/else` blocks in the pipeline.
- [ ] **State Machine Planner:** Upgrade the ReAct planner from a simple `while` loop to a robust State Graph (e.g., LangGraph or custom state machine) to prevent infinite loops and improve tool recovery.

## 3. The "Jarvis" Feature Roadmap
Once the core is optimized, we will build the features that make this a true digital companion.

### Feature 1: True Barge-In (Interruptibility)
- Implement continuous audio buffering. If the Wake-Word is detected *while* the TTS is speaking, immediately send a `SIGINT` to the playback thread and process the new command.

### Feature 2: Screen Awareness (Visual Grounding)
- Integrate a `CaptureScreenTool`. When the user says "What am I looking at?", the tool uses `scrot` or `grim` to capture the desktop, passes it to the local vision model (`qwen-vl` or similar), and feeds the description to the Planner.

### Feature 3: Deep System Control
- Expand the `ExecuteCommandTool` into a suite of specialized OS tools: `ManageWindowsTool` (using `wmctrl` or `xdotool` where appropriate), `ClipboardTool`, and `MediaControlTool`.

## 4. Open-Source Readiness Strategy
When we are ready to make this public, it must be deployable by anyone.
- [ ] **Dockerization:** Containerize the entire Python environment, not just the databases.
- [ ] **Config Standardization:** Ensure no hardcoded paths (`/home/omar/...`) exist anywhere in the codebase.
- [ ] **Documentation:** Write a comprehensive `README.md` with clear architectural diagrams based on `UPDATED_PLAN_V6.md`.
