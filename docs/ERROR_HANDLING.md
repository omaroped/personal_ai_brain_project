# MODULE: Error Handling Model

This document summarizes the standardized error handling and logging strategy for the Personal AI Brain project.

## 1. Core Philosophy

- **Graceful Degradation:** The system should remain partially functional even if specific components (e.g., OCR, embedding) fail.
- **Retry First:** Transient failures (network timeouts, model loading delays) should be handled via automated retries.
- **Hard Stop & Log:** Persistent failures that cannot be resolved after multiple attempts must be logged to `ERRORS.md` and the process stopped to prevent data corruption.

## 2. Standard Retry Pattern

All "risky" operations (Ollama calls, database writes, file system I/O) must implement the following pattern:

- **MAX_RETRIES:** Default is 3 attempts.
- **Backoff:** Exponential backoff (e.g., 1s, 2s, 4s) between retries.
- **Specific Exceptions:** Never use bare `except:`. Always catch specific, expected exceptions.

### Implementation Template

```python
import logging
import time
from datetime import datetime

MAX_RETRIES = 3
logger = logging.getLogger(__name__)

for attempt in range(MAX_RETRIES):
    try:
        result = risky_operation()
        break
    except SpecificException as e:
        logger.warning(f"Attempt {attempt+1}/{MAX_RETRIES} failed: {e}")
        if attempt == MAX_RETRIES - 1:
            # Final failure: Log to ERRORS.md and escalate
            with open("ERRORS.md", "a") as f:
                f.write(f"\n## ERROR: {datetime.now().isoformat()}\n")
                f.write(f"- Operation: risky_operation\n")
                f.write(f"- Error: {str(e)}\n")
                f.write(f"- Status: UNRESOLVED\n")
            raise
        time.sleep(2 ** attempt)
```

## 3. The `ERRORS.md` Registry

The `ERRORS.md` file serves as the definitive log of system failures and "Institutional Memory" of past mistakes. 

### Logging Format

When a failure is escalated, it must be appended to `ERRORS.md` using the following template:

```markdown
## ERROR [ID]: Short description
- **Date:** YYYY-MM-DD
- **Phase/Task:** Current Phase and Task ID
- **Operation:** Detailed description of what was attempted
- **Error message:** Exact traceback or error text
- **Root cause:** Technical explanation of why it happened
- **Fix applied:** (Optional) If resolved, what was the fix?
- **Status:** RESOLVED / UNRESOLVED / WORKAROUND APPLIED
```

## 4. Component-Specific Strategies

### 4.1 Database Writes (LanceDB)
- **Locking:** All writes must be wrapped in a file-lock (`fasteners.InterProcessLock`) to prevent concurrent write corruption.
- **Atomic Operations:** Prefer batching writes to minimize the time the database is locked.

### 4.2 LLM & Embedding (Ollama)
- **Warmup:** Send a dummy request on startup to trigger model loading and avoid timeout on the first real request.
- **Thread Safety:** Run Ollama calls in a thread pool executor when used within async FastAPI endpoints to avoid blocking the event loop.

### 4.3 Voice Pipeline
- **Offline Fallback:** Check for cached model weights (Silero VAD, Kokoro TTS) before attempting network-dependent operations.
- **Latency Monitoring:** Log execution time for each stage; if STT > 500ms for a 5s clip, escalate as a performance error.
