# MODULE: Speech-to-Text service wrapper for transcribing audio clips using faster-whisper.
"""STT Service component using faster-whisper and hardware acceleration."""

from __future__ import annotations

import io
import wave
from pathlib import Path
import numpy as np
import torch

from src.common.logging_utils import configure_logging

LOGGER = configure_logging(__name__)


def wav_bytes_to_float32(wav_bytes: bytes) -> np.ndarray:
    """Read WAV bytes and decode them into a 1D float32 numpy array normalized to [-1.0, 1.0]."""
    wav_io = io.BytesIO(wav_bytes)
    with wave.open(wav_io, "rb") as wav_file:
        params = wav_file.getparams()
        if params.nchannels != 1:
            LOGGER.warning("Input audio has %d channels, expected 1 (mono)", params.nchannels)
        if params.sampwidth != 2:
            LOGGER.warning("Input audio sample width is %d bytes, expected 2 (16-bit)", params.sampwidth)

        frames = wav_file.readframes(params.nframes)
        # Interpret bytes as 16-bit integers
        audio_data = np.frombuffer(frames, dtype=np.int16)
        # Normalize to float32 between -1.0 and 1.0
        return audio_data.astype(np.float32) / 32768.0


class SpeechToTextService:
    """Transcribes spoken speech audio using faster-whisper."""

    def __init__(
        self,
        model_size: str = "base",
        device: str = "cuda",
        compute_type: str = "float16",
    ) -> None:
        """Initialize the Speech to Text Service.

        Parameters:
            model_size: Size of the Whisper model to load (e.g. tiny, base, small).
            device: Host device to execute on (cuda or cpu).
            compute_type: Computation precision (e.g. float16, int8).
        """
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.model = None

    def warmup(self) -> None:
        """Load and warm up the Whisper model."""
        if self.model is not None:
            return

        from faster_whisper import WhisperModel

        actual_device = self.device
        actual_compute = self.compute_type

        # Verify CUDA availability
        if actual_device == "cuda" and not torch.cuda.is_available():
            LOGGER.warning("CUDA requested but not available. Falling back to CPU.")
            actual_device = "cpu"
            actual_compute = "int8"

        LOGGER.info("Loading WhisperModel '%s' on %s (%s)...", self.model_size, actual_device, actual_compute)
        try:
            self.model = WhisperModel(self.model_size, device=actual_device, compute_type=actual_compute)
        except Exception as exc:
            if actual_device == "cuda":
                LOGGER.warning("Failed to initialize Whisper on GPU (%s). Retrying on CPU.", exc)
                actual_device = "cpu"
                actual_compute = "int8"
                self.model = WhisperModel(self.model_size, device=actual_device, compute_type=actual_compute)
            else:
                raise exc

        # Warm up the model with a tiny silence buffer to compile pipelines
        LOGGER.info("Warming up Whisper model...")
        warmup_audio = np.zeros(16000, dtype=np.float32)  # 1 second of silence
        self.model.transcribe(warmup_audio)
        LOGGER.info("STT model warmed up successfully.")

    def transcribe_bytes(self, audio_bytes: bytes) -> str:
        """Transcribe an in-memory WAV byte stream.

        Parameters:
            audio_bytes: In-memory WAV file bytes.

        Returns:
            str: Transcribed text transcript.
        """
        if not audio_bytes:
            return ""

        if self.model is None:
            self.warmup()

        try:
            audio_array = wav_bytes_to_float32(audio_bytes)
            return self._transcribe(audio_array)
        except Exception as exc:
            LOGGER.error("Error transcribing audio bytes: %s", exc)
            return ""

    def transcribe_file(self, audio_path: Path) -> str:
        """Transcribe an audio file saved on disk.

        Parameters:
            audio_path: Path to the audio file.

        Returns:
            str: Transcribed text transcript.
        """
        if not audio_path.exists():
            LOGGER.warning("Audio path %s does not exist", audio_path)
            return ""

        if self.model is None:
            self.warmup()

        try:
            segments, _ = self.model.transcribe(str(audio_path), beam_size=5)
            return "".join(segment.text for segment in segments).strip()
        except Exception as exc:
            LOGGER.error("Error transcribing file %s: %s", audio_path, exc)
            return ""

    def _transcribe(self, audio_array: np.ndarray) -> str:
        """Helper to call transcribe on a float32 numpy array."""
        segments, _ = self.model.transcribe(audio_array, beam_size=5)
        return "".join(segment.text for segment in segments).strip()
