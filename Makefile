.PHONY: help setup test smoke run-api run-voice health clean bootstrap

# Default Python environment
PYTHON := venv/bin/python
PIP := venv/bin/pip

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup: ## Create venv, install dependencies, and setup env
	@echo "Setting up Python environment..."
	python3.10 -m venv venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@if [ ! -f .env ]; then cp .env.example .env; echo "Created .env from .env.example. Please update it."; fi
	@echo "Setup complete. Run 'source venv/bin/activate' to activate."

bootstrap: setup ## Full system bootstrap (Python, Docker, Models)
	@echo "Bootstrapping full system..."
	@bash scripts/rebuild_venv.sh
	@echo "Starting Docker services (Letta)..."
	@cd docker && docker-compose up -d
	@echo "Pulling local Ollama models..."
	@ollama pull mistral || echo "Make sure Ollama is running."
	@ollama pull nomic-embed-text || echo "Make sure Ollama is running."
	@echo "Bootstrap complete."

test: ## Run the full unit test suite
	$(PYTHON) -m pytest tests/ -v

smoke: ## Run core workflow smoke tests
	@echo "Running Ingestion Smoke Test..."
	$(PYTHON) scripts/smoke_test_ingestion.py
	@echo "Running Voice Benchmark..."
	$(PYTHON) scripts/benchmark_voice.py

run-api: ## Start the Master FastAPI server
	$(PYTHON) src/api/main.py

run-voice: ## Start the Voice Pipeline Orchestrator
	$(PYTHON) src/voice/pipeline.py

health: ## Check system health (API, DB, Ollama, Letta)
	$(PYTHON) scripts/brain_status.py

clean: ## Remove cache, pyc, and temp files
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	rm -rf data/sandbox_output/*
	@echo "Cleaned pycache and temp files."
