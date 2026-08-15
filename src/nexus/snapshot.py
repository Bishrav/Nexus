"""Versioned JSON snapshots for repository indexes."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from nexus.domain import (
    SCHEMA_VERSION,
    RelationshipContract,
    RelationshipKind,
    SourceFileContract,
    SymbolContract,
    SymbolKind,
)
from nexus.index import IndexValidationError, RepositoryIndex
from nexus.ingestion import DiagnosticContract, DiagnosticSeverity


SNAPSHOT_VERSION = "nexus.snapshot.v1"


class SnapshotError(ValueError):
    """Raised when a snapshot cannot be serialized or restored."""


def snapshot_dict(index: RepositoryIndex) -> dict[str, Any]:
    return {
        "snapshot_version": SNAPSHOT_VERSION,
        "schema_version": SCHEMA_VERSION,
        "repository_id": index.repository_id,
        "revision": index.revision,
        "files": [source_file.to_dict() for source_file in index.files],
        "symbols": [symbol.to_dict() for symbol in index.symbols],
        "relationships": [relationship.to_dict() for relationship in index.relationships],
        "diagnostics": [diagnostic.to_dict() for diagnostic in index.diagnostics],
    }


def snapshot_text(index: RepositoryIndex) -> str:
    return json.dumps(snapshot_dict(index), indent=2, sort_keys=True) + "\n"


def restore_snapshot(payload: str) -> RepositoryIndex:
    try:
        data = json.loads(payload)
    except json.JSONDecodeError as error:
        raise SnapshotError(f"invalid snapshot JSON: {error.msg}") from error
    if not isinstance(data, dict):
        raise SnapshotError("snapshot root must be an object")
    if data.get("snapshot_version") != SNAPSHOT_VERSION:
        raise SnapshotError("unsupported snapshot version")
    if data.get("schema_version") != SCHEMA_VERSION:
        raise SnapshotError("unsupported domain schema version")
    try:
        index = RepositoryIndex(data["repository_id"], data["revision"])
        for item in data["files"]:
            index.add_source_file(
                SourceFileContract(
                    item["repository_id"],
                    item["path"],
                    item["language"],
                    item["content_hash"],
                    item["size_bytes"],
                )
            )
        for item in data["symbols"]:
            index.add_symbol(
                SymbolContract(
                    item["symbol_id"],
                    item["repository_id"],
                    item["name"],
                    SymbolKind(item["kind"]),
                    item["file_path"],
                    item["start_line"],
                    item["end_line"],
                )
            )
        for item in data["relationships"]:
            index.add_relationship(
                RelationshipContract(
                    item["repository_id"],
                    item["source_id"],
                    item["target_id"],
                    RelationshipKind(item["kind"]),
                )
            )
        for item in data["diagnostics"]:
            index.add_diagnostic(
                DiagnosticContract(
                    DiagnosticSeverity(item["severity"]),
                    item["code"],
                    item["message"],
                    item.get("path"),
                )
            )
    except (KeyError, TypeError, ValueError, IndexValidationError) as error:
        raise SnapshotError(f"invalid snapshot data: {error}") from error
    return index


def save_snapshot(index: RepositoryIndex, path: str | Path) -> None:
    try:
        Path(path).write_text(snapshot_text(index), encoding="utf-8", newline="\n")
    except OSError as error:
        raise SnapshotError(f"could not write snapshot {path}: {error}") from error


def load_snapshot(path: str | Path) -> RepositoryIndex:
    try:
        payload = Path(path).read_text(encoding="utf-8")
    except OSError as error:
        raise SnapshotError(f"could not read snapshot {path}: {error}") from error
    return restore_snapshot(payload)
