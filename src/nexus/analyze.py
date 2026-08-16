"""Local, deterministic Python file analysis workflow."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from nexus.domain import SourceFileContract
from nexus.index import RepositoryIndex
from nexus.parser import ParseStatus, ParserInputContract
from nexus.python_parser import PythonParserAdapter


@dataclass(frozen=True, slots=True)
class AnalysisResult:
    """Normalized output for one local source-file analysis."""

    source_file: SourceFileContract
    status: ParseStatus
    summary: dict[str, int | str]
    symbols: tuple[dict[str, Any], ...]
    relationships: tuple[dict[str, Any], ...]
    diagnostics: tuple[dict[str, Any], ...]

    @property
    def succeeded(self) -> bool:
        return self.status == ParseStatus.COMPLETE

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_file": self.source_file.to_dict(),
            "status": self.status.value,
            "summary": self.summary,
            "symbols": list(self.symbols),
            "relationships": list(self.relationships),
            "diagnostics": list(self.diagnostics),
        }


def analyze_python_file(path: Path, repository_id: str = "local:analysis") -> AnalysisResult:
    """Parse and index one Python file using the repository's core contracts."""

    content = path.read_text(encoding="utf-8")
    relative_path = path.resolve().relative_to(Path.cwd().resolve()).as_posix()
    encoded_content = content.encode("utf-8")
    source_file = SourceFileContract(
        repository_id=repository_id,
        path=relative_path,
        language="python",
        content_hash=hashlib.sha256(encoded_content).hexdigest(),
        size_bytes=len(encoded_content),
    )
    parser_output = PythonParserAdapter().parse(ParserInputContract(source_file, content))
    index = RepositoryIndex(repository_id, revision="working-tree")
    index.add_parser_output(parser_output)
    return AnalysisResult(
        source_file=source_file,
        status=parser_output.status,
        summary=index.summary(),
        symbols=tuple(symbol.to_dict() for symbol in index.symbols),
        relationships=tuple(relationship.to_dict() for relationship in index.relationships),
        diagnostics=tuple(diagnostic.to_dict() for diagnostic in index.diagnostics),
    )
