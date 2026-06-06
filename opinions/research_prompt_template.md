# RESEARCH PROMPT TEMPLATE — Personal AI Brain Project
**Version: 2.1 | Owner: Omar | For use with Claude / Claude Code**

## IDENTITY & CONSTRAINTS

You are helping Omar, a Mechatronics Engineer building a **local-first Personal AI Brain**.

**Environment:**
- OS: Ubuntu 22.04 LTS
- CPU: AMD Ryzen 5 5600H (12 threads)
- GPU: NVIDIA RTX 3060 Laptop — 6GB VRAM (max safe allocation: 5.5GB)
- RAM: 22GB
- Python: 3.11 (venv always active)

**Models:**
- Local LLM: `mistral-7b-instruct` via Ollama (uses ~4.1GB VRAM)
- Cloud LLM: Claude Sonnet 4 (used only for complex synthesis, never for private data)

**Hard privacy rule (non‑negotiable):**
- Any data tagged as **personal** or **religion** domain MUST NEVER be sent to any cloud API.
- Any solution that touches those domains must be 100% local (models, storage, and processing).

---

## THE TOPIC

**Problem / Feature / Question:**
- [TOPIC — be specific]

**Current situation:**
- [CONTEXT — architecture, config, logs, failures]

**What a good answer looks like:**
- [EXPECTED OUTPUT SHAPE]

---

## ANALYSIS FRAMEWORK

### LENS 1 — Hardware & Resource Reality
*"Will this actually run on my machine without breaking something else?"*
1. **VRAM and RAM usage**: Estimated cost vs budget.
2. **CPU and GPU interaction**: Thread usage and CUDA requirements.
3. **Runtime / thermal considerations**: Sustainability on a laptop GPU.

### LENS 2 — Engineering Design
*"What is the correct technical architecture for this?"*
1. **Core pattern**: Exact algorithm or design pattern.
2. **Libraries and versions**: Specific pip package names and versions.
3. **Interface and integration**: Function/class signatures and project placement.
4. **Edge cases, failure modes, and thread safety**: Robustness and isolation.

### LENS 3 — User Experience
*"What does this feel like to Omar when it works and when it fails?"*
1. **Latency and responsiveness**: Target <300ms added latency.
2. **Failure UX**: Graceful degradation vs system freeze.
3. **Automation vs. manual intervention**: Cold start behavior and setup.

---

## THE GOLDEN PATH

1. **Recommendation**: One specific choice with 2-3 sentence justification.
2. **Implementation order**: Ordered task list for `STATUS.md`.
3. **Unlocking code (first 10 lines)**: Core skeleton proving the approach.
4. **Red flags**: 2-3 observable symptoms of failure.
