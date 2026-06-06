# MODULE: Unit tests for the Embedder component.
"""Test Ollama embedding integration, including retries, warmup, and batching."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from src.ingestion.embedder import Embedder


class FakeOllamaClient:
    """Minimal Ollama client stub for testing."""

    def __init__(self) -> None:
        """Initialize the fake client."""
        self.embeddings_calls = 0

    def embeddings(self, model: str, prompt: str) -> dict:
        """Simulate an embedding response.

        Parameters:
            model: Model name.
            prompt: Text to embed.

        Returns:
            dict: Mocked embedding response.
        """
        self.embeddings_calls += 1
        return {"embedding": [0.1, 0.2, 0.3]}


@patch("src.ingestion.embedder.ollama.Client")
@patch("src.ingestion.embedder.RETRY_BACKOFF_SECONDS", (0, 0, 0))
def test_embedder_retry_logic(mock_client_class) -> None:
    """Embedder should retry on failure and eventually succeed or raise."""
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client

    mock_client.embeddings.side_effect = [
        Exception("Fail 1"),
        Exception("Fail 2"),
        {"embedding": [1.0, 2.0]},
    ]

    with patch.object(Embedder, "_warmup"):
        embedder = Embedder()
        result = embedder.embed("test text")

        assert result == [1.0, 2.0]
        assert mock_client.embeddings.call_count == 3


@patch("src.ingestion.embedder.ollama.Client")
@patch("src.ingestion.embedder.RETRY_BACKOFF_SECONDS", (0, 0, 0))
def test_embedder_raises_after_max_retries(mock_client_class) -> None:
    """Embedder should raise RuntimeError after MAX_RETRIES failures."""
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    mock_client.embeddings.side_effect = Exception("Permanent failure")

    with patch.object(Embedder, "_warmup"):
        embedder = Embedder()
        with pytest.raises(RuntimeError, match="Embedding failed after 3 attempts"):
            embedder.embed("test text")


@patch("src.ingestion.embedder.ollama.Client")
def test_embedder_warmup_behavior(mock_client_class) -> None:
    """Embedder should call _warmup during initialization."""
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client

    with patch.object(Embedder, "_warmup") as mock_warmup:
        Embedder()

    mock_warmup.assert_called_once_with()


def test_embedder_blank_input_returns_empty() -> None:
    """Blank or whitespace-only input should return an empty list immediately."""
    embedder = Embedder.__new__(Embedder)
    embedder.client = MagicMock()

    assert embedder.embed("") == []
    assert embedder.embed("   ") == []
    assert embedder.client.embeddings.call_count == 0


@patch("src.ingestion.embedder.ollama.Client")
def test_embedder_batch_fallback_logic(mock_client_class) -> None:
    """Embedder should fall back to individual calls if batch API is missing."""
    mock_client = FakeOllamaClient()
    mock_client_class.return_value = mock_client

    embedder = Embedder.__new__(Embedder)
    embedder.client = mock_client
    embedder.logger = MagicMock()

    results = embedder._embed_batch_compat(["a", "b"])

    assert results == [[0.1, 0.2, 0.3], [0.1, 0.2, 0.3]]
    assert mock_client.embeddings_calls == 2


@patch("src.ingestion.embedder.ollama.Client")
def test_embedder_uses_batch_api_when_available(mock_client_class) -> None:
    """Embedder should use the batch API (client.embed) when available."""
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client

    mock_client.embed.return_value = {"embeddings": [[1.0], [2.0]]}

    embedder = Embedder.__new__(Embedder)
    embedder.client = mock_client

    results = embedder._embed_batch_compat(["a", "b"])

    assert results == [[1.0], [2.0]]
    mock_client.embed.assert_called_once()
    assert mock_client.embeddings.call_count == 0
