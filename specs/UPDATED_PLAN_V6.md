# PERSONAL AI BRAIN — UPDATED MASTER PLAN v6.0
# Status-Based Reality Check + Phase 5 Deep Engineering
# Written: June 6, 2026
# Based on: Full codebase audit of what was actually built

---

## FIRST: AN HONEST AUDIT OF WHAT YOU BUILT

Reading your actual code, not what STATUS.md claims. Here is the truth.

### What is genuinely solid and production-ready

**`src/ingestion/` — 9/10**
This is the strongest part of the project. The pipeline is well-engineered:
- `watcher.py` — OS-level inotify, debounce, per-path locking, dedup. Correct.
- `pdf_extractor.py` — scanned detection, OCR fallback, reference section stripping. Correct.
- `chunker.py` — structural + recursive hybrid, domain-aware chunk sizes. Correct.
- `auto_tagger.py` — Arabic/German/English detection, domain keywords. Correct.
- `embedder.py` — warmup, retry with exponential backoff, batch compat layer. Correct.
- `vector_store.py` — LanceDB with RRF hybrid search, write locking, correct schema. Correct.
- `pipeline.py` — threaded watcher+worker, private/public routing, summary gen, ERRORS.md logging. Correct.
- `web_endpoint.py` + `youtube_ingestor.py` — FastAPI endpoints, bookmarklet, yt-dlp. Correct.

**`src/common/` — 10/10**
Every utility is clean: logging, health checks, text normalization, file types, benchmarks.
These are production-grade helpers that Phase 5 will reuse heavily.

**`src/voice/` — 8/10**
The individual components (VAD, STT, TTS, hotkey) are well-written.
The `pipeline.py` wires them together correctly.
One real problem: the TTS `speak()` method calls `sd.wait()` on the FIRST sentence before
starting the second — this cancels the latency gain from sentence splitting.
Fixed version is documented in Section 3 below.

**`src/memory/` — 6/10**
This is where the gap is. Here is what was actually built vs what the project needs:

| Component | Built? | Quality | Problem |
|---|---|---|---|
| `core_memory.py` | Yes | Good | LettaRuntime HTTP wrapper tries too many endpoint paths — fragile |
| `daily_review.py` | Yes | OK | Generates reviews from STATUS.md only — not from actual session data |
| `extractor.py` | Yes | OK | Pattern matching is too simple — misses most real daily log entries |
| `mistake_tracker.py` | Yes | Good | Token-based search is weak — needs vector search |
| `letta_agent.py` | NOT BUILT | — | Missing entirely. No actual Letta agent conversation exists |

The Letta integration is the biggest gap. `voice/pipeline.py` calls
`http://localhost:8283/v1/agents/{agent_id}/messages` but there is no code
that actually creates the agent, sets its system prompt, or manages its tools.
The `LettaRuntime` class in `core_memory.py` is just a health-check wrapper —
it does not create a real conversational agent.

**`src/agents/` — 3/10**
`planner.py` exists but calls `ollama.chat()` directly with `format="json"` —
this is an unstructured LLM call, not a real task planner.
It has no tool execution, no sub-agent delegation, no safety gates.
`sub_agent.py`, `proactive.py` — NOT BUILT.

**`src/api/privacy_router.py` — 10/10**
Genuinely excellent. The `PrivacyDecision` dataclass, `choose_model_route()`,
and `CLOUD_BLOCKED_DOMAINS` enforcement are correct and well-structured.
This should be the model for everything else.

---

## WHAT TO DO BEFORE PHASE 5

These are not new features. These are gaps in what is claimed to be complete.
Fix these first. Phase 5 will break without them.

---

### FIX 1 — Build the real Letta agent (`src/memory/letta_agent.py`)

**The problem:** `voice/pipeline.py` sends messages to an agent that may not exist,
has no system prompt, no memory tools configured, and no connection to the LanceDB vault.

**What to build:**

