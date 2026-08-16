# NEXUS

NEXUS is an in-development repository intelligence engine for AI-assisted software engineering.

It turns source code and Git revisions into deterministic, queryable facts: files, symbols, imports, calls, diagnostics, and incremental change plans. The goal is to give future developer tools verified repository context before they attempt reasoning or code changes.

## Project status

**In Development - Phase 7 productization and market validation**

The core research prototype is implemented and tested. NEXUS currently supports Python AST symbol extraction, syntactic import/call relationships, in-memory indexing, incremental change planning/application, Git change discovery, JSON snapshots, runtime metrics, benchmarks, golden evaluation, and bounded failure handling.

AI providers, vector retrieval, multi-language parsing, persistent databases, and production deployment are planned; they are not implemented.

## Why this project matters

AI coding tools often reason from incomplete file snippets. NEXUS establishes a deterministic repository-facts layer first, so later tools can query exact source locations and relationships instead of relying only on inferred architecture.

Example workflow:

```text
Git revision -> changed files -> parser adapter -> symbols/relationships
             -> repository index -> impact/evidence queries
```

## Implemented capabilities

- Versioned domain contracts for repositories, source files, symbols, relationships, ingestion, and diagnostics
- Parser adapter protocol and deterministic language registry
- Python parser based on the standard-library `ast` module
- Class, function, method, and assignment symbol extraction
- Syntactic Python import and call relationships, including recursive call edges
- Deterministic in-memory repository index with symbol and relationship queries
- Incremental added/changed/removed/unchanged file planning and index application
- Git revision lookup and changed-file parsing with rename detection
- Versioned JSON index snapshots with validation and restoration
- Optional parser metrics for counts, failures, and measured durations
- Benchmark, golden-evaluation, and sequential load-test CLI commands
- Git timeout, bounded retry, and parser source-size safeguards

## Architecture

```text
Local repository
      |
      v
Git revision reader --> incremental change planner
      |                         |
      +-------------------------v
                   parser registry
                         |
                         v
                 Python AST adapter
                         |
                         v
             normalized domain contracts
                         |
             +-----------+-----------+
             v                       v
       repository index       JSON snapshot
             |
             v
       deterministic queries
```

The current implementation is deliberately local and dependency-light. The architecture baseline and design decision record are in [docs/architecture.md](docs/architecture.md) and [docs/decisions/0001-deterministic-core-first.md](docs/decisions/0001-deterministic-core-first.md).

## Local setup

NEXUS requires Python 3.11 or newer and the Git command-line tool for Git integration.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v
python -m nexus --help
python -m nexus --version
```

Editable installation is supported in a normal writable environment:

```powershell
python -m pip install --no-deps -e .
nexus --version
```

## CLI examples

Run a parser benchmark:

```powershell
python -m nexus benchmark --fixture tests/fixtures/python_parser.py --iterations 10
```

Run golden evaluation:

```powershell
python -m nexus evaluate `
  --fixture tests/evaluation/python_basic.py `
  --expected tests/evaluation/python_basic.json
```

Run a sequential parser load test:

```powershell
python -m nexus load-test --fixture tests/fixtures/python_parser.py --operations 100
```

These commands report local observations and correctness results. They do not claim production throughput, scalability, or model quality.

## Validation and CI

Run the local test and syntax checks:

```powershell
$env:PYTHONPATH = "src"
python scripts/verify.py
```

The repository verification command runs the test suite, checks Python syntax
without writing cache files, checks CLI startup, runs the end-to-end example, and validates local
README links. GitHub Actions runs the same verification after package
installation across Python 3.11, 3.12, and 3.13. See
[.github/workflows/ci.yml](.github/workflows/ci.yml).

The current suite contains 56 tests covering contracts, parser behavior, indexing, Git failure handling, snapshots, benchmarks, and evaluation fixtures.

## Documentation

- [Domain contracts](docs/domain-contracts.md)
- [Ingestion contracts](docs/ingestion-contracts.md)
- [Parser adapters](docs/parser-adapters.md)
- [Python parser](docs/python-parser.md)
- [Parser registry](docs/parser-registry.md)
- [Repository index](docs/repository-index.md)
- [Incremental indexing](docs/incremental-indexing.md)
- [Git integration](docs/git-source.md)
- [Snapshots](docs/snapshots.md)
- [Observability](docs/observability.md)
- [Benchmarks](docs/benchmarks.md)
- [Golden evaluation](docs/evaluation.md)
- [Operational limits](docs/operational-limits.md)
- [Load tests](docs/load-tests.md)
- [Developer guide](docs/developer-guide.md)
- [ADR 0002: Explicit boundaries](docs/decisions/0002-explicit-boundaries-and-deterministic-evidence.md)
- [Portfolio-readiness checklist](docs/portfolio-readiness.md)
- [Phase 6 finalization audit](docs/finalization-audit.md)
- [Product brief](docs/product-brief.md)

## Known limitations

- Only Python parsing is implemented.
- Call and import targets are syntactic IDs; name binding and cross-file resolution are not implemented.
- The repository index is in memory; snapshots are explicit JSON files rather than a database.
- Incremental planning does not yet read file contents or schedule parser jobs automatically.
- Git retries cover timeout and OS-level execution failures only.
- Metrics and benchmark results are process-local observations.
- No AI provider, vector index, hosted API, or production deployment is included.

## Roadmap

1. Phase 7: expose a coherent local developer workflow around repository facts.
2. Add stronger graph queries and cross-file symbol resolution.
3. Add additional language adapters behind the existing parser protocol.
4. Add persistent storage and background indexing workflows.
5. Add retrieval and typed evidence tooling after deterministic facts are reliable.
6. Conduct external user validation before making any market-fit claim.

## Repository structure

```text
src/nexus/       Core contracts, parser, index, Git, snapshots, and CLI
tests/           Unit, integration, evaluation, and benchmark tests
examples/        Small runnable workflows for local exploration
scripts/         Repository verification commands
docs/            Architecture, contracts, operations, and evaluation notes
.github/         Continuous integration workflow
pyproject.toml   Package metadata and CLI entry point
.env.example     Non-secret configuration template
```
