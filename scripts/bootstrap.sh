#!/bin/bash
# bootstrap.sh — Personal AI Brain Project Setup
# Run ONCE to create the full project structure and verify the environment.

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

PROJECT_ROOT=$(pwd)

# Read required version from .python-version, defaulting to 3.10 if missing
if [ -f "$PROJECT_ROOT/.python-version" ]; then
    REQUIRED_PYTHON_VERSION=$(cat "$PROJECT_ROOT/.python-version" | tr -d '[:space:]')
else
    REQUIRED_PYTHON_VERSION="3.10.12"
fi

# Extract major.minor for the command
PYTHON_CMD="python${REQUIRED_PYTHON_VERSION%.*}"

echo -e "${GREEN}Starting Personal AI Brain Bootstrap...${NC}"

# 1. Strict Python version check
echo -n "Checking Python version ($REQUIRED_PYTHON_VERSION)... "
if ! command -v $PYTHON_CMD &>/dev/null; then
    echo -e "\n${RED}✗ $PYTHON_CMD is required. Please install it first.${NC}"
    echo "  Suggested fix: sudo apt-get install $PYTHON_CMD $PYTHON_CMD-venv $PYTHON_CMD-dev"
    exit 1
fi

ACTUAL_VERSION=$($PYTHON_CMD -c 'import platform; print(platform.python_version())')
if [ "$ACTUAL_VERSION" != "$REQUIRED_PYTHON_VERSION" ]; then
    echo -e "\n${YELLOW}⚠ Warning: Found Python $ACTUAL_VERSION. Recommended is $REQUIRED_PYTHON_VERSION.${NC}"
else
    echo -e "${GREEN}OK ($ACTUAL_VERSION)${NC}"
fi

# 2. Setup Virtual Environment
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    $PYTHON_CMD -m venv venv
fi

source venv/bin/activate
pip install --upgrade pip --quiet

# 3. Install Requirements
echo -e "${YELLOW}Installing dependencies...${NC}"
if [ -f "requirements-core.txt" ]; then
    pip install -r requirements-core.txt -r requirements-voice.txt -r requirements-agents.txt -r requirements-dev.txt --quiet
elif [ -f "requirements.txt" ]; then
    pip install -r requirements.txt --quiet
else
    echo -e "${RED}✗ requirements files missing.${NC}"
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

echo -e "${YELLOW}Validating runtime environment...${NC}"
python scripts/validate_environment.py || true

echo -e "${GREEN}Bootstrap complete! You can now run ./scripts/start_brain.sh${NC}"