```python
# src/memory/letta_agent.py
# MODULE: Real Letta agent creation, conversation, and memory tool integration

class OmarBrainAgent:
    """
    Creates and manages the persistent omar_brain Letta agent.
    
    System prompt gives the agent:
    - Omar's identity (name, domains, privacy rules)
    - Instructions to use core_memory_replace when learning new facts
    - Instructions to call search_archival before answering knowledge questions
    - The privacy rule: NEVER repeat personal/religion content to cloud
    
    Tools the agent must have:
    - core_memory_replace (built-in to Letta)
    - archival_memory_search (built-in to Letta)
    - recall_memory_search (built-in to Letta)
    - search_vault (CUSTOM: calls our LanceDB via FastAPI endpoint)
    - add_mistake (CUSTOM: calls mistake_tracker.py)
    """
    
    SYSTEM_PROMPT = \"\"\"
    You are Omar's personal AI brain — a persistent digital partner that grows
    smarter with every conversation. You know Omar personally.
    
    OMAR'S IDENTITY (core memory):
    - Name: Omar
    - Domains: Psychology, Islamic Studies, AI/Technology, Education
    - Privacy rule: NEVER share or synthesize personal/ or religion/ data using cloud models
    - Language: Responds in whatever language Omar uses (Arabic or English)
    - Tone: Direct, technical, like a knowledgeable friend — not a generic assistant
    
    MEMORY RULES:
    - When Omar tells you something new about himself, call core_memory_replace immediately
    - When answering knowledge questions, ALWAYS call search_vault first
    - When starting a task Omar has done before, call recall_memory_search for past context
    - When Omar makes a mistake or correction, call add_mistake
    
    PERSONALITY:
    - You remember everything. You grow. You do not reset.
    - You speak first from memory, then from the vault, then from reasoning.
    - You are allowed to say \"I don't know\" and then search.
    \"\"\"
```

**System prompt in Letta — exact API call:**

```python
agent = client.agents.create(
    name="omar_brain",
    agent_type="memgpt_agent",
    llm_config=LLMConfig(
        model="ollama/mistral",
        model_endpoint_type="ollama",
        model_endpoint="http://localhost:11434",
        context_window=8192,
    ),
    embedding_config=EmbeddingConfig(
        embedding_endpoint_type="ollama",
        embedding_endpoint="http://localhost:11434",
        embedding_model="nomic-embed-text",
        embedding_dim=768,
    ),
    memory=BasicBlockMemory(
        blocks=[
            CreateBlock(
                label="human",
                value="Name: Omar. Domains: Psychology, Religion, AI. Language: Arabic/English.",
                limit=2000,
            ),
            CreateBlock(
                label="persona",
                value=SYSTEM_PROMPT,
                limit=4000,
            ),
        ]
    ),
)
```

**Custom tool — search_vault:**
This is the missing bridge between Letta and your LanceDB.

```python
def search_vault(query: str, domain: str = None) -> str:
    \"\"\"Search Omar's personal knowledge vault for relevant information.\"\"\"
    # Calls http://localhost:8001/search?q={query}&domain={domain}
    # Returns top 3 results as formatted text for the agent to read
    response = httpx.get(
        "http://localhost:8001/search",
        params={"q": query, "domain": domain, "top_k": 3}
    )
    results = response.json()["results"]
    if not results:
        return "No relevant information found in the vault."
    return \"\\n\\n\".join([
        f\"[{r['source_file']}, p.{r['page_number']}]\\n{r['text']}\"
        for r in results
    ])
```

Add a `/search` endpoint to `src/api/` that calls `vector_store.hybrid_search()`.
Register `search_vault` as a Letta tool on the agent.
Now every voice question automatically searches your vault before answering.

---

### FIX 2 — Voice TTS latency bug (`src/voice/tts.py`)

**The problem in current code:**
```python
for i, sentence in enumerate(sentences):
    samples, sample_rate = self.kokoro.create(sentence, ...)
    if i > 0:
        sd.wait()     ← WRONG: waits for previous sentence to FINISH before generating next
    sd.play(samples, sample_rate)
```

**The correct streaming pattern:**
Generate sentence N+1 while sentence N is playing. Use a thread.

```python
def speak(self, text: str) -> float:
    sentences = re.split(r\"(?<=[.!?])\\s+\", text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    start_time = time.perf_counter()
    first_chunk_latency = 0.0
    
    audio_queue = queue.Queue()
    
    def synthesize_all():
        for sentence in sentences:
            samples, sr = self.kokoro.create(sentence, voice=self.voice_name, ...)
            audio_queue.put((samples, sr))
        audio_queue.put(None)  # sentinel
    
    synth_thread = threading.Thread(target=synthesize_all, daemon=True)
    synth_thread.start()
    
    first = True
    while True:
        item = audio_queue.get()
        if item is None:
            sd.wait()
            break
        samples, sr = item
        if first:
            first_chunk_latency = (time.perf_counter() - start_time) * 1000
            first = False
        sd.wait()          # wait for PREVIOUS chunk to finish
        sd.play(samples, sr)
    
    return first_chunk_latency
```

