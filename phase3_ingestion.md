# SPEC: Phase 3 — Ingestion Pipelines
# Agent reads this before writing any Phase 3 code.
# This file is the contract. Code must match this spec exactly.

---

## Scope

**What this phase builds:** Automated capture pipelines for web pages, bookmarks,
YouTube transcripts, and follow-up summaries that feed the vault and vector store.

**Files the agent may create or modify in this phase:**
```
src/ingestion/web_endpoint.py
src/ingestion/youtube_ingestor.py
src/ingestion/auto_tagger.py
src/api/privacy_router.py
tests/test_phase3.py
requirements.txt          (only to add Phase 3 libraries)
```

**Files the agent must NOT touch in this phase:**
- Anything in `src/voice/`
- Anything in `src/agents/`
- `CLAUDE.md`

---

## Task 3.1 — src/ingestion/web_endpoint.py

### What to build
A FastAPI endpoint that accepts clipped web content and routes it into the ingestion pipeline.

### Interface
```python
class WebIngestPayload(BaseModel):
    url: str
    title: str
    text: str
    source: str
    tags: list[str] = []

@app.post("/ingest/web")
async def ingest_web(payload: WebIngestPayload) -> dict: ...
```

### Behaviour rules
- Validate required fields
- Reject empty `text`
- Write clipped content into a stable local artifact before ingestion
- Reuse Phase 1 chunking and storage instead of inventing a parallel path
- Slow local model calls must run off the main async event loop

---

## Task 3.2 — Bookmarklet

### What to build
A browser bookmarklet script that sends page URL, title, and selected/main text to the local endpoint.

### Behaviour rules
- Must work with minimal setup in a normal browser bookmark
- If the endpoint is unavailable, show a visible failure instead of silently doing nothing
- Payload format must match `WebIngestPayload`

### Done when
- Triggering the bookmarklet on a web page stores the article locally and ingests it

---

## Task 3.3 — src/ingestion/youtube_ingestor.py

### What to build
A YouTube transcript ingestion pipeline based on `yt-dlp`.

### Interface
```python
class YouTubeIngestor:
    def fetch_transcript(self, url: str) -> str: ...
    def normalize_transcript(self, raw_text: str) -> str: ...
    def ingest(self, url: str) -> dict: ...
```

### Behaviour rules
- Prefer transcript/subtitle extraction, not audio download
- Normalize timestamps/noise before chunking
- If no transcript is available, fail clearly and log the reason
- Store source metadata: title, URL, channel if available

---

## Task 3.4 — src/ingestion/auto_tagger.py

### What to build
A content classifier that assigns domain and content-type tags for new web and video ingests.

### Interface
```python
class AutoTagger:
    def detect_domain(self, text: str) -> str: ...
    def detect_content_type(self, source: str, text: str) -> str: ...
    def detect_sensitivity(self, text: str) -> str: ...
```

### Required outputs
- `domain`
- `content_type`
- `sensitivity`

### Behaviour rules
- Use deterministic rules first
- Mark likely private or religious content conservatively
- Tagging must be testable without a remote LLM

---

## Task 3.5 — Summary generation

### What to build
A summary step for all newly ingested web and video entries.

### Behaviour rules
- Save summaries into the vault in a predictable location
- Summary generation must obey privacy routing
- Summaries should contain source URL/title plus concise key points
- If summarization fails, raw ingestion must still succeed

---

## Task 3.6 — tests/test_phase3.py

### Required acceptance tests
- Web endpoint accepts valid payloads and rejects invalid ones
- Bookmarklet-compatible payload reaches storage
- YouTube transcript ingestion handles a transcript successfully
- Missing transcript path fails clearly
- Auto tagger assigns domain and sensitivity deterministically
- Summary generation does not block raw ingestion on failure

---

## Definition of Done for Phase 3

- Web clipping works locally
- YouTube transcript ingestion works for supported videos
- All new captured knowledge is tagged and summarized
- Privacy boundaries are enforced
- All Phase 3 tests pass
