# MODULE: Proactive monitor that suggests relevant info based on active window.
"""Proactive monitoring service to provide contextual help based on user activity."""

from __future__ import annotations

import os
import subprocess
import time
import logging
from pathlib import Path
from typing import Optional

from src.common.logging_utils import configure_logging
from src.ingestion.vector_store import VectorStore
import config

LOGGER = configure_logging(__name__)

def get_active_window_title() -> str:
    """Get active window title using the best available method for the OS/Desktop."""
    # 1. Check for Wayland (GNOME)
    try:
        if os.environ.get("XDG_SESSION_TYPE") == "wayland":
            result = subprocess.run(
                ["gdbus", "call", "--session",
                 "--dest", "org.gnome.Shell",
                 "--object-path", "/org/gnome/Shell",
                 "--method", "org.gnome.Shell.Eval",
                 "global.display.focus_window.title"],
                capture_output=True, text=True, timeout=1
            )
            output = result.stdout.strip()
            # GNOME Eval returns: (true, '"Window Title"')
            if '"' in output:
                return output.split('"')[1]
    except Exception:
        pass

    # 2. Fallback to xdotool (X11)
    try:
        result = subprocess.run(["xdotool", "getactivewindow", "getwindowname"], capture_output=True, text=True, timeout=1)
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    
    return ""

class ProactiveMonitor:
    """Monitors the user's active window and notifies them of relevant vault content."""

    CHECK_INTERVAL = 30
    RELEVANCE_THRESHOLD = 0.8
    COOLDOWN = 300 # 5 minutes between similar notifications

    def __init__(self) -> None:
        self.vector_store = VectorStore("documents")
        self.last_notified_title = ""
        self.last_notify_time = 0
        self.is_running = False

    def run(self) -> None:
        """Start the monitoring loop."""
        LOGGER.info("Proactive Monitor started.")
        self.is_running = True
        
        while self.is_running:
            try:
                title = get_active_window_title()
                
                # Basic filtering
                if not title or len(title) < 5:
                    time.sleep(self.CHECK_INTERVAL)
                    continue

                # Skip if too soon or same as last time
                if title == self.last_notified_title or (time.time() - self.last_notify_time < self.COOLDOWN):
                    time.sleep(self.CHECK_INTERVAL)
                    continue

                # Search vault for title relevance
                results = self.vector_store.hybrid_search(title, top_k=1)
                if results:
                    best = results[0]
                    if best.score >= self.RELEVANCE_THRESHOLD:
                        self._notify(best.section, Path(best.source_file).name)
                        self.last_notified_title = title
                        self.last_notify_time = time.time()
                
            except KeyboardInterrupt:
                break
            except Exception as exc:
                LOGGER.error("Monitor loop error: %s", exc)
            
            time.sleep(self.CHECK_INTERVAL)

    def _notify(self, section: str, filename: str) -> None:
        """Send a system notification."""
        message = f"💡 Related: '{section}' from {filename}"
        LOGGER.info("Contextual suggestion: %s", message)
        try:
            subprocess.run(["notify-send", "AI Brain", message, "--expire-time=5000"], check=False)
        except Exception as e:
            LOGGER.error("Failed to send notification: %s", e)

if __name__ == "__main__":
    monitor = ProactiveMonitor()
    monitor.run()
