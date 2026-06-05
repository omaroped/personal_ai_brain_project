# MODULE: Ollama embedding client with warmup, retries, and batch processing helpers.
"""Generate vector embeddings for chunk text using a local Ollama server."""

from __future__ import annotations

import time

import ollama

from config import EMBED_MODEL, OLLAMA_BASE_URL
from src.common.logging_utils import configure_logging

MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = (1.0, 2.0, 4.0)


class Embedder:
    """Generate embeddings through Ollama with warmup and retry handling."""

    def __init__(self) -> None:
        """Initialize the Ollama client and warm up the embedding model."""
        self.logger = configure_logging(__name__)
        self.client = ollama.Client(host=OLLAMA_BASE_URL)
        self._warmup()

    def embed(self, text: str) -> list[float]:
        """Generate an embedding vector for one text input.

        Parameters:
            text: Text to embed.

        Returns:
            list[float]: Embedding vector returned by Ollama.
        """
        if not text.strip():
            return []

        last_error: Exception | None = None
        for attempt in range(MAX_RETRIES):
            try:
                response = self.client.embeddings(model=EMBED_MODEL, prompt=text)
                return list(response["embedding"])
            except Exception as exc:
                last_error = exc
                self.logger.warning(
                    "Embedding attempt %d/%d failed: %s",
                    attempt + 1,
                    MAX_RETRIES,
                    exc,
                )
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_BACKOFF_SECONDS[attempt])

        raise RuntimeError(f"Embedding failed after {MAX_RETRIES} attempts: {last_error}")

    def embed_batch(self, texts: list[str], batch_size: int = 10) -> list[list[float]]:
        """Generate embeddings for a list of texts in batches.

        Parameters:
            texts: Text items to embed.
            batch_size: Number of texts to process per batch.

        Returns:
            list[list[float]]: Embedding vectors in input order.
        """
        vectors: list[list[float]] = []
        total = len(texts)
        for start in range(0, total, batch_size):
            batch = texts[start : start + batch_size]
            batch_vectors = self._embed_batch_compat(batch)
            vectors.extend(batch_vectors)
            self.logger.info("Embedded %d/%d chunks.", min(start + len(batch), total), total)
        return vectors

    def _warmup(self) -> None:
        """Warm up the embedding model with a dummy request before real traffic."""
        self.logger.info("Warming up Ollama embedding model...")
        self.embed("warmup")
        self.logger.info("Ollama embedding model ready.")

    def _embed_batch_compat(self, texts: list[str]) -> list[list[float]]:
        """Use the best available Ollama batch interface, falling back to per-item calls.

        Parameters:
            texts: Batch of text items to embed.

        Returns:
            list[list[float]]: Embedding vectors in input order.
        """
        if not texts:
            return []

        if hasattr(self.client, "embed"):
            response = self.client.embed(model=EMBED_MODEL, input=texts)
            embeddings = response.get("embeddings", [])
            return [list(vector) for vector in embeddings]

        return [self.embed(text) for text in texts]
