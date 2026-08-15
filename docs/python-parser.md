# NEXUS Python parser

The first concrete parser adapter is [`src/nexus/python_parser.py`](../src/nexus/python_parser.py). It uses Python's standard-library `ast` module and emits the normalized `SymbolContract` records defined in Phase 1.

## Supported symbols

- Classes
- Synchronous and asynchronous functions
- Methods defined directly inside classes
- Named assignments and annotated assignments, including tuple/list targets

Each symbol includes a deterministic ID, kind, qualified scope encoded in the ID, repository-relative file path, and source line range.

Syntax errors produce a failed `ParserOutputContract` with a `SYNTAX_ERROR` diagnostic and no partial symbols. Import relationships, call relationships, decorators, type references, and persistence are not implemented by this milestone.

The parser is deterministic for the same source content and Python AST behavior. The fixture and exact-output tests live in [`tests/test_python_parser.py`](../tests/test_python_parser.py).
