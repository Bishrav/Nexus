import unittest
from pathlib import Path

from nexus.domain import RelationshipKind, SourceFileContract
from nexus.index import IndexValidationError, RepositoryIndex
from nexus.parser import ParserInputContract
from nexus.python_parser import PythonParserAdapter


HASH = "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
FIXTURE = Path(__file__).parent / "fixtures" / "python_calls.py"


class RepositoryIndexTests(unittest.TestCase):
    def setUp(self) -> None:
        self.source_file = SourceFileContract("repo:nexus", "tests/fixtures/python_calls.py", "python", HASH, 120)
        parser = PythonParserAdapter()
        self.output = parser.parse(
            ParserInputContract(self.source_file, FIXTURE.read_text(encoding="utf-8"))
        )
        self.index = RepositoryIndex("repo:nexus", "a1b2c3d")
        self.index.add_parser_output(self.output)

    def test_parser_output_is_queryable_end_to_end(self) -> None:
        self.assertEqual(self.index.summary()["file_count"], 1)
        self.assertEqual(self.index.summary()["symbol_count"], 3)
        main = self.index.find_symbols("main")[0]
        calls = self.index.relationships_from(main.symbol_id, RelationshipKind.CALLS)
        self.assertEqual(len(calls), 2)
        self.assertIsNotNone(self.index.get_symbol("symbol:repo:nexus:tests/fixtures/python_calls.py:helper"))

    def test_readding_same_output_is_idempotent(self) -> None:
        before = self.index.summary()
        self.index.add_parser_output(self.output)
        self.assertEqual(self.index.summary(), before)

    def test_cross_repository_output_is_rejected(self) -> None:
        other_file = SourceFileContract("repo:other", "other.py", "python", HASH, 1)
        with self.assertRaises(IndexValidationError):
            self.index.add_source_file(other_file)

    def test_conflicting_file_revision_is_rejected(self) -> None:
        changed_file = SourceFileContract("repo:nexus", self.source_file.path, "python", HASH, 999)
        with self.assertRaises(IndexValidationError):
            self.index.add_source_file(changed_file)


if __name__ == "__main__":
    unittest.main()
