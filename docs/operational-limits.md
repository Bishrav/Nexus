# NEXUS operational limits

The parser and Git source boundaries now fail explicitly when work exceeds configured safety limits:

- `PythonParserAdapter(max_source_bytes=...)` rejects oversized UTF-8 source content with a `SOURCE_TOO_LARGE` diagnostic.
- `GitRevisionReader(timeout_seconds=...)` passes a timeout to each Git subprocess and converts timeout failures to `GitSourceError`.

These are bounded-failure controls, not performance guarantees. The default values are implementation defaults and should be tuned only with measured workload evidence. No retry policy, process isolation, or resource quota system is implemented yet.
