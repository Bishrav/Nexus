# ADR 0001: Build deterministic repository facts before AI tooling

- Status: Accepted
- Date: 2026-08-15

## Context

NEXUS is intended to support AI-assisted software engineering tasks such as impact analysis and repository questions. Those tasks require reliable knowledge of files, symbols, and relationships. Starting with model calls would make it difficult to distinguish missing repository facts from model reasoning errors.

## Decision

The first implementation stages will build deterministic repository facts first:

1. Repository and file discovery
2. Language-specific parsing
3. Normalized symbols and source locations
4. Import/call relationships
5. Query and evidence interfaces

AI tooling will consume these interfaces rather than reaching directly into parser or storage internals.

## Consequences

Positive consequences:

- Parser and graph behavior can be tested with exact fixtures.
- AI answers can be evaluated against source evidence.
- Model providers remain replaceable.
- Early milestones can run locally without API credentials.

Tradeoffs:

- The first demonstrations will be less visually impressive than a chatbot-first prototype.
- Domain contracts and fixtures must be designed before broad feature work.
- Useful AI workflows arrive after the indexing foundation is reliable.