This generates sentence 2 while sentence 1 is playing. True streaming.
Expected latency improvement: 200-400ms on a 3-sentence response.

---

### FIX 3 — Add `/search` endpoint to FastAPI (`src/api/main.py`)

Currently there is no unified search endpoint. The voice pipeline and Letta custom tool both need one.

```python
# src/api/main.py — add this endpoint

@app.get("/search")
async def search_vault_endpoint(
    q: str,
    domain: str = None,
    top_k: int = 5
):
    \"\"\"
    Unified search endpoint used by Letta custom tools and the voice pipeline.
    Privacy router enforces domain restrictions.
    \"\"\"
    decision = choose_model_route(domain)
    store = VectorStore("personal" if domain in CLOUD_BLOCKED_DOMAINS else "documents")
    results = store.hybrid_search(q, top_k=top_k)
    return {
        "query": q,
        "domain": domain,
        "route": decision.route,
        "results": [asdict(r) for r in results]
    }
```

---

### FIX 4 — Make daily_review.py actually useful

**Current problem:** The daily review generates text from `STATUS.md` content only.
It does not capture what Omar actually said or did today.

**The fix — two modes:**

**Mode A (Interactive):** Prompt Omar with 5 questions in the terminal,
capture his typed answers, write those as the review.

**Mode B (Automatic):** Parse today's voice session logs from
`data/logs/sessions/` (add session logging to `voice/pipeline.py`),
extract entities and facts using Ollama, write a summary.

Add session logging to `voice/pipeline.py`:
```python
# After each handle_transcript() call, append to session log:
session_log_path = LOGS_DIR / "sessions" / f"{date.today().isoformat()}.jsonl"
with session_log_path.open("a") as f:
    json.dump({
        "timestamp": datetime.now().isoformat(),
        "user": transcript,
        "brain": response_text,
    }, f)
    f.write(\"\\n\")
```

Then `daily_review.py` reads the JSONL, sends it to Ollama for extraction,
and produces a structured markdown log with real content from the day.

---

## PHASE 5 — THE AGENCY LAYER (The Real Plan)

Now you can build Phase 5 correctly. Here is the full engineering spec.

---

### 5.1 — Planner Agent (Rewrite `src/agents/planner.py`)

**What is wrong with current planner:**
It calls Ollama with `format=\"json\"` and hopes for a task list.
It has no tool definitions, no execution loop, no safety checks, no sub-agent delegation.
It is a JSON prompt wrapper, not a planner.

**The correct architecture — ReAct pattern:**

```
User goal → Planner thinks → Planner picks a tool → Tool runs → 
Planner sees result → Planner thinks again → ... → Planner declares done
```

Each \"think-act-observe\" cycle is one LLM call.
The planner never runs code itself — it delegates to sub-agents.

**Tool registry the planner knows about:**

| Tool name | What it does | File |
|---|---|---|
| `search_vault` | Semantic search in LanceDB | via FastAPI /search |
| `read_file` | Read a file from the vault | src/agents/tools/file_reader.py |
| `write_file` | Write to vault (with confirmation) | src/agents/tools/file_writer.py |
| `run_python` | Execute Python in Bytebot sandbox | src/agents/tools/sandbox_runner.py |
| `browse_url` | Visit a URL in Bytebot sandbox | src/agents/tools/browser.py |
| `query_brain` | Ask Letta a question | via FastAPI /brain |
| `send_notification` | Desktop notify-send | src/agents/tools/notifier.py |

**Planner loop (pseudocode):**

```python
class TaskPlanner:
    MAX_STEPS = 10  # hard cap — prevents infinite loops
    
    def execute(self, goal: str) -> str:
        history = [{"role": "user", "content": f"Goal: {goal}"}]
        
        for step in range(self.MAX_STEPS):
            # Think
            response = ollama_call(PLANNER_SYSTEM_PROMPT, history)
            
            # Parse response — is it a tool call or a final answer?
            if response.get("type") == "final_answer":
                return response["content"]
            
            if response.get("type") == "tool_call":
                tool_name = response["tool"]
                tool_args = response["args"]
                
                # Human checkpoint for dangerous tools
                if tool_name in {"write_file", "run_python"}:
                    confirmed = ask_user_confirmation(tool_name, tool_args)
                    if not confirmed:
                        history.append({"role": "user", "content": "Action cancelled by user."})
                        continue
                
                # Execute tool
                result = self.tool_registry[tool_name](**tool_args)
                
                # Feed result back
                history.append({"role": "assistant", "content": str(response)})
                history.append({"role": "user", "content": f"Tool result: {result}"})
            
        return "Reached maximum steps without completing goal."
```

