# MODULE: Global hotkey listener using pynput to trigger voice processing.
"""Global hotkey listener to trigger the voice pipeline."""

from __future__ import annotations

import threading
from typing import Callable
from pynput import keyboard

from src.common.logging_utils import configure_logging

LOGGER = configure_logging(__name__)

class HotkeyListener:
    """Listens for a specific hotkey combination and executes a callback."""

    def __init__(self, hotkey_str: str = "<ctrl>+<alt>+v", callback: Callable[[], None] = None) -> None:
        """
        Initialize the hotkey listener.

        Parameters:
            hotkey_str: The pynput-style hotkey string (e.g. "<ctrl>+<alt>+v").
            callback: Function to call when the hotkey is triggered.
        """
        self.hotkey_str = hotkey_str
        self.callback = callback
        self.listener: keyboard.GlobalHotKeys | None = None
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        """Start the hotkey listener in a background thread."""
        if self.listener:
            return

        LOGGER.info("Starting hotkey listener for %s...", self.hotkey_str)
        
        # Define the hotkey map
        hotkeys = {
            self.hotkey_str: self._on_triggered
        }
        
        self.listener = keyboard.GlobalHotKeys(hotkeys)
        self.listener.start()
        LOGGER.info("Hotkey listener active.")

    def stop(self) -> None:
        """Stop the hotkey listener."""
        if self.listener:
            self.listener.stop()
            self.listener = None
            LOGGER.info("Hotkey listener stopped.")

    def _on_triggered(self) -> None:
        """Internal callback for when the hotkey is pressed."""
        LOGGER.info("Hotkey %s triggered!", self.hotkey_str)
        if self.callback:
            try:
                self.callback()
            except Exception as exc:
                LOGGER.error("Error in hotkey callback: %s", exc)

if __name__ == "__main__":
    # Test script
    import time
    def test_callback():
        print("Hotkey caught!")

    listener = HotkeyListener(callback=test_callback)
    listener.start()
    print("Press Ctrl+Space to test. Press Ctrl+C to quit.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        listener.stop()
