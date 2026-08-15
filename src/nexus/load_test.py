"""Sequential parser load-test harness for raw local observations."""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass

from nexus.domain import SourceFileContract
from nexus.parser import ParseStatus, ParserInputContract
from nexus.python_parser import PythonParserAdapter


@dataclass(frozen=True, slots=True)
class LoadTestResult:
    fixture: str
    operations: int
    successes: int
    failures: int
    durations_ms: tuple[float, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "fixture": self.fixture,
            "operations": self.operations,
            "successes": self.successes,
            "failures": self.failures,
            "durations_ms": list(self.durations_ms),
        }


def run_sequential_load_test(content: str, fixture: str, operations: int = 10) -> LoadTestResult:
    """Run repeated parser operations and return raw observations."""

    if operations < 1:
        raise ValueError("operations must be positive")
    encoded = content.encode("utf-8")
    source_file = SourceFileContract(
        "load-test:local",
        fixture.replace("\\", "/"),
        "python",
        hashlib.sha256(encoded).hexdigest(),
        len(encoded),
    )
    parser = PythonParserAdapter()
    parser_input = ParserInputContract(source_file, content)
    durations: list[float] = []
    successes = 0
    for _ in range(operations):
        started = time.perf_counter()
        result = parser.parse(parser_input)
        durations.append((time.perf_counter() - started) * 1000)
        if result.status == ParseStatus.COMPLETE:
            successes += 1
    return LoadTestResult(fixture, operations, successes, operations - successes, tuple(durations))
