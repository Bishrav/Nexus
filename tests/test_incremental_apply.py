import unittest

from nexus.domain import SourceFileContract, SymbolContract, SymbolKind
from nexus.index import RepositoryIndex
from nexus.indexing import (
    IndexingValidationError,
    apply_incremental_plan,
    plan_incremental_update,
)
from nexus.parser import ParseStatus, ParserOutputContract


HASH_A = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
HASH_B = "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"


def output(path: str, content_hash: str, name: str) -> ParserOutputContract:
    source_file = SourceFileContract("repo:nexus", path, "python", content_hash, 10)
    symbol = SymbolContract(
        f"symbol:repo:nexus:{path}:{name}",
        "repo:nexus",
        name,
        SymbolKind.FUNCTION,
        path,
        1,
        1,
    )
    return ParserOutputContract(source_file, ParseStatus.COMPLETE, symbols=(symbol,))


class IncrementalApplyTests(unittest.TestCase):
    def test_apply_replaces_changed_facts_and_adds_new_facts(self) -> None:
        old = output("src/old.py", HASH_A, "old_name")
        changed = output("src/old.py", HASH_B, "new_name")
        added = output("src/new.py", HASH_B, "added_name")
        index = RepositoryIndex("repo:nexus", "rev-1")
        index.add_parser_output(old)
        plan = plan_incremental_update(
            "repo:nexus", "rev-1", "rev-2", [old.source_file], [changed.source_file, added.source_file]
        )

        apply_incremental_plan(index, plan, {"src/old.py": changed, "src/new.py": added})

        self.assertEqual(index.revision, "rev-2")
        self.assertIsNone(index.get_symbol("symbol:repo:nexus:src/old.py:old_name"))
        self.assertIsNotNone(index.get_symbol("symbol:repo:nexus:src/old.py:new_name"))
        self.assertIsNotNone(index.get_symbol("symbol:repo:nexus:src/new.py:added_name"))

    def test_revision_mismatch_prevents_mutation(self) -> None:
        index = RepositoryIndex("repo:nexus", "rev-0")
        plan = plan_incremental_update("repo:nexus", "rev-1", "rev-2", [], [])
        with self.assertRaises(IndexingValidationError):
            apply_incremental_plan(index, plan, {})
        self.assertEqual(index.revision, "rev-0")

    def test_missing_parser_output_is_rejected(self) -> None:
        old = output("src/old.py", HASH_A, "old_name")
        changed = output("src/old.py", HASH_B, "new_name")
        index = RepositoryIndex("repo:nexus", "rev-1")
        index.add_parser_output(old)
        plan = plan_incremental_update(
            "repo:nexus", "rev-1", "rev-2", [old.source_file], [changed.source_file]
        )
        with self.assertRaises(IndexingValidationError):
            apply_incremental_plan(index, plan, {})
        self.assertIsNotNone(index.get_symbol("symbol:repo:nexus:src/old.py:old_name"))


if __name__ == "__main__":
    unittest.main()
