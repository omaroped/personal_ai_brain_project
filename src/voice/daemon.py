# MODULE: Independent background daemon for Voice I/O.
"""Voice Daemon that communicates with the Brain API via WebSockets."""

from __future__ import annotations

import asyncio
import json
import logging
import websockets
import time

from src.common.logging_utils import configure_logging
from src.voice.vad import VoiceActivityDetector
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
                        payload = json.loads(response_data)
                        
                        if payload.get("type") == "tts_response":
                            text = payload.get("text", "")
                            if text:
                                LOGGER.info("Brain response received. Speaking...")
                                self.vad.pause()
                                try:
                                    # Run TTS (blocking)
                                    self.tts.speak(text)
                                    time.sleep(0.5) # Wait for room echo to clear
                                finally:
                                    self.vad.resume()

            except websockets.exceptions.ConnectionClosed:
                LOGGER.warning("Connection to Brain API lost. Reconnecting in 5s...")
                await asyncio.sleep(5)
            except Exception as e:
                LOGGER.error("Voice Daemon error: %s. Restarting in 5s...", e)
                await asyncio.sleep(5)

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
                await websocket.send(json.dumps({
                    "type": "transcript",
                    "text": transcript
                }))
                
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
