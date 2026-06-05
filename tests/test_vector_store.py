# MODULE: Unit tests for src/ingestion/vector_store.py
import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
import lancedb
from src.ingestion.vector_store import VectorStore, SearchResult, LANCEDB_SCHEMA

@pytest.fixture
def mock_embedder():
    """Provides a mocked embedder that returns deterministic vectors."""
    embedder = MagicMock()
    # Return a 768-dim list of floats
    embedder.embed.return_value = [0.1] * 768
    return embedder

def test_vector_store_bootstrap(temp_data_dir, mock_embedder):
    """Verifies that the vector store creates the table with correct schema."""
    with patch("src.ingestion.vector_store.VECTORDB_DIR", temp_data_dir / "vectordb"):
        store = VectorStore(table_name="test_table", embedder=mock_embedder)
        assert "test_table" in store.db.table_names()
        
        table = store.table
        assert table.schema.equals(LANCEDB_SCHEMA)

def test_search_result_dataclass():
    """Verifies the SearchResult dataclass structure."""
    res = SearchResult(
        text="test",
        display_text="[Source: x] test",
        source_file="x.pdf",
        page_number=1,
        domain="general",
        score=0.9
    )
    assert res.text == "test"
    assert res.score == 0.9

def test_rrf_merge():
    """Verifies the Reciprocal Rank Fusion merging logic."""
    # We can test the internal _rrf_merge without a full store instance
    store = MagicMock(spec=VectorStore)
    # Mocking self._rrf_merge for unit testing is tricky since it's an instance method,
    # but we can call it on a dummy instance or test it via the real class logic if isolated.
    
    list_a = [{"id": "a", "val": 1}, {"id": "b", "val": 2}]
    list_b = [{"id": "b", "val": 2}, {"id": "c", "val": 3}]
    
    # Using real implementation for logic check
    merged = VectorStore._rrf_merge(store, list_a, list_b, k=60)
    
    assert merged[0]["id"] == "b"  # 'b' appears in both, should be top
    assert len(merged) == 3
    assert "_rrf_score" in merged[0]

def test_search_empty_query(temp_data_dir, mock_embedder):
    """Verifies that empty queries return empty results without calling embedder."""
    with patch("src.ingestion.vector_store.VECTORDB_DIR", temp_data_dir / "vectordb"):
        store = VectorStore(table_name="empty_test", embedder=mock_embedder)
        results = store.search("")
        assert results == []
        mock_embedder.embed.assert_not_called()

def test_already_ingested_missing(temp_data_dir, mock_embedder):
    """Verifies already_ingested behavior for non-existent hashes."""
    with patch("src.ingestion.vector_store.VECTORDB_DIR", temp_data_dir / "vectordb"):
        store = VectorStore(table_name="ingest_test", embedder=mock_embedder)
        assert store.already_ingested("missing_hash") is False
        assert store.already_ingested("") is False
