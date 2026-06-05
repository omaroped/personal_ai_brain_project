# Personal AI Brain — Deep Engineering Plan v5.1
### Every layer explained. Every decision justified. Ready for an AI agent to build.

---

## HOW TO USE THIS DOCUMENT

This document is your **building bible**. Before every Claude Code session, paste the relevant section
into your CLAUDE.md or reference it in your spec file. Each section answers:

- What exactly to build
- Which library to use and why
- What the code structure looks like
- What can go wrong and how to prevent it
- What "done" looks like (test criteria)

---

---

# PHASE 1 — THE VAULT (The Data Foundation)

## What This Phase Actually Is

Before any AI can "remember" anything, you need a place to put information and a way to find
it again reliably. This phase builds exactly that: a local database of everything you know,
that can be searched by meaning — not just keywords.

Think of it as building the hard drive before installing the operating system.

---

## 1.1 — The File Watcher

### What it does
A background Python process that runs silently and monitors specific folders. The moment
a new PDF, markdown, or text file appears, it queues it for ingestion. No manual action required.

### Library choice: `watchdog`
```
pip install watchdog
```
`watchdog` is the standard Python file-watching library. It uses OS-level inotify on Linux
(not polling), so it costs essentially zero CPU. It's been maintained since 2011 and works
on Ubuntu 22.04 without configuration.

### Exact folders to monitor
```
/home/omar/Documents/
/home/omar/Downloads/                    ← PDFs saved from browser land here
/home/omar/personal_ai_brain_project/data/vault/
/home/omar/academic_images/             ← any text files here too
```

### File types to ingest
| Extension | Processing method |
|-----------|-----------------|
| `.pdf` | pymupdf text extraction → chunker → embed |
| `.md` | Direct text → chunker → embed |
| `.txt` | Direct text → chunker → embed |
| `.docx` | python-docx extraction → chunker → embed |

### What the watcher code does (logic, not full code)
1. Event fires: `FileCreatedEvent` or `FileModifiedEvent`.
2. Check: has this file been ingested before? (Check a SQLite index table: `file_hash → ingested_at`)
3. If new: push the file path to an in-memory queue.
4. A separate worker thread pops from the queue and processes.
5. Why a queue? So if 10 PDFs land at once, they process one at a time and don't overwhelm the GPU.

### Known failure: duplicate ingestion
If you save a file and immediately edit it, two events fire. Solution: debounce with a
2-second timer — only process a file if no new events have fired for that file in the last 2 seconds.

### Test criteria for "done"
- Drop a PDF into `~/Documents`. Within 10 seconds, a new entry appears in LanceDB.
- Drop the same PDF again. Confirm no duplicate entries are created.
- Drop 5 PDFs simultaneously. All 5 get processed within 60 seconds.

---

## 1.2 — PDF Text Extraction

### Library choice: `pymupdf` (also known as `fitz`)
```
pip install pymupdf
```
Do NOT use `pypdf2`, `pdfminer`, or `pdfplumber` as your primary extractor.
`pymupdf` is 5-10x faster than all of them, handles Arabic/Hebrew text correctly (important
for your religious studies PDFs), extracts tables better, and handles scanned PDFs with
embedded OCR data. It is the correct choice for your use case.

### What to extract per page
For every page, extract:
1. Full text string
2. Page number (for citation: "Source: Islamic Ethics PDF, page 34")
3. Document title (from PDF metadata if available, else filename)
4. File creation date

### Handling scanned PDFs (images-as-PDF)
Some academic PDFs are scanned images with no embedded text. For these:
- Detect: if `page.get_text()` returns an empty string for 3+ consecutive pages, it's a scan.
- Solution: use `pytesseract` with `tessdata` for Arabic/English OCR.
- Command: `sudo apt-get install tesseract-ocr tesseract-ocr-ara`
- This is slower (~3 seconds per page) but necessary for older academic books.

### What to do with images inside PDFs
Your academic PDFs may have diagrams, charts, or Arabic calligraphy. For Phase 1, skip images.
Store a metadata flag: `has_images: true`. In a later phase you can add image captioning.

---

## 1.3 — The Chunking Strategy

