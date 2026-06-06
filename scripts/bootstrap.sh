#!/bin/bash
# bootstrap.sh — Personal AI Brain Project Setup
# Run ONCE to create the full project structure and verify the environment.

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

PROJECT_ROOT=$(pwd)
PYTHON="python3.11"

echo -e "${GREEN}Starting Personal AI Brain Bootstrap...${NC}"

# 1. Check Python version
if ! command -v $PYTHON &>/dev/null; then
    echo -e "${RED}✗ Python 3.11 is required. Please install it first.${NC}"
    exit 1
fi

# 2. Setup Virtual Environment
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    $PYTHON -m venv venv
fi

source venv/bin/activate
pip install --upgrade pip --quiet

# 3. Install Requirements
echo -e "${YELLOW}Installing dependencies...${NC}"
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt --quiet
else
    echo -e "${RED}✗ requirements.txt missing.${NC}"
    exit 1
fi

# 4. Check Docker & Ollama
if ! command -v docker &>/dev/null; then
    echo -e "${RED}✗ Docker is required for Letta memory. Please install it.${NC}"
fi

if ! command -v ollama &>/dev/null; then
    echo -e "${RED}✗ Ollama is required for local models. Please install it.${NC}"
else
    echo -e "${YELLOW}Pulling required Ollama models...${NC}"
    ollama pull nomic-embed-text || true
    ollama pull deepseek-r1:7b || true
fi

# 5. Environment Config
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env file from template...${NC}"
    cp .env.example .env
fi

echo -e "${GREEN}Bootstrap complete! You can now run ./scripts/start_brain.sh${NC}"
