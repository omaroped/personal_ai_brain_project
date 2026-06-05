# Watcher Behavior

Documentation of the filesystem watcher's debounce logic and duplicate prevention strategies.

## Debounce Logic

File writes are often non-atomic, especially for large PDFs or browser downloads. To prevent the system from attempting to ingest a partial file, `src/ingestion/watcher.py` implements a debounce mechanism:

1. **Event Capture**: The watcher listens for `FileCreatedEvent` and `FileModifiedEvent`.
2. **Timer Initialization**: When an event is received, a 2-second timer is started for that file path.
3. **Reset on Activity**: If another event is received for the same path before the timer expires, the timer is reset.
4. **Finalization**: Only after 2 seconds of silence (no events) is the file added to the `IngestionPipeline` queue.

## Duplicate Prevention

The system ensures that each version of a file is only embedded and stored once.

### SHA-256 Content Hashing
The `IngestionStateStore` computes a SHA-256 hash of every file's content. This hash serves as the definitive identity of the file's state.

### State Persistence
- Hashes are stored in a SQLite database (`ingestion_index.db`) alongside the file path and last-ingested timestamp.
- Before processing a file, the system compares its current hash against the database.
- If the hash matches, the file is skipped with a `skipped (already_ingested)` status.

### Handling Moves and Renames
If a file is moved or renamed, its content hash remains the same. The system recognizes that the content is already in the vector store and skips re-embedding, although it may update the path reference in the state store.
