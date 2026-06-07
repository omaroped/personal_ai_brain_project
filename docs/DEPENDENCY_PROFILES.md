# Dependency Profiles

## Purpose

This document classifies the project's dependencies into install profiles so contributors do not need the full stack for every workflow.

## Profiles

### Core

Used for:

- API
- ingestion
- retrieval
- local memory
- basic CLI workflows

Install file:

- `requirements-core.txt`

### Voice

Used for:

- VAD
- STT
- TTS
- audio device integration

Install file:

- `requirements-voice.txt`

Heavy dependencies:

- `torch`
- `torchaudio`
- `onnxruntime-gpu`
- `faster-whisper`

### Agents

Used for:

- cloud bridges
- websocket-based daemon communication

Install file:

- `requirements-agents.txt`

### Development

Used for:

- tests
- local verification

Install file:

- `requirements-dev.txt`

## Recommended Install Paths

### Minimal contributor setup

```bash
pip install -r requirements-core.txt -r requirements-dev.txt
```

### Full local brain setup

```bash
pip install -r requirements-core.txt -r requirements-voice.txt -r requirements-agents.txt -r requirements-dev.txt
```
