"""Small, dependency-free runtime metrics primitives."""

from __future__ import annotations

from dataclasses import dataclass
from threading import Lock


@dataclass
class _OperationTotals:
    count: int = 0
    failures: int = 0
    total_duration_ms: float = 0.0


class MetricsCollector:
    """Collect runtime operation counts and durations without inventing values."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._operations: dict[str, _OperationTotals] = {}

    def record(self, operation: str, outcome: str, duration_ms: float) -> None:
        if not operation.strip():
            raise ValueError("operation must be non-empty")
        if outcome not in {"success", "failure"}:
            raise ValueError("outcome must be 'success' or 'failure'")
        if duration_ms < 0:
            raise ValueError("duration_ms must be non-negative")
        with self._lock:
            totals = self._operations.setdefault(operation, _OperationTotals())
            totals.count += 1
            totals.failures += int(outcome == "failure")
            totals.total_duration_ms += duration_ms

    def snapshot(self) -> dict[str, dict[str, int | float]]:
        with self._lock:
            return {
                operation: {
                    "count": totals.count,
                    "failures": totals.failures,
                    "total_duration_ms": totals.total_duration_ms,
                }
                for operation, totals in sorted(self._operations.items())
            }