**The planner system prompt:**

```
You are a task execution agent. Your job is to complete a user goal using tools.

For each step, respond ONLY with JSON in one of two formats:

Format A — use a tool:
{"type": "tool_call", "thought": "why I'm doing this", "tool": "tool_name", "args": {...}}

Format B — done:  
{"type": "final_answer", "content": "what was accomplished and where the result is"}

Available tools: search_vault, read_file, write_file, run_python, browse_url, query_brain, send_notification

Rules:
1. Always search_vault BEFORE write_file — check what already exists
2. Always use query_brain for memory questions — don't answer from your own knowledge
3. Never run_python without explaining what the code will do in your \"thought\"
4. Stop at 10 steps maximum — summarize what was achieved
5. Privacy: if the goal involves personal or religious data, only use local tools
```

---

### 5.2 — Sub-Agent: Isolated Context Executor (`src/agents/sub_agent.py`)

**What it does:**
Runs a single focused task with a fresh context window.
The planner calls sub-agents for tasks that require extended back-and-forth
without polluting the planner's own context.

**When to use a sub-agent vs direct tool call:**
- Direct tool call: fetch a file, run a search, write a note (< 3 steps)
- Sub-agent: \"summarize 10 PDFs\", \"research a topic and write a report\" (> 3 steps)

```python
class SubAgent:
    def __init__(self, task: str, context: dict, allowed_tools: list[str]):
        \"\"\"
        task: What this agent must accomplish
        context: Only the data it needs (not the entire planner history)
        allowed_tools: Whitelist — sub-agents can't use tools the planner didn't grant
        \"\"\"
        self.task = task
        self.context = context
        self.allowed_tools = allowed_tools
        self.MAX_STEPS = 5  # sub-agents get fewer steps than the planner
    
    def run(self) -> str:
        \"\"\"Execute the task and return a summary of what was accomplished.\"\"\"
        # Same ReAct loop as planner but with smaller scope
        ...
```

---

### 5.3 — Bytebot Integration (`src/agents/tools/sandbox_runner.py`)

Bytebot runs in Docker containers, giving the agent a virtual desktop that can use any application, process files, browse websites, and complete multi-step workflows using natural language — all completely self-hosted.

**Critical insight from research:** Bytebot is NOT just for script execution.
It is a full virtual Linux desktop. The agent can open a browser, navigate YouTube,
download files, fill forms — all visually, without APIs.

**How to connect your planner to Bytebot:**

```python
# src/agents/tools/sandbox_runner.py

BYTEBOT_URL = "http://localhost:9992"

def run_task_in_bytebot(task_description: str, timeout_seconds: int = 60) -> str:
    \"\"\"
    Send a natural language task to Bytebot and return the result.
    
    Bytebot handles: clicking, typing, browsing, file operations.
    Everything runs in an isolated Docker container.
    Your host filesystem is not touched.
    \"\"\"
    response = httpx.post(
        f\"{BYTEBOT_URL}/api/tasks\",
        json={"task": task_description},
        timeout=timeout_seconds,
    )
    return response.json().get("result", "Task completed.")

def browse_url_in_bytebot(url: str, action: str = "read") -> str:
    \"\"\"Navigate to a URL and return page content or perform an action.\"\"\"
    task = f\"Navigate to {url} and {action}. Return the text content.\"
    return run_task_in_bytebot(task)
```

**Add Bytebot to docker-compose.yml:**

```yaml
bytebot:
  image: bytebot/bytebot:latest
  container_name: brain_bytebot
  restart: unless-stopped
  environment:
    ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}    # Bytebot uses Claude for visual reasoning
  ports:
    - "9992:9992"    # Bytebot UI + API
  volumes:
    - /home/omar/personal_ai_brain_project/data/sandbox_output:/output
  # Network isolation — Bytebot can reach internet but NOT your local services
  networks:
    - bytebot_isolated

networks:
  bytebot_isolated:
    driver: bridge
```

