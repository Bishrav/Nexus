import unittest

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


if __name__ == "__main__":
    unittest.main()