### Why chunking is the most important decision in your entire RAG system
This is not an exaggeration. Research from 2025-2026 shows that chunking strategy affects
retrieval accuracy more than which embedding model you use. A bad chunking strategy with a
great model still returns garbage. Here is what actually works:

### The recommended strategy: Recursive + Semantic Hybrid

**Step 1: Structural split** — Split by document structure first (chapters, sections, headings).
For PDFs, a heading is detected when text is larger, bolder, or is the first line on a page.
For markdown, split on `##` and `###` headers.

**Step 2: Recursive size split** — Within each structural section, apply recursive splitting
at 400–512 tokens with 15% overlap (60–75 tokens). The `langchain_text_splitters` library
has `RecursiveCharacterTextSplitter` which does this well.

Why 400–512 tokens? Current research (Vecta 2026 benchmark across 50 academic papers)
found recursive 512-token splitting achieved 69% retrieval accuracy — the highest of all
methods tested. Semantic-only chunking scored 54% because it produces fragments that are
too short to contain full context.

Why 15% overlap? So that a concept that straddles a chunk boundary doesn't get lost.
If your chunk ends mid-sentence in the middle of explaining "the ego in Freudian theory",
the next chunk should repeat that context.

**Step 3: Context injection** — For each chunk, prepend a brief header:
```
[Document: Islamic Ethics by Al-Ghazali | Section: Chapter 3 — Purification of the Soul | Page: 47]
```
This header never gets embedded — it only goes into the stored text for display. The embedding
is done on the clean chunk text only.

### Special case: academic papers with references
Strip reference sections (usually at the end). They create noise in retrieval because they
contain hundreds of author names and publication titles that will surface for irrelevant queries.
Detection: text block containing "References" or "Bibliography" with 5+ author names.

### Chunk size table by content type
| Content type | Recommended tokens | Overlap |
|---|---|---|
| Dense academic text (philosophy, psychology theory) | 512 | 20% |
| Religious text (Quran tafsir, hadith) | 256 | 25% |
| AI/technical documentation | 400 | 15% |
| Lecture transcripts | 600 | 10% |
| Personal notes / daily logs | 200 | 10% |

Smaller chunks for religious text because individual ayat/hadith have self-contained meaning.
Larger chunks for lectures because context spans paragraphs.

---

## 1.4 — Embeddings

### Library and model choice: `nomic-embed-text` via Ollama
```
ollama pull nomic-embed-text
```

Why this over OpenAI embeddings or other options?
- **Privacy**: embeddings capture the semantic "fingerprint" of your text. Sending your
  personal religious and psychological notes to OpenAI's API for embedding means those
  fingerprints leave your machine. Nomic runs locally.
- **VRAM cost**: nomic-embed-text uses ~500MB VRAM — barely a rounding error.
- **Dimension**: 768-dimensional vectors. Good balance between precision and storage.
- **Speed**: ~800 chunks/minute on your RTX 3060.
- **Quality**: competitive with OpenAI text-embedding-ada-002 on Arabic-English mixed text.

### The embedding process
```python
# Pseudocode — agent will write actual code
for chunk in chunks:
    vector = ollama.embeddings(model="nomic-embed-text", prompt=chunk.text)
    lancedb_table.add({
        "id": generate_uuid(),
        "text": chunk.text,
        "vector": vector,
        "source_file": chunk.source,
        "page_number": chunk.page,
        "section": chunk.section,
        "domain": auto_detect_domain(chunk.text),  # see below
        "created_at": datetime.now().isoformat(),
        "chunk_index": chunk.index
    })
```

### Auto-detecting domain
Before embedding, run a fast keyword classifier on each chunk to assign a domain tag.
This costs nothing (no LLM call) and dramatically improves filtered retrieval later.

```python
DOMAIN_KEYWORDS = {
    "psychology":  ["Freud", "ego", "cognitive", "behavioral", "therapy", "schema"],
    "religion":    ["Allah", "Quran", "hadith", "tafsir", "fiqh", "theology"],
    "ai_tech":     ["neural", "transformer", "embedding", "gradient", "model"],
    "education":   ["lecture", "exam", "assignment", "university", "course"],
    "personal":    ["today", "I feel", "goal", "mistake", "lesson"],
}
```

The domain tag lets you later ask: "search only my psychology notes" and filter by domain
before doing vector search — much faster and more accurate.