**The key safety rule:** Bytebot's output folder `/output` maps to
`data/sandbox_output/` on your host. Results land there. Nothing else
on your filesystem is accessible from the sandbox.

---

### 5.4 — Proactive Monitor (`src/agents/proactive.py`)

**Critical issue found in research:**
xdotool is X11-only and does not work with Wayland. Ubuntu 22.04 GNOME desktop defaults to Wayland. xdotool will silently fail on your machine.

**The fix — use `wnck` (via gi) or the clipboard instead:**

```python
# Option A: GNOME Shell DBus (works on Wayland)
import subprocess

def get_active_window_title() -> str:
    \"\"\"Get active window title using GNOME Shell DBus — Wayland compatible.\"\"\"
    try:
        result = subprocess.run(
            ["gdbus", "call", "--session",
             "--dest", "org.gnome.Shell",
             "--object-path", "/org/gnome/Shell",
             "--method", "org.gnome.Shell.Eval",
             "global.display.focus_window.title"],
            capture_output=True, text=True, timeout=2
        )
        # Parse the output — GNOME returns ('true', '\"Window Title\"')
        output = result.stdout.strip()
        title = output.split('\"')[1] if '\"' in output else ""
        return title
    except Exception:
        return ""

# Option B: Read clipboard content (simpler, very reliable)
import subprocess

def get_clipboard_text() -> str:
    \"\"\"Read clipboard text — useful for context when user copies something.\"\"\"
    result = subprocess.run(
        ["xclip", "-selection", "clipboard", "-o"],
        capture_output=True, text=True
    )
    return result.stdout.strip()
```

**The proactive monitor logic:**

```python
class ProactiveMonitor:
    CHECK_INTERVAL_SECONDS = 30
    MIN_RELEVANCE_SCORE = 0.82
    NOTIFICATION_COOLDOWN_SECONDS = 300  # don't spam — max 1 per 5 minutes
    
    def run(self):
        last_notified_at = 0
        last_title = ""
        
        while True:
            time.sleep(self.CHECK_INTERVAL_SECONDS)
            
            title = get_active_window_title()
            
            # Skip if title is too short or unchanged
            if len(title) < 10 or title == last_title:
                continue
            
            # Skip system windows
            if title.lower() in {"files", "terminal", "settings", "nautilus"}:
                continue
            
            last_title = title
            
            # Don't notify too frequently
            if time.time() - last_notified_at < self.NOTIFICATION_COOLDOWN_SECONDS:
                continue
            
            # Search vault for related content
            results = vector_store.hybrid_search(title, top_k=3)
            strong_results = [r for r in results if r.score > self.MIN_RELEVANCE_SCORE]
            
            if strong_results:
                best = strong_results[0]
                message = f\"💡 Related: '{best.section}' from {Path(best.source_file).name}\"
                subprocess.run(["notify-send", "Brain", message, "--expire-time=5000"])
                last_notified_at = time.time()
```

---

### 5.5 — Human Confirmation System (`src/agents/confirmation.py`)

Every destructive action goes through this before executing.

```python
class ConfirmationGate:
    \"\"\"
    Displays a confirmation prompt before any destructive agent action.
    Supports both terminal and desktop dialog modes.
    \"\"\"
    
    ALWAYS_CONFIRM = {
        "write_file",
        "run_python", 
        "run_task_in_bytebot",
        "send_email",
        "delete_file",
    }
    
    def request(self, action: str, details: dict) -> bool:
        \"\"\"
        Show the user what the agent is about to do.
        Returns True if approved, False if rejected.
        \"\"\"
        print(f\"\\n{'='*50}\")
        print(f\"⚠️  AGENT ACTION REQUEST\")
        print(f\"{'='*50}\")
        print(f\"Action:  {action}\")
        for key, value in details.items():
            print(f\"{key:10}: {value}\")
        print(f\"{'='*50}\")
        
        response = input(\"Approve? [y/N]: \").strip().lower()
        return response == \"y\"
```

---

### 5.6 — Sleep-Time Compute (The Nightly Brain Daemon)

This is the feature that separates a chatbot from a real second brain.
Sleep-time compute means the agent is not idle between user sessions — it reviews and indexes new documents, re-evaluates previous conclusions, generates summaries, and runs low-priority analysis tasks during off-peak hours.

