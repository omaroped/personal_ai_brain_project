#!/bin/bash
# start_brain.sh — Unified startup for AI Brain services.

# ── Colors ────────────────────────────────────────────────────────────
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PROJECT_ROOT="/home/omar/personal_ai_brain_project"
export PYTHONPATH=$PROJECT_ROOT

cd "$PROJECT_ROOT"
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

# Kill any existing API process on port 8001
fuser -k 8001/tcp &>/dev/null || true

echo -e "${YELLOW}Starting Master API in background...${NC}"
python3 src/api/main.py &

echo -e "${GREEN}Brain is ready! Starting Voice Pipeline...${NC}"
echo -e "Press Ctrl+Alt+V to talk. Press Ctrl+C to shutdown."

python3 src/voice/pipeline.py
