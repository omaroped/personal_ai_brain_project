# MODULE: Primary FastAPI application entry point for the AI Brain.
"""Main API entry point coordinating ingestion, memory, and agency."""

from __future__ import annotations

import logging
from dataclasses import asdict
from fastapi import FastAPI, HTTPException, Query, Request, Form, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import sounddevice as sd
import json
import time

import config
from src.common.logging_utils import configure_logging
from src.common.health import collect_core_health
from src.api.privacy_router import choose_model_route
from src.ingestion.vector_store import VectorStore
from src.memory.letta_agent import OmarBrainAgent
from src.memory.openclaw_agent import OpenClawAgent
from src.agents.planner import TaskPlanner
from src.api.ws_manager import manager as ws_manager

# Import existing routers/apps
from src.ingestion.web_endpoint import app as ingestion_app

LOGGER = configure_logging(__name__)

app = FastAPI(title="Personal AI Brain - Master API")

# Setup templates and static files
app.mount("/static", StaticFiles(directory="src/api/static"), name="static")
templates = Jinja2Templates(directory="src/api/templates")

# Mount specialized APIs
app.mount("/ingest", ingestion_app)

# Global Agents
letta_agent = OmarBrainAgent()
openclaw_agent = OpenClawAgent()
task_planner = TaskPlanner()

class IdentityManager:
    """Centralizes routing logic previously tangled in the voice pipeline."""
    @staticmethod
    def handle_input(transcript: str) -> str:
        # Check if it's an action command
        action_keywords = ["open", "search", "find", "summarize", "read", "run", "execute", "notify", "remind", "delegate"]
        first_word = transcript.split()[0].lower() if transcript else ""
        is_action = first_word in action_keywords or "open" in transcript.lower()

        if is_action:
            LOGGER.info("Action detected. Routing to Task Planner: '%s'", transcript)
            goal = f"The user just said via voice: '{transcript}'. Execute tools if necessary and return a spoken summary."
            return task_planner.execute(goal)

        # Read settings
        turbo_mode = False
        openclaw_mode = True
        if config.SETTINGS_FILE.exists():
            try:
                with open(config.SETTINGS_FILE, "r") as f:
                    settings = json.load(f)
                    turbo_mode = settings.get("turbo", False)
                    openclaw_mode = settings.get("openclaw", True)
            except Exception: pass

        # OpenClaw
        if openclaw_mode:
            response = openclaw_agent.send_message(transcript)
            if "Error:" not in response and "trouble connecting" not in response:
                return response
            LOGGER.warning("OpenClaw bypass failed: %s", response)

        # Gemini
        if turbo_mode and config.GEMINI_API_KEY:
            LOGGER.info("Turbo Mode active. Routing to Gemini...")
            try:
                import google.generativeai as genai
                genai.configure(api_key=config.GEMINI_API_KEY)
                model = genai.GenerativeModel('gemini-1.5-flash')
                return model.generate_content(transcript).text
            except Exception as e:
                LOGGER.error("Gemini Turbo failed: %s", e)

        # Letta
        return letta_agent.send_message(transcript)

@app.websocket("/ws/voice")
async def websocket_voice_endpoint(websocket: WebSocket):
    """WebSocket endpoint for the decoupled Voice Daemon."""
    await ws_manager.connect(websocket)
    try:
        while True:
            # Expecting JSON: {"type": "transcript", "text": "Hello"}
            data = await websocket.receive_text()
            payload = json.loads(data)

            if payload.get("type") == "transcript":
                transcript = payload.get("text", "")
                LOGGER.info("Received transcript via WS: %s", transcript)

                await ws_manager.broadcast_status("thinking")

                # Process through IdentityManager
                start_query = time.perf_counter()
                response_text = IdentityManager.handle_input(transcript)
                duration_query = (time.perf_counter() - start_query) * 1000

                LOGGER.info("Brain responded: '%s' [%.2fms]", response_text, duration_query)

                # Send response back to daemon to play
                await websocket.send_text(json.dumps({
                    "type": "tts_response",
                    "text": response_text
                }))

                # Send back to idle state
                await ws_manager.broadcast_status("idle")

    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        LOGGER.error("WebSocket error: %s", e)
        ws_manager.disconnect(websocket)

@app.get("/", response_class=HTMLResponse)


class BrainRequest(BaseModel):
    """Input for conversational brain queries."""
    input: str
    agent_id: str | None = None
    turbo: bool = False

@app.get("/", response_class=HTMLResponse)
async def dashboard_home(request: Request):
    """Serve the modern glassmorphism dashboard."""
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/auth/authorize", response_class=HTMLResponse)
async def authorize_app(request: Request, app_name: str = "External App", redirect_uri: str = "http://localhost:8080"):
    """OAuth-style authorization screen."""
    return templates.TemplateResponse("authorize.html", {
        "request": request, 
        "app_name": app_name,
        "redirect_uri": redirect_uri
    })