**What it does every night at 2:00 AM (systemd timer):**

```python
# src/agents/sleep_daemon.py
# MODULE: Nightly background compute — the brain's \"sleep\" cycle

class SleepTimeDaemon:
    \"\"\"Runs proactive memory consolidation while Omar sleeps.\"\"\"
    
    def run_nightly_cycle(self):
        \"\"\"
        Step 1: Find all chunks ingested today that have no summary
        Step 2: Generate connection notes — \"this new Psychology chunk 
                relates to the Islamic ethics chunk from last week\"
        Step 3: Update the mistake tracker — scan today's session logs
                for patterns that match known mistakes
        Step 4: Generate tomorrow's \"briefing\" — a 200-word summary of
                what the brain learned today, ready for the morning
        Step 5: Compress old session logs into episodic summaries
                (daily JSONL → weekly markdown → monthly insight)
        \"\"\"
        self._connect_new_with_old()
        self._scan_session_for_mistakes()
        self._generate_morning_briefing()
        self._compress_old_logs()
    
    def _connect_new_with_old(self):
        \"\"\"Find semantic connections between today's new chunks and the existing vault.\"\"\"
        today_chunks = get_chunks_from_today()
        for chunk in today_chunks:
            related = vector_store.hybrid_search(chunk.text, top_k=3)
            strong = [r for r in related if r.score > 0.88 and r.source_file != chunk.source_file]
            if strong:
                connection_note = f\"\"\"
## Connection Found: {date.today()}
**New:** {chunk.section} ({Path(chunk.source_file).name})
**Related:** {strong[0].section} ({Path(strong[0].source_file).name})
**Semantic overlap score:** {strong[0].score:.2f}
\"\"\"
                (VAULT_DIR / "connections" / f"{date.today()}.md").write_text(connection_note)
```

---

## THE NEW STATUS.MD — PHASE 5 TASKS

Replace the Phase 5 section with these specific tasks:

```markdown
## Phase 5 Tasks — Agency & Proactivity

### 5.0 — Pre-Phase Fixes (do these first)
- [ ] **Task 5.0.1** — Build `src/memory/letta_agent.py` with real agent creation,
                        system prompt, and search_vault custom tool
- [ ] **Task 5.0.2** — Add `/search` and `/brain` endpoints to `src/api/main.py`
- [ ] **Task 5.0.3** — Fix TTS streaming in `src/voice/tts.py` (producer/consumer pattern)
- [ ] **Task 5.0.4** — Add session JSONL logging to `src/voice/pipeline.py`
- [ ] **Task 5.0.5** — Verify Letta agent responds correctly via voice pipeline end-to-end

### 5.1 — Task Planner (Rewrite)
- [ ] **Task 5.1.1** — Define tool registry and interfaces in `src/agents/tools/__init__.py`
- [ ] **Task 5.1.2** — Rewrite `src/agents/planner.py` with ReAct loop + MAX_STEPS=10
- [ ] **Task 5.1.3** — Implement `src/agents/confirmation.py` (gate for destructive actions)
- [ ] **Task 5.1.4** — Write `tests/test_planner.py` (mock all tools, verify loop logic)

### 5.2 — Sub-Agent Executor
- [ ] **Task 5.2.1** — Build `src/agents/sub_agent.py` with isolated context + tool whitelist
- [ ] **Task 5.2.2** — Test: \"summarize 3 PDFs and save to vault\" — must work end-to-end

### 5.3 — Bytebot Sandbox
- [ ] **Task 5.3.1** — Add Bytebot service to `docker/docker-compose.yml`
- [ ] **Task 5.3.2** — Build `src/agents/tools/sandbox_runner.py`
- [ ] **Task 5.3.3** — Build `src/agents/tools/browser.py` (browse_url wrapper)
- [ ] **Task 5.3.4** — Network isolation test: verify Bytebot cannot reach localhost:8283

### 5.4 — Proactive Monitor
- [ ] **Task 5.4.1** — Detect display server: X11 vs Wayland (auto-select window title method)
- [ ] **Task 5.4.2** — Build `src/agents/proactive.py` with cooldown, score threshold, notify-send
- [ ] **Task 5.4.3** — Run as systemd user service (always-on, low CPU)

### 5.5 — Sleep-Time Daemon
- [ ] **Task 5.5.1** — Build `src/agents/sleep_daemon.py` with 4 consolidation steps
- [ ] **Task 5.5.2** — Add 2:00 AM systemd timer
- [ ] **Task 5.5.3** — Test: verify morning briefing appears in data/logs/ each day

### 5.6 — Phase 5 Acceptance Tests
- [ ] **Task 5.6.1** — Voice: say \"summarize my consciousness notes\" → brain searches vault → speaks answer
- [ ] **Task 5.6.2** — Planner: \"create a study guide from my psychology PDFs\" → guide appears in vault
- [ ] **Task 5.6.3** — Proactive: open a window titled \"cognitive behavioral therapy\" → notification fires
- [ ] **Task 5.6.4** — Sleep daemon: check morning briefing at 7:00 AM after first nightly run
```

