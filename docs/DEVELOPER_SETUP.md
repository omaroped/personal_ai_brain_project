# Developer Setup

## Supported Runtime

- Python version: see `.python-version`
- primary workflow: local venv
- local services: Ollama and Letta

## Setup Modes

### Core contributor

Use this if you are working on retrieval, API, docs, or memory logic only.

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements-core.txt -r requirements-dev.txt
python scripts/validate_environment.py
```

### Full local brain contributor

Use this if you are working on voice, planner, or runtime integration.

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements-core.txt -r requirements-voice.txt -r requirements-agents.txt -r requirements-dev.txt
python scripts/validate_environment.py
```

## Troubleshooting

### Wrong Python interpreter

- activate the repo venv explicitly
- check `python --version`
- run `python scripts/validate_environment.py`

### Missing local services

- start Ollama
- start Letta from `docker/docker-compose.yml`
- re-run the environment validator

### Audio issues

- verify local audio devices
- avoid running voice tests in headless CI
- use CI-safe tests first before voice integration tests
