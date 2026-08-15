# NEXUS parser adapter boundary

The parser boundary is defined in [`src/nexus/parser.py`](../src/nexus/parser.py). It separates language-specific workers from the normalized NEXUS domain model.

## Input

`ParserInputContract` provides one validated `SourceFileContract` and its source content. A parser worker receives one file at a time, which keeps failures isolated and makes fixture tests deterministic.

## Adapter protocol

`ParserAdapter` requires a language identifier and a `parse()` method. A Python, JavaScript, or future language adapter can implement this protocol without changing ingestion or graph consumers.

## Output

`ParserOutputContract` contains the original source-file identity, normalized `SymbolContract` and `RelationshipContract` records, a parse status, and structured diagnostics.

- `complete` means parsing produced records without incomplete-processing diagnostics.
- `partial` allows normalized records plus diagnostics describing recovery or skipped constructs.
- `failed` must produce diagnostics and no normalized records.

The output serializer sorts records by stable identifiers so equivalent parser results have deterministic representations. The parser adapter does not persist data, build a global graph, call an AI provider, or decide storage strategy.

The compatibility fixture is [`tests/fixtures/parser_contract.json`](../tests/fixtures/parser_contract.json).
