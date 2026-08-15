"""Golden-fixture evaluation for deterministic parser behavior."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from nexus.domain import SourceFileContract
from nexus.parser import ParseStatus, ParserInputContract
from nexus.python_parser import PythonParserAdapter


@dataclass(frozen=True, slots=True)
class EvaluationResult:
    fixture: str
    expected: str
    passed: bool
    mismatches: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "fixture": self.fixture,
            "expected": self.expected,
            "passed": self.passed,
            "mismatches": list(self.mismatches),
        }


def evaluate_python_fixture(fixture_path: str | Path, expected_path: str | Path) -> EvaluationResult:
    fixture = Path(fixture_path)
    expected = Path(expected_path)
    fixture_name = fixture.as_posix()
    expected_name = expected.as_posix()
    content = fixture.read_text(encoding="utf-8")
    golden = json.loads(expected.read_text(encoding="utf-8"))
    source_file = SourceFileContract(
        "evaluation:local",
        fixture_name,
        "python",
        hashlib.sha256(content.encode("utf-8")).hexdigest(),
        len(content.encode("utf-8")),
    )
    output = PythonParserAdapter().parse(ParserInputContract(source_file, content))
    actual = {
        "status": output.status.value,
        "symbols": [symbol.to_dict() for symbol in output.symbols],
        "relationships": [relationship.to_dict() for relationship in output.relationships],
    }
    mismatches = tuple(
        key for key in ("status", "symbols", "relationships") if actual.get(key) != golden.get(key)
    )
    if output.status != ParseStatus.COMPLETE and "diagnostics" not in golden:
        mismatches = (*mismatches, "diagnostics")
    return EvaluationResult(fixture_name, expected_name, not mismatches, mismatches)