@app.post("/auth/approve")
async def approve_app(
    request: Request, 
    app_name: str = Form(...), 
    redirect_uri: str = Form(...)
):
    """Handle app approval and redirect back or show success page."""
    LOGGER.info("User approved connection for app: %s", app_name)
    
    # If the redirect is the default test port and nothing is listening,
    # it's better to show our own success page.
    if "localhost:8080" in redirect_uri:
        return templates.TemplateResponse("authorized.html", {
            "request": request, 
            "app_name": app_name
        })

    return RedirectResponse(url=f"{redirect_uri}?status=authorized&brain_id=omar_brain", status_code=303)

@app.get("/auth/success", response_class=HTMLResponse)
async def auth_success(request: Request, app_name: str = "External App"):
    """Standalone success page."""
    return templates.TemplateResponse("authorized.html", {
        "request": request, 
        "app_name": app_name
    })

@app.get("/health")
async def health_status():
    """Return the health status of core dependencies."""
    return {"health": [asdict(status) for status in collect_core_health()]}

@app.get("/search")
async def search_vault(
    q: str = Query(..., description="Semantic search query"),
    domain: str = Query(None, description="Domain filter (optional)"),
    top_k: int = Query(5, description="Number of results to return"),
):
    """
    Unified search endpoint used by Letta custom tools and the voice pipeline.
    Privacy router enforces domain restrictions.
    """
    try:
        # 1. Enforce privacy routing
        decision = choose_model_route(domain)
        LOGGER.info("Search requested: '%s' | Domain: %s | Route: %s", q, domain, decision.route)
        
        # 2. Select appropriate vector store based on domain
        db_name = "personal" if domain == "personal" else "documents"
        store = VectorStore(db_name)
        
        # 3. Perform hybrid search
        results = store.hybrid_search(q, top_k=top_k)
        
        return {
            "query": q,
            "domain": domain,
            "route": decision.route,
            "results": [asdict(r) for r in results]
        }
    except Exception as exc:
        LOGGER.error("Search endpoint failed: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))

@app.post("/brain")
async def query_brain(request: BrainRequest):
    """
    Conversational endpoint that routes user input to the persistent Letta agent.
    If turbo is True, it will attempt to use Gemini for speed.
    """
    try:
        if request.turbo and config.GEMINI_API_KEY:
            LOGGER.info("Turbo Mode: Querying Gemini directly...")
            # Direct Gemini call for speed
            import google.generativeai as genai
            genai.configure(api_key=config.GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Simple direct response (bypass Letta for speed)
            response = model.generate_content(request.input)
            return {
                "input": request.input,
                "mode": "turbo",
                "response": response.text
            }

        # Ensure agent is ready
        if not letta_agent.agent_id:
            letta_agent.ensure_agent()
        
        # Send message and get response
        response = letta_agent.send_message(request.input)
        
        return {
            "input": request.input,
            "agent_id": letta_agent.agent_id,
            "mode": "standard",
            "response": response
        }
    except Exception as exc:
        LOGGER.error("Brain endpoint failed: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to communicate with Letta brain.")

@app.get("/memory/stream")
async def get_memory_stream(limit: int = 10):
    """Return the last few interactions from the JSONL session logs."""
    from datetime import date
    import json
    log_file = config.LOGS_DIR / "sessions" / f"{date.today().isoformat()}.jsonl"
    if not log_file.exists():
        return {"stream": []}
    
    entries = []
    try:
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    entries.append(json.loads(line))
    except Exception as e:
        LOGGER.error("Failed to read session logs for dashboard: %s", e)
    
    return {"stream": entries[-limit:][::-1]} # Newest first

@app.get("/audio/devices")
async def get_audio_devices():
    """List available audio input devices."""
    return {"devices": list_input_devices()}

@app.get("/audio/settings")
async def get_audio_settings():
    """Get current audio settings."""
    if config.SETTINGS_FILE.exists():
        with open(config.SETTINGS_FILE, "r") as f:
            return json.load(f)
    return {"mic_index": None}

@app.post("/audio/settings")
async def update_audio_settings(settings: dict):
    """Update audio settings (e.g., mic_index)."""
    current_settings = {}
    if config.SETTINGS_FILE.exists():
        with open(config.SETTINGS_FILE, "r") as f:
            current_settings = json.load(f)
    
    current_settings.update(settings)
    
    with open(config.SETTINGS_FILE, "w") as f:
        json.dump(current_settings, f)
    
    LOGGER.info("Updated audio settings: %s", current_settings)
    return {"status": "success", "settings": current_settings}

@app.post("/voice/trigger")
async def trigger_voice_interaction():
    """Programmatic trigger for the voice pipeline (Click-to-Talk)."""
    try:
        # Use a temporary file as a signal for the VoicePipeline
        trigger_file = config.DATA_DIR / "voice_trigger.tmp"
        trigger_file.touch()
        LOGGER.info("External voice trigger received via Dashboard.")
        return {"status": "triggered"}
    except Exception as e:
        LOGGER.error("Failed to trigger voice: %s", e)
        raise HTTPException(status_code=500, detail="Failed to trigger voice interaction.")

if __name__ == "__main__":
    import uvicorn
    LOGGER.info("Starting Master API server on %s:%s", config.FASTAPI_HOST, config.FASTAPI_PORT)
    uvicorn.run(app, host=config.FASTAPI_HOST, port=config.FASTAPI_PORT)
