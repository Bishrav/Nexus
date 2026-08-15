# NEXUS operational limits

The parser and Git source boundaries now fail explicitly when work exceeds configured safety limits:

- `PythonParserAdapter(max_source_bytes=...)` rejects oversized UTF-8 source content with a `SOURCE_TOO_LARGE` diagnostic.
- `GitRevisionReader(timeout_seconds=...)` passes a timeout to each Git subprocess and converts timeout failures to `GitSourceError`.

Git timeouts and OS-level execution failures receive a bounded retry policy controlled by `max_attempts` and `retry_delay_seconds`. Git commands that execute and return a non-zero exit status fail fast because their cause is not assumed to be transient.

These are bounded-failure controls, not performance guarantees. The default values are implementation defaults and should be tuned only with measured workload evidence. Process isolation and resource quota systems are not implemented yet.