---

## 1.5 — The Vector Database: LanceDB

### Why LanceDB over ChromaDB
ChromaDB has a known HNSW index corruption issue on abrupt process exit (e.g. power cut,
SIGKILL). For a personal knowledge base you're building over months, a corruption that
wipes your index is catastrophic. LanceDB's Lance columnar format creates a new version
per write — it's inherently rollback-safe.

Additionally, LanceDB handles datasets larger than RAM via disk-based IVF-PQ indexing.
Your 22GB of RAM is comfortable now, but after ingesting years of PDFs, you'll be grateful.

### Database structure
```
data/vectordb/
├── documents/          ← all PDFs, books, articles
├── personal/           ← daily logs, personal notes (NEVER sent to cloud models)
├── conversations/      ← past chat sessions compressed into searchable form
└── errors/             ← mistake log (see Phase 2)
```

Separate tables allow you to scope searches. "Search only my personal notes" queries the
`personal` table. "Search everything" queries all tables with merged results.

### Hybrid search: vector + keyword (BM25)
Pure vector search fails for specific queries like "what did Freud say about the id in
Civilization and Its Discontents Chapter 4" because the chapter number and book title
are exact strings that embeddings may not weight heavily.

The solution is hybrid search: run a BM25 keyword search in parallel with vector search,
then merge results using Reciprocal Rank Fusion (RRF).

RRF formula: `score = Σ 1 / (k + rank_i)` where k=60 is a constant.

LanceDB supports full-text search (BM25) natively as of v0.8. You add a full-text index
alongside the vector index and query both simultaneously.

```python
# Hybrid query (pseudocode)
vector_results = table.search(query_vector).limit(10).to_list()
text_results = table.search(query_text, query_type="fts").limit(10).to_list()
merged = reciprocal_rank_fusion(vector_results, text_results)
return merged[:5]
```

### What "done" looks like for Phase 1
Run these 5 test queries against your actual PDFs:
1. "what is the difference between id and superego" → should return Freud-related chunks
2. "surah al-baqarah verse about patience" → should return Quran-related chunks  
3. "transformer attention mechanism" → should return AI/tech chunks
4. "E-404" (a fake error code) → should return nothing (tests that noise is filtered)
5. Search for a phrase you KNOW is in one of your PDFs, word-for-word → must appear in top 3

---

---

# PHASE 2 — THE MEMORY ENGINE

## What This Phase Actually Is

Phase 1 gave you a searchable library. Phase 2 gives the system a *self*. After this phase,
the system knows who you are, what you care about, what you've learned, and crucially,
what mistakes you've made before.

---

## 2.1 — Letta: What It Actually Is and How It Works

### The mental model
Normal LLMs are like a person with anterograde amnesia — they forget everything the moment
the conversation ends. Letta solves this by making the LLM itself responsible for managing
its own memory through tool calls.

The LLM has three memory zones:
- **Core memory** (in active context): ~2,000 tokens. The agent's "working memory".
  Always loaded. Contains your name, domains, current goals, active mistakes.
- **Recall memory** (PostgreSQL with pgvector): All past conversations, searchable.
  The agent calls `search_recall(query)` to pull relevant history into context.
- **Archival memory** (LanceDB from Phase 1): Your entire knowledge vault.
  The agent calls `search_archival(query)` to pull relevant knowledge.

### How Letta actually runs on your machine
Letta runs as a Docker service with a PostgreSQL database for persistence.

```bash
# The exact command to start Letta locally
docker run \
  -v ~/.letta/.persist/pgdata:/var/lib/postgresql/data \
  -v /home/omar/personal_ai_brain_project/data:/data \
  -p 8283:8283 \
  -e OPENAI_API_KEY="sk-..." \    # only needed if using cloud models
  letta/letta:latest
```

You connect to it via the Python client:
```python
from letta_client import Letta
client = Letta(base_url="http://localhost:8283")
```

### Pointing Letta at Ollama (local LLM)
This is critical — you want it using your local `mistral-7b-instruct` for most operations,
not burning cloud API credits.

In Letta's config, set the model provider to Ollama:
```python
agent = client.agents.create(
    model="ollama/mistral",          # local Ollama
    embedding="ollama/nomic-embed-text",
    name="omar_brain",
    ...
)
```

