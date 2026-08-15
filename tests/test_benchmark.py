import io
import json
import unittest
from contextlib import redirect_stdout

from nexus.benchmark import run_python_parser_benchmark
from nexus.cli import main


FIXTURE = "class Example:\n    value = 1\n\n    def run(self):\n        return self.value\n"


class BenchmarkTests(unittest.TestCase):
    def test_runner_reports_measured_iterations_and_record_counts(self) -> None:
        result = run_python_parser_benchmark(FIXTURE, "fixture.py", iterations=2)
        self.assertEqual(result.iterations, 2)
        self.assertEqual(result.symbol_count, 3)
        self.assertEqual(result.relationship_count, 0)
        self.assertEqual(len(result.durations_ms), 2)
        self.assertTrue(all(duration >= 0 for duration in result.durations_ms))

    def test_non_positive_iterations_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            run_python_parser_benchmark(FIXTURE, "fixture.py", iterations=0)

    def test_cli_emits_json_benchmark_result(self) -> None:
        output = io.StringIO()
        with redirect_stdout(output):
            exit_code = main(["benchmark", "--fixture", "tests/fixtures/python_parser.py", "--iterations", "1"])
        payload = json.loads(output.getvalue())
        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["iterations"], 1)
        self.assertIn("durations_ms", payload)


if __name__ == "__main__":
    unittest.main()
