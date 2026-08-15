"""Command-line entry point for NEXUS."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from nexus import __version__
from nexus.benchmark import run_python_parser_benchmark
from nexus.evaluation import evaluate_python_fixture
from nexus.load_test import run_sequential_load_test


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nexus",
        description="Repository intelligence tools for AI-assisted software engineering.",
    )
    parser.add_argument("--version", action="version", version=__version__)
    commands = parser.add_subparsers(dest="command")
    benchmark = commands.add_parser("benchmark", help="measure the Python parser on a fixture")
    benchmark.add_argument("--fixture", default="tests/fixtures/python_parser.py")
    benchmark.add_argument("--iterations", type=int, default=3)
    evaluate = commands.add_parser("evaluate", help="compare parser output with a golden fixture")
    evaluate.add_argument("--fixture", required=True)
    evaluate.add_argument("--expected", required=True)
    load_test = commands.add_parser("load-test", help="run repeated parser operations")
    load_test.add_argument("--fixture", default="tests/fixtures/python_parser.py")
    load_test.add_argument("--operations", type=int, default=10)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "benchmark":
        fixture = Path(args.fixture)
        content = fixture.read_text(encoding="utf-8")
        result = run_python_parser_benchmark(content, fixture.as_posix(), args.iterations)
        print(json.dumps(result.to_dict(), sort_keys=True))
    elif args.command == "evaluate":
        result = evaluate_python_fixture(args.fixture, args.expected)
        print(json.dumps(result.to_dict(), sort_keys=True))
        return 0 if result.passed else 1
    elif args.command == "load-test":
        fixture = Path(args.fixture)
        result = run_sequential_load_test(
            fixture.read_text(encoding="utf-8"), fixture.as_posix(), args.operations
        )
        print(json.dumps(result.to_dict(), sort_keys=True))
    return 0
