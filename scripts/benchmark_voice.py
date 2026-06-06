# MODULE: Benchmark script to measure STT and TTS latency and correctness.
"""Measure component and pipeline latencies using local hardware."""

from __future__ import annotations

import sys
import time
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from src.voice.stt import SpeechToTextService
from src.voice.tts import TextToSpeechService


def main() -> None:
    """Run voice benchmarks and report results."""
    print("=========================================")
    print("🎙️ Personal AI Brain Voice Benchmark 🎙️")
    print("=========================================\n")

    # Initialize services
    print("Initializing services...")
    stt = SpeechToTextService(model_size="base")
    tts = TextToSpeechService()

    print("\nWarming up STT model (loads weights and runs a test pass)...")
    start_stt_warm = time.perf_counter()
    stt.warmup()
    print(f"STT warmup completed in {time.perf_counter() - start_stt_warm:.2f}s")

    print("\nWarming up TTS model (downloads weights if missing, runs test pass)...")
    start_tts_warm = time.perf_counter()
    tts.warmup()
    print(f"TTS warmup completed in {time.perf_counter() - start_tts_warm:.2f}s")

    # 1. Benchmark TTS
    phrase = "Hello. This is a five second voice benchmark test."
    print(f"\nBenchmarking TTS synthesis for phrase: '{phrase}'")
    start_tts = time.perf_counter()
    wav_bytes = tts.synthesize(phrase)
    tts_latency = (time.perf_counter() - start_tts) * 1000
    print(f"TTS Synthesis Latency: {tts_latency:.2f}ms")
    print(f"Generated WAV size: {len(wav_bytes)} bytes")

    # Save test file
    test_file = Path("data/voice_benchmark_test.wav")
    test_file.parent.mkdir(parents=True, exist_ok=True)
    test_file.write_bytes(wav_bytes)
    print(f"Saved temporary benchmark audio to {test_file}")

    # 2. Benchmark STT on the file
    print(f"\nBenchmarking STT transcription on saved file...")
    start_stt_file = time.perf_counter()
    transcript_file = stt.transcribe_file(test_file)
    stt_file_latency = (time.perf_counter() - start_stt_file) * 1000
    print(f"STT File Transcription Latency: {stt_file_latency:.2f}ms")
    print(f"Transcript (file): '{transcript_file}'")

    # 3. Benchmark STT on bytes in-memory
    print("\nBenchmarking STT transcription on in-memory bytes...")
    start_stt_bytes = time.perf_counter()
    transcript_bytes = stt.transcribe_bytes(wav_bytes)
    stt_bytes_latency = (time.perf_counter() - start_stt_bytes) * 1000
    print(f"STT Bytes Transcription Latency: {stt_bytes_latency:.2f}ms")
    print(f"Transcript (bytes): '{transcript_bytes}'")

    # Clean up test file
    if test_file.exists():
        test_file.unlink()

    print("\n=========================================")
    print("📝 Latency Summary (Target: STT < 200ms)")
    print(f"TTS Synthesis: {tts_latency:.2f}ms")
    print(f"STT File:      {stt_file_latency:.2f}ms")
    print(f"STT Bytes:     {stt_bytes_latency:.2f}ms")
    print("=========================================")


if __name__ == "__main__":
    main()
