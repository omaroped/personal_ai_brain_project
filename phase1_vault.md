# SPEC: Phase 1 — The Vault
# Agent reads this before writing any Phase 1 code.
# This file is the contract. Code must match this spec exactly.

---

## Scope

**What this phase builds:** A searchable local knowledge base that automatically ingests
PDFs, markdown files, and text documents and allows semantic + keyword search over them.

**Files the agent may create or modify in this phase:**
```
config.py
src/ingestion/watcher.py
src/ingestion/pdf_extractor.py
src/ingestion/chunker.py
src/ingestion/embedder.py
src/ingestion/vector_store.py
src/ingestion/pipeline.py
query.py
tests/test_phase1.py
requirements.txt (only to add Phase 1 libraries)
```

**Files the agent must NOT touch in this phase:**
- Anything in `src/memory/`
- Anything in `src/voice/`
- Anything in `src/agents/`
- `docker/docker-compose.yml` (already written)
- `CLAUDE.md`

---

## Task 1.0 — Bootstrap

### Commands to run (in order)
```bash
cd /home/omar/personal_ai_brain_project
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start Docker services
docker compose -f docker/docker-compose.yml up -d
sleep 5

# Verify services
curl http://localhost:11434/api/tags              # Ollama
curl http://localhost:8283/health                 # Letta
curl http://localhost:8001/health 2>/dev/null || echo "FastAPI not started yet (OK)"

# Pull Ollama models
ollama pull mistral
ollama pull nomic-embed-text

# Pre-download silero-vad (Phase 4 prep, do it now while online)
python -c "import torch; torch.hub.load('snakers4/silero-vad', 'silero_vad')"
```

### Done when
- `pip install` completes with no errors
- Both curl health checks return 200
- Both ollama models show in `ollama list`

---

## Task 1.1 — config.py

### What to build
A single file with all constants. No logic, no functions. Just paths and settings.

### Required contents
```python
# MODULE: Central configuration — all paths and settings for the AI Brain project
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── Paths ──────────────────────────────────────────────────────
PROJECT_ROOT    = Path("/home/omar/personal_ai_brain_project")
DATA_DIR        = PROJECT_ROOT / "data"
VAULT_DIR       = DATA_DIR / "vault"
VECTORDB_DIR    = DATA_DIR / "vectordb"
LOGS_DIR        = DATA_DIR / "logs"

# Watched folders — watcher monitors these for new files
WATCH_DIRS = [
    Path("/home/omar/Documents"),
    Path("/home/omar/Downloads"),
    VAULT_DIR,
]

# ── LanceDB tables ─────────────────────────────────────────────
LANCEDB_DOCUMENTS   = VECTORDB_DIR / "documents"
LANCEDB_PERSONAL    = VECTORDB_DIR / "personal"
LANCEDB_CONVOS      = VECTORDB_DIR / "conversations"
LANCEDB_ERRORS      = VECTORDB_DIR / "errors"

# ── Models ─────────────────────────────────────────────────────
OLLAMA_BASE_URL     = "http://localhost:11434"
EMBED_MODEL         = "nomic-embed-text"
EMBED_DIMENSIONS    = 768
LOCAL_LLM_MODEL     = "mistral"
CLOUD_LLM_MODEL     = "claude-sonnet-4-20250514"

# ── Chunking ───────────────────────────────────────────────────
CHUNK_SIZE_DEFAULT       = 512   # tokens
CHUNK_OVERLAP_DEFAULT    = 80    # tokens (~15%)
CHUNK_SIZE_RELIGIOUS     = 256
CHUNK_OVERLAP_RELIGIOUS  = 64
CHUNK_SIZE_LECTURE       = 600
CHUNK_OVERLAP_LECTURE    = 60

# ── Privacy ────────────────────────────────────────────────────
CLOUD_BLOCKED_DOMAINS = {"personal", "religion"}

# ── API ────────────────────────────────────────────────────────
FASTAPI_PORT = 8001

# ── Letta ──────────────────────────────────────────────────────
LETTA_BASE_URL    = "http://localhost:8283"
LETTA_AGENT_NAME  = "omar_brain"

# ── Secrets (from .env) ────────────────────────────────────────
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
```

