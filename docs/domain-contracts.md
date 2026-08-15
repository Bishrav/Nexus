# NEXUS domain contracts

The first Phase 1 contracts live in [`src/nexus/domain.py`](../src/nexus/domain.py). They are immutable Python dataclasses with explicit validation and a stable `to_dict()` representation.

## Contract version

Every serialized record includes `schema_version: "nexus.domain.v1"`. A future incompatible change must introduce a new version rather than silently changing the meaning of an existing field.

## Current records

| Record | Purpose |
| --- | --- |
| `RepositoryContract` | Identifies a repository and the revision being analyzed |
| `SourceFileContract` | Identifies a source file, language, SHA-256 content hash, and size |
| `SymbolContract` | Identifies a symbol and its source location |
| `RelationshipContract` | Describes a directed relationship between two graph node IDs |

The contracts deliberately do not perform parsing, persistence, graph traversal, or AI calls. Those responsibilities belong to later modules.

## Validation guarantees

- IDs are non-empty and contain no whitespace.
- Source paths are relative to the repository and cannot escape through `..` segments.
- Source hashes are 64-character hexadecimal SHA-256 digests.
- Symbol locations use positive, ordered line numbers.
- Relationship endpoints cannot be the same node.
- Enum values are explicit and serialized as strings.

The deterministic fixture in [`tests/fixtures/domain_contract.json`](../tests/fixtures/domain_contract.json) is the compatibility reference for the initial representation.
