import unittest

from nexus.domain import SourceFileContract, SymbolContract, SymbolKind
from nexus.parser import ParseStatus, ParserInputContract, ParserOutputContract
from nexus.registry import ParserRegistry, ParserRegistryError


HASH = "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"


class RecordingParser:
    def __init__(self, language: str) -> None:
        self.language = language
        self.calls = 0

    def parse(self, parser_input: ParserInputContract) -> ParserOutputContract:
        self.calls += 1
        symbol = SymbolContract(
            f"symbol:{self.language}.entry",
            parser_input.source_file.repository_id,
            "entry",
            SymbolKind.FUNCTION,
            parser_input.source_file.path,
            1,
            1,
        )
        return ParserOutputContract(parser_input.source_file, ParseStatus.COMPLETE, (symbol,))


class ParserRegistryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = ParserRegistry()
        self.python_parser = RecordingParser("python")
        self.registry.register(self.python_parser)

    def test_dispatches_by_case_insensitive_source_language(self) -> None:
        source_file = SourceFileContract("repo:nexus", "src/main.py", "Python", HASH, 10)
        output = self.registry.parse(ParserInputContract(source_file, "def entry(): pass"))
        self.assertEqual(output.status, ParseStatus.COMPLETE)
        self.assertEqual(self.python_parser.calls, 1)

    def test_languages_are_sorted_and_duplicate_registration_is_rejected(self) -> None:
        self.registry.register(RecordingParser("javascript"))
        self.assertEqual(self.registry.languages, ("javascript", "python"))
        with self.assertRaises(ParserRegistryError):
            self.registry.register(RecordingParser("PYTHON"))

    def test_unsupported_language_is_rejected(self) -> None:
        source_file = SourceFileContract("repo:nexus", "src/main.go", "go", HASH, 10)
        with self.assertRaises(ParserRegistryError):
            self.registry.parse(ParserInputContract(source_file, "package main"))

    def test_non_adapter_registration_is_rejected(self) -> None:
        with self.assertRaises(ParserRegistryError):
            self.registry.register(object())


if __name__ == "__main__":
    unittest.main()
