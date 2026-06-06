# MODULE: Voice Brain terminal runner script supporting hotkey triggers and fallbacks.
"""Terminal entry point for running the voice assistant loop."""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from src.common.logging_utils import configure_logging
from src.voice.pipeline import VoicePipeline

LOGGER = configure_logging(__name__)


def run_manual_loop(pipeline: VoicePipeline) -> None:
    """Fallback manual trigger loop when hotkeys cannot be registered."""
    print("\n------------------------------------------------------------")
    print("⌨️ Keyboard listener failed to initialize (headless environment).")
    print("👉 Manual trigger active: Press ENTER to speak. Type 'exit' to quit.")
    print("------------------------------------------------------------\n")

    while True:
        try:
            cmd = input("\n[Press Enter to Speak, or type 'exit']: ").strip()
            if cmd.lower() in {"exit", "quit"}:
                break
            # Trigger VAD capture and processing
            pipeline.process_once()
        except (KeyboardInterrupt, EOFError):
            break


def main() -> None:
    """Start the voice pipeline and hook up keyboard trigger listener."""
    print("\n==============================================")
    print("🎙️ Personal AI Brain - Voice Assistant CLI 🎙️")
    print("==============================================\n")

    pipeline = VoicePipeline()
    pipeline.warmup()

    # Attempt to setup pynput hotkey trigger
    try:
        from pynput import keyboard

        LOGGER.info("Registering keyboard hotkey: Ctrl+Space")
        
        # Flag to track active listening state
        is_processing = False

        def on_trigger() -> None:
            nonlocal is_processing
            if is_processing:
                return
            is_processing = True
            try:
                print("\n🎙️ Listening (Ctrl+Space triggered)...")
                pipeline.process_once()
            except Exception as exc:
                LOGGER.error("Error during voice process tick: %s", exc)
            finally:
                is_processing = False
                print("\n😴 Sleeping. Press Ctrl+Space to talk again.")

        # Construct global hotkey definition
        hotkey = keyboard.HotKey(
            keyboard.HotKey.parse("<ctrl>+<space>"),
            on_trigger,
        )

        def on_press(key: any) -> None:
            hotkey.press(listener.canonical(key))

        def on_release(key: any) -> None:
            hotkey.release(listener.canonical(key))

        # Start pynput Listener
        listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        listener.start()
        
        print("\n------------------------------------------------------------")
        print("✅ Keyboard listener active!")
        print("👉 Press Ctrl+Space to activate the microphone.")
        print("👉 Press Ctrl+C in this terminal to exit.")
        print("------------------------------------------------------------\n")
        
        # Keep main thread alive
        listener.join()

    except Exception as exc:
        LOGGER.warning("Could not initialize keyboard hotkey listener: %s.", exc)
        run_manual_loop(pipeline)

    print("\n👋 Goodbye!")


if __name__ == "__main__":
    main()
