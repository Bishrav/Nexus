"""Git revision and changed-file discovery for incremental indexing."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Callable, Sequence

from nexus.domain import ContractValidationError, _require_identifier


class GitSourceError(ContractValidationError):
    """Raised when Git metadata cannot be read or parsed."""


class GitChangeKind(StrEnum):
    ADDED = "added"
    MODIFIED = "modified"
    DELETED = "deleted"
    RENAMED = "renamed"


@dataclass(frozen=True, slots=True)
class GitFileChange:
    path: str
    kind: GitChangeKind
    previous_path: str | None = None

    def to_dict(self) -> dict[str, str | None]:
        return {
            "path": self.path,
            "kind": self.kind.value,
            "previous_path": self.previous_path,
        }


CommandRunner = Callable[[Sequence[str]], str]


class GitRevisionReader:
    """Read revisions and file changes from one local Git repository."""

    def __init__(self, root: str | Path, runner: CommandRunner | None = None) -> None:
        self.root = Path(root)
        self._runner = runner or self._run_git

    def current_revision(self) -> str:
        revision = self._runner(("rev-parse", "HEAD")).strip()
        _require_identifier(revision, "revision")
        return revision

    def changed_files(self, previous_revision: str, current_revision: str = "HEAD") -> tuple[GitFileChange, ...]:
        _require_identifier(previous_revision, "previous_revision")
        _require_identifier(current_revision, "current_revision")
        output = self._runner(
            ("diff", "--name-status", "-M", previous_revision, current_revision, "--")
        )
        changes = [self._parse_change(line) for line in output.splitlines() if line.strip()]
        return tuple(sorted(changes, key=lambda change: change.path))

    @staticmethod
    def _parse_change(line: str) -> GitFileChange:
        fields = line.split("\t")
        if len(fields) < 2:
            raise GitSourceError(f"invalid Git name-status line: {line!r}")
        status = fields[0]
        code = status[:1]
        if code == "A":
            return GitFileChange(fields[1], GitChangeKind.ADDED)
        if code == "M":
            return GitFileChange(fields[1], GitChangeKind.MODIFIED)
        if code == "D":
            return GitFileChange(fields[1], GitChangeKind.DELETED)
        if code == "R" and len(fields) >= 3:
            return GitFileChange(fields[2], GitChangeKind.RENAMED, fields[1])
        raise GitSourceError(f"unsupported Git change status: {line!r}")

    def _run_git(self, args: Sequence[str]) -> str:
        try:
            completed = subprocess.run(
                ("git", *args),
                cwd=self.root,
                check=True,
                capture_output=True,
                text=True,
            )
        except (OSError, subprocess.CalledProcessError) as error:
            raise GitSourceError(f"Git command failed in {self.root}: {error}") from error
        return completed.stdout
