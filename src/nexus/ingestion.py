"""Contracts for repository ingestion requests, results, and diagnostics."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from nexus.domain import (
    SCHEMA_VERSION,
    ContractValidationError,
    SourceFileContract,
    _require_identifier,
    _require_relative_path,
    _require_text,
)


class DiagnosticSeverity(StrEnum):
    WARNING = "warning"
    ERROR = "error"


class IngestionStatus(StrEnum):
    COMPLETE = "complete"
    PARTIAL = "partial"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class IngestionRequestContract:
    request_id: str
    repository_id: str
    root_path: str
    revision: str
    languages: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _require_identifier(self.request_id, "request_id")
        _require_identifier(self.repository_id, "repository_id")
        _require_text(self.root_path, "root_path")
        _require_identifier(self.revision, "revision")
        if not isinstance(self.languages, tuple):
            raise ContractValidationError("languages must be a tuple")
        for language in self.languages:
            _require_identifier(language, "language")

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "type": "ingestion_request",
            "request_id": self.request_id,
            "repository_id": self.repository_id,
            "root_path": self.root_path,
            "revision": self.revision,
            "languages": list(self.languages),
        }


@dataclass(frozen=True, slots=True)
class DiagnosticContract:
    severity: DiagnosticSeverity
    code: str
    message: str
    path: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.severity, DiagnosticSeverity):
            raise ContractValidationError("severity must be a DiagnosticSeverity")
        _require_identifier(self.code, "code")
        _require_text(self.message, "message")
        if self.path is not None:
            _require_relative_path(self.path, "path")

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "type": "diagnostic",
            "severity": self.severity.value,
            "code": self.code,
            "message": self.message,
            "path": self.path,
        }


@dataclass(frozen=True, slots=True)
class IngestionResultContract:
    request_id: str
    repository_id: str
    revision: str
    status: IngestionStatus
    files: tuple[SourceFileContract, ...] = ()
    diagnostics: tuple[DiagnosticContract, ...] = ()

    def __post_init__(self) -> None:
        _require_identifier(self.request_id, "request_id")
        _require_identifier(self.repository_id, "repository_id")
        _require_identifier(self.revision, "revision")
        if not isinstance(self.status, IngestionStatus):
            raise ContractValidationError("status must be an IngestionStatus")
        if not isinstance(self.files, tuple) or not all(
            isinstance(file, SourceFileContract) for file in self.files
        ):
            raise ContractValidationError("files must be a tuple of SourceFileContract values")
        if not isinstance(self.diagnostics, tuple) or not all(
            isinstance(diagnostic, DiagnosticContract) for diagnostic in self.diagnostics
        ):
            raise ContractValidationError("diagnostics must be a tuple of DiagnosticContract values")
        if any(file.repository_id != self.repository_id for file in self.files):
            raise ContractValidationError("all files must belong to the result repository")
        if self.status == IngestionStatus.FAILED and self.files:
            raise ContractValidationError("failed ingestion cannot contain indexed files")
        if self.status in (IngestionStatus.PARTIAL, IngestionStatus.FAILED) and not self.diagnostics:
            raise ContractValidationError("incomplete ingestion requires diagnostics")

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "type": "ingestion_result",
            "request_id": self.request_id,
            "repository_id": self.repository_id,
            "revision": self.revision,
            "status": self.status.value,
            "files": [file.to_dict() for file in sorted(self.files, key=lambda item: item.path)],
            "diagnostics": [
                diagnostic.to_dict()
                for diagnostic in sorted(
                    self.diagnostics,
                    key=lambda item: (item.path or "", item.code, item.message),
                )
            ],
        }
