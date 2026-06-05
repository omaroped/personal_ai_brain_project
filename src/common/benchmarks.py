# MODULE: Timing helpers for benchmarks and latency tracking across project subsystems.
"""Benchmark helpers for measuring latency of local operations."""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Any, Callable


@dataclass
class BenchmarkResult:
    """Represents the latency and output of one measured function call.

    Parameters:
        name: Human-readable benchmark name.
        duration_ms: Elapsed time in milliseconds.
        value: Returned value from the measured function call.
    """

    name: str
    duration_ms: float
    value: Any


def measure_call(name: str, func: Callable[..., Any], *args: Any, **kwargs: Any) -> BenchmarkResult:
    """Measure the execution time of a function call.

    Parameters:
        name: Human-readable benchmark name.
        func: Callable to execute.
        *args: Positional arguments for the callable.
        **kwargs: Keyword arguments for the callable.

    Returns:
        BenchmarkResult: Elapsed time and return value.
    """
    start = perf_counter()
    value = func(*args, **kwargs)
    duration_ms = (perf_counter() - start) * 1000
    return BenchmarkResult(name=name, duration_ms=duration_ms, value=value)


class BenchmarkRecorder:
    """Accumulates benchmark results for later reporting."""

    def __init__(self) -> None:
        """Initialize an empty benchmark recorder."""
        self.results: list[BenchmarkResult] = []

    def record(self, result: BenchmarkResult) -> None:
        """Add a benchmark result to the recorder.

        Parameters:
            result: Measured benchmark result to store.
        """
        self.results.append(result)

    def summary(self) -> dict[str, float]:
        """Return a simple name-to-duration summary.

        Returns:
            dict[str, float]: Mapping of benchmark name to elapsed milliseconds.
        """
        return {result.name: result.duration_ms for result in self.results}
