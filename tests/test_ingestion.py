import json
import unittest
from pathlib import Path

from nexus.domain import SourceFileContract
from nexus.ingestion import (
    DiagnosticContract,
    DiagnosticSeverity,
    IngestionRequestContract,
    IngestionResultContract,
    IngestionStatus,
)


FIXTURE = Path(__file__).parent / "fixtures" / "ingestion_contract.json"
HASH = "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"


class IngestionContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_request_and_partial_result_serialize_deterministically(self) -> None:
        request = IngestionRequestContract(
            "ingest:001", "repo:nexus", "C:/work/Nexus", "a1b2c3d", ("python",)
        )
        file = SourceFileContract("repo:nexus", "src/nexus/cli.py", "python", HASH, 64)
        diagnostic = DiagnosticContract(
            DiagnosticSeverity.WARNING,
            "UNSUPPORTED_FILE",
            "Skipped an unsupported file.",
            "assets/logo.bin",
        )
        result = IngestionResultContract(
            "ingest:001",
            "repo:nexus",
            "a1b2c3d",
            IngestionStatus.PARTIAL,
            (file,),
            (diagnostic,),
        )
        self.assertEqual(request.to_dict(), self.fixture["request"])
        self.assertEqual(result.to_dict(), self.fixture["result"])

    def test_partial_result_requires_diagnostics(self) -> None:
        with self.assertRaises(ValueError):
            IngestionResultContract(
                "ingest:001", "repo:nexus", "a1b2c3d", IngestionStatus.PARTIAL
            )

    def test_failed_result_cannot_include_files(self) -> None:
        file = SourceFileContract("repo:nexus", "src/nexus/cli.py", "python", HASH, 64)
        diagnostic = DiagnosticContract(DiagnosticSeverity.ERROR, "READ_FAILED", "Could not read file.")
        with self.assertRaises(ValueError):
            IngestionResultContract(
                "ingest:001",
                "repo:nexus",
                "a1b2c3d",
                IngestionStatus.FAILED,
                (file,),
                (diagnostic,),
            )

    def test_result_rejects_files_from_another_repository(self) -> None:
        file = SourceFileContract("repo:other", "src/other.py", "python", HASH, 64)
        with self.assertRaises(ValueError):
            IngestionResultContract(
                "ingest:001",
                "repo:nexus",
                "a1b2c3d",
                IngestionStatus.COMPLETE,
                (file,),
            )


if __name__ == "__main__":
    unittest.main()
