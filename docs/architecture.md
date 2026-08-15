# NEXUS architecture baseline

## Purpose

NEXUS will provide structured repository facts to developer workflows and AI tools. The system should be able to answer questions such as which symbols depend on a changed function, which tests cover an affected module, and which repository files provide the evidence for an answer.

The architecture is intentionally staged. The first implementation will establish deterministic repository facts before adding retrieval or model providers.

## Planned boundaries

```text
Repository input
        |
        v
Repository service ---- Git history reader
        |
        v
Parser coordinator ---- language parser workers
        |
        v
Normalized domain model
        |
        +--> Symbol and source index
        +--> Relationship graph
        +--> Evidence and query layer
                         |
                         v
                 AI tooling adapters
```

### Repository service

Owns repository identity, working-tree discovery, file enumeration, and later Git revision tracking. It must not contain parser-specific logic.

### Parser coordinator

Selects a parser based on detected language and converts parser output into versioned NEXUS domain records. Parser workers are replaceable and independently testable.

### Normalized domain model

Defines stable records for repositories, files, symbols, and relationships. Downstream indexes and graph queries consume these records instead of language-specific parser objects.

### Index and graph layers

The source/symbol index supports exact lookup. The relationship graph supports dependency traversal, impact analysis, and later evidence construction. Storage choices remain open until the domain contracts and fixture workload are measured.

### AI tooling adapters

AI features will call typed query interfaces and receive evidence that identifies the relevant files, symbols, and relationships. Model providers must remain outside the core indexing and graph logic.

## First vertical slice

The first functional slice is intentionally narrow:

1. Accept a local repository path.
2. Detect supported source files.
3. Parse one language into deterministic symbol records.
4. Persist or return those records through a stable interface.
5. Test the result against checked-in fixtures.

No vector database, external model provider, hosted service, or production deployment is part of this slice.

## Reliability principles

- Parsing results must be deterministic for the same input revision.
- Unsupported files must be reported explicitly rather than silently treated as parsed.
- A parser failure for one file must preserve diagnostics and avoid corrupting records for unrelated files.
- Domain records should carry source locations so later answers can cite evidence precisely.
- Incremental indexing will be introduced only after full indexing has correctness fixtures.

## Current status

This document describes the Phase 0 architecture baseline. It is a design target, not evidence that the parser, graph, index, or AI layers are implemented.
