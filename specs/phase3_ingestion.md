# Phase 3 Spec: Ingestion Pipelines

## Goal
Automate the capture of new knowledge from the web, local files, and video platforms.

## Components
- **Browser Bookmarklet:** Sends URL/Title/Text to the brain.
- **FastAPI Ingestion API:** Processes incoming web data.
- **Auto-PDF Processor:** Monitors `~/Documents` for new research/handbooks.
- **YouTube Fetcher:** Ingests video transcripts.

## Tasks
1. [ ] Develop JS Bookmarklet for web clipping.
2. [ ] Build FastAPI `POST /ingest` endpoint.
3. [ ] Integrate `pymupdf` for high-quality text extraction.
4. [ ] Build `yt-dlp` transcript ingestion service.
5. [ ] Automate summary generation for all new entries.

## Validation
- Adding a new web article or PDF results in its summary appearing in the `vault/summaries` folder within 60 seconds.
