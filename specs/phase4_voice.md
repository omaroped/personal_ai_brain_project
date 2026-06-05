# Phase 4 Spec: The Voice Layer (v5.1 Deep)

## Goal
Low-latency (1.2s-1.5s) voice interaction.

## 1. STT: Faster-Whisper
- **Engine:** `faster-whisper` (CTranslate2 optimized for NVIDIA).
- **Model:** `base` (multilingual for Arabic/English).
- **Target:** ~150ms transcription for 5s audio.

## 2. VAD: Silero
- **Engine:** `silero-vad` (CPU-based, 100ms window).
- **Logic:** 0.8s silence threshold for end-of-speech detection.

## 3. TTS: Kokoro ONNX
- **Engine:** `kokoro-onnx` (CPU, streaming).
- **Voice:** `af_bella` (Female, high quality).
- **Target:** ~200ms first-token audio latency.

## 4. Integration
- **Hotkey:** Ctrl+Space via `pynput`.
- **Pre-loading:** Models stay warm in memory.
