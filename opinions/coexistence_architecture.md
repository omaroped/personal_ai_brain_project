# Coexistence Architecture for a Local-First Voice-Activated AI Workstation

## Hardware and Resource Reality

Deploying a real-time, local-first voice agent on a consumer mechatronics workstation powered by an AMD Ryzen 5 5600H CPU and an NVIDIA RTX 3060 Laptop GPU requires strict resource budgeting to prevent performance degradation. The hardware platform presents a hard memory barrier: while the physical VRAM is 6GB, the maximum safe allocation to prevent operating system instability, display flickering, and CUDA out-of-memory crashes is exactly 5.5GB (5632 MB).

The primary VRAM allocation conflict arises between the local Large Language Model (LLM), the Speech-to-Text (STT) transcription engine, and the vector embedding model. Running mistral-7b-instruct via Ollama in 4-bit precision (specifically the Q4_K_M quantization) requires a persistent allocation of approximately 4.1GB (4198 MB) of VRAM. Additionally, a local Whisper-based STT engine utilizing the Whisper Base model in FP16 precision consumes approximately 600MB (614 MB) of VRAM to ensure rapid, streaming transcription.

Subtracting these allocations from the safe memory budget leaves a highly constrained VRAM headroom:
$$V_{\text{headroom}} = V_{\text{safe}} - (V_{\text{LLM}} + V_{\text{STT}})$$
$$V_{\text{headroom}} = 5632\text{ MB} - (4198\text{ MB} + 614\text{ MB}) = 820\text{ MB}$$

If the system attempts to load a dense local embedding model such as bge-m3 onto the GPU, the allocation ceiling is breached. Although bge-m3 requires a nominal 1.06GB of VRAM to initialize at FP16, its memory footprint climbs dynamically to ~5.7GB during batch processing with default configurations, causing immediate system failure. A larger quantized embedding model like qwen3-embedding:8b similarly demands approximately 5GB of VRAM, which is wholly incompatible with this concurrent setup.

To resolve this conflict, the architecture must offload the embedding model entirely to the CPU. The optimal candidate for this offloaded role is nomic-embed-text-v1.5. This model has a disk footprint of only 274MB and is designed to execute on consumer laptop CPUs with 0MB of VRAM usage. It utilizes Matryoshka Representation Learning, allowing the vector dimensions to be truncated (for example, from 768 down to 512 or 256 dimensions) to dramatically reduce downstream RAM usage and vector search latency without significantly degrading retrieval accuracy.

### Coexistence Matrix

| Component | Model / Engine | Compute Device | VRAM Footprint |
|-----------|----------------|----------------|----------------|
| Local LLM | Mistral-7B-Instruct (Q4_K_M) | GPU (via Ollama) | 4198 MB |
| STT Engine | Whisper-Base (FP16) | GPU (via CUDA) | 614 MB |
| VAD Engine | Silero VAD | CPU (ONNX) | 0 MB |
| Embeddings| Nomic-Embed-Text-v1.5 | CPU | 0 MB |
| Agent | Letta Server (Postgres) | CPU | 0 MB |
| **Total** | **Hybrid Pipeline** | **Mixed** | **4812 MB (820 MB Headroom)** |

To prevent the 12 logical CPU threads of the AMD Ryzen 5 5600H from thrashing, CPU thread allocation must be explicitly bound. Thread limits must be hard-coded in config.py and environment configurations:
$$T_{\text{allocated}} = T_{\text{Ollama}} (4) + T_{\text{STT}} (2) + T_{\text{VAD/Embedder}} (2) + T_{\text{OS/API}} (4) = 12\text{ Threads}$$

## Engineering Design and Concurrency Architecture

A real-time voice conversational agent cannot rely solely on an asynchronous single-threaded event loop like asyncio. While asyncio scales well for I/O-bound operations, it exhibits high tail-latency spikes when mixed with CPU-bound processing.

In a local voice pipeline, operations like raw audio signal downsampling, Silero Voice Activity Detection (VAD) calculations, PyTorch tensor manipulation for Whisper STT, and audio driver playback writing are CPU-bound. The optimal design is a hybrid concurrency model: a multi-threaded, queue-based pipeline where dedicated, OS-level threads run synchronous processing blocks, coordinated by thread-safe first-in, first-out (FIFO) queues.

### Latency-Reduction Mathematics
The mathematical justification for this multi-threaded streaming model is the minimization of the total Time-To-First-Audio ($TTFA$) response.
$$TTFA_{\text{streaming}} = L_{\text{STT\_final}} + L_{\text{LLM\_TTFT}} + L_{\text{sentence\_agg}} + L_{\text{TTS\_TTFB}} + L_{\text{transport}}$$
This reduces $TTFA_{\text{streaming}}$ to an optimal range of 250–480ms, matching human conversational pacing.

## Letta Stateful Memory and REST Integration

Letta serves as the persistent agentic state manager. The architecture must transition away from the legacy MemGPT agent loop to the modern `letta_v1_agent` loop. The Letta V1 architecture deprecates the `send_message` tool and continuous heartbeats, executing a cleaner loop where the LLM natively streams text or issues tool calls in a single step, significantly lowering local inference overhead.

## failure Mode Graceful Degradation

To prevent the mechatronic brain from freezing when models exhaust local memory or Letta's PostgreSQL database encounters a thread lock, the voice orchestrator implements a cascading fallback mechanism:
1. **VRAM Monitor Watchdog**: A lightweight background thread monitors VRAM usage. If allocation exceeds 5.6GB, it immediately signals Ollama to flush its system cache.
2. **Audio State Degrade**: If the Letta memory update loop fails to respond within 800ms, the pipeline triggers a fallback interrupt, loads a stateless memory state from disk, and plays a pre-synthesized offline alert.
