# MODULE: Audio utility functions for device management.
"""Utilities for listing and managing audio input/output devices."""

from __future__ import annotations

import sounddevice as sd
from src.common.logging_utils import configure_logging

LOGGER = configure_logging(__name__)

def list_input_devices() -> list[dict]:
    """Return a list of available audio input devices."""
    devices = sd.query_devices()
    input_devices = []
    for i, dev in enumerate(devices):
        if dev['max_input_channels'] > 0:
            input_devices.append({
                "index": i,
                "name": dev['name'],
                "hostapi": dev['hostapi'],
                "max_input_channels": dev['max_input_channels'],
                "default_samplerate": dev['default_samplerate']
            })
    return input_devices

if __name__ == "__main__":
    for d in list_input_devices():
        print(f"[{d['index']}] {d['name']}")
