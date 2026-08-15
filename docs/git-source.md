# NEXUS Git source integration

[`src/nexus/git_source.py`](../src/nexus/git_source.py) provides the first real Git integration for incremental indexing.

`GitRevisionReader.current_revision()` resolves `git rev-parse HEAD`. `changed_files()` runs `git diff --name-status -M <previous> <current> --` and converts added, modified, deleted, and renamed paths into typed `GitFileChange` records.

The command runner is injectable so parsing and failure behavior can be tested without depending on a particular checkout. In a normal repository, command failures are converted into `GitSourceError` with the repository path and underlying Git failure.

This reader does not read file contents, select parser languages, or apply changes to an index. It is the Git metadata boundary for the existing incremental plan/apply pipeline.
