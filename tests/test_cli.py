import json
import unittest
from contextlib import redirect_stdout
from io import StringIO

from nexus import __version__
from nexus.cli import build_parser, main


class CliTests(unittest.TestCase):
    def test_parser_exposes_project_name(self) -> None:
        self.assertEqual(build_parser().prog, "nexus")

    def test_version_flag_is_available(self) -> None:
        with self.assertRaises(SystemExit) as result:
            main(["--version"])
        self.assertEqual(result.exception.code, 0)

    def test_initial_version_is_defined(self) -> None:
        self.assertEqual(__version__, "0.1.0")

    def test_analyze_command_emits_indexed_facts_as_json(self) -> None:
        output = StringIO()
        with redirect_stdout(output):
            exit_code = main(
                [
                    "analyze",
                    "--file",
                    "tests/fixtures/python_parser.py",
                    "--format",
                    "json",
                ]
            )
        result = json.loads(output.getvalue())
        self.assertEqual(exit_code, 0)
        self.assertEqual(result["status"], "complete")
        self.assertEqual(result["summary"]["file_count"], 1)
        self.assertGreater(result["summary"]["symbol_count"], 0)


if __name__ == "__main__":
    unittest.main()
