import unittest

from nexus.domain import SourceFileContract
from nexus.observability import MetricsCollector
from nexus.parser import ParserInputContract
from nexus.python_parser import PythonParserAdapter


HASH = "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"


class ObservabilityTests(unittest.TestCase):
    def test_parser_records_success_and_failure_metrics(self) -> None:
        metrics = MetricsCollector()
        source_file = SourceFileContract("repo:nexus", "main.py", "python", HASH, 10)
        parser = PythonParserAdapter(metrics)
        parser.parse(ParserInputContract(source_file, "def main(): pass"))
        parser.parse(ParserInputContract(source_file, "def broken(:"))
        self.assertEqual(
            metrics.snapshot()["python.parse"]["count"],
            2,
        )
        self.assertEqual(metrics.snapshot()["python.parse"]["failures"], 1)
        self.assertGreaterEqual(metrics.snapshot()["python.parse"]["total_duration_ms"], 0)

    def test_invalid_metric_values_are_rejected(self) -> None:
        metrics = MetricsCollector()
        with self.assertRaises(ValueError):
            metrics.record("op", "unknown", 1)
        with self.assertRaises(ValueError):
            metrics.record("op", "success", -1)


if __name__ == "__main__":
    unittest.main()
