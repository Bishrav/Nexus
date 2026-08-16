# Developer guide

This guide walks through the smallest complete NEXUS workflow: read one source
file, parse it into versioned contracts, add the result to an index, and inspect
the normalized facts.

## Run the example

From the repository root, configure the source checkout on `PYTHONPATH` and run
the checked-in example:

```powershell
$env:PYTHONPATH = "src"
python examples/inspect_fixture.py
```

The command prints JSON containing the parser status, index summary, symbols,
and relationships extracted from `tests/fixtures/python_parser.py`. The output
is generated from the fixture at runtime; it is not a benchmark or a claim
about production repository coverage.

## How the workflow fits together

1. `SourceFileContract` records repository identity, relative path, language,
   content hash, and byte size.
2. `ParserInputContract` pairs that source metadata with source text.
3. `PythonParserAdapter` uses the standard-library AST parser and emits a
   `ParserOutputContract` containing symbols, syntactic imports, syntactic
   calls, and diagnostics.
4. `RepositoryIndex` stores the normalized facts and exposes deterministic
   queries such as `find_symbols` and `relationships_from`.

The example's central flow is intentionally short:

```python
parser_output = PythonParserAdapter().parse(
    ParserInputContract(source_file, content)
)
index = RepositoryIndex("example:local", revision="fixture")
index.add_parser_output(parser_output)
print(index.summary())
```

The parser and index are independent of the command-line interface, which
allows later services or background jobs to reuse the same boundaries.

## Adding repository changes

For Git-backed indexing, `GitRevisionReader` discovers added, modified,
deleted, and renamed paths between revisions. `plan_incremental_update` turns
those changes into an explicit plan, and `apply_incremental_plan` removes stale
facts before adding replacement parser output. See [Git integration](git-source.md)
and [incremental indexing](incremental-indexing.md) for the current contracts
and failure behavior.

## Saving an index

The in-memory index can be serialized as a versioned JSON snapshot and restored
later. Snapshot persistence is explicit and deterministic; it is not a database
or a background indexing service. See [snapshots](snapshots.md).

## Verification

Run the full local suite after changing parser or index behavior:

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v
```

The repository's CI workflow repeats the supported checks on Python 3.11,
3.12, and 3.13. Current implementation limits, including Python-only parsing
and syntactic rather than resolved call targets, are documented in the
[README](../README.md).
