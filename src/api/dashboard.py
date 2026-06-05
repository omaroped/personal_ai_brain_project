# MODULE: Minimal FastAPI shell for the local project dashboard.
"""Dashboard API for monitoring health, ingestion, and search status."""

from __future__ import annotations

from dataclasses import asdict

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from src.common.health import collect_core_health

app = FastAPI(title="Personal AI Brain Dashboard")


@app.get("/", response_class=HTMLResponse)
async def root():
    """Placeholder for the dashboard home page."""
    return """
    <html>
        <head><title>Brain Dashboard</title></head>
        <body>
            <h1>Personal AI Brain Dashboard</h1>
            <ul>
                <li><a href="/health">Health Status</a></li>
                <li><a href="/ingestion">Ingestion Status</a></li>
                <li><a href="/search">Search Interface</a></li>
                <li><a href="/memory">Memory Status</a></li>
            </ul>
        </body>
    </html>
    """


@app.get("/health")
async def health_status():
    """Return the health status of core dependencies."""
    return {"health": [asdict(status) for status in collect_core_health()]}


@app.get("/ingestion")
async def ingestion_status():
    """Placeholder for ingestion pipeline status."""
    return {"status": "Ingestion status integration pending."}


@app.get("/search")
async def search_interface():
    """Placeholder for search interface status."""
    return {"status": "Search interface integration pending."}


@app.get("/memory")
async def memory_status():
    """Placeholder for Letta memory status."""
    return {"status": "Memory status integration pending."}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8002)
