#!/bin/bash
# smoke_test_full.sh — Validates the local environment without external APIs.
# Usage: ./scripts/smoke_test_full.sh

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

PROJECT_ROOT=$(pwd)
export PYTHONPATH=$PROJECT_ROOT

echo -e "${YELLOW}Starting Full Local Smoke Test...${NC}\n"

# 1. Check Python Environment
echo -n "1. Checking Python Environment... "
if [ -d "venv" ] && source venv/bin/activate; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}FAILED (venv missing)${NC}"
    exit 1
fi

# 2. Check System Dependencies
echo -n "2. Checking System Dependencies (PortAudio/FFmpeg)... "
if dpkg -l | grep -q libportaudio2 && command -v ffmpeg &>/dev/null; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}FAILED (Missing PortAudio or FFmpeg)${NC}"
    exit 1
fi

# 3. Import Checks (Linting)
echo -n "3. Running Import Checks (Ruff)... "
if pip show ruff &>/dev/null; then
    if ruff check . --select=E9,F63,F7,F82 --quiet; then
        echo -e "${GREEN}OK${NC}"
    else
        echo -e "${RED}FAILED (Syntax/Import errors found)${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}SKIPPED (Ruff not installed)${NC}"
fi

# 4. Check Databases
echo -n "4. Checking Vector Store (LanceDB)... "
if python3 -c "from src.ingestion.vector_store import VectorStore; VectorStore('smoke_test')" &>/dev/null; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}FAILED (LanceDB connection error)${NC}"
    exit 1
fi

# 5. Offline Model Verification
echo -n "5. Verifying Local Models (Ollama)... "
if curl -s http://localhost:11434/api/tags | grep -q "nomic-embed-text"; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}FAILED (Ollama offline or models missing)${NC}"
fi

# 6. Core Logic Tests
echo "6. Running Offline Unit Tests..."
# We explicitly run tests that don't require the cloud or heavy GPU loads
if pytest tests/test_chunker.py tests/test_vector_store.py tests/test_text_normalization.py -v --quiet; then
    echo -e "${GREEN}Unit Tests: OK${NC}"
else
    echo -e "${RED}Unit Tests: FAILED${NC}"
    exit 1
fi

echo -e "\n${GREEN}===========================================${NC}"
echo -e "${GREEN}  ✓ SMOKE TEST PASSED. ENVIRONMENT HEALTHY. ${NC}"
echo -e "${GREEN}===========================================${NC}"
