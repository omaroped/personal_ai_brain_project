# MODULE: Voice pipeline coordinating VAD, STT, Letta queries, and TTS.
"""VoicePipeline connects STT, VAD, Letta agent backend, and TTS."""

from __future__ import annotations

import httpx
import time
import threading
import json
import config

from src.common.logging_utils import configure_logging
from src.agents.planner import TaskPlanner
from src.memory.letta_agent import OmarBrainAgent
from src.memory.openclaw_agent import OpenClawAgent
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
        self.brain = OmarBrainAgent()
        self.openclaw = OpenClawAgent()
        self.planner = TaskPlanner()
        self.is_running = False
        self._trigger_event = threading.Event()
        self._cached_language = None
        self._language_streak = 0

    def warmup(self) -> None:
        """Warm up all subsystems."""
        LOGGER.info("Warming up voice pipeline components...")
        self.stt.warmup()
        self.tts.warmup()

        # Connect to Letta and find agent
        try:
            self.brain.ensure_agent()
            LOGGER.info("Connected to Letta agent: %s (ID: %s)", self.brain.agent_name, self.brain.agent_id)
        except Exception as exc:
            LOGGER.error("Failed to connect to Letta agent: %s. Voice queries will fail.", exc)

    def run_forever(self) -> None:
        """Continuously loop, waiting for hotkey or wake word trigger."""
        self.warmup()
        self.vad.start()
        self.hotkey.start()
        self.is_running = True

        try:
            from openwakeword.model import Model
            oww_model = Model(inference_framework="onnx")
            LOGGER.info("Wake word model loaded. Say 'Hey Jarvis' or 'Alexa' to trigger.")
        except Exception as e:
            LOGGER.warning("OpenWakeWord failed to load. Only hotkey/dashboard triggers will work: %s", e)
            oww_model = None

        LOGGER.info("Voice Pipeline active. Press %s, click Dashboard, or use Wake Word to talk!", self.hotkey.hotkey_str)
        trigger_file = config.DATA_DIR / "voice_trigger.tmp"
        
        try:
            while self.is_running:
                # 1. Check for settings changes
                self._check_settings()

                # 2. Fast check for dashboard trigger
                triggered = False
                if trigger_file.exists():
                    LOGGER.info("Detected dashboard voice trigger.")
                    try:
                        trigger_file.unlink() # consume trigger
                    except: pass
                    triggered = True
                
                # 3. Fast check for hotkey
                if not triggered and self._trigger_event.is_set():
                    self._trigger_event.clear()
                    triggered = True

                # 4. Background Wake Word Detection
                if not triggered and not self.vad.is_paused and oww_model:
                    import queue
                    import numpy as np
                    try:
                        # Peek at the audio stream safely without blocking the VAD loop completely
                        # OpenWakeWord expects 16khz 1D arrays
                        # Get a chunk from the queue (VAD queue gets updated continuously)
                        # We use get_nowait to not block
                        chunk = self.vad._audio_queue.get_nowait()
                        # Convert to right format for openwakeword
                        chunk_flat = chunk.squeeze()
                        if chunk_flat.dtype == np.float32:
                            # Convert float32 to int16 for OWW
                            chunk_int16 = (np.clip(chunk_flat, -1.0, 1.0) * 32767).astype(np.int16)
                            prediction = oww_model.predict(chunk_int16)
                            
                            # Check if any model crossed the threshold
                            for mdl, score in prediction.items():
                                if score > 0.5:
                                    LOGGER.info("Wake word detected: %s (score: %.2f)", mdl, score)
                                    triggered = True
                                    # Play a short "bloop" or just trigger
                                    break
                    except queue.Empty:
                        pass
                    except Exception as e:
                        pass
                        
                if triggered:
                    self.process_once()
                else:
                    # Give CPU a tiny rest if we didn't do anything
                    import time
                    time.sleep(0.05)
        except KeyboardInterrupt:
            LOGGER.info("Voice Pipeline stopped via keyboard interrupt.")
        finally:
            self.hotkey.stop()
            self.vad.stop()

    def _check_settings(self) -> None:
        """Check for updated settings from the web API."""
        if not config.SETTINGS_FILE.exists():
            return

        try:
            with open(config.SETTINGS_FILE, "r") as f:
                settings = json.load(f)
            
            new_mic_index = settings.get("mic_index")
            if new_mic_index is not None and new_mic_index != self.vad.device_index:
                LOGGER.info("Detected mic change in settings: %s -> %s", self.vad.device_index, new_mic_index)
                self.vad.stop()
                self.vad.device_index = new_mic_index
                self.vad.start()
        except Exception as exc:
            LOGGER.error("Failed to check or apply settings: %s", exc)

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
        transcript, info = self.stt.transcribe_bytes(audio_bytes, language=self._cached_language)
        duration_stt = (time.perf_counter() - start_stt) * 1000

        if not transcript.strip():
            LOGGER.info("VAD captured noise or empty segment. Ignoring.")
            return

        # Language auto-detection optimization
        if info:
            detected_lang = info.language
            if self._cached_language != detected_lang:
                self._language_streak = 0
                self._cached_language = detected_lang
                LOGGER.info("Switching voice language to: %s", detected_lang)
            else:
                self._language_streak += 1
                if self._language_streak >= 3:
                    LOGGER.debug("Stable language detected: %s", detected_lang)

        LOGGER.info("User said: '%s' [VAD: %.2fms | STT: %.2fms | Lang: %s]", 
                    transcript, duration_vad, duration_stt, self._cached_language)

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
        
        # Pause VAD to prevent the microphone from picking up the TTS output (speaker echo loop)
        self.vad.pause()
        try:
            first_token_latency_tts = self.tts.speak(response_text)
            # Give the room echo a moment to clear before turning mic back on
            time.sleep(0.5)
        finally:
            self.vad.resume()
            
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

        # 5. Log session for daily review
        self._log_session(transcript, response_text)

    def _log_session(self, user_text: str, brain_text: str) -> None:
        """Append interaction to daily JSONL log."""
        import json
        from datetime import datetime, date
        import config

        log_dir = config.LOGS_DIR / "sessions"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / f"{date.today().isoformat()}.jsonl"

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user": user_text,
            "brain": brain_text,
        }

        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        except Exception as exc:
            LOGGER.error("Failed to write session log: %s", exc)

    def handle_transcript(self, transcript: str) -> str:
        """Send transcript to TaskPlanner or Brain."""
        
        # Determine if this is an actionable command or just a chat.
        # Simple heuristic: if it starts with verbs like 'open', 'search', 'remind', 'tell', 'summarize'
        action_keywords = ["open", "search", "find", "summarize", "read", "run", "execute", "notify", "remind", "delegate"]
        first_word = transcript.split()[0].lower() if transcript else ""
        
        is_action = first_word in action_keywords or "open" in transcript.lower()

        if is_action:
            LOGGER.info("Action detected. Routing to Task Planner: '%s'", transcript)
            # We add context so the planner knows it's a voice command
            goal = f"The user just said via voice: '{transcript}'. Execute the necessary tools and return a spoken summary."
            return self.planner.execute(goal)

        # 1. Check for Turbo Mode and OpenClaw in settings
        turbo_mode = False
        openclaw_mode = True # Default to trying OpenClaw first as per new spec
        
        if config.SETTINGS_FILE.exists():
            try:
                with open(config.SETTINGS_FILE, "r") as f:
                    settings = json.load(f)
                    turbo_mode = settings.get("turbo", False)
                    if "openclaw" in settings:
                        openclaw_mode = settings.get("openclaw")
            except Exception:
                pass
        
        # 2. Try OpenClaw Bypass (Highest Priority if enabled)
        if openclaw_mode:
            response = self.openclaw.send_message(transcript)
            if "Error:" not in response and "trouble connecting" not in response:
                return response
            LOGGER.warning("OpenClaw bypass failed, falling back: %s", response)
        
        # 3. Try Gemini Turbo Mode
        if turbo_mode and config.GEMINI_API_KEY:
            LOGGER.info("Turbo Mode active. Routing to Gemini...")
            try:
                import google.generativeai as genai
                genai.configure(api_key=config.GEMINI_API_KEY)
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(transcript)
                return response.text
            except Exception as e:
                LOGGER.error("Gemini Turbo failed, falling back to Letta: %s", e)

        # 4. Fallback to Local Letta Agent
        return self.brain.send_message(transcript)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", type=int, help="Audio device index", default=None)
    args = parser.parse_args()

    pipeline = VoicePipeline(audio_device=args.device)
    pipeline.run_forever()
