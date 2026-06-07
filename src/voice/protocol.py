# MODULE: Typed protocol models for communication between the voice daemon and Brain API.
"""Canonical voice IPC message schemas and serialization helpers."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json
import uuid


VOICE_PROTOCOL_VERSION = "1.0"


class VoiceMessageType:
    """String constants for voice IPC message categories."""

    TRANSCRIPT = "transcript"
    TTS_RESPONSE = "tts_response"
    STATUS = "status"
    ERROR = "error"
    CONTROL = "control"


class VoiceStatus:
    """Canonical voice runtime states."""

    IDLE = "idle"
    LISTENING = "listening"
    THINKING = "thinking"
    SPEAKING = "speaking"
    INTERRUPTED = "interrupted"
    ERROR = "error"


@dataclass
class VoiceEnvelope:
    """Shared metadata wrapper for voice IPC payloads."""

    type: str
    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    protocol_version: str = VOICE_PROTOCOL_VERSION

    def to_json(self) -> str:
        """Serialize the message to a JSON string."""
        return json.dumps(asdict(self))


@dataclass
class TranscriptEvent(VoiceEnvelope):
    """Voice daemon -> Brain API transcript payload."""

    text: str = ""
    detected_language: str | None = None
    source: str = "voice_daemon"

    def __init__(
        self,
        text: str,
        detected_language: str | None = None,
        trace_id: str | None = None,
        source: str = "voice_daemon",
    ) -> None:
        super().__init__(
            type=VoiceMessageType.TRANSCRIPT,
            trace_id=trace_id or str(uuid.uuid4()),
        )
        self.text = text
        self.detected_language = detected_language
        self.source = source


@dataclass
class TTSResponseEvent(VoiceEnvelope):
    """Brain API -> voice daemon playback payload."""

    text: str = ""
    status: str = VoiceStatus.SPEAKING

    def __init__(self, text: str, trace_id: str, status: str = VoiceStatus.SPEAKING) -> None:
        super().__init__(type=VoiceMessageType.TTS_RESPONSE, trace_id=trace_id)
        self.text = text
        self.status = status


@dataclass
class VoiceStatusEvent(VoiceEnvelope):
    """Status event for dashboard or voice control state updates."""

    status: str = VoiceStatus.IDLE
    detail: str | None = None

    def __init__(self, status: str, trace_id: str | None = None, detail: str | None = None) -> None:
        super().__init__(
            type=VoiceMessageType.STATUS,
            trace_id=trace_id or str(uuid.uuid4()),
        )
        self.status = status
        self.detail = detail


@dataclass
class VoiceErrorEvent(VoiceEnvelope):
    """Error event exchanged across voice IPC."""

    message: str = ""

    def __init__(self, message: str, trace_id: str | None = None) -> None:
        super().__init__(
            type=VoiceMessageType.ERROR,
            trace_id=trace_id or str(uuid.uuid4()),
        )
        self.message = message


def parse_voice_message(raw_text: str) -> dict:
    """Parse and lightly normalize inbound voice JSON payloads."""
    payload = json.loads(raw_text)
    if "protocol_version" not in payload:
        payload["protocol_version"] = VOICE_PROTOCOL_VERSION
    if "trace_id" not in payload:
        payload["trace_id"] = str(uuid.uuid4())
    return payload
