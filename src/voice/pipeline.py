# MODULE: Voice pipeline coordinating VAD, STT, Letta queries, and TTS.
"""VoicePipeline connects STT, VAD, Letta agent backend, and TTS."""

from __future__ import annotations

import httpx
import time
import threading

from src.common.logging_utils import configure_logging
from src.memory.core_memory import LettaRuntime
from src.voice.vad import VoiceActivityDetector
from src.voice.stt import SpeechToTextService
from src.voice.tts import TextToSpeechService
from src.voice.hotkey import HotkeyListener

LOGGER = configure_logging(__name__)


class VoicePipeline:
    """Manages the continuous loop of listening, transcribing, reasoning, and speaking."""

    def __init__(
        self,
        vad: VoiceActivityDetector | None = None,
        stt: SpeechToTextService | None = None,
        tts: TextToSpeechService | None = None,
        hotkey_str: str = "<ctrl>+<alt>+v",
        audio_device: int | None = None,
    ) -> None:
        """Initialize the Voice Pipeline.

        Parameters:
            vad: Optional custom VAD instance.
            stt: Optional custom STT service instance.
            tts: Optional custom TTS service instance.
            hotkey_str: Hotkey string to trigger interaction.
            audio_device: Specific microphone device index.
        """
        self.vad = vad or VoiceActivityDetector(device_index=audio_device)
        self.stt = stt or SpeechToTextService()
        self.tts = tts or TextToSpeechService()
        self.hotkey = HotkeyListener(hotkey_str=hotkey_str, callback=self.trigger_interaction)
        self.letta_runtime = LettaRuntime()
        self.agent_id = None
        self.is_running = False
        self._trigger_event = threading.Event()

    def warmup(self) -> None:
        """Warm up all subsystems."""
        LOGGER.info("Warming up voice pipeline components...")
        self.stt.warmup()
        self.tts.warmup()

        # Connect to Letta and find agent
        try:
            agent = self.letta_runtime.ensure_agent()
            self.agent_id = agent.get("id") or agent.get("agent_id")
            LOGGER.info("Connected to Letta agent: %s (ID: %s)", agent.get("name"), self.agent_id)
        except Exception as exc:
            LOGGER.error("Failed to connect to Letta agent: %s. Voice queries will fail.", exc)

    def run_forever(self) -> None:
        """Continuously loop, waiting for hotkey trigger."""
        self.warmup()
        self.vad.start()
        self.hotkey.start()
        self.is_running = True

        LOGGER.info("Voice Pipeline active. Press %s to talk!", self.hotkey.hotkey_str)
        try:
            while self.is_running:
                # Wait for hotkey trigger
                if self._trigger_event.wait(timeout=1.0):
                    self._trigger_event.clear()
                    self.process_once()
        except KeyboardInterrupt:
            LOGGER.info("Voice Pipeline stopped via keyboard interrupt.")
        finally:
            self.hotkey.stop()
            self.vad.stop()

    def trigger_interaction(self) -> None:
        """Callback for hotkey trigger."""
        LOGGER.info("Interaction triggered via hotkey.")
        self._trigger_event.set()

    def process_once(self) -> None:
        """Capture one utterance, run STT, query the brain, and output TTS."""
        # 1. Capture speech (VAD)
        start_vad = time.perf_counter()
        audio_bytes = self.vad.read_utterance()
        duration_vad = (time.perf_counter() - start_vad) * 1000

        if not audio_bytes:
            return

        # 2. Transcribe (STT)
        start_stt = time.perf_counter()
        transcript = self.stt.transcribe_bytes(audio_bytes)
        duration_stt = (time.perf_counter() - start_stt) * 1000

        if not transcript.strip():
            LOGGER.info("VAD captured noise or empty segment. Ignoring.")
            return

        LOGGER.info("User said: '%s' [VAD: %.2fms | STT: %.2fms]", transcript, duration_vad, duration_stt)

        # 3. Query Brain (Letta)
        start_query = time.perf_counter()
        response_text = self.handle_transcript(transcript)
        duration_query = (time.perf_counter() - start_query) * 1000

        if not response_text.strip():
            LOGGER.warning("Brain returned empty response.")
            return

        LOGGER.info("Brain responded: '%s' [Query: %.2fms]", response_text, duration_query)

        # 4. Speak response (TTS)
        LOGGER.info("Synthesizing and playing response...")
        start_tts = time.perf_counter()
        first_token_latency_tts = self.tts.speak(response_text)
        duration_tts_total = (time.perf_counter() - start_tts) * 1000

        # End-to-end latency is from start of STT to start of TTS audio
        total_e2e_latency = duration_stt + duration_query + first_token_latency_tts
        
        LOGGER.info(
            "Latency summary: STT=%.2fms | Query=%.2fms | TTS_first=%.2fms | E2E_latency=%.2fms | TTS_total=%.2fms",
            duration_stt,
            duration_query,
            first_token_latency_tts,
            total_e2e_latency,
            duration_tts_total,
        )

    def handle_transcript(self, transcript: str) -> str:
        """Send transcript to Letta agent and return the response string.

        Parameters:
            transcript: Transcribed user input text.

        Returns:
            str: Brain response text.
        """
        if not self.agent_id:
            try:
                agent = self.letta_runtime.ensure_agent()
                self.agent_id = agent.get("id") or agent.get("agent_id")
            except Exception as exc:
                LOGGER.error("Cannot resolve Letta agent: %s", exc)
                return "Error connecting to Letta agent."

        url = f"http://localhost:8283/v1/agents/{self.agent_id}/messages"
        payload = {"input": transcript}

        try:
            resp = httpx.post(url, json=payload, timeout=60.0)
            if resp.status_code == 422 or resp.status_code == 400:
                # Fallback to standard messages format if needed
                alt_payload = {
                    "messages": [{"role": "user", "content": transcript}]
                }
                resp = httpx.post(url, json=alt_payload, timeout=60.0)

            resp.raise_for_status()
            response_data = resp.json()

            # Parse responses to extract the assistant content
            messages = response_data.get("messages", response_data)
            assistant_replies = []
            if isinstance(messages, list):
                for msg in messages:
                    role = msg.get("role") or msg.get("message_type")
                    text = msg.get("text") or msg.get("content")
                    thought = msg.get("thought") or msg.get("reasoning")
                    if thought:
                        LOGGER.info("Brain Thought: %s", thought)
                    if (role == "assistant" or role == "assistant_message") and text:
                        assistant_replies.append(text)
                return "\n".join(assistant_replies).strip()
            else:
                return str(response_data)
        except Exception as exc:
            LOGGER.error("Error communicating with Letta agent: %s", exc)
            return "Sorry, I had trouble communicating with my memory engine."

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", type=int, help="Audio device index", default=None)
    args = parser.parse_args()

    pipeline = VoicePipeline(audio_device=args.device)
    pipeline.run_forever()
