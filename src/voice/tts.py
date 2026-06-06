# MODULE: Text-to-Speech service using kokoro-onnx and sounddevice streaming playback.
"""TTS Service component wrapping Kokoro TTS and sounddevice output."""

from __future__ import annotations

import io
import urllib.request
import wave
from pathlib import Path
import numpy as np
from kokoro_onnx import Kokoro
import sounddevice as sd

from src.common.logging_utils import configure_logging

LOGGER = configure_logging(__name__)


class TextToSpeechService:
    """Synthesizes text to spoken audio using Kokoro ONNX and plays it back."""

    def __init__(
        self,
        model_path: str = "data/models/kokoro/kokoro-v1.0.onnx",
        voices_path: str = "data/models/kokoro/voices-v1.0.bin",
        voice_name: str = "af_bella",
    ) -> None:
        """Initialize the TTS Service.

        Parameters:
            model_path: Local path where the ONNX model should live.
            voices_path: Local path where the voices binaries should live.
            voice_name: Default speaker voice to use.
        """
        self.model_path = Path(model_path)
        self.voices_path = Path(voices_path)
        self.voice_name = voice_name
        self.kokoro = None

    def warmup(self) -> None:
        """Ensure models are downloaded and load them."""
        if self.kokoro is not None:
            return

        # 1. Ensure models directory exists
        self.model_path.parent.mkdir(parents=True, exist_ok=True)

        # 2. Download missing files
        self._ensure_models()

        # 3. Load Kokoro ONNX
        LOGGER.info("Loading Kokoro ONNX model from %s...", self.model_path)
        self.kokoro = Kokoro(str(self.model_path), str(self.voices_path))

        # 4. Warmup run
        LOGGER.info("Warming up Kokoro TTS model...")
        self.kokoro.create("warmup", voice=self.voice_name, speed=1.0, lang="en-us")
        LOGGER.info("TTS model warmed up successfully.")

    def synthesize(self, text: str) -> bytes:
        """Synthesize text and return it as 16-bit PCM WAV bytes.

        Parameters:
            text: Text to synthesize.

        Returns:
            bytes: WAV audio file bytes.
        """
        if not text.strip():
            return b""

        if self.kokoro is None:
            self.warmup()

        try:
            samples, sample_rate = self.kokoro.create(
                text,
                voice=self.voice_name,
                speed=1.0,
                lang="en-us",
            )
            return self._to_wav_bytes(samples, sample_rate)
        except Exception as exc:
            LOGGER.error("Failed to synthesize text: %s", exc)
            return b""

    def speak(self, text: str) -> float:
        """Synthesizes text and plays it using streaming (sentence by sentence) for low latency.

        Parameters:
            text: Text to speak.

        Returns:
            float: Latency in milliseconds to the start of the first audio chunk.
        """
        if not text.strip():
            return 0.0

        if self.kokoro is None:
            self.warmup()

        import re
        import time

        # Split into sentences (keeping punctuation)
        sentences = re.split(r"(?<=[.!?])\s+", text)
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            return 0.0

        first_byte_latency = 0.0
        start_time = time.perf_counter()

        try:
            LOGGER.info("Starting streaming audio playback (%d segments)...", len(sentences))
            # Synthesis and playback first sentence immediately
            for i, sentence in enumerate(sentences):
                samples, sample_rate = self.kokoro.create(
                    sentence,
                    voice=self.voice_name,
                    speed=1.0,
                    lang="en-us",
                )
                
                if i == 0:
                    first_byte_latency = (time.perf_counter() - start_time) * 1000
                    LOGGER.debug("First segment ready in %.2fms", first_byte_latency)
                
                if i > 0:
                    sd.wait()
                
                sd.play(samples, sample_rate)
            
            sd.wait()
            LOGGER.info("Audio playback complete.")
        except Exception as exc:
            LOGGER.error("Error during streaming speak playback: %s", exc)
        
        return first_byte_latency


    def _ensure_models(self) -> None:
        """Download model files if not present."""
        model_url = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx"
        voices_url = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin"
        
        if not self.model_path.exists():
            LOGGER.info("Downloading kokoro model from %s...", model_url)
            urllib.request.urlretrieve(model_url, self.model_path)
            LOGGER.info("Model download complete.")

        if not self.voices_path.exists():
            LOGGER.info("Downloading kokoro voices from %s...", voices_url)
            urllib.request.urlretrieve(voices_url, self.voices_path)
            LOGGER.info("Voices download complete.")

    def _to_wav_bytes(self, pcm_float: np.ndarray, sample_rate: int) -> bytes:
        """Convert float32 PCM array to 16-bit PCM WAV bytes."""
        pcm_int16 = np.clip(pcm_float, -1.0, 1.0)
        pcm_int16 = (pcm_int16 * 32767.0).astype(np.int16)

        wav_io = io.BytesIO()
        with wave.open(wav_io, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(pcm_int16.tobytes())

        return wav_io.getvalue()
