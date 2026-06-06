# MODULE: Acceptance tests for Phase 4 Voice Layer components.
"""Unit and integration tests for the Voice Layer."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch
import numpy as np
import pytest

from src.voice.pipeline import VoicePipeline
from src.voice.stt import SpeechToTextService
from src.voice.tts import TextToSpeechService
from src.voice.vad import VoiceActivityDetector


def test_stt_empty_audio_no_crash() -> None:
    """STT should handle empty bytes or missing files without raising exceptions."""
    service = SpeechToTextService(model_size="tiny")
    # Should handle empty bytes by returning empty string
    assert service.transcribe_bytes(b"") == ""
    # Should handle non-existent file by returning empty string
    assert service.transcribe_file(Path("non_existent_file.wav")) == ""


@patch("src.voice.tts.urllib.request.urlretrieve")
@patch("src.voice.tts.Kokoro")
def test_tts_generates_bytes(mock_kokoro, mock_urlretrieve) -> None:
    """TTS synthesize should return valid WAV bytes for non-empty text."""
    mock_inst = MagicMock()
    mock_inst.create.return_value = (np.zeros(16000, dtype=np.float32), 16000)
    mock_kokoro.return_value = mock_inst

    service = TextToSpeechService()
    service.kokoro = mock_inst  # Force set loaded model

    wav_bytes = service.synthesize("hello")
    assert len(wav_bytes) > 44  # WAV header is 44 bytes
    assert service.synthesize("") == b""


def test_vad_boundary_detection() -> None:
    """VAD should correctly detect speech boundaries and return WAV bytes."""
    # Mock Silero model
    mock_model = MagicMock()
    # Sequence of probabilities: silence -> speech start -> silence
    probs = [0.1] * 5 + [0.9] * 2 + [0.1] * 10
    
    # We mock the model call to return the next probability
    def model_call(tensor, sample_rate):
        val = probs.pop(0) if probs else 0.1
        # Mocking the item call on returned tensor
        item_mock = MagicMock()
        item_mock.item.return_value = val
        return item_mock

    mock_model.side_effect = model_call

    vad = VoiceActivityDetector(
        threshold=0.5,
        sample_rate=16000,
        chunk_size=512,
        silence_duration_sec=0.1,
    )
    vad.model = mock_model
    vad.is_running = True

    # Fill queue with mock chunk frames
    for _ in range(20):
        vad._audio_queue.put(np.zeros(512, dtype=np.float32))

    wav_bytes = vad.read_utterance()
    assert len(wav_bytes) > 44  # Valid WAV bytes returned


@patch("src.voice.pipeline.httpx.post")
def test_voice_pipeline_process_once(mock_post) -> None:
    """VoicePipeline should link VAD -> STT -> Letta -> TTS correctly."""
    # Mock Letta HTTP response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "messages": [
            {
                "message_type": "assistant_message",
                "content": "I am ready to help.",
            }
        ]
    }
    mock_post.return_value = mock_response

    # Setup mocked pipeline components
    mock_vad = MagicMock()
    mock_vad.read_utterance.return_value = b"fake_wav_bytes"

    mock_stt = MagicMock()
    mock_stt.transcribe_bytes.return_value = "hello there"

    mock_tts = MagicMock()

    pipeline = VoicePipeline(vad=mock_vad, stt=mock_stt, tts=mock_tts)
    pipeline.agent_id = "agent-mock"

    # Execute single voice processing tick
    pipeline.process_once()

    # Assertions
    mock_vad.read_utterance.assert_called_once()
    mock_stt.transcribe_bytes.assert_called_once_with(b"fake_wav_bytes")
    mock_tts.speak.assert_called_once_with("I am ready to help.")


@pytest.mark.timeout(30)
@patch("src.voice.tts.sd")
def test_end_to_end_latency(mock_sd) -> None:
    """Benchmark end-to-end latency (STT + Brain + TTS). Target: < 1.5s."""
    import time
    from src.voice.stt import SpeechToTextService
    from src.voice.tts import TextToSpeechService
    
    # 1. Setup real STT and TTS (with mocked sd)
    stt = SpeechToTextService(model_size="base", device="cuda")
    tts = TextToSpeechService()
    
    # 2. Mock VAD and Brain
    audio_path = Path("tests/benchmark_5s.wav")
    if not audio_path.exists():
        pytest.skip("Benchmark audio file not found.")
    
    with open(audio_path, "rb") as f:
        audio_bytes = f.read()
    
    mock_vad = MagicMock()
    mock_vad.read_utterance.return_value = audio_bytes
    
    # Mock Letta call in handle_transcript
    with patch("src.voice.pipeline.httpx.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "messages": [{"role": "assistant", "content": "I am processing your request."}]
        }
        mock_post.return_value = mock_response
        
        pipeline = VoicePipeline(vad=mock_vad, stt=stt, tts=tts)
        pipeline.agent_id = "latency-test-agent"
        
        # Warm up once
        pipeline.process_once()
        
        # 3. Measure latency on second run
        start_time = time.perf_counter()
        pipeline.process_once()
        end_time = time.perf_counter()
        
        total_latency_ms = (end_time - start_time) * 1000
        print(f"\nEnd-to-End Latency: {total_latency_ms:.2f}ms")
        
        assert total_latency_ms < 1500, f"Latency {total_latency_ms:.2f}ms exceeds 1.5s limit"
