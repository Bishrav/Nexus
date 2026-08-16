"""Run a small end-to-end NEXUS analysis against a checked-in Python fixture."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from nexus.domain import SourceFileContract
from nexus.index import RepositoryIndex
from nexus.parser import ParserInputContract
from nexus.python_parser import PythonParserAdapter


def main() -> None:
    fixture_path = Path("tests/fixtures/python_parser.py")
    content = fixture_path.read_text(encoding="utf-8")
    repository_id = "example:local"
    source_file = SourceFileContract(
        repository_id=repository_id,
        path=fixture_path.as_posix(),
        language="python",
        content_hash=hashlib.sha256(content.encode("utf-8")).hexdigest(),
        size_bytes=len(content.encode("utf-8")),
    )

    parser_output = PythonParserAdapter().parse(ParserInputContract(source_file, content))
    index = RepositoryIndex(repository_id, revision="fixture")
    index.add_parser_output(parser_output)

    print(
        json.dumps(
            {
                "parser_status": parser_output.status.value,
                "summary": index.summary(),
                "symbols": [symbol.to_dict() for symbol in index.symbols],
                "relationships": [
                    relationship.to_dict() for relationship in index.relationships
                ],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
