# SPEC: Phase 4 — The Voice Layer
# Agent reads this before writing any Phase 4 code.
# This file is the contract. Code must match this spec exactly.

---

## Scope

**What this phase builds:** A low-latency local voice loop from microphone input
to transcript, reasoning, and streamed spoken response.

**Files the agent may create or modify in this phase:**
```
src/voice/vad.py
src/voice/stt.py
src/voice/tts.py
src/voice/pipeline.py
tests/test_phase4.py
requirements.txt          (only to add Phase 4 libraries)
```

**Files the agent must NOT touch in this phase:**
- Anything in `src/agents/`
- `CLAUDE.md`

---

## Task 4.1 — Environment and benchmark

### What to build
A verified local runtime for `faster-whisper`, `silero-vad`, and `kokoro-onnx`.

### Behaviour rules
- CUDA path must be validated before STT benchmarks
- Models must be warmed up once at startup
- Baseline latency measurements must be recorded in test output or logs

### Done when
- A 5-second audio clip transcribes in the expected latency range on local hardware
- First-run model initialization no longer causes misleading hangs

---

## Task 4.2 — src/voice/vad.py

### What to build
A voice activity detector that listens continuously and decides when speech starts and ends.

### Interface
```python
class VoiceActivityDetector:
    def start(self) -> None: ...
    def stop(self) -> None: ...
    def read_utterance(self) -> bytes: ...
```

### Behaviour rules
- Use `silero-vad`
- Windowing should be small enough for responsive start detection
- End-of-speech should trigger after a short silence threshold
- Background noise should not constantly trigger recording

---

## Task 4.3 — src/voice/stt.py

### What to build
A speech-to-text service wrapping `faster-whisper`.

### Interface
```python
class SpeechToTextService:
    def warmup(self) -> None: ...
    def transcribe_bytes(self, audio_bytes: bytes) -> str: ...
    def transcribe_file(self, audio_path: Path) -> str: ...
```

### Behaviour rules
- Use multilingual support for Arabic and English
- Return clean text with minimal formatting noise
- If CUDA is unavailable, log fallback behaviour clearly
- Empty or near-empty utterances should return an empty string, not an exception

---

## Task 4.4 — src/voice/tts.py

### What to build
A text-to-speech service wrapping `kokoro-onnx` with streaming playback.

### Interface
```python
class TextToSpeechService:
    def warmup(self) -> None: ...
    def synthesize(self, text: str) -> bytes: ...
    def speak(self, text: str) -> None: ...
```

### Behaviour rules
- Optimize for low first-audio latency
- Avoid blocking the whole app during playback when possible
- Skip synthesis for empty text
- Support one stable default voice only at first

---

## Task 4.5 — src/voice/pipeline.py

### What to build
A full loop that connects VAD, STT, the brain query path, and TTS.

### Interface
```python
class VoicePipeline:
    def run_forever(self) -> None: ...
    def process_once(self) -> None: ...
    def handle_transcript(self, transcript: str) -> str: ...
```

### Behaviour rules
- Ignore empty transcripts
- Responses should come from the existing brain/query path instead of a separate ad hoc responder
- The pipeline must log component latency for:
  - VAD capture
  - STT
  - reasoning/query
  - TTS

---

## Task 4.6 — Hotkey trigger

### What to build
A keyboard trigger using `Ctrl+Space` to start active listening.

### Behaviour rules
- Hotkey must be explicit and reliable
- If the hotkey subsystem fails, manual invocation must still work

---

## Task 4.7 — tests/test_phase4.py

### Required acceptance tests
- VAD detects a speech segment boundary
- STT returns text for a sample clip
- Empty audio does not crash STT
- TTS produces audio bytes for non-empty text
- End-to-end pipeline stays within target latency on the benchmark path

---

## Definition of Done for Phase 4

- Voice input can be captured locally
- Speech is transcribed and answered locally
- Spoken responses are synthesized reliably
- Latency stays near the stated target on real hardware
- All Phase 4 tests pass
