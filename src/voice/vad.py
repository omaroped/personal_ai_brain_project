# MODULE: Voice Activity Detector using Silero VAD and sounddevice microphone capture.
"""Voice activity detection module to capture user spoken utterances."""

from __future__ import annotations

import io
import queue
import sys
import wave
import numpy as np
import torch

from src.common.logging_utils import configure_logging

LOGGER = configure_logging(__name__)


class VoiceActivityDetector:
    """Listens continuously to microphone input and captures individual spoken utterances."""

    def __init__(
        self,
        threshold: float = 0.5,
        sample_rate: int = 16000,
        chunk_size: int = 512,
        silence_duration_sec: float = 1.0,
        device_index: int | None = None,
    ) -> None:
        """Initialize the voice activity detector.

        Parameters:
            threshold: Probability threshold above which audio is considered speech.
            sample_rate: Audio sampling rate (Silero VAD supports 8000 or 16000).
            chunk_size: Chunk size in samples for the VAD model.
            silence_duration_sec: Seconds of silence to wait before ending speech segment.
            device_index: Specific sounddevice index to use for input.
        """
        self.threshold = threshold
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.silence_duration_sec = silence_duration_sec
        self.device_index = device_index
        self.model: torch.jit.ScriptModule | None = None
        self.is_running = False
        self._audio_queue: queue.Queue[np.ndarray] = queue.Queue()
        self._stream = None

    def start(self) -> None:
        """Start microphone recording and load Silero VAD."""
        if self.is_running:
            return

        import sounddevice as sd

        # 1. Load Silero VAD model
        if self.model is None:
            try:
                # Attempt to load from silero_vad package
                from silero_vad import load_silero_vad
                self.model = load_silero_vad()
            except Exception as exc:
                LOGGER.warning("Could not load via silero_vad package: %s. Falling back to torch.hub.", exc)
                # Fallback to torch hub
                self.model, _ = torch.hub.load(
                    repo_or_dir="snakers4/silero-vad",
                    model="silero_vad",
                    trust_repo=True,
                )

        # Reset model state
        if hasattr(self.model, "reset_states"):
            self.model.reset_states()

        # 2. Setup audio queue and sounddevice stream
        self._audio_queue = queue.Queue()
        self.is_running = True

        def callback(indata: np.ndarray, frames: int, time_info: any, status: any) -> None:
            if status:
                LOGGER.warning("sounddevice stream status: %s", status)
            self._audio_queue.put(indata.copy())

        self._stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype="float32",
            callback=callback,
            blocksize=self.chunk_size,
            device=self.device_index,
        )
        self._stream.start()
        LOGGER.info("VoiceActivityDetector started on device %s", self.device_index or "default")

    def stop(self) -> None:
        """Stop microphone recording stream."""
        self.is_running = False
        if self._stream:
            try:
                self._stream.stop()
                self._stream.close()
            except Exception as exc:
                LOGGER.error("Error closing stream: %s", exc)
            self._stream = None
        LOGGER.info("VoiceActivityDetector stopped.")

    def read_utterance(self) -> bytes:
        """Block until an utterance is completed, and return it as 16-bit PCM WAV bytes."""
        if not self.is_running:
            raise RuntimeError("VAD is not running. Call start() first.")

        LOGGER.info("Listening for speech...")
        collected_frames: list[np.ndarray] = []
        in_speech = False
        silence_chunks_threshold = int((self.silence_duration_sec * self.sample_rate) / self.chunk_size)
        silence_chunks_count = 0

        # Keep a ring buffer of a few pre-speech frames to avoid clipping the start of speech
        pre_speech_ring: list[np.ndarray] = []
        pre_speech_limit = 5  # keep last ~150ms of audio

        while self.is_running:
            try:
                chunk = self._audio_queue.get(timeout=0.1)
            except queue.Empty:
                continue

            # Ensure chunk is 1D array
            chunk_flat = chunk.squeeze()

            # Run model prediction
            # Convert numpy to PyTorch tensor
            tensor_chunk = torch.from_numpy(chunk_flat)
            with torch.no_grad():
                prob = self.model(tensor_chunk, self.sample_rate).item()

            if not in_speech:
                if prob >= self.threshold:
                    in_speech = True
                    # Prepend pre-speech frames to avoid clipping the start of the utterance
                    collected_frames.extend(pre_speech_ring)
                    collected_frames.append(chunk_flat)
                    LOGGER.info("Speech started...")
                else:
                    pre_speech_ring.append(chunk_flat)
                    if len(pre_speech_ring) > pre_speech_limit:
                        pre_speech_ring.pop(0)
            else:
                collected_frames.append(chunk_flat)
                if prob < self.threshold:
                    silence_chunks_count += 1
                    if silence_chunks_count >= silence_chunks_threshold:
                        LOGGER.info("Speech ended (silence threshold reached).")
                        break
                else:
                    silence_chunks_count = 0

        if not collected_frames:
            return b""

        # Concatenate and convert to 16-bit PCM WAV bytes
        audio_data = np.concatenate(collected_frames)
        return self._to_wav_bytes(audio_data)

    def _to_wav_bytes(self, pcm_float: np.ndarray) -> bytes:
        """Convert float32 PCM array to 16-bit PCM WAV bytes."""
        # Normalize/clamp float32 to range [-1.0, 1.0] and scale to int16
        pcm_int16 = np.clip(pcm_float, -1.0, 1.0)
        pcm_int16 = (pcm_int16 * 32767.0).astype(np.int16)

        wav_io = io.BytesIO()
        with wave.open(wav_io, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)  # 2 bytes per sample (16-bit)
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(pcm_int16.tobytes())

        return wav_io.getvalue()
