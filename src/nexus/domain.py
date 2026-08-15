"""Versioned, dependency-free domain contracts for repository intelligence."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any


SCHEMA_VERSION = "nexus.domain.v1"


class ContractValidationError(ValueError):
    """Raised when a domain contract contains invalid data."""


class SymbolKind(StrEnum):
    CLASS = "class"
    FUNCTION = "function"
    METHOD = "method"
    VARIABLE = "variable"


class RelationshipKind(StrEnum):
    IMPORTS = "imports"
    CALLS = "calls"
    DEFINES = "defines"
    DEPENDS_ON = "depends_on"


def _require_text(value: str, field: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ContractValidationError(f"{field} must be a non-empty string")


def _require_identifier(value: str, field: str) -> None:
    _require_text(value, field)
    if any(character.isspace() for character in value):
        raise ContractValidationError(f"{field} must not contain whitespace")


def _require_relative_path(value: str, field: str) -> None:
    _require_text(value, field)
    if value.startswith(("/", "\\")) or ".." in value.replace("\\", "/").split("/"):
        raise ContractValidationError(f"{field} must be a relative repository path")


def _require_positive(value: int, field: str) -> None:
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise ContractValidationError(f"{field} must be a positive integer")


@dataclass(frozen=True, slots=True)
class RepositoryContract:
    repository_id: str
    name: str
    revision: str

    def __post_init__(self) -> None:
        _require_identifier(self.repository_id, "repository_id")
        _require_text(self.name, "name")
        _require_identifier(self.revision, "revision")

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "type": "repository",
            "repository_id": self.repository_id,
            "name": self.name,
            "revision": self.revision,
        }


@dataclass(frozen=True, slots=True)
class SourceFileContract:
    repository_id: str
    path: str
    language: str
    content_hash: str
    size_bytes: int

    def __post_init__(self) -> None:
        _require_identifier(self.repository_id, "repository_id")
        _require_relative_path(self.path, "path")
        _require_identifier(self.language, "language")
        _require_identifier(self.content_hash, "content_hash")
        if len(self.content_hash) != 64 or any(
            character not in "0123456789abcdef" for character in self.content_hash.lower()
        ):
            raise ContractValidationError("content_hash must be a SHA-256 hexadecimal digest")
        if not isinstance(self.size_bytes, int) or isinstance(self.size_bytes, bool) or self.size_bytes < 0:
            raise ContractValidationError("size_bytes must be a non-negative integer")

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "type": "source_file",
            "repository_id": self.repository_id,
            "path": self.path,
            "language": self.language,
            "content_hash": self.content_hash,
            "size_bytes": self.size_bytes,
        }


@dataclass(frozen=True, slots=True)
class SymbolContract:
    symbol_id: str
    repository_id: str
    name: str
    kind: SymbolKind
    file_path: str
    start_line: int
    end_line: int

    def __post_init__(self) -> None:
        _require_identifier(self.symbol_id, "symbol_id")
        _require_identifier(self.repository_id, "repository_id")
        _require_text(self.name, "name")
        if not isinstance(self.kind, SymbolKind):
            raise ContractValidationError("kind must be a SymbolKind")
        _require_relative_path(self.file_path, "file_path")
        _require_positive(self.start_line, "start_line")
        _require_positive(self.end_line, "end_line")
        if self.end_line < self.start_line:
            raise ContractValidationError("end_line must not precede start_line")

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "type": "symbol",
            "symbol_id": self.symbol_id,
            "repository_id": self.repository_id,
            "name": self.name,
            "kind": self.kind.value,
            "file_path": self.file_path,
            "start_line": self.start_line,
            "end_line": self.end_line,
        }


@dataclass(frozen=True, slots=True)
class RelationshipContract:
    repository_id: str
    source_id: str
    target_id: str
    kind: RelationshipKind

    def __post_init__(self) -> None:
        _require_identifier(self.repository_id, "repository_id")
        _require_identifier(self.source_id, "source_id")
        _require_identifier(self.target_id, "target_id")
        if not isinstance(self.kind, RelationshipKind):
            raise ContractValidationError("kind must be a RelationshipKind")
        if self.source_id == self.target_id:
            raise ContractValidationError("source_id and target_id must identify different nodes")

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "type": "relationship",
            "repository_id": self.repository_id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "kind": self.kind.value,
        }
