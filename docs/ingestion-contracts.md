# NEXUS ingestion contracts

The ingestion boundary is represented by [`src/nexus/ingestion.py`](../src/nexus/ingestion.py). It defines communication between a future repository scanner/parser coordinator and downstream indexing components without implementing either component yet.

## Request

`IngestionRequestContract` identifies the request, repository, local root, revision, and optional language filter. The request is immutable and contains no credentials or provider-specific settings.

## Result

`IngestionResultContract` returns the request identity, analyzed revision, status, discovered source files, and diagnostics. Files are sorted by repository-relative path during serialization, making output deterministic.

Statuses are:

- `complete`: all requested work completed without diagnostics that indicate incomplete processing.
- `partial`: some files were processed, but one or more warnings/errors explain what was skipped or failed.
- `failed`: no indexed files were produced and at least one error explains the failure.

## Diagnostics

`DiagnosticContract` contains a stable code, human-readable message, severity, and optional repository-relative path. Diagnostics are data, not raised exceptions, because one unreadable or unsupported file should not hide successful processing of unrelated files.

The deterministic fixture in [`tests/fixtures/ingestion_contract.json`](../tests/fixtures/ingestion_contract.json) is the compatibility reference for this boundary.