### Done when
- `python config.py` runs with no errors
- All paths are `pathlib.Path` objects
- No hardcoded strings appear anywhere else in the codebase (use these constants)

---

## Task 1.2 — src/ingestion/watcher.py

### What to build
A `FileWatcher` class that monitors `WATCH_DIRS` for new or modified files,
debounces duplicate events, and pushes file paths to a queue.

### Interface (exact signatures)
```python
class FileWatcher:
    def __init__(self, queue: Queue, watch_dirs: list[Path]): ...
    def start(self) -> None: ...  # blocking — runs in a thread
    def stop(self) -> None: ...

class IngestionEventHandler(FileSystemEventHandler):
    def on_created(self, event) -> None: ...
    def on_modified(self, event) -> None: ...
    def _debounce(self, path: str) -> bool: ...  # returns True if should process
```

### Behaviour rules
- Only process files with extensions: `.pdf`, `.md`, `.txt`, `.docx`
- Debounce: ignore events for a path if the same path fired within the last 2 seconds
- Use a SQLite database at `data/ingestion_index.db` to track ingested file hashes
- If a file hash already exists in the index → skip (already ingested)
- Log every accepted file at INFO level: `"New file queued: {filename}"`
- Log every skipped file at DEBUG level: `"Skipping duplicate: {filename}"`

### Libraries
```
watchdog==4.0.x
```

---

## Task 1.3 — src/ingestion/pdf_extractor.py

### What to build
A `PDFExtractor` class that extracts clean text from PDFs with page-level metadata.

### Interface
```python
@dataclass
class ExtractedPage:
    text: str
    page_number: int
    source_file: str
    document_title: str
    is_scanned: bool

class PDFExtractor:
    def extract(self, pdf_path: Path) -> list[ExtractedPage]: ...
    def _is_scanned(self, page) -> bool: ...
    def _detect_title(self, pdf_path: Path) -> str: ...
```

