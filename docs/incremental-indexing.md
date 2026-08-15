# NEXUS incremental indexing plan

The first Phase 3 indexing primitive is [`src/nexus/indexing.py`](../src/nexus/indexing.py). It compares two validated source-file manifests and produces a deterministic `IncrementalPlan`.

## Change classification

- `added`: path exists only in the current revision and must be parsed.
- `changed`: path exists in both revisions but its contract differs and must be reparsed.
- `removed`: path exists only in the previous revision and its old facts must be removed.
- `unchanged`: the source-file contracts are identical and can be reused.

The plan sorts paths, exposes `reparsed_paths` and `removed_paths`, and preserves previous/current content hashes for auditability.

## Current boundary

This milestone plans changes only. It does not read Git, persist snapshots, delete facts from `RepositoryIndex`, or execute parser jobs. Those operations will consume this plan after correctness tests cover the update semantics.
