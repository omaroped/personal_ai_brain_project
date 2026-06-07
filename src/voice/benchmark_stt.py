# MODULE: STT Benchmarking
import time
import logging
from faster_whisper import WhisperModel
import os
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def benchmark_stt(model_size: str = "base", device: str = "cuda", compute_type: str = "float16"):
    """
    Benchmarks the faster-whisper model on a 5s audio clip.
    """
    audio_path = str((Path(__file__).resolve().parents[2] / "tests" / "benchmark_5s.wav"))
    
    if not os.path.exists(audio_path):
        logger.error(f"Audio file not found: {audio_path}")
        return

    logger.info(f"Loading model '{model_size}' on '{device}' with '{compute_type}'...")
    start_load = time.time()
    model = WhisperModel(model_size, device=device, compute_type=compute_type)
    load_duration = time.time() - start_load
    logger.info(f"Model loaded in {load_duration:.2f}s")

    # Warm-up run
    logger.info("Performing warm-up run...")
    model.transcribe(audio_path, beam_size=1)
    
    # Benchmark run
    logger.info("Starting benchmark transcription...")
    start_transcribe = time.time()
    segments, info = model.transcribe(audio_path, beam_size=1)
    # Segments is a generator, must iterate to finish transcription
    text = "".join([segment.text for segment in segments])
    transcribe_duration = (time.time() - start_transcribe) * 1000 # in ms
    
    logger.info(f"Transcription finished in {transcribe_duration:.2f}ms")
    logger.info(f"Detected language: {info.language} ({info.language_probability:.2f})")
    
    if transcribe_duration < 200:
        logger.info("SUCCESS: Transcription latency is below 200ms.")
    else:
        logger.warning(f"FAILURE: Transcription latency ({transcribe_duration:.2f}ms) is above 200ms.")

if __name__ == "__main__":
    benchmark_stt()
