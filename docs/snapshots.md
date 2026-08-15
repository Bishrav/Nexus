# NEXUS durable index snapshots

The snapshot boundary is implemented in [`src/nexus/snapshot.py`](../src/nexus/snapshot.py). It serializes an in-memory `RepositoryIndex` as deterministic JSON and restores it through the same validated domain contracts used during indexing.

## Format

Snapshots include:

- `snapshot_version`: currently `nexus.snapshot.v1`
- `schema_version`: currently `nexus.domain.v1`
- repository ID and revision
- source files
- symbols
- relationships
- diagnostics

Serialization uses sorted JSON keys, stable record ordering, and a trailing newline. Loading rejects malformed JSON, incompatible versions, missing fields, invalid enum values, cross-repository records, and conflicting facts.

The current implementation provides durable file APIs but does not yet add locking, atomic rename, compression, migrations, encryption, or remote object storage. Those operational concerns belong to a later reliability milestone.
