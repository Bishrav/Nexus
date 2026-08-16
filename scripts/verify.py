"""Run the repository's documented local verification checks."""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def run(*args: str) -> None:
    command = [sys.executable, *args]
    print(f"$ {' '.join(command)}")
    subprocess.run(command, cwd=ROOT, check=True)


def check_readme_links() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    links = re.findall(r"\[[^\]]+\]\(([^)]+)\)", readme)
    local_links = [link for link in links if not link.startswith(("http://", "https://", "#"))]
    missing = [link for link in local_links if not (ROOT / link).exists()]
    if missing:
        raise SystemExit(f"Missing README links: {', '.join(missing)}")
    print(f"README local links verified: {len(local_links)}")


def check_python_syntax() -> None:
    roots = (ROOT / "src", ROOT / "tests", ROOT / "examples", ROOT / "scripts")
    files = [path for root in roots for path in root.rglob("*.py")]
    for path in files:
        source = path.read_text(encoding="utf-8")
        compile(source, str(path), "exec")
    print(f"Python syntax verified: {len(files)} files")


def main() -> None:
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(ROOT / "src")

    print("Running NEXUS verification")
    subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
        cwd=ROOT,
        env=environment,
        check=True,
    )
    check_python_syntax()
    subprocess.run(
        [sys.executable, "-m", "nexus", "--version"],
        cwd=ROOT,
        env=environment,
        check=True,
    )
    subprocess.run(
        [sys.executable, "-m", "nexus", "--help"],
        cwd=ROOT,
        env=environment,
        check=True,
        stdout=subprocess.DEVNULL,
    )
    subprocess.run(
        [sys.executable, "examples/inspect_fixture.py"],
        cwd=ROOT,
        env=environment,
        check=True,
        stdout=subprocess.DEVNULL,
    )
    check_readme_links()
    print("Verification passed")


if __name__ == "__main__":
    main()
