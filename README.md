# Personal AI Brain

Local-first personal intelligence system for:
- knowledge ingestion,
- semantic retrieval,
- structured memory,
- voice interaction,
- safe agent execution.

The repository currently contains:
- project governance and specs,
- phased architecture plans,
- early shared infrastructure,
- the start of the implementation foundation.

## Current Status

- Active phase: Phase 1, The Vault
- Main status tracker: `STATUS.md`
- Governing rules: `CLAUDE.md`
- Known issues log: `ERRORS.md`

## Repository Layout

```text
.
├── CLAUDE.md
├── STATUS.md
├── ERRORS.md
├── config.py
├── requirements.txt
├── specs/
├── src/
├── tests/
├── data/
├── docker/
└── codex/
```

## Setup

### 1. Create the virtual environment

```bash
cd /home/omar/personal_ai_brain_project
python3.11 -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
cp .env.example .env
```

Fill in any values you need in `.env`.

### 4. Verify local services

Ollama:

```bash
curl http://localhost:11434/api/tags
```

Letta:

```bash
docker compose -f docker/docker-compose.yml up -d
curl http://localhost:8283/health
```

### 5. Pull required Ollama models

```bash
ollama pull mistral
ollama pull nomic-embed-text
```

## Tests

Run baseline tests:

```bash
source venv/bin/activate
pytest -v
```

## Notes

- The `codex/` folder contains analysis, restructuring notes, and execution planning.
- Root `phase*.md` files are detailed contracts for each phase.
- `specs/` contains the shorter phase summaries.
