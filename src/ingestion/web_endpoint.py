# MODULE: FastAPI server for receiving browser clippings and running immediate ingestion.
"""FastAPI endpoint to ingest web clippings into the AI Brain."""

from __future__ import annotations

from datetime import datetime
import logging
from pathlib import Path
import re

from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel

from config import FASTAPI_HOST, FASTAPI_PORT, VAULT_DIR
from src.common.logging_utils import configure_logging
from src.ingestion.pipeline import IngestionPipeline
from src.ingestion.youtube_ingestor import download_and_parse_transcript, YouTubeIngestionError

LOGGER = configure_logging(__name__)

app = FastAPI(title="Personal AI Brain Ingestion API")

# Shared pipeline instance
# Note: IngestionPipeline initialization warms up embedder. If Ollama is offline,
# this might raise an error. We want to handle initialization gracefully.
pipeline = IngestionPipeline()


class WebPayload(BaseModel):
    """Pydantic schema representing the clipping sent from the browser bookmarklet."""

    url: str
    title: str
    selected: str | None = None
    body: str


def run_background_ingest(filepath: Path) -> None:
    """Run file ingestion in the background to avoid blocking the API client.

    Parameters:
        filepath: Path to the written file.
    """
    try:
        LOGGER.info("Starting background ingestion for file: %s", filepath)
        result = pipeline.ingest_file(filepath)
        LOGGER.info("Background ingestion completed for %s: %s", filepath.name, result)
    except Exception as exc:
        LOGGER.error("Failed background ingestion for %s: %s", filepath.name, exc)


@app.post("/ingest/web")
async def ingest_web(payload: WebPayload, background_tasks: BackgroundTasks) -> dict:
    """Ingest web clipping payload from the browser bookmarklet.

    Parameters:
        payload: Received WebPayload object.
        background_tasks: FastAPI background tasks queue.

    Returns:
        dict: Ingestion acknowledgement status and path.
    """
    # 1. Validate payload
    if not payload.url or not payload.title or not payload.body:
        raise HTTPException(status_code=400, detail="Missing required payload fields (url, title, body).")

    # 2. Format filename safely
    # Clean the title of unsafe filename characters
    safe_title = re.sub(r"[^a-zA-Z0-9_\-]", "_", payload.title)
    safe_title = safe_title[:50].strip("_")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"web_{safe_title}_{timestamp}.md"

    # Ensure web_clippings folder exists inside the vault
    clippings_dir = VAULT_DIR / "web_clippings"
    clippings_dir.mkdir(parents=True, exist_ok=True)
    filepath = clippings_dir / filename

    # 3. Format markdown content
    selected_passage = payload.selected.strip() if payload.selected else ""
    selected_section = f"- **Selected Passage:**\n{selected_passage}\n\n" if selected_passage else ""

    markdown_content = (
        f"# {payload.title}\n"
        f"- **URL:** {payload.url}\n"
        f"{selected_section}"
        f"{payload.body}\n"
    )

    try:
        # 4. Save markdown file
        filepath.write_text(markdown_content, encoding="utf-8")
        LOGGER.info("Saved web clipping to %s", filepath)
    except Exception as exc:
        LOGGER.error("Failed to write web clipping file %s: %s", filepath, exc)
        raise HTTPException(status_code=500, detail=f"Failed to save clipping: {exc}")

    # 5. Enqueue background ingestion task
    background_tasks.add_task(run_background_ingest, filepath)

    return {
        "status": "ok",
        "message": "Web clipping saved. Ingestion queued in background.",
        "file": str(filepath),
    }


@app.post("/ingest/youtube")
async def ingest_youtube(url: str, background_tasks: BackgroundTasks) -> dict:
    """Ingest a YouTube transcript by video URL.

    Parameters:
        url: The YouTube video URL.
        background_tasks: FastAPI background tasks queue.

    Returns:
        dict: Ingestion acknowledgement status and path.
    """
    if not url.strip():
        raise HTTPException(status_code=400, detail="Missing YouTube video URL.")

    try:
        # Download and clean the transcript
        LOGGER.info("Fetching transcript for video: %s", url)
        data = download_and_parse_transcript(url)
    except YouTubeIngestionError as exc:
        LOGGER.error("Failed to download YouTube transcript for %s: %s", url, exc)
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        LOGGER.error("Unexpected error fetching YouTube transcript for %s: %s", url, exc)
        raise HTTPException(status_code=500, detail=f"Unexpected error: {exc}")

    # Ensure youtube_clippings directory exists inside the vault
    youtube_dir = VAULT_DIR / "youtube_clippings"
    youtube_dir.mkdir(parents=True, exist_ok=True)
    
    video_id = data["video_id"]
    filepath = youtube_dir / f"yt_{video_id}.md"

    # Format transcript markdown
    markdown_content = (
        f"# {data['title']}\n"
        f"- **URL:** {data['url']}\n"
        f"- **Channel:** {data['channel']}\n"
        f"- **Video ID:** {video_id}\n\n"
        f"## Transcript\n"
        f"{data['transcript']}\n"
    )

    try:
        # Save transcript file
        filepath.write_text(markdown_content, encoding="utf-8")
        LOGGER.info("Saved YouTube transcript clipping to %s", filepath)
    except Exception as exc:
        LOGGER.error("Failed to write YouTube clipping file %s: %s", filepath, exc)
        raise HTTPException(status_code=500, detail=f"Failed to save YouTube clipping: {exc}")

    # Enqueue background ingestion task
    background_tasks.add_task(run_background_ingest, filepath)

    return {
        "status": "ok",
        "message": "YouTube transcript clipping saved. Ingestion queued in background.",
        "file": str(filepath),
    }


if __name__ == "__main__":
    import uvicorn
    LOGGER.info("Starting Ingestion API server on %s:%s", FASTAPI_HOST, FASTAPI_PORT)
    uvicorn.run(app, host=FASTAPI_HOST, port=FASTAPI_PORT)
