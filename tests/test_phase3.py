# MODULE: Test suite for Phase 3 web ingestion endpoint and automated summarization.
"""Tests for web ingestion endpoint and automated summaries."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from src.ingestion.pdf_extractor import ExtractedPage
from src.ingestion.pipeline import IngestionPipeline


@pytest.fixture
def mock_pipeline():
    """Create a mock ingestion pipeline instance with mocked stores."""
    with patch("src.ingestion.pipeline.IngestionStateStore") as mock_state_store, \
         patch("src.ingestion.pipeline.VectorStore"), \
         patch("src.ingestion.pipeline.Embedder"), \
         patch("src.ingestion.pipeline.PDFExtractor"), \
         patch("src.ingestion.pipeline.Chunker"), \
         patch("src.ingestion.pipeline.ollama.Client") as mock_ollama_client:

        # Configure mock state store to avoid skipped already_ingested state
        state_store_instance = MagicMock()
        state_store_instance.has_hash.return_value = False
        mock_state_store.return_value = state_store_instance

        # Configure mock ollama client
        client_instance = MagicMock()
        client_instance.generate.return_value = {
            "response": "## Summary\nA test summary.\n\n## Key Facts\n- Fact 1\n- Fact 2\n- Fact 3"
        }
        mock_ollama_client.return_value = client_instance

        pipeline = IngestionPipeline()
        pipeline.ollama_client = client_instance
        yield pipeline


def test_web_endpoint_saves_markdown_and_queues_ingestion(tmp_path: Path, monkeypatch) -> None:
    """The /ingest/web endpoint should parse payload, save clipping file, and queue background task."""
    # Temporarily redirect VAULT_DIR to our tmp_path
    monkeypatch.setattr("src.ingestion.web_endpoint.VAULT_DIR", tmp_path)

    # Import the FastAPI app inside the test to use the patched values
    from src.ingestion.web_endpoint import app, pipeline

    # Mock the pipeline methods
    mock_ingest = MagicMock(return_value={"status": "ok", "chunks": 5})
    monkeypatch.setattr(pipeline, "ingest_file", mock_ingest)

    client = TestClient(app)
    payload = {
        "url": "https://example.com/article",
        "title": "My Test Article",
        "selected": "Some highlighted passage",
        "body": "This is the full body text of the article."
    }

    response = client.post("/ingest/web", json=payload)

    # Assert API response
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "web_clippings" in data["file"]

    # Verify file was written on disk
    filepath = Path(data["file"])
    assert filepath.exists()
    file_content = filepath.read_text(encoding="utf-8")
    assert "# My Test Article" in file_content
    assert "https://example.com/article" in file_content
    assert "Some highlighted passage" in file_content
    assert "This is the full body text of the article." in file_content


def test_pipeline_generate_and_save_summary(tmp_path: Path, mock_pipeline) -> None:
    """The pipeline should call Ollama to generate a summary and save it to vault/summaries."""
    # Set summaries_dir to tmp_path / "summaries"
    mock_pipeline.summaries_dir = tmp_path / "summaries"

    pages = [
        ExtractedPage(
            text="This is page 1 content that needs to be summarized.",
            page_number=1,
            source_file="test.pdf",
            document_title="Test Title",
            is_scanned=False
        )
    ]

    filepath = Path("test.pdf")

    # Run summary generation
    mock_pipeline._generate_and_save_summary(filepath, pages)

    # Verify Ollama was called
    mock_pipeline.ollama_client.generate.assert_called_once()

    # Check that summary file was created
    summary_file = tmp_path / "summaries" / "test.md"
    assert summary_file.exists()
    content = summary_file.read_text(encoding="utf-8")
    assert "## Summary" in content
    assert "## Key Facts" in content


def test_pipeline_ingest_file_triggers_summary(tmp_path: Path, mock_pipeline, monkeypatch) -> None:
    """Ingesting a file should trigger the summary generation method."""
    mock_pipeline.summaries_dir = tmp_path / "summaries"

    # Mock extract pages, chunker, embedder and stores
    test_file = tmp_path / "input.md"
    test_file.write_text("Markdown body content.", encoding="utf-8")

    # Stub methods to return dummy values to avoid actual model execution
    mock_pipeline.chunker.chunk.return_value = [
        MagicMock(text="chunk", domain="general")
    ]
    mock_pipeline.embedder.embed_batch.return_value = [[0.1] * 768]

    # Stub the generate and save summary method to verify it is called
    mock_summary_gen = MagicMock()
    monkeypatch.setattr(mock_pipeline, "_generate_and_save_summary", mock_summary_gen)

    # Run ingestion
    result = mock_pipeline.ingest_file(test_file)

    assert result["status"] == "ok"
    # Verify summary generation helper was triggered
    mock_summary_gen.assert_called_once()


def test_youtube_ingestor_clean_vtt_content(tmp_path: Path) -> None:
    """The clean_vtt_content function should correctly clean WebVTT formats and deduplicate lines."""
    from src.ingestion.youtube_ingestor import clean_vtt_content
    vtt_file = tmp_path / "test.vtt"
    vtt_file.write_text(
        "WEBVTT\n"
        "Kind: captions\n"
        "Language: en\n"
        "Style:\n"
        "  ::cue {\n"
        "    color: white;\n"
        "  }\n"
        "\n"
        "00:00:01.000 --> 00:00:03.000\n"
        "Hello <c.color>world</c>\n"
        "\n"
        "00:00:03.000 --> 00:00:05.000\n"
        "Hello <c.color>world</c>\n"
        "\n"
        "00:00:05.000 --> 00:00:07.000\n"
        "This is unique text.\n",
        encoding="utf-8"
    )
    result = clean_vtt_content(vtt_file)
    assert result == "Hello world This is unique text."


def test_youtube_ingestor_download_and_parse_transcript(tmp_path: Path, monkeypatch) -> None:
    """The download_and_parse_transcript function should correctly wrap yt-dlp and extract subtitles."""
    import tempfile
    
    # Set DATA_DIR to tmp_path
    monkeypatch.setattr("src.ingestion.youtube_ingestor.DATA_DIR", tmp_path)

    # Class mimicking TemporaryDirectory to inject a fake subtitle file
    class MockTempDir:
        def __init__(self, **kwargs):
            self.name = str(tmp_path / "mock_temp_dir")
            Path(self.name).mkdir(parents=True, exist_ok=True)
            vtt_file = Path(self.name) / "sub_12345.en.vtt"
            vtt_file.write_text(
                "WEBVTT\n\n00:00:01.000 --> 00:00:03.000\nThis is a mocked transcript sentence.\n",
                encoding="utf-8"
            )
        def __enter__(self):
            return self.name
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    with patch("src.ingestion.youtube_ingestor.yt_dlp.YoutubeDL") as mock_ytdl, \
         patch("src.ingestion.youtube_ingestor.tempfile.TemporaryDirectory", MockTempDir):
        
        ytdl_instance = MagicMock()
        mock_ytdl.return_value.__enter__.return_value = ytdl_instance
        ytdl_instance.extract_info.return_value = {
            "id": "12345",
            "title": "Mocked YouTube Video",
            "uploader": "Mocked Channel",
        }

        from src.ingestion.youtube_ingestor import download_and_parse_transcript
        data = download_and_parse_transcript("https://www.youtube.com/watch?v=12345")

        assert data["video_id"] == "12345"
        assert data["title"] == "Mocked YouTube Video"
        assert data["channel"] == "Mocked Channel"
        assert "This is a mocked transcript sentence." in data["transcript"]


def test_youtube_endpoint_saves_markdown_and_queues_ingestion(tmp_path: Path, monkeypatch) -> None:
    """The /ingest/youtube endpoint should fetch transcript, write clipping file, and queue background task."""
    # Temporarily redirect VAULT_DIR to our tmp_path
    monkeypatch.setattr("src.ingestion.web_endpoint.VAULT_DIR", tmp_path)

    # Mock download_and_parse_transcript to return mock data
    mock_download = MagicMock(return_value={
        "video_id": "98765",
        "title": "FastAPI Tutorial",
        "channel": "Coding Channel",
        "transcript": "In this video we learn FastAPI.",
        "url": "https://youtube.com/watch?v=98765"
    })
    monkeypatch.setattr("src.ingestion.web_endpoint.download_and_parse_transcript", mock_download)

    # Import the FastAPI app inside the test to use the patched values
    from src.ingestion.web_endpoint import app, pipeline

    # Mock the pipeline methods
    mock_ingest = MagicMock(return_value={"status": "ok", "chunks": 2})
    monkeypatch.setattr(pipeline, "ingest_file", mock_ingest)

    client = TestClient(app)
    response = client.post("/ingest/youtube?url=https://youtube.com/watch?v=98765")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "youtube_clippings" in data["file"]

    # Verify file was written on disk
    filepath = Path(data["file"])
    assert filepath.exists()
    file_content = filepath.read_text(encoding="utf-8")
    assert "# FastAPI Tutorial" in file_content
    assert "https://youtube.com/watch?v=98765" in file_content
    assert "Coding Channel" in file_content
    assert "In this video we learn FastAPI." in file_content


def test_auto_tagger_classification() -> None:
    """The AutoTagger should correctly classify domain, language, type, and privacy level."""
    from src.ingestion.auto_tagger import AutoTagger
    tagger = AutoTagger()

    # 1. Test domain detection
    psych_text = "The Freudian ego and superego interact in classical conditioning."
    assert tagger.detect_domain(psych_text) == "psychology"

    religion_text = "In this tafsir of the Quran, we study Allah's mercy."
    assert tagger.detect_domain(religion_text) == "religion"

    ai_text = "A neural network transformer generates embeddings."
    assert tagger.detect_domain(ai_text) == "ai_tech"

    general_text = "This is some random information about clouds."
    assert tagger.detect_domain(general_text) == "general"

    # 2. Test language detection
    english_text = "This is a simple English sentence."
    assert tagger.detect_language(english_text) == "en"

    arabic_text = "هذا نص باللغة العربية لشرح التفسير والحديث الشريف."
    assert tagger.detect_language(arabic_text) == "ar"

    german_text = "Ich bin ein Student und das ist mein Projekt."
    assert tagger.detect_language(german_text) == "de"

    # 3. Test content type detection
    book_file = Path("chapter1.pdf")
    assert tagger.detect_content_type("This is the intro chapter.", book_file) == "book"

    note_file = Path("clipping.md")
    assert tagger.detect_content_type("A markdown note file content.", note_file) == "note"

    transcript_text = "Speaker 1: Hello. Speaker 2: Hi there. [00:01:00]"
    assert tagger.detect_content_type(transcript_text) == "transcript"

    # 4. Test full tag_text dict & privacy routing
    religion_tags = tagger.tag_text(religion_text)
    assert religion_tags["domain"] == "religion"
    assert religion_tags["privacy_level"] == "private"

    ai_tags = tagger.tag_text(ai_text)
    assert ai_tags["domain"] == "ai_tech"
    assert ai_tags["privacy_level"] == "public"


