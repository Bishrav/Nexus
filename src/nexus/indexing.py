"""Deterministic incremental indexing change planning."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Iterable, Mapping

from nexus.domain import ContractValidationError, SourceFileContract, _require_identifier
from nexus.index import IndexValidationError, RepositoryIndex
from nexus.parser import ParserOutputContract


class IndexingValidationError(ContractValidationError):
    """Raised when revisions cannot be compared safely."""


class FileChangeKind(StrEnum):
    ADDED = "added"
    CHANGED = "changed"
    REMOVED = "removed"
    UNCHANGED = "unchanged"


@dataclass(frozen=True, slots=True)
class FileChange:
    path: str
    kind: FileChangeKind
    previous_hash: str | None
    current_hash: str | None

    def to_dict(self) -> dict[str, str | None]:
        return {
            "path": self.path,
            "kind": self.kind.value,
            "previous_hash": self.previous_hash,
            "current_hash": self.current_hash,
        }


@dataclass(frozen=True, slots=True)
class IncrementalPlan:
    repository_id: str
    previous_revision: str
    current_revision: str
    changes: tuple[FileChange, ...]

    @property
    def reparsed_paths(self) -> tuple[str, ...]:
        return tuple(
            change.path
            for change in self.changes
            if change.kind in (FileChangeKind.ADDED, FileChangeKind.CHANGED)
        )

    @property
    def removed_paths(self) -> tuple[str, ...]:
        return tuple(change.path for change in self.changes if change.kind == FileChangeKind.REMOVED)

    def to_dict(self) -> dict[str, object]:
        return {
            "repository_id": self.repository_id,
            "previous_revision": self.previous_revision,
            "current_revision": self.current_revision,
            "changes": [change.to_dict() for change in self.changes],
            "reparsed_paths": list(self.reparsed_paths),
            "removed_paths": list(self.removed_paths),
        }


def plan_incremental_update(
    repository_id: str,
    previous_revision: str,
    current_revision: str,
    previous_files: Iterable[SourceFileContract],
    current_files: Iterable[SourceFileContract],
) -> IncrementalPlan:
    """Compare two file manifests and return a deterministic update plan."""

    _require_identifier(repository_id, "repository_id")
    _require_identifier(previous_revision, "previous_revision")
    _require_identifier(current_revision, "current_revision")
    previous = _manifest(repository_id, previous_files)
    current = _manifest(repository_id, current_files)
    changes: list[FileChange] = []
    for path in sorted(set(previous) | set(current)):
        old = previous.get(path)
        new = current.get(path)
        if old is None:
            changes.append(FileChange(path, FileChangeKind.ADDED, None, new.content_hash))
        elif new is None:
            changes.append(FileChange(path, FileChangeKind.REMOVED, old.content_hash, None))
        elif old == new:
            changes.append(FileChange(path, FileChangeKind.UNCHANGED, old.content_hash, new.content_hash))
        else:
            changes.append(FileChange(path, FileChangeKind.CHANGED, old.content_hash, new.content_hash))
    return IncrementalPlan(repository_id, previous_revision, current_revision, tuple(changes))


def apply_incremental_plan(
    index: RepositoryIndex,
    plan: IncrementalPlan,
    outputs: Mapping[str, ParserOutputContract],
) -> None:
    """Apply a validated plan and advance the index revision atomically by intent."""

    if index.repository_id != plan.repository_id:
        raise IndexingValidationError("plan and index repository IDs do not match")
    if index.revision != plan.previous_revision:
        raise IndexingValidationError(
            f"plan starts at {plan.previous_revision!r}, but index is at {index.revision!r}"
        )
    expected_paths = set(plan.reparsed_paths)
    if set(outputs) != expected_paths:
        raise IndexingValidationError("parser outputs must exactly match added and changed paths")
    for path in plan.removed_paths:
        index.remove_file(path)
    for path in plan.reparsed_paths:
        output = outputs[path]
        if output.source_file.path != path:
            raise IndexingValidationError(f"parser output path mismatch for {path!r}")
        index.remove_file(path)
        try:
            index.add_parser_output(output)
        except IndexValidationError:
            raise
    index.revision = plan.current_revision


def _manifest(
    repository_id: str, files: Iterable[SourceFileContract]
) -> dict[str, SourceFileContract]:
    manifest: dict[str, SourceFileContract] = {}
    for source_file in files:
        if source_file.repository_id != repository_id:
            raise IndexingValidationError(
                f"expected repository {repository_id!r}, received {source_file.repository_id!r}"
            )
        if source_file.path in manifest:
            raise IndexingValidationError(f"duplicate source file path {source_file.path!r}")
        manifest[source_file.path] = source_file
    return manifest
