# MODULE: Benchmark demonstration script using shared timing utilities.
"""Example of how to measure and report operation latency."""

from __future__ import annotations

import time
import random
from pathlib import Path
import sys

# Ensure project root is in path
sys.path.append(str(Path(__file__).parent.parent))

from src.common.benchmarks import BenchmarkRecorder, measure_call

def fake_heavy_operation(duration: float):
    """Simulate a task with a specific duration."""
    time.sleep(duration)
    return "success"

def main():
    """Run a series of fake benchmarks and print the summary."""
    recorder = BenchmarkRecorder()
    
    print("Running benchmark stubs...")
    
    # 1. Measure individual calls
    recorder.record(measure_call("fast_op", fake_heavy_operation, 0.05))
    recorder.record(measure_call("slow_op", fake_heavy_operation, 0.25))
    
    # 2. Simulate random batch
    for i in range(3):
        latency = random.uniform(0.01, 0.1)
        recorder.record(measure_call(f"batch_task_{i}", fake_heavy_operation, latency))
        
    # 3. Print report
    summary = recorder.summary()
    print("\n=== Latency Report (ms) ===")
    for name, duration in summary.items():
        print(f"{name:<15}: {duration:>8.2f} ms")
    
    avg_latency = sum(summary.values()) / len(summary)
    print("-" * 27)
    print(f"{'AVERAGE':<15}: {avg_latency:>8.2f} ms\n")

if __name__ == "__main__":
    main()
