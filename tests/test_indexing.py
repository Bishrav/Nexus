import unittest

from nexus.domain import SourceFileContract
from nexus.indexing import (
    FileChangeKind,
    IndexingValidationError,
    plan_incremental_update,
)


HASH_A = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
HASH_B = "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
HASH_C = "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"


def file(path: str, content_hash: str, size: int = 10) -> SourceFileContract:
    return SourceFileContract("repo:nexus", path, "python", content_hash, size)


class IncrementalIndexingTests(unittest.TestCase):
    def test_classifies_added_changed_removed_and_unchanged_files(self) -> None:
        previous = [file("same.py", HASH_A), file("changed.py", HASH_A), file("removed.py", HASH_C)]
        current = [file("same.py", HASH_A), file("changed.py", HASH_B), file("added.py", HASH_B)]
        plan = plan_incremental_update("repo:nexus", "rev-1", "rev-2", previous, current)
        self.assertEqual(
            [(change.path, change.kind) for change in plan.changes],
            [
                ("added.py", FileChangeKind.ADDED),
                ("changed.py", FileChangeKind.CHANGED),
                ("removed.py", FileChangeKind.REMOVED),
                ("same.py", FileChangeKind.UNCHANGED),
            ],
        )
        self.assertEqual(plan.reparsed_paths, ("added.py", "changed.py"))
        self.assertEqual(plan.removed_paths, ("removed.py",))

    def test_identical_manifests_are_deterministic(self) -> None:
        files = [file("b.py", HASH_B), file("a.py", HASH_A)]
        plan = plan_incremental_update("repo:nexus", "rev-1", "rev-1", files, reversed(files))
        self.assertEqual([change.kind for change in plan.changes], [FileChangeKind.UNCHANGED] * 2)
        self.assertEqual(plan.to_dict()["changes"][0]["path"], "a.py")

    def test_cross_repository_files_are_rejected(self) -> None:
        other = SourceFileContract("repo:other", "other.py", "python", HASH_A, 10)
        with self.assertRaises(IndexingValidationError):
            plan_incremental_update("repo:nexus", "rev-1", "rev-2", [], [other])

    def test_duplicate_paths_are_rejected(self) -> None:
        with self.assertRaises(IndexingValidationError):
            plan_incremental_update(
                "repo:nexus", "rev-1", "rev-2", [file("same.py", HASH_A), file("same.py", HASH_B)], []
            )


if __name__ == "__main__":
    unittest.main()
