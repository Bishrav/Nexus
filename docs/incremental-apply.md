# Applying incremental index plans

`apply_incremental_plan()` in [`src/nexus/indexing.py`](../src/nexus/indexing.py) connects change planning to `RepositoryIndex`.

Before applying changes it verifies that the plan targets the same repository and starts at the index's current revision. It also requires exactly one parser output for every added or changed path.

Application removes stale facts for removed and changed files, adds the new parser outputs, and updates the index revision. A missing output or revision mismatch fails before mutation. Parser failures may still be supplied as outputs; the file remains represented and its diagnostic is retained without stale symbols.

This remains an in-memory operation. Durable snapshots, Git diff discovery, transactional persistence, and crash recovery are future work.