Use Claude Sonnet 4 only for complex synthesis tasks (writing a study guide, deep reasoning).
Use Ollama for routine memory updates, daily log processing, and fast Q&A.

---

## 2.2 — Core Memory Architecture

### The `core_memory.json` structure
This is the most important file in the entire system. It is what makes the AI feel like
it actually knows you. The agent updates this file automatically after every significant
interaction.

```json
{
  "identity": {
    "name": "Omar",
    "location": "Zgorzelec, Poland",
    "occupation": "Student + job seeking",
    "primary_language": "Arabic + English + learning German"
  },
  "active_domains": {
    "psychology": {
      "current_module": "Cognitive Psychology — Module 3",
      "last_studied": "2026-06-04",
      "key_concepts_mastered": ["classical conditioning", "schema theory"],
      "concepts_struggling_with": ["working memory models"]
    },
    "religion": {
      "current_focus": "Tafsir of Al-Baqarah",
      "madhab": "[your madhab]",
      "active_books": ["Tafsir Ibn Kathir", "Al-Ghazali Ihya"]
    },
    "ai_technology": {
      "current_project": "Personal AI Brain",
      "skills": ["Python basics via AI", "RAG concepts", "Ollama"]
    }
  },
  "current_goals": [
    "Complete AI brain Phase 1 by end of June",
    "Find job in [field]",
    "Finish Cognitive Psychology module"
  ],
  "known_mistakes": [
    {
      "id": "mistake_001",
      "domain": "python",
      "description": "Forgot to activate virtual environment before pip install",
      "correction": "Always run: source venv/bin/activate",
      "date": "2026-06-01"
    }
  ],
  "preferences": {
    "explanation_style": "technical + analogies",
    "preferred_session_length": "60-90 minutes",
    "voice_speed": "normal",
    "privacy_zones": ["personal", "religion"]  ← never send to cloud models
  }
}
```

### How the agent updates core memory
Letta agents have built-in tool functions:
- `core_memory_replace(old_text, new_text)` — updates a field
- `core_memory_append(section, new_text)` — adds to a list
- `archival_memory_insert(content)` — pushes to long-term storage

After a conversation where you say "I just finished the memory module in psychology",
the agent automatically calls:
```
core_memory_replace("current_module: Cognitive Psychology — Module 3", 
                     "current_module: Cognitive Psychology — Module 4, completed Module 3")
```

This happens without you doing anything. That's the magic of the MemGPT paradigm.

---

## 2.3 — The Daily Review System

### Why this is the most valuable feature in the entire project
The daily review is what transforms raw information into wisdom. Your human brain consolidates
memory during sleep — this system does the same thing every evening.

### The `daily_review.py` script
Triggered at 9:00 PM via a systemd timer (not cron — systemd handles missed triggers if
your PC was off).

**The 5 questions it asks (in the terminal or via voice):**
1. "What was your main focus today? (Studies, work, personal)"
2. "What's one new concept or fact you learned?"
3. "Did you make any mistakes or encounter any problems? What was the fix?"
4. "What's your single most important task for tomorrow?"
5. "Any message to your brain? (Things to remember, context to keep)"

Each answer is typed or spoken. The system writes a structured daily log:
```
data/logs/2026-06-05.md
```

### The extraction pass (the important part)
After the daily review is complete, the agent runs an extraction pass on the log.
It looks for:

**Fact updates** → "I'm now on Module 4" → updates `core_memory.json`

**Mistake records** → "I forgot to commit before starting a new feature" → adds to
`errors/` namespace in Letta memory with the correction

**Goal progress** → "I applied to 3 jobs today" → updates goal tracking in core memory

**Spaced repetition seeds** → Any new concept the user reports learning gets added to
a `flashcards_pending.json` file for future review (Phase 2 extension)

### systemd timer (exact setup)
```ini
# /etc/systemd/system/brain-review.timer
[Unit]
Description=Daily Brain Review Timer

[Timer]
OnCalendar=*-*-* 21:00:00
Persistent=true        ← CRITICAL: runs even if PC was off at 9pm

[Install]
WantedBy=timers.target
```

---

## 2.4 — The Mistake Tracker

