import json
import unittest
from pathlib import Path

from nexus.domain import (
    RelationshipContract,
    SourceFileContract,
    SymbolContract,
    SymbolKind,
)
from nexus.ingestion import DiagnosticContract, DiagnosticSeverity
from nexus.parser import (
    ParseStatus,
    ParserAdapter,
    ParserInputContract,
    ParserOutputContract,
)


FIXTURE = Path(__file__).parent / "fixtures" / "parser_contract.json"
HASH = "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"


class FakePythonParser:
    language = "python"

    def parse(self, parser_input: ParserInputContract) -> ParserOutputContract:
        symbol = SymbolContract(
            "symbol:nexus.cli.main",
            parser_input.source_file.repository_id,
            "main",
            SymbolKind.FUNCTION,
            parser_input.source_file.path,
            12,
            14,
        )
        diagnostic = DiagnosticContract(
            DiagnosticSeverity.WARNING,
            "SYNTAX_RECOVERY",
            "Parser recovered after an unsupported construct.",
            parser_input.source_file.path,
        )
        return ParserOutputContract(
            parser_input.source_file,
            ParseStatus.PARTIAL,
            (symbol,),
            (),
            (diagnostic,),
        )


class ParserContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        cls.source_file = SourceFileContract("repo:nexus", "src/nexus/cli.py", "python", HASH, 64)

    def test_adapter_protocol_and_output_are_normalized(self) -> None:
        adapter = FakePythonParser()
        self.assertIsInstance(adapter, ParserAdapter)
        parser_input = ParserInputContract(self.source_file, "def main():\n    pass\n")
        output = adapter.parse(parser_input)
        self.assertEqual(output.to_dict(), self.fixture)

    def test_symbols_must_belong_to_the_parsed_file(self) -> None:
        symbol = SymbolContract(
            "symbol:other",
            "repo:nexus",
            "other",
            SymbolKind.FUNCTION,
            "src/other.py",
            1,
            2,
        )
        with self.assertRaises(ValueError):
            ParserOutputContract(self.source_file, ParseStatus.COMPLETE, (symbol,))

    def test_failed_output_requires_diagnostics_and_no_records(self) -> None:
        diagnostic = DiagnosticContract(DiagnosticSeverity.ERROR, "PARSE_FAILED", "Unable to parse file.")
        output = ParserOutputContract(
            self.source_file,
            ParseStatus.FAILED,
            diagnostics=(diagnostic,),
        )
        self.assertEqual(output.status, ParseStatus.FAILED)
        with self.assertRaises(ValueError):
            ParserOutputContract(self.source_file, ParseStatus.FAILED)


if __name__ == "__main__":
    unittest.main()
