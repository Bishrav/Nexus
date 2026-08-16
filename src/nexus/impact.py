"""Deterministic impact and evidence queries over one analysis result."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from nexus.analyze import AnalysisResult


@dataclass(frozen=True, slots=True)
class ImpactResult:
    """Callers and source evidence for one symbol name."""

    symbol: dict[str, Any]
    callers: tuple[dict[str, Any], ...]

    def to_dict(self) -> dict[str, Any]:
        return {"symbol": self.symbol, "callers": list(self.callers)}


def find_symbol_impact(result: AnalysisResult, name: str) -> ImpactResult | None:
    """Find exact-name callers of a symbol in one analyzed file."""

    matches = [symbol for symbol in result.symbols if symbol["name"] == name]
    if not matches:
        return None
    symbol = matches[0]
    callers_by_id = {item["symbol_id"]: item for item in result.symbols}
    callers: list[dict[str, Any]] = []
    for relationship in result.relationships:
        if relationship["kind"] != "calls" or relationship["target_id"] != symbol["symbol_id"]:
            continue
        callers.append(
            {
                "relationship": relationship,
                "caller": callers_by_id.get(relationship["source_id"]),
            }
        )
    return ImpactResult(symbol=symbol, callers=tuple(callers))
