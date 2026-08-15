import io
import json
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from nexus.cli import main
from nexus.evaluation import evaluate_python_fixture


FIXTURE = Path("tests/evaluation/python_basic.py")
EXPECTED = Path("tests/evaluation/python_basic.json")


class EvaluationTests(unittest.TestCase):
    def test_checked_in_python_case_passes(self) -> None:
        result = evaluate_python_fixture(FIXTURE, EXPECTED)
        self.assertTrue(result.passed)
        self.assertEqual(result.mismatches, ())

    def test_cli_returns_success_for_matching_golden_case(self) -> None:
        output = io.StringIO()
        with redirect_stdout(output):
            exit_code = main(["evaluate", "--fixture", str(FIXTURE), "--expected", str(EXPECTED)])
        self.assertEqual(exit_code, 0)
        self.assertTrue(json.loads(output.getvalue())["passed"])


if __name__ == "__main__":
    unittest.main()
