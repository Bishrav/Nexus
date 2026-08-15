import unittest
from pathlib import Path

from nexus.domain import SourceFileContract, SymbolKind
from nexus.parser import ParseStatus, ParserInputContract
from nexus.python_parser import PythonParserAdapter


HASH = "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
FIXTURE = Path(__file__).parent / "fixtures" / "python_parser.py"
IMPORT_FIXTURE = Path(__file__).parent / "fixtures" / "python_imports.py"
CALL_FIXTURE = Path(__file__).parent / "fixtures" / "python_calls.py"


class PythonParserTests(unittest.TestCase):
    def setUp(self) -> None:
        self.source_file = SourceFileContract("repo:nexus", "tests/fixtures/python_parser.py", "python", HASH, 200)
        self.parser = PythonParserAdapter()

    def test_extracts_deterministic_symbols_and_locations(self) -> None:
        result = self.parser.parse(ParserInputContract(self.source_file, FIXTURE.read_text(encoding="utf-8")))
        self.assertEqual(result.status, ParseStatus.COMPLETE)
        self.assertEqual(
            [(symbol.name, symbol.kind, symbol.start_line, symbol.end_line) for symbol in result.symbols],
            [
                ("Greeter", SymbolKind.CLASS, 1, 5),
                ("message", SymbolKind.VARIABLE, 2, 2),
                ("greet", SymbolKind.METHOD, 4, 5),
                ("build_greeter", SymbolKind.FUNCTION, 8, 10),
                ("greeter", SymbolKind.VARIABLE, 9, 9),
            ],
        )

    def test_syntax_failure_returns_structured_diagnostic(self) -> None:
        result = self.parser.parse(ParserInputContract(self.source_file, "def broken(:\n    pass\n"))
        self.assertEqual(result.status, ParseStatus.FAILED)
        self.assertEqual(len(result.diagnostics), 1)
        self.assertEqual(result.diagnostics[0].code, "SYNTAX_ERROR")
        self.assertEqual(result.symbols, ())

    def test_extracts_import_relationships(self) -> None:
        source_file = SourceFileContract(
            "repo:nexus", "tests/fixtures/python_imports.py", "python", HASH, 80
        )
        result = self.parser.parse(
            ParserInputContract(source_file, IMPORT_FIXTURE.read_text(encoding="utf-8"))
        )
        self.assertEqual(
            [
                (relationship.source_id, relationship.target_id, relationship.kind.value)
                for relationship in result.relationships
            ],
            [
                (
                    "file:repo:nexus:tests/fixtures/python_imports.py",
                    "module:python:.helpers.normalize",
                    "imports",
                ),
                (
                    "file:repo:nexus:tests/fixtures/python_imports.py",
                    "module:python:collections.deque",
                    "imports",
                ),
                (
                    "file:repo:nexus:tests/fixtures/python_imports.py",
                    "module:python:os",
                    "imports",
                ),
            ],
        )

    def test_extracts_call_relationships_and_recursive_self_edges(self) -> None:
        source_file = SourceFileContract(
            "repo:nexus", "tests/fixtures/python_calls.py", "python", HASH, 120
        )
        result = self.parser.parse(
            ParserInputContract(source_file, CALL_FIXTURE.read_text(encoding="utf-8"))
        )
        self.assertEqual(
            [
                (relationship.source_id, relationship.target_id, relationship.kind.value)
                for relationship in result.relationships
                if relationship.kind.value == "calls"
            ],
            [
                (
                    "symbol:repo:nexus:tests/fixtures/python_calls.py:main",
                    "symbol:repo:nexus:tests/fixtures/python_calls.py:helper",
                    "calls",
                ),
                (
                    "symbol:repo:nexus:tests/fixtures/python_calls.py:main",
                    "symbol:repo:nexus:tests/fixtures/python_calls.py:service.run",
                    "calls",
                ),
                (
                    "symbol:repo:nexus:tests/fixtures/python_calls.py:recursive",
                    "symbol:repo:nexus:tests/fixtures/python_calls.py:recursive",
                    "calls",
                ),
            ],
        )


if __name__ == "__main__":
    unittest.main()
