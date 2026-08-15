# NEXUS parser registry

The parser registry in [`src/nexus/registry.py`](../src/nexus/registry.py) owns language-to-adapter selection. It is deliberately small so parser workers remain independently testable and the coordinator does not need language-specific conditionals.

## Behavior

- Language identifiers are normalized to lowercase for registration and lookup.
- Only one adapter can be registered for a language.
- Registered languages are exposed in sorted order for deterministic inspection.
- Unsupported languages produce a structured `ParserRegistryError`.
- Dispatch accepts only `ParserInputContract` values and returns a `ParserOutputContract`.

The registry does not discover files, parse content itself, persist records, or recover parser failures. Those responsibilities remain with repository ingestion, adapters, and later orchestration layers.