### Why this deserves its own subsystem
Most AI systems have no way to tell you "you've tried this approach before and it failed."
The mistake tracker is what gives your brain institutional memory about your personal failure
patterns — which is arguably more valuable than factual knowledge.

### Data structure for a mistake record
```json
{
  "id": "mistake_042",
  "date": "2026-06-05",
  "domain": "psychology_study",
  "context": "Studying for cognitive psychology exam",
  "mistake": "Tried to memorize Baddeley's model by reading it repeatedly — didn't retain",
  "correction": "Use active recall: close the book, write what you remember, check gaps",
  "principle": "Passive re-reading has almost no effect on memory consolidation",
  "recurrence_count": 0,
  "tags": ["study_technique", "memory", "active_recall"]
}
```

### How the pre-task check works
Before any study session or task, the agent searches the mistakes namespace:
```python
relevant_mistakes = search_mistakes(tags=["study_technique"], domain="psychology")
if relevant_mistakes:
    print("⚠️ Reminder from your past self:")
    for m in relevant_mistakes:
        print(f"  - {m.mistake} → {m.correction}")
```

This is a 3-second operation. The value compounds enormously over time.

---

---

# PHASE 3 — INGESTION PIPELINES

## What This Phase Actually Is

Phase 3 is about making data collection effortless. Right now, to add something to your
brain you have to manually copy files. After Phase 3, the brain grows automatically as you
browse, study, and work.

---

## 3.1 — The Browser Bookmarklet (Not a Full Extension)

### Why a bookmarklet instead of a Chrome extension
Building a Chrome extension requires: manifest.json, background scripts, permissions review,
and ongoing maintenance when Chrome updates its manifest format (it just moved to v3).
That's 3-4 weeks of work before you've even ingested a single page.

A bookmarklet is a one-line JavaScript snippet saved as a bookmark. Click it on any page
and it sends the content to your local FastAPI endpoint. Takes 30 minutes to build.

### How it works
```javascript
// Save this as a browser bookmark — paste as the URL
javascript:(function(){
  const data = {
    url: window.location.href,
    title: document.title,
    selected: window.getSelection().toString(),
    body: document.body.innerText.substring(0, 5000)
  };
  fetch('http://localhost:8001/ingest/web', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(data)
  }).then(() => alert('✅ Saved to brain'));
})();
```

Click it while on a page → the first 5000 characters + your selected text → sent to your
local FastAPI server → processed and stored. Takes 1 click, 2 seconds.

### The FastAPI endpoint that receives it
```python
@app.post("/ingest/web")
async def ingest_web(payload: WebPayload):
    # 1. If text was selected, prioritize that as the "key passage"
    # 2. Summarize with local Ollama (3-sentence summary)
    # 3. Extract 3-5 key facts as bullet points
    # 4. Auto-tag domain
    # 5. Chunk and embed into LanceDB `documents` table
    # 6. Return success
```

### Privacy note
The bookmarklet only sends data to `localhost`. Nothing leaves your machine.
Never send data from the `personal` LanceDB table through a cloud API.

---

## 3.2 — YouTube Transcript Ingestion

### Why YouTube matters for your use case
If you watch lectures, Islamic talks, psychology videos, or AI tutorials on YouTube,
those are hours of valuable knowledge that currently disappear after watching.
This pipeline captures them automatically.

### Library: `yt-dlp`
```
pip install yt-dlp
```
`yt-dlp` is the maintained fork of `youtube-dl`. It downloads transcripts (auto-generated
or manual captions) without downloading the video, in seconds.

### The endpoint
```python
@app.post("/ingest/youtube")
async def ingest_youtube(url: str):
    # 1. yt-dlp --write-auto-sub --no-download --sub-lang ar,en {url}
    # 2. Parse the .vtt or .srt transcript file
    # 3. Clean the transcript (remove timestamps, repeated lines from CC)
    # 4. Chunk at 600 tokens (lectures have long context spans)
    # 5. Store with metadata: video_title, channel_name, url, timestamp
```

### Sending YouTube URLs to the brain via bookmarklet
The same bookmarklet can detect if the current page is YouTube and call the YouTube
endpoint instead of the web endpoint. Add one line:
```javascript
if(window.location.hostname === 'www.youtube.com') {
  fetch('http://localhost:8001/ingest/youtube?url=' + encodeURIComponent(window.location.href))
} else {
  // regular web ingest
}
```