---

## THE ARCHITECTURE THAT NOW EXISTS (Accurate)

```
┌──────────────────────────────────────────────────────────┐
│  INTERFACE LAYER (built and working)                     │
│  Voice pipeline: VAD → STT → Letta → TTS  [802ms E2E]   │
│  Browser bookmarklet → FastAPI /ingest/web               │
│  CLI: query.py → hybrid_search                           │
└──────────────────────┬───────────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────────┐
│  AGENT LAYER (being built in Phase 5)                    │
│  Planner → ReAct loop → Tool registry                   │
│  Sub-agents → Isolated context execution                 │
│  Proactive monitor → Window title → notify-send          │
│  Sleep daemon → 2AM nightly consolidation                │
└──────────────────────┬───────────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────────┐
│  MEMORY LAYER (partially built, letta_agent.py missing)  │
│  Letta: Core → Recall → Archival                         │
│  core_memory.json ← daily_review.py ← extractor.py      │
│  mistake_tracker.py ← session logs ← voice pipeline     │
└──────────────────────┬───────────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────────┐
│  DATA LAYER (built and solid)                            │
│  LanceDB: documents/ personal/ conversations/ errors/    │
│  Ingestion: watcher → PDF → chunker → embedder → store  │
│  SQLite: dedup index (ingestion_index.db)                │
│  Logs: sessions/ (JSONL) + daily reviews (MD)            │
└──────────────────────────────────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────────┐
│  SANDBOX LAYER (Phase 5.3)                               │
│  Bytebot Docker: isolated desktop, browser, scripts      │
│  Output: data/sandbox_output/ (only bridge to host)      │
└──────────────────────────────────────────────────────────┘
```

---

## PRIORITY ORDER FOR THE NEXT AGENT SESSION

Give these instructions to Claude Code, in this order:

**Session 1 (Fix foundations):**
\"Read CLAUDE.md and STATUS.md. Build Task 5.0.1: create src/memory/letta_agent.py.
It must: create the omar_brain Letta agent if it doesn't exist, set the system prompt
defined in UPDATED_PLAN_V6.md, register the search_vault custom tool, and expose
send_message(text) → str as the public API. Do not start anything else.\"

**Session 2 (Connect voice to real brain):**
\"Build Tasks 5.0.2 and 5.0.4. Add /search and /brain to src/api/main.py.
Add session JSONL logging to voice/pipeline.py. Test: voice input → Letta → vault search → response.\"

**Session 3 (Fix TTS):**
\"Build Task 5.0.3. Rewrite the speak() method in src/voice/tts.py
using the producer/consumer threading pattern in UPDATED_PLAN_V6.md.
Run the latency benchmark test. Target: first audio < 300ms.\"

**Session 4 (Planner):**
\"Build Tasks 5.1.1 through 5.1.3. Define tools/__init__.py. Rewrite planner.py.
Build confirmation.py. Do NOT build Bytebot integration yet — use mock tool stubs.\"

**Session 5+ (Sandbox, Proactive, Sleep):**
Tasks 5.3, 5.4, 5.5 in order.

---

## WHAT THIS SYSTEM BECOMES WHEN PHASE 5 IS DONE

You speak to it. It searches what you know. It remembers what you've learned.
It warns you when you're about to repeat a mistake. At night, it reads everything
new it ingested and finds connections to what you already knew. When you give it
a goal, it breaks it into steps, executes them in a safe sandbox, asks you before
touching your files, and delivers a result.

That is not a chatbot. That is a digital twin.

---
*Updated: June 6, 2026 | Based on full codebase audit*
*Next review: after Phase 5.0.5 is complete*
