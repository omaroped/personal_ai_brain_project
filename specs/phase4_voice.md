# Phase 4 Spec: The Voice Layer

## Goal
Enable natural, low-latency (sub-1.5s) voice interaction with the Digital Twin.

## Components
- **STT:** `whisper.cpp` (GPU accelerated).
- **VAD:** `Silero VAD` for silence detection.
- **TTS:** `Kokoro ONNX` for high-speed voice synthesis.
- **Controller:** `listen.py` orchestrates the loop.

## Tasks
1. [ ] Install and GPU-optimize `whisper.cpp`.
2. [ ] Benchmarking STT latency (<400ms).
3. [ ] Set up persistent `Kokoro ONNX` server.
4. [ ] Build the end-to-end `listen.py` loop.
5. [ ] Integrate hotkey (Ctrl+Space) for trigger.

## Validation
- Asking a voice question results in a spoken response in under 2 seconds.
