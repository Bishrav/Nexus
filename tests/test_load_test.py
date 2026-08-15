import io
import json
import unittest
from contextlib import redirect_stdout

from nexus.cli import main
from nexus.load_test import run_sequential_load_test


FIXTURE = "def main():\n    return 1\n"


class LoadTestTests(unittest.TestCase):
    def test_runner_reports_all_operations_and_raw_durations(self) -> None:
        result = run_sequential_load_test(FIXTURE, "fixture.py", operations=3)
        self.assertEqual(result.operations, 3)
        self.assertEqual(result.successes, 3)
        self.assertEqual(result.failures, 0)
        self.assertEqual(len(result.durations_ms), 3)

    def test_non_positive_operations_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            run_sequential_load_test(FIXTURE, "fixture.py", operations=0)

    def test_cli_emits_load_test_json(self) -> None:
        output = io.StringIO()
        with redirect_stdout(output):
            exit_code = main(
                ["load-test", "--fixture", "tests/fixtures/python_parser.py", "--operations", "1"]
            )
        payload = json.loads(output.getvalue())
        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["operations"], 1)


if __name__ == "__main__":
    unittest.main()
