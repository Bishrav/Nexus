# NEXUS observability baseline

The first runtime observability primitive is [`src/nexus/observability.py`](../src/nexus/observability.py). `MetricsCollector` records measured operation counts, failures, and accumulated elapsed time. It does not generate benchmark claims or estimate unobserved values.

The Python parser accepts an optional collector and records `python.parse` outcomes as `success` or `failure`. Metrics are disabled by default and do not change parser output or error handling.

The current metrics are process-local and in-memory. They are suitable for tests and local demonstrations, but are not yet exported to Prometheus, logs, a database, or a hosted monitoring system.
