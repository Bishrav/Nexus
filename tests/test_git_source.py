import unittest

from nexus.git_source import GitChangeKind, GitRevisionReader, GitSourceError


class FakeGit:
    def __init__(self) -> None:
        self.calls: list[tuple[str, ...]] = []

    def __call__(self, args: tuple[str, ...]) -> str:
        self.calls.append(args)
        if args == ("rev-parse", "HEAD"):
            return "abc123\n"
        return "M\tsrc/changed.py\nA\tsrc/added.py\nD\tsrc/removed.py\nR100\told.py\tnew.py\n"


class GitRevisionReaderTests(unittest.TestCase):
    def test_reads_current_revision_and_sorted_changes(self) -> None:
        fake = FakeGit()
        reader = GitRevisionReader("C:/repo", fake)
        self.assertEqual(reader.current_revision(), "abc123")
        changes = reader.changed_files("oldrev", "newrev")
        self.assertEqual(
            [(change.path, change.kind, change.previous_path) for change in changes],
            [
                ("new.py", GitChangeKind.RENAMED, "old.py"),
                ("src/added.py", GitChangeKind.ADDED, None),
                ("src/changed.py", GitChangeKind.MODIFIED, None),
                ("src/removed.py", GitChangeKind.DELETED, None),
            ],
        )
        self.assertEqual(fake.calls[1], ("diff", "--name-status", "-M", "oldrev", "newrev", "--"))

    def test_malformed_change_line_is_rejected(self) -> None:
        reader = GitRevisionReader("C:/repo", lambda _: "X\tfile.py\n")
        with self.assertRaises(GitSourceError):
            reader.changed_files("oldrev")

    def test_invalid_revision_is_rejected_before_running_git(self) -> None:
        calls: list[tuple[str, ...]] = []

        def runner(args: tuple[str, ...]) -> str:
            calls.append(args)
            return ""

        reader = GitRevisionReader("C:/repo", runner)
        with self.assertRaises(ValueError):
            reader.changed_files(" ")
        self.assertEqual(calls, [])


if __name__ == "__main__":
    unittest.main()