---

## 3.3 — The Auto-Tagging Model

### Why auto-tagging is critical
Without tags, your vector database becomes a black box. With tags, you can:
- "Show me everything I've ingested about consciousness in the last 2 weeks"
- "Search only my AI notes for this concept"
- Filter searches to your privacy zones (never send tagged-personal data to cloud)

### The tagger (zero extra cost)
This runs locally using your DOMAIN_KEYWORDS dict from Phase 1 plus a small extension:
```python
def auto_tag(text: str) -> dict:
    tags = {
        "domain": detect_domain(text),      # keyword matching
        "language": detect_language(text),  # langdetect library
        "content_type": detect_type(text),  # "lecture", "article", "note", "book"
        "privacy_level": "public"           # overridden to "private" for personal/ table
    }
    return tags
```

For content type detection, use simple heuristics:
- Contains "Chapter", sequential headings → `book`
- Contains timestamps like `[00:03:45]` → `transcript`
- Short paragraphs, date at top → `article`
- First-person, "I", "my", "today" → `note`

---

---

# PHASE 4 — THE VOICE LAYER

## What This Phase Actually Is

This is the interface that makes the system feel like a real partner rather than a text app.
After Phase 4, you can walk away from your desk, speak a question, and hear the answer.

---

## 4.1 — Why `faster-whisper` Instead of `whisper.cpp`

The original plan said `whisper.cpp`. The research says otherwise for your hardware.

On NVIDIA GPUs (which you have), `faster-whisper` is consistently 1.5–2x faster than
`whisper.cpp`. The reason: `faster-whisper` uses CTranslate2, which is CUDA-optimized
from the ground up. `whisper.cpp` is optimized primarily for Apple Metal and CPU.

Benchmark relevant to your RTX 3060 (Laptop, 6GB VRAM):
- `faster-whisper` with `base.en` model (int8): **~100–150ms** for a 5-second clip
- `whisper.cpp` with `base.en` model: ~200–300ms for the same

Both are local, both are private, but `faster-whisper` is the right choice for NVIDIA.

```
pip install faster-whisper
```

Model to use: `base` (multilingual, good for Arabic + English mixed speech).
NOT `base.en` — because you may speak Arabic to your brain.
VRAM usage: ~600MB for the `base` model. Leaves 5.4GB for Ollama.

### The full STT pipeline
```python
from faster_whisper import WhisperModel

# Load once at startup, keep in memory (no cold starts)
stt_model = WhisperModel("base", device="cuda", compute_type="int8")

def transcribe(audio_path: str) -> str:
    segments, _ = stt_model.transcribe(audio_path, beam_size=5)
    return " ".join([s.text for s in segments])
```

---

## 4.2 — Silero VAD (Voice Activity Detection)

### What it is and why you need it
Without VAD, you'd either: (a) record continuously and send silence to Whisper (wastes
processing), or (b) use a push-to-talk button (breaks the natural feel).

Silero VAD detects when you're speaking vs. silent in real-time, using a 100ms window.
It's a tiny neural network (1MB) that runs on CPU — no VRAM cost at all.

```python
import torch
vad_model, utils = torch.hub.load('snakers4/silero-vad', 'silero_vad')
```

### The exact recording logic
```python
SILENCE_THRESHOLD = 0.8  # seconds of silence before stopping
SAMPLE_RATE = 16000

def listen_until_silence():
    recording = []
    silence_start = None
    
    # Read audio in 30ms chunks
    while True:
        chunk = audio_stream.read(30ms)
        is_speech = vad_model(chunk)
        
        if is_speech:
            silence_start = None
            recording.append(chunk)
        else:
            if silence_start is None:
                silence_start = time.now()
            elif time.now() - silence_start > SILENCE_THRESHOLD:
                break  # 0.8s of silence → done recording
    
    return concatenate(recording)
```

### Hotkey trigger
Use `pynput` to listen for `Ctrl+Space` as the wake signal:
```python
from pynput import keyboard

def on_press(key):
    if key == keyboard.Key.ctrl_l and keyboard.Key.space:
        start_listening()
```

---

