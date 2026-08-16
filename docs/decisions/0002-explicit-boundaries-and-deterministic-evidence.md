# ADR 0002: Keep indexing boundaries explicit before evidence generation

- Status: Accepted
- Date: 2026-08-16

## Context

NEXUS needs to support future impact analysis and AI-assisted repository
questions. It would be possible to combine Git discovery, parsing, storage,
retrieval, and model calls in one workflow, but that would make failures hard
to localize and make correctness difficult to evaluate. The current prototype
also has only syntactic call/import relationships and one in-memory index.

## Decision

Keep the workflow split into independently testable boundaries:

1. Git revision discovery produces typed file changes.
2. Incremental planning decides which paths need replacement or removal.
3. Parser adapters produce versioned domain contracts.
4. The repository index stores and queries normalized facts.
5. Snapshots provide explicit, schema-validated persistence.
6. Future evidence and AI adapters consume query results without reaching into
   parser or storage internals.

## Why this boundary matters

Each boundary gives the project a place to test a specific failure mode:

- Git timeouts and transient execution failures are handled at the Git boundary.
- Syntax errors and source-size limits are represented as parser diagnostics.
- Revision mismatches and stale facts are handled by incremental application.
- Snapshot schema incompatibility is rejected before restoration.
- Exact symbols and relationships can be checked against deterministic fixtures.

## Tradeoffs

This structure adds contracts and coordination code before the project has a
user-facing AI workflow. It also means the current relationship graph is useful
for syntactic queries but does not yet provide semantic name resolution. The
tradeoff is intentional: future retrieval or model behavior can be evaluated
against a stable, inspectable fact layer.

## Status and follow-up

The Git, parser, index, snapshot, metrics, benchmark, evaluation, and load-test
boundaries are implemented. Evidence construction, semantic cross-file
resolution, persistent storage, and AI tooling adapters are planned follow-up
work.
