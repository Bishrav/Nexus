import unittest

from nexus.domain import SourceFileContract, SymbolContract, SymbolKind
from nexus.index import RepositoryIndex
from nexus.snapshot import SnapshotError, restore_snapshot, snapshot_text


HASH = "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"


class SnapshotTests(unittest.TestCase):
    def setUp(self) -> None:
        self.index = RepositoryIndex("repo:nexus", "rev-1")
        source_file = SourceFileContract("repo:nexus", "src/main.py", "python", HASH, 10)
        self.index.add_source_file(source_file)
        self.index.add_symbol(
            SymbolContract("symbol:repo:nexus:src/main.py:main", "repo:nexus", "main", SymbolKind.FUNCTION, "src/main.py", 1, 1)
        )

    def test_snapshot_round_trip_is_deterministic(self) -> None:
        payload = snapshot_text(self.index)
        restored = restore_snapshot(payload)
        self.assertEqual(snapshot_text(restored), payload)
        self.assertEqual(restored.summary(), self.index.summary())

    def test_invalid_json_is_rejected(self) -> None:
        with self.assertRaises(SnapshotError):
            restore_snapshot("not json")

    def test_incompatible_version_is_rejected(self) -> None:
        payload = snapshot_text(self.index).replace("nexus.snapshot.v1", "nexus.snapshot.v2")
        with self.assertRaises(SnapshotError):
            restore_snapshot(payload)

    def test_missing_required_data_is_rejected(self) -> None:
        with self.assertRaises(SnapshotError):
            restore_snapshot('{"snapshot_version":"nexus.snapshot.v1"}')


if __name__ == "__main__":
    unittest.main()