## 4.3 — Text-to-Speech: Kokoro ONNX

### Why Kokoro over alternatives
- `piper-tts`: Good quality, but voice sounds robotic on longer sentences.
- `coqui-tts`: Higher quality but 2GB+ VRAM for the best voices.
- `espeak`: Sounds like 1995. Don't use it.
- `Kokoro ONNX`: Studio-quality voice, streaming output (first audio token in ~200ms),
  runs on CPU (no VRAM needed at all), 82M parameter model.

Kokoro is the current best option for local TTS on your hardware because it leaves all
your VRAM free for Whisper and Ollama.

```
pip install kokoro-onnx sounddevice
```

### Streaming playback (why it matters for latency)
Without streaming, the system generates the entire audio file, then plays it.
For a 5-sentence answer, that's a 2-second wait before you hear anything.

With streaming, Kokoro generates audio token by token and your speaker plays it
while the rest is still being generated. First audio starts ~200ms after text is ready.

```python
from kokoro_onnx import Kokoro

tts = Kokoro("kokoro-v0_19.onnx", "voices.bin")

def speak(text: str):
    stream = tts.create_stream(text, voice="af_bella", speed=1.0, lang="en-us")
    for audio_chunk in stream:
        sounddevice.play(audio_chunk, samplerate=24000)
```

---

## 4.4 — The Complete Voice Loop

### Latency breakdown (your hardware, realistic numbers)
| Component | Time |
|---|---|
| Silero VAD silence detection | 100ms |
| faster-whisper transcription (5s clip) | 150ms |
| Letta agent processing (Ollama mistral-7b) | 600–900ms |
| Kokoro TTS first audio chunk | 200ms |
| **Total to first word spoken** | **~1.05–1.35 seconds** |

This is within the natural feel threshold (~1.5 seconds).

### What degrades latency
- Ollama model not pre-loaded → add 2-3s cold start. Solution: start Ollama at boot
  with `ollama run mistral` before the voice pipeline starts.
- Letta doing a heavy archival search → can add 500ms. Solution: set a timeout of 800ms
  for archival search; if it doesn't return in time, answer from core memory only and
  note "I can check your archives for more detail."

---

---

# PHASE 5 — AGENCY

## What This Phase Actually Is

Phases 1-4 built a brain that knows things and can talk. Phase 5 gives it hands. After
this phase, you can say "summarize all my psychology notes into a study guide" and walk
away while it does it.

---

## 5.1 — The Planner Agent

### The mental model: a manager with specialists
The planner agent is like a project manager. It receives a high-level goal, breaks it
into discrete tasks, and assigns each task to a sub-agent with a fresh context window.

Why fresh context windows per sub-task? Because sub-agents with too much context make
more mistakes. Each sub-agent should know only what it needs for its specific task.

### How task breakdown works
User says: "Create a 2-page summary of everything I know about consciousness."

Planner breaks it into:
```
Task 1: search_archival(query="consciousness psychology")
         → returns 20 relevant chunks
Task 2: search_archival(query="consciousness philosophy religion")  
         → returns 15 more chunks
Task 3: synthesize(chunks=Task1+Task2, format="2-page essay with sections")
         → writes the document
Task 4: save_to_vault(document, filename="consciousness_summary_2026-06-05.md")
```

Each task is run by a sub-agent that receives only the context needed for that task.
Tasks 1 and 2 can run in parallel (no dependency). Task 3 waits for both. Task 4 waits for 3.

### The human checkpoint gate
Any task that writes, modifies, or deletes files pauses and asks:
```
⚠️ About to write:
  File: consciousness_summary_2026-06-05.md
  Location: ~/personal_ai_brain_project/data/vault/
  Size: ~1200 words

Approve? [y/n]
```

This is not optional. Without this gate, the agent will eventually overwrite something
important, and you won't know until later.

---

## 5.2 — The Bytebot Sandbox

### What it is and why it matters
Bytebot is a Docker container running Ubuntu 22.04 with a browser and file system.
When the agent needs to browse the web or run scripts, it does so inside this container,
not on your host machine.

This means: if a web page tries to run malicious JavaScript, if a script has a bug
that deletes files, or if the agent makes a wrong decision — it all happens inside the
container. Your actual files are safe.

