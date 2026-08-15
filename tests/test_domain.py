import json
import unittest
from pathlib import Path

from nexus.domain import (
    ContractValidationError,
    RelationshipContract,
    RelationshipKind,
    RepositoryContract,
    SourceFileContract,
    SymbolContract,
    SymbolKind,
)


FIXTURE = Path(__file__).parent / "fixtures" / "domain_contract.json"


class DomainContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_contracts_serialize_to_fixture_shape(self) -> None:
        self.assertEqual(
            RepositoryContract("repo:nexus", "NEXUS", "a1b2c3d").to_dict(),
            self.fixture["repository"],
        )
        self.assertEqual(
            SourceFileContract(
                "repo:nexus",
                "src/nexus/domain.py",
                "python",
                "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
                128,
            ).to_dict(),
            self.fixture["source_file"],
        )
        self.assertEqual(
            SymbolContract(
                "symbol:nexus.domain.RepositoryContract",
                "repo:nexus",
                "RepositoryContract",
                SymbolKind.CLASS,
                "src/nexus/domain.py",
                44,
                61,
            ).to_dict(),
            self.fixture["symbol"],
        )
        self.assertEqual(
            RelationshipContract(
                "repo:nexus",
                "symbol:nexus.cli.main",
                "symbol:nexus.cli.build_parser",
                RelationshipKind.CALLS,
            ).to_dict(),
            self.fixture["relationship"],
        )

    def test_invalid_source_file_hash_is_rejected(self) -> None:
        with self.assertRaises(ContractValidationError):
            SourceFileContract("repo:nexus", "README.md", "text", "not-a-hash", 10)

    def test_invalid_symbol_range_is_rejected(self) -> None:
        with self.assertRaises(ContractValidationError):
            SymbolContract(
                "symbol:bad",
                "repo:nexus",
                "bad",
                SymbolKind.FUNCTION,
                "src/bad.py",
                10,
                9,
            )

    def test_absolute_and_parent_paths_are_rejected(self) -> None:
        with self.assertRaises(ContractValidationError):
            SourceFileContract(
                "repo:nexus",
                "../outside.py",
                "python",
                "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
                1,
            )


if __name__ == "__main__":
    unittest.main()
