# NEXUS in-memory repository index

The first queryable storage layer is [`src/nexus/index.py`](../src/nexus/index.py). `RepositoryIndex` stores one repository revision in memory and consumes normalized parser outputs.

## Behavior

- Source files are keyed by repository-relative path.
- Symbols are keyed by deterministic symbol ID.
- Relationships are keyed by source ID, target ID, and relationship kind.
- Re-adding identical parser output is idempotent.
- Conflicting file or symbol definitions are rejected.
- Facts from another repository are rejected.
- Files, symbols, and relationships are exposed in deterministic order.
- Symbol lookup, name search, and incoming/outgoing relationship queries are supported.

This is intentionally an in-memory foundation for correctness tests. It is not persistent storage, does not support incremental updates yet, and does not resolve syntactic targets to verified definitions.
