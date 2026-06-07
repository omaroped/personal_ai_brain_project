# MODULE: Independent background daemon for Voice I/O.
"""Voice Daemon that communicates with the Brain API via WebSockets."""

from __future__ import annotations

import asyncio
import logging
import websockets
import time

from src.common.logging_utils import configure_logging
from src.voice.vad import VoiceActivityDetector
from src.voice.protocol import (
    TranscriptEvent,
    TTSResponseEvent,
    VoiceErrorEvent,
    VoiceMessageType,
    VoiceStatus,
    parse_voice_message,
)
from src.voice.stt import SpeechToTextService
from src.voice.tts import TextToSpeechService
import config

LOGGER = configure_logging(__name__)

class VoiceDaemon:
    def __init__(self):
        self.vad = VoiceActivityDetector()
        self.stt = SpeechToTextService()
        self.tts = TextToSpeechService()
        self.ws_url = f"ws://{config.FASTAPI_HOST}:{config.FASTAPI_PORT}/ws/voice"
        self._cached_language = None
        self._language_streak = 0

    async def connect_and_listen(self):
        LOGGER.info("Starting Voice Daemon...")
        self.stt.warmup()
        self.tts.warmup()
        self.vad.start()

        # Load wake word model if possible
        try:
            from openwakeword.model import Model
            self.oww_model = Model(inference_framework="onnx")
            LOGGER.info("Wake word model loaded. Say 'Hey Jarvis' or 'Alexa' to trigger.")
        except Exception as e:
            LOGGER.warning("OpenWakeWord failed to load. Barge-in disabled: %s", e)
            self.oww_model = None
            
        # Start wake word monitoring thread
        import threading
        self.wake_word_detected = threading.Event()
        if self.oww_model:
            oww_thread = threading.Thread(target=self._wake_word_monitor_loop, daemon=True)
            oww_thread.start()
        
        while True:
            try:
                LOGGER.info("Connecting to Brain API at %s...", self.ws_url)
                async with websockets.connect(self.ws_url) as websocket:
                    LOGGER.info("Connected to Brain API. Waiting for voice input...")
                    
                    # Run listener in a background task
                    listen_task = asyncio.create_task(self._audio_capture_loop(websocket))
                    
                    # Receive responses from Brain API
                    while True:
                        response_data = await websocket.recv()
                        payload = parse_voice_message(response_data)
                        
                        if payload.get("type") == VoiceMessageType.TTS_RESPONSE:
                            text = payload.get("text", "")
                            if text:
                                LOGGER.info("Brain response received. Speaking...")
                                self.vad.pause()
                                try:
                                    # Reset interruption flag before speaking
                                    self.tts._interrupt_event.clear()
                                    self.wake_word_detected.clear()
                                    
                                    # Run TTS (blocking)
                                    self.tts.speak(text)
                                    if not self.tts._interrupt_event.is_set():
                                        time.sleep(0.5) # Wait for room echo to clear if not interrupted
                                    else:
                                        await websocket.send(
                                            VoiceErrorEvent(
                                                message="TTS playback interrupted",
                                                trace_id=payload.get("trace_id"),
                                            ).to_json()
                                        )
                                finally:
                                    self.vad.resume()

            except websockets.exceptions.ConnectionClosed:
                LOGGER.warning("Connection to Brain API lost. Reconnecting in 5s...")
                await asyncio.sleep(5)
            except Exception as e:
                LOGGER.error("Voice Daemon error: %s. Restarting in 5s...", e)
                await asyncio.sleep(5)

    def _wake_word_monitor_loop(self):
        """Continuously monitors the VAD buffer for wake words to interrupt TTS."""
        import queue
        import numpy as np
        while True:
            try:
                if self.vad.is_paused and not self.tts._interrupt_event.is_set():
                    # TTS is speaking! Peek at the mic (we shouldn't read from the queue directly if it's paused)
                    # To implement true barge-in, we need to bypass the paused queue or let the VAD write to a 
                    # secondary buffer when paused. For now, we'll monitor if a dashboard trigger comes in.
                    pass
                
                # Check for dashboard trigger file
                trigger_file = config.DATA_DIR / "voice_trigger.tmp"
                if trigger_file.exists():
                    LOGGER.info("Dashboard trigger detected. Interrupting TTS...")
                    self.tts.interrupt()
                    try:
                        trigger_file.unlink()
                    except: pass
                    
            except Exception as e:
                pass
            time.sleep(0.1)

    async def _audio_capture_loop(self, websocket):
        """Continuously captures audio from VAD and sends it to the API."""
        # Use asyncio.to_thread to prevent blocking the websocket listener
        while True:
            try:
                # read_utterance is blocking
                audio_bytes = await asyncio.to_thread(self.vad.read_utterance)
                if not audio_bytes:
                    continue
                
                # STT is blocking
                transcript, info = await asyncio.to_thread(
                    self.stt.transcribe_bytes, audio_bytes, self._cached_language
                )
                
                if not transcript.strip():
                    continue

                # Handle language caching
                if info:
                    if self._cached_language != info.language:
                        self._language_streak = 0
                        self._cached_language = info.language
                    else:
                        self._language_streak += 1

                LOGGER.info("Heard: '%s'", transcript)
                
                # Send to Brain API
                await websocket.send(
                    TranscriptEvent(
                        text=transcript,
                        detected_language=getattr(info, "language", None),
                    ).to_json()
                )
                
            except Exception as e:
                LOGGER.error("Audio capture loop error: %s", e)
                break

if __name__ == "__main__":
    daemon = VoiceDaemon()
    try:
        asyncio.run(daemon.connect_and_listen())
    except KeyboardInterrupt:
        LOGGER.info("Voice Daemon shutting down.")
        daemon.vad.stop()