### Behaviour rules
- Use `pymupdf` (import as `fitz`) for extraction
- Detect scanned pages: if `page.get_text()` is empty or < 50 chars, it's likely scanned
- For scanned pages: set `is_scanned=True` and use pytesseract if available;
  if pytesseract not installed, log a WARNING and skip the page (don't crash)
- Strip reference sections: if a page's first line matches `References|Bibliography|Works Cited`
  (case-insensitive), skip that page and all remaining pages
- Document title: use PDF metadata `doc.metadata.get("title")` if available,
  else use the filename without extension
- Handle corrupt PDFs: catch `fitz.FileDataError` and log WARNING, return empty list

### Libraries
```
pymupdf==1.24.x
pytesseract  (optional — graceful degradation if not installed)
```

---

## Task 1.4 — src/ingestion/chunker.py

### What to build
A `Chunker` class that splits extracted text into semantically meaningful chunks.

### Interface
```python
@dataclass
class Chunk:
    text: str           # clean text for embedding
    display_text: str   # text with source header prepended (for display only)
    source_file: str
    page_number: int
    section: str        # detected section heading or "Unknown"
    chunk_index: int    # position in document
    domain: str         # auto-detected (psychology, religion, ai_tech, etc.)
    content_type: str   # book, article, transcript, note

class Chunker:
    def chunk(self, pages: list[ExtractedPage], filepath: Path) -> list[Chunk]: ...
    def _detect_domain(self, text: str) -> str: ...
    def _detect_content_type(self, text: str, filepath: Path) -> str: ...
    def _get_chunk_size(self, domain: str, content_type: str) -> tuple[int, int]: ...
```

### Chunking strategy (implement exactly this)

**Step 1:** Concatenate all page texts, tracking page boundaries.

**Step 2:** Split on structural markers first:
- Markdown: split on `\n## ` and `\n### ` headings
- PDF: detect headings by checking if a line is < 80 chars, ends without period,
  and is followed by paragraph text

**Step 3:** Within each structural section, apply `RecursiveCharacterTextSplitter`
from `langchain_text_splitters` using the domain-appropriate chunk size.

**Step 4:** For each chunk, prepend the display header (NOT embedded, only for display):
```
[Source: {document_title} | Section: {section} | Page: {page_number}]
```

**Step 5:** Domain detection via keyword matching (use DOMAIN_KEYWORDS dict below):
```python
DOMAIN_KEYWORDS = {
    "psychology":  ["Freud", "ego", "cognitive", "behavioral", "therapy",
                    "schema", "attachment", "neuroscience", "memory", "perception"],
    "religion":    ["Allah", "Quran", "Qur'an", "hadith", "tafsir", "fiqh",
                    "theology", "Islamic", "prayer", "salah", "sunnah"],
    "ai_tech":     ["neural", "transformer", "embedding", "gradient", "model",
                    "algorithm", "dataset", "training", "inference", "LLM"],
    "education":   ["lecture", "exam", "assignment", "university", "course",
                    "semester", "syllabus", "module", "professor"],
    "personal":    ["today", "I feel", "my goal", "I made a mistake",
                    "I learned", "tomorrow I will"],
}
```
Assign the domain with the most keyword matches. Default: `"general"`.

### Libraries
```
langchain-text-splitters==0.3.x
```

---

## Task 1.5 — src/ingestion/embedder.py

### What to build
An `Embedder` class that converts chunks to vector embeddings using Ollama.

### Interface
```python
class Embedder:
    def __init__(self): ...          # warmup Ollama on init
    def embed(self, text: str) -> list[float]: ...
    def embed_batch(self, texts: list[str], batch_size: int = 10) -> list[list[float]]: ...
```

### Behaviour rules
- Embed only `chunk.text` (not `display_text`) — the header pollutes the embedding
- Batch size: 10 chunks per Ollama request (balance between speed and memory)
- On Ollama timeout (>10s): retry up to 3 times with exponential backoff
- Log embedding progress at INFO: `"Embedded {n}/{total} chunks from {filename}"`
- Warmup on init: send one dummy request and wait for response before returning

### Libraries
```
ollama==0.3.x
```

---

## Task 1.6 — src/ingestion/vector_store.py

### What to build
A `VectorStore` class wrapping LanceDB with read/write operations and hybrid search.

### Interface
```python
class VectorStore:
    def __init__(self, table_name: str): ...   # "documents", "personal", etc.
    def add(self, chunks: list[Chunk], vectors: list[list[float]]) -> None: ...
    def search(self, query: str, top_k: int = 5, domain_filter: str = None) -> list[SearchResult]: ...
    def hybrid_search(self, query: str, top_k: int = 5) -> list[SearchResult]: ...
    def count(self) -> int: ...
    def already_ingested(self, file_hash: str) -> bool: ...

@dataclass
class SearchResult:
    text: str
    display_text: str
    source_file: str
    page_number: int
    domain: str
    score: float          # 0.0 to 1.0
```

### Schema (use this exactly — see ERRORS.md PRE-08)
```python
import pyarrow as pa
LANCEDB_SCHEMA = pa.schema([
    pa.field("id",            pa.string()),
    pa.field("text",          pa.string()),
    pa.field("display_text",  pa.string()),
    pa.field("vector",        pa.list_(pa.float32(), 768)),
    pa.field("source_file",   pa.string()),
    pa.field("page_number",   pa.int32()),
    pa.field("section",       pa.string()),
    pa.field("chunk_index",   pa.int32()),
    pa.field("domain",        pa.string()),
    pa.field("content_type",  pa.string()),
    pa.field("file_hash",     pa.string()),
    pa.field("created_at",    pa.string()),
])
```

### Hybrid search implementation
```python
def hybrid_search(self, query: str, top_k: int = 5) -> list[SearchResult]:
    """Combine vector search + BM25 keyword search using Reciprocal Rank Fusion."""
    query_vector = self.embedder.embed(query)

    # Vector search
    vector_results = self.table.search(query_vector).limit(top_k * 2).to_list()

    # Keyword search (BM25 full-text search)
    text_results = self.table.search(query, query_type="fts").limit(top_k * 2).to_list()

    # Reciprocal Rank Fusion
    merged = self._rrf_merge(vector_results, text_results, k=60)
    return merged[:top_k]

def _rrf_merge(self, list_a, list_b, k=60) -> list:
    """Merge two ranked lists using RRF scoring."""
    scores = {}
    for rank, item in enumerate(list_a):
        scores[item["id"]] = scores.get(item["id"], 0) + 1 / (k + rank + 1)
    for rank, item in enumerate(list_b):
        scores[item["id"]] = scores.get(item["id"], 0) + 1 / (k + rank + 1)
    sorted_ids = sorted(scores, key=scores.get, reverse=True)
    # Reconstruct result objects from sorted IDs
    ...
```

### Write locking (see ERRORS.md PRE-01)
Wrap all `table.add()` calls with `fasteners.InterProcessLock('/tmp/lancedb_write.lock')`.

### Libraries
```
lancedb==0.8.x
pyarrow==16.x
fasteners==0.19
```

---

## Task 1.7 — src/ingestion/pipeline.py

### What to build
The orchestrator that wires watcher → extractor → chunker → embedder → vector_store
into a single running pipeline.

### Interface
```python
class IngestionPipeline:
    def __init__(self): ...
    def start(self) -> None: ...   # starts watcher, processes queue in background
    def ingest_file(self, filepath: Path) -> dict: ...  # returns stats dict
    def ingest_directory(self, dirpath: Path) -> dict: ... # bulk ingest

def main():
    """Entry point: start the pipeline and keep it running."""
```

### Behaviour rules
- Queue worker runs in a daemon thread
- If ingest_file fails: log ERROR, write to ERRORS.md, continue (don't crash the pipeline)
- Print stats after each file: `"✅ {filename}: {n} chunks ingested in {t:.1f}s"`
- On startup, run `ingest_directory` on VAULT_DIR to catch any files added while offline

---

## Task 1.8 — tests/test_phase1.py

### The 5 mandatory acceptance tests

```python
def test_watcher_detects_new_pdf():
    """Drop a PDF, confirm it appears in LanceDB within 15 seconds."""

def test_no_duplicate_ingestion():
    """Drop the same PDF twice, confirm only one set of chunks exists."""

def test_arabic_pdf_extraction():
    """Extract text from a PDF with Arabic content, confirm non-empty result."""

def test_hybrid_search_finds_known_content():
    """Search for a phrase known to be in an ingested PDF, confirm top result."""

def test_domain_tagging_accuracy():
    """Ingest a psychology text, confirm domain tag is 'psychology'."""
```

All 5 tests must pass. No partial credit.

---

## Task 1.9 — query.py (CLI)

### What to build
A command-line tool for searching the vault from the terminal.

### Usage
```bash
# Basic search
python query.py "what is cognitive dissonance"

# Domain-filtered search
python query.py "consciousness" --domain psychology

# Limit results
python query.py "Allah mercy" --domain religion --top 3
```

### Output format
```
🔍 Query: "what is cognitive dissonance"
📚 Results from: documents table

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[1] Score: 0.94 | Source: cognitive_psychology.pdf | Page: 47
    Section: Chapter 3 — Attitude Change

    Cognitive dissonance refers to the mental discomfort experienced when
    a person holds two or more contradictory beliefs simultaneously...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[2] Score: 0.87 | Source: ...
```

---

## Phase 1 Definition of Done

Phase 1 is complete when ALL of the following are true:

- [ ] All 9 tasks above are marked complete in STATUS.md
- [ ] All 5 tests in `tests/test_phase1.py` pass
- [ ] `python query.py "test query"` returns relevant results from actual PDFs
- [ ] The watcher is running and auto-ingests a dropped PDF without manual intervention
- [ ] No unresolved entries in ERRORS.md
- [ ] Every `.py` file has a `# MODULE:` header and all functions have docstrings
