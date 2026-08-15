"""Reproducible, measurement-only parser benchmark harness."""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass

from nexus.domain import SourceFileContract
from nexus.parser import ParserInputContract
from nexus.python_parser import PythonParserAdapter


@dataclass(frozen=True, slots=True)
class BenchmarkResult:
    fixture: str
    iterations: int
    symbol_count: int
    relationship_count: int
    durations_ms: tuple[float, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "fixture": self.fixture,
            "iterations": self.iterations,
            "symbol_count": self.symbol_count,
            "relationship_count": self.relationship_count,
            "durations_ms": list(self.durations_ms),
        }


def run_python_parser_benchmark(
    content: str,
    fixture: str,
    iterations: int = 3,
) -> BenchmarkResult:
    """Run a fixed parser workload and return measured observations."""

    if iterations < 1:
        raise ValueError("iterations must be positive")
    content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
    source_file = SourceFileContract(
        "benchmark:local",
        fixture.replace("\\", "/"),
        "python",
        content_hash,
        len(content.encode("utf-8")),
    )
    parser = PythonParserAdapter()
    parser_input = ParserInputContract(source_file, content)
    durations: list[float] = []
    symbol_count = 0
    relationship_count = 0
    for _ in range(iterations):
        started = time.perf_counter()
        output = parser.parse(parser_input)
        durations.append((time.perf_counter() - started) * 1000)
        if output.status.value != "complete":
            raise ValueError("benchmark fixture did not parse successfully")
        symbol_count = len(output.symbols)
        relationship_count = len(output.relationships)
    return BenchmarkResult(fixture, iterations, symbol_count, relationship_count, tuple(durations))