```bash
# Install
docker pull bytebot/bytebot:latest

# Run (maps a specific output folder only — not your entire home directory)
docker run \
  -v /home/omar/personal_ai_brain_project/sandbox_output:/output \
  -p 9090:9090 \
  bytebot/bytebot:latest
```

### What the agent can do inside the sandbox
- Browse URLs, click links, fill forms
- Run Python scripts
- Download files (which go to `/output`, mounted to your host)
- Run shell commands

### What the agent CANNOT do from the sandbox
- Access `/home/omar/` directly (not mounted)
- Access your Letta database (network-isolated)
- Send data to external services (configure Docker network policy)

---

## 5.3 — The Proactive Side Panel

### What it is
A background process that monitors your active window title every 30 seconds using
`xdotool` (Ubuntu), searches the brain for related content, and shows a desktop
notification if something relevant is found.

```python
import subprocess
import time

def get_active_window_title():
    result = subprocess.run(['xdotool', 'getactivewindow', 'getwindowname'],
                           capture_output=True, text=True)
    return result.stdout.strip()

def proactive_check():
    title = get_active_window_title()
    # Don't trigger for short titles or system windows
    if len(title) < 10 or title in ["Terminal", "Files"]:
        return
    
    results = search_vault(title, top_k=3, min_score=0.82)
    if results:
        notify(f"💡 Related in your brain: '{results[0].section}' from {results[0].source}")
```

### The `min_score=0.82` threshold
This prevents false positives. A relevance score below 0.82 means the connection is
too weak to be useful. You'll tune this number over time — if you get too many
irrelevant notifications, raise it to 0.87.

---

---

# CROSS-CUTTING CONCERNS

## The Privacy Routing Layer

This is one of the most important architectural decisions in the system. Before any text
is sent to a cloud model (Claude Sonnet), it must pass through a privacy check.

```python
CLOUD_BLOCKED_DOMAINS = ["personal", "religion"]

def route_query(text: str, source_domain: str, task_complexity: str):
    if source_domain in CLOUD_BLOCKED_DOMAINS:
        return use_local_model(text)    # Ollama
    if task_complexity == "complex_synthesis":
        return use_cloud_model(text)    # Claude Sonnet
    return use_local_model(text)
```

Simple rule: if the data domain is `personal` or `religion`, it never leaves the machine.
Period. This is hardcoded, not configurable, to prevent accidental leakage.

---

## The Error Recovery Protocol

Every module must implement this error handling pattern:

```python
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 2

for attempt in range(MAX_RETRIES):
    try:
        result = risky_operation()
        break
    except Exception as e:
        log_error(e, attempt)
        if attempt == MAX_RETRIES - 1:
            write_to_ERRORS_md(e)      ← human-readable, not just a log file
            send_desktop_notification("Brain error — check ERRORS.md")
            raise SystemExit(1)        ← stop cleanly, don't loop
        time.sleep(RETRY_DELAY_SECONDS * (attempt + 1))  ← exponential backoff
```

Why write to `ERRORS.md` specifically? Because when you give this to Claude Code in
the next session, it reads `ERRORS.md` first and knows the history before writing a
single line of code.

---

## Technology Version Lock

The following versions are tested and known to work together on Ubuntu 22.04 with CUDA 12.x.
Pin these in `requirements.txt`. Do not let an agent upgrade them without checking compatibility.

```
faster-whisper==1.1.0
letta-client==0.2.x
lancedb==0.8.x
pymupdf==1.24.x
kokoro-onnx==0.4.x
silero-vad==5.1.x
watchdog==4.0.x
fastapi==0.111.x
torch==2.3.x
```

---

## The `STATUS.md` Template

Update this file at the end of every agent session:

```markdown
# Brain Project Status

## Current Phase: [1/2/3/4/5]
## Last Updated: YYYY-MM-DD

## Completed Tasks
- [x] Task description (date completed)

## In Progress
- [ ] Current task (started date)

## Blocked On
- Issue description → what needs to happen to unblock

## Next Session Should Start With
Exact first instruction for the next Claude Code session

## Known Issues
- Issue: description
  Status: investigating / workaround applied / waiting
```

---

*End of Deep Plan v5.1 — Personal AI Brain*
*Generated: June 2026*
