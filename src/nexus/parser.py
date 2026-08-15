"""Parser input/output contracts and adapter protocol."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Protocol, runtime_checkable

from nexus.domain import (
    SCHEMA_VERSION,
    ContractValidationError,
    RelationshipContract,
    SourceFileContract,
    SymbolContract,
    _require_text,
)
from nexus.ingestion import DiagnosticContract


class ParseStatus(StrEnum):
    COMPLETE = "complete"
    PARTIAL = "partial"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class ParserInputContract:
    source_file: SourceFileContract
    content: str

    def __post_init__(self) -> None:
        if not isinstance(self.source_file, SourceFileContract):
            raise ContractValidationError("source_file must be a SourceFileContract")
        _require_text(self.content, "content")


@dataclass(frozen=True, slots=True)
class ParserOutputContract:
    source_file: SourceFileContract
    status: ParseStatus
    symbols: tuple[SymbolContract, ...] = ()
    relationships: tuple[RelationshipContract, ...] = ()
    diagnostics: tuple[DiagnosticContract, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.source_file, SourceFileContract):
            raise ContractValidationError("source_file must be a SourceFileContract")
        if not isinstance(self.status, ParseStatus):
            raise ContractValidationError("status must be a ParseStatus")
        if not isinstance(self.symbols, tuple) or not all(
            isinstance(symbol, SymbolContract) for symbol in self.symbols
        ):
            raise ContractValidationError("symbols must be a tuple of SymbolContract values")
        if not isinstance(self.relationships, tuple) or not all(
            isinstance(relationship, RelationshipContract) for relationship in self.relationships
        ):
            raise ContractValidationError(
                "relationships must be a tuple of RelationshipContract values"
            )
        if not isinstance(self.diagnostics, tuple) or not all(
            isinstance(diagnostic, DiagnosticContract) for diagnostic in self.diagnostics
        ):
            raise ContractValidationError("diagnostics must be a tuple of DiagnosticContract values")
        if any(
            symbol.repository_id != self.source_file.repository_id
            or symbol.file_path != self.source_file.path
            for symbol in self.symbols
        ):
            raise ContractValidationError("all symbols must belong to the parsed source file")
        if any(
            relationship.repository_id != self.source_file.repository_id
            for relationship in self.relationships
        ):
            raise ContractValidationError("all relationships must belong to the source repository")
        if self.status == ParseStatus.FAILED and (self.symbols or self.relationships):
            raise ContractValidationError("failed parsing cannot contain normalized records")
        if self.status in (ParseStatus.PARTIAL, ParseStatus.FAILED) and not self.diagnostics:
            raise ContractValidationError("incomplete parsing requires diagnostics")

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "type": "parser_output",
            "source_file": self.source_file.to_dict(),
            "status": self.status.value,
            "symbols": [
                symbol.to_dict() for symbol in sorted(self.symbols, key=lambda item: item.symbol_id)
            ],
            "relationships": [
                relationship.to_dict()
                for relationship in sorted(
                    self.relationships,
                    key=lambda item: (item.source_id, item.target_id, item.kind.value),
                )
            ],
            "diagnostics": [
                diagnostic.to_dict()
                for diagnostic in sorted(
                    self.diagnostics,
                    key=lambda item: (item.path or "", item.code, item.message),
                )
            ],
        }


@runtime_checkable
class ParserAdapter(Protocol):
    """Interface implemented by a language-specific parser worker."""

    language: str

    def parse(self, parser_input: ParserInputContract) -> ParserOutputContract:
        """Parse one source file into normalized symbols and relationships."""
