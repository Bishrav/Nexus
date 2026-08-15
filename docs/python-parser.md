# NEXUS Python parser

The first concrete parser adapter is [`src/nexus/python_parser.py`](../src/nexus/python_parser.py). It uses Python's standard-library `ast` module and emits the normalized `SymbolContract` records defined in Phase 1.

## Supported symbols

- Classes
- Synchronous and asynchronous functions
- Methods defined directly inside classes
- Named assignments and annotated assignments, including tuple/list targets

Each symbol includes a deterministic ID, kind, qualified scope encoded in the ID, repository-relative file path, and source line range.

Import statements emit graph-ready `IMPORTS` relationships from `file:<repository_id>:<path>` to `module:python:<module>` or `module:python:<module>.<name>` IDs. Ordinary imports, `from ... import ...`, and relative imports are supported.

Call expressions emit `CALLS` relationships from the enclosing function or method symbol to a syntactic target symbol ID. Top-level calls use the file node as their source, and recursive calls are represented as self-edges.

Syntax errors produce a failed `ParserOutputContract` with a `SYNTAX_ERROR` diagnostic and no partial symbols. Name binding, overload resolution, decorators, type references, and persistence are not implemented by this milestone. Module and call targets are syntactic IDs; repository-aware resolution is a later concern.

The parser is deterministic for the same source content and Python AST behavior. The fixture and exact-output tests live in [`tests/test_python_parser.py`](../tests/test_python_parser.py).
