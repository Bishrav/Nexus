"""Deterministic in-memory storage and query operations for repository facts."""

from __future__ import annotations

from nexus.domain import (
    ContractValidationError,
    RelationshipContract,
    RelationshipKind,
    SourceFileContract,
    SymbolContract,
    _require_identifier,
)
from nexus.ingestion import DiagnosticContract
from nexus.parser import ParserOutputContract, ParseStatus


class IndexValidationError(ContractValidationError):
    """Raised when an index receives inconsistent repository facts."""


class RepositoryIndex:
    """Store and query one repository revision in memory."""

    def __init__(self, repository_id: str, revision: str) -> None:
        _require_identifier(repository_id, "repository_id")
        _require_identifier(revision, "revision")
        self.repository_id = repository_id
        self.revision = revision
        self._files: dict[str, SourceFileContract] = {}
        self._symbols: dict[str, SymbolContract] = {}
        self._relationships: dict[tuple[str, str, RelationshipKind], RelationshipContract] = {}
        self._diagnostics: list[DiagnosticContract] = []

    @property
    def files(self) -> tuple[SourceFileContract, ...]:
        return tuple(self._files[path] for path in sorted(self._files))

    @property
    def symbols(self) -> tuple[SymbolContract, ...]:
        return tuple(self._symbols[symbol_id] for symbol_id in sorted(self._symbols))

    @property
    def relationships(self) -> tuple[RelationshipContract, ...]:
        return tuple(
            self._relationships[key]
            for key in sorted(self._relationships, key=lambda item: (item[0], item[1], item[2].value))
        )

    @property
    def diagnostics(self) -> tuple[DiagnosticContract, ...]:
        return tuple(self._diagnostics)

    def add_source_file(self, source_file: SourceFileContract) -> None:
        self._require_repository(source_file.repository_id)
        existing = self._files.get(source_file.path)
        if existing is not None and existing != source_file:
            raise IndexValidationError(f"source file {source_file.path!r} changed within one index revision")
        self._files[source_file.path] = source_file

    def add_parser_output(self, output: ParserOutputContract) -> None:
        self.add_source_file(output.source_file)
        if output.status == ParseStatus.FAILED:
            self._diagnostics.extend(output.diagnostics)
            return
        for symbol in output.symbols:
            self._add_symbol(symbol)
        for relationship in output.relationships:
            self._add_relationship(relationship)
        self._diagnostics.extend(output.diagnostics)

    def remove_file(self, path: str) -> None:
        """Remove one file and all facts whose identity is scoped to it."""

        self._files.pop(path, None)
        symbol_prefix = f"symbol:{self.repository_id}:{path}:"
        file_id = f"file:{self.repository_id}:{path}"
        for symbol_id, symbol in tuple(self._symbols.items()):
            if symbol.file_path == path or symbol_id.startswith(symbol_prefix):
                del self._symbols[symbol_id]
        for key, relationship in tuple(self._relationships.items()):
            if (
                relationship.source_id == file_id
                or relationship.source_id.startswith(symbol_prefix)
                or relationship.target_id.startswith(symbol_prefix)
            ):
                del self._relationships[key]
        self._diagnostics = [diagnostic for diagnostic in self._diagnostics if diagnostic.path != path]

    def get_symbol(self, symbol_id: str) -> SymbolContract | None:
        return self._symbols.get(symbol_id)

    def find_symbols(self, name: str) -> tuple[SymbolContract, ...]:
        return tuple(symbol for symbol in self.symbols if symbol.name == name)

    def relationships_from(
        self, source_id: str, kind: RelationshipKind | None = None
    ) -> tuple[RelationshipContract, ...]:
        return tuple(
            relationship
            for relationship in self.relationships
            if relationship.source_id == source_id and (kind is None or relationship.kind == kind)
        )

    def relationships_to(
        self, target_id: str, kind: RelationshipKind | None = None
    ) -> tuple[RelationshipContract, ...]:
        return tuple(
            relationship
            for relationship in self.relationships
            if relationship.target_id == target_id and (kind is None or relationship.kind == kind)
        )

    def summary(self) -> dict[str, int | str]:
        return {
            "repository_id": self.repository_id,
            "revision": self.revision,
            "file_count": len(self._files),
            "symbol_count": len(self._symbols),
            "relationship_count": len(self._relationships),
            "diagnostic_count": len(self._diagnostics),
        }

    def _add_symbol(self, symbol: SymbolContract) -> None:
        self._require_repository(symbol.repository_id)
        existing = self._symbols.get(symbol.symbol_id)
        if existing is not None and existing != symbol:
            raise IndexValidationError(f"symbol {symbol.symbol_id!r} has conflicting definitions")
        self._symbols[symbol.symbol_id] = symbol

    def _add_relationship(self, relationship: RelationshipContract) -> None:
        self._require_repository(relationship.repository_id)
        key = (relationship.source_id, relationship.target_id, relationship.kind)
        self._relationships[key] = relationship

    def _require_repository(self, repository_id: str) -> None:
        if repository_id != self.repository_id:
            raise IndexValidationError(
                f"expected repository {self.repository_id!r}, received {repository_id!r}"
            )
