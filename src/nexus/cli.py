"""Command-line entry point for NEXUS."""

from __future__ import annotations

import argparse

from nexus import __version__


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nexus",
        description="Repository intelligence tools for AI-assisted software engineering.",
    )
    parser.add_argument("--version", action="version", version=__version__)
    return parser


def main(argv: list[str] | None = None) -> int:
    build_parser().parse_args(argv)
    return 0
