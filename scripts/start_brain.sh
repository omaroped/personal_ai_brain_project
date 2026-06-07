#!/bin/bash
# start_brain.sh — Unified startup for AI Brain services.

# ── Colors ────────────────────────────────────────────────────────────
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH=$PROJECT_ROOT

cd "$PROJECT_ROOT"

# Fast-fail runtime checks
if [ ! -d "venv" ]; then
    echo -e "${RED}Error: 'venv' directory not found.${NC}"
    echo "Please run ./scripts/bootstrap.sh first."
    exit 1
fi

if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Warning: .env file not found. Falling back to defaults.${NC}"
fi

source venv/bin/activate

echo -e "${YELLOW}Starting AI Brain Health Check...${NC}"
python3 scripts/brain_status.py

if [ $? -ne 0 ]; then
    echo -e "${YELLOW}Trying to start Docker services...${NC}"
    cd docker && sudo docker-compose up -d && cd ..
    echo "Waiting for services to initialize (15s)..."
    sleep 15
fi

# Run validation again
python3 scripts/brain_status.py || exit 1

echo -e "${GREEN}Services are ONLINE.${NC}"

# Kill any existing processes
fuser -k 8001/tcp &>/dev/null || true
pkill -f "python3 src/api/main.py" || true
pkill -f "python3 src/voice/daemon.py" || true
pkill -f "python3 src/voice/pipeline.py" || true

echo -e "${YELLOW}Starting Master API in background...${NC}"
nohup python3 src/api/main.py > /dev/null 2>&1 &
sleep 5 # Wait for API to boot before daemon connects

echo -e "${GREEN}Brain is ready! Starting Voice Daemon...${NC}"
echo -e "Press Ctrl+C to shutdown."

python3 src/voice/daemon.py
