# NEXUS

NEXUS is an in-development repository intelligence engine for AI-assisted software engineering.

It is intended to build a deterministic, machine-readable representation of a software repository so developers and AI tools can inspect architecture, dependencies, history, and change impact using verified source evidence.

## Project status

**In Development — Phase 0: Discovery and foundation**

The repository currently contains only the initial Python package and CLI foundation. AST parsing, graph construction, indexing, retrieval, and AI tooling are planned milestones; they are not implemented yet.

## Initial development setup

NEXUS requires Python 3.11 or newer.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v
python -m nexus --help
python -m nexus --version
```

The package can be installed locally after the environment is activated:

```powershell
python -m pip install --no-deps -e .
nexus --version
```

If editable installation is unavailable in a restricted checkout, keep `PYTHONPATH` set to `src` and use `python -m nexus`.

## Validation

The repository CI workflow installs the package in a clean environment and verifies supported Python versions, unit tests, Python syntax, and the installed CLI entry point. Run the equivalent local checks with:

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v
python -c "from pathlib import Path; files=list(Path('src').rglob('*.py'))+list(Path('tests').rglob('*.py')); [compile(p.read_text(encoding='utf-8'), str(p), 'exec') for p in files]"
```

## Planned engineering direction

The implementation will grow in focused milestones:

1. Define versioned repository, file, symbol, and graph contracts.
2. Add a deterministic single-language parser and symbol index.
3. Add import and call graphs with queryable relationships.
4. Add Git history and incremental indexing.
5. Add retrieval, impact analysis, typed evidence, and evaluation fixtures.

The project will report only capabilities that are implemented and verified in this repository.

## Architecture

See [the architecture baseline](docs/architecture.md) and [ADR 0001](docs/decisions/0001-deterministic-core-first.md) for the current boundaries and engineering rationale. These documents describe planned architecture; they do not claim that the parser, graph, index, or AI layers are implemented.

## Repository structure

```text
src/nexus/       Python package and CLI
tests/           Deterministic automated tests
.env.example     Non-secret local configuration template
pyproject.toml   Package metadata and development entry point
docs/            Architecture notes and decision records
.github/         Continuous integration workflow
```

Phase 1 domain contracts are documented in [docs/domain-contracts.md](docs/domain-contracts.md).
Ingestion request, result, and diagnostic semantics are documented in [docs/ingestion-contracts.md](docs/ingestion-contracts.md).
