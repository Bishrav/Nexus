"""Deterministic Python symbol extraction using the standard-library AST."""

from __future__ import annotations

import ast

from nexus.domain import RelationshipContract, RelationshipKind, SymbolContract, SymbolKind
from nexus.ingestion import DiagnosticContract, DiagnosticSeverity
from nexus.parser import ParseStatus, ParserInputContract, ParserOutputContract


class PythonParserAdapter:
    """Extract Python classes, functions, methods, and named assignments."""

    language = "python"

    def parse(self, parser_input: ParserInputContract) -> ParserOutputContract:
        source_file = parser_input.source_file
        try:
            tree = ast.parse(parser_input.content, filename=source_file.path)
        except SyntaxError as error:
            line = error.lineno or 1
            message = error.msg or "invalid Python syntax"
            diagnostic = DiagnosticContract(
                DiagnosticSeverity.ERROR,
                "SYNTAX_ERROR",
                f"{message} (line {line})",
                source_file.path,
            )
            return ParserOutputContract(source_file, ParseStatus.FAILED, diagnostics=(diagnostic,))

        extractor = _SymbolExtractor(source_file.repository_id, source_file.path)
        extractor.visit(tree)
        symbols = tuple(sorted(extractor.symbols, key=lambda symbol: (symbol.start_line, symbol.symbol_id)))
        relationships = tuple(
            sorted(
                extractor.relationships,
                key=lambda relationship: (relationship.source_id, relationship.target_id),
            )
        )
        return ParserOutputContract(
            source_file,
            ParseStatus.COMPLETE,
            symbols=symbols,
            relationships=relationships,
        )


class _SymbolExtractor(ast.NodeVisitor):
    def __init__(self, repository_id: str, file_path: str) -> None:
        self.repository_id = repository_id
        self.file_path = file_path
        self.symbols: list[SymbolContract] = []
        self.relationships: list[RelationshipContract] = []
        self._scope: list[tuple[str, SymbolKind | None]] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._add(node, node.name, SymbolKind.CLASS)
        self._scope.append((node.name, SymbolKind.CLASS))
        self.generic_visit(node)
        self._scope.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        kind = SymbolKind.METHOD if self._scope and self._scope[-1][1] == SymbolKind.CLASS else SymbolKind.FUNCTION
        self._add(node, node.name, kind)
        self._scope.append((node.name, kind))
        self.generic_visit(node)
        self._scope.pop()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self.visit_FunctionDef(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        for target in node.targets:
            for name in _target_names(target):
                self._add(node, name, SymbolKind.VARIABLE)
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        for name in _target_names(node.target):
            self._add(node, name, SymbolKind.VARIABLE)
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        source_id = f"file:{self.repository_id}:{self.file_path}"
        for imported in node.names:
            self.relationships.append(
                RelationshipContract(
                    self.repository_id,
                    source_id,
                    f"module:python:{imported.name}",
                    RelationshipKind.IMPORTS,
                )
            )
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        source_id = f"file:{self.repository_id}:{self.file_path}"
        module = "." * node.level + (node.module or "")
        for imported in node.names:
            target = ".".join(part for part in (module, imported.name) if part)
            self.relationships.append(
                RelationshipContract(
                    self.repository_id,
                    source_id,
                    f"module:python:{target}",
                    RelationshipKind.IMPORTS,
                )
            )
        self.generic_visit(node)

    def _add(self, node: ast.AST, name: str, kind: SymbolKind) -> None:
        qualified_name = ".".join([item[0] for item in self._scope] + [name])
        start_line = getattr(node, "lineno", 1)
        end_line = getattr(node, "end_lineno", start_line) or start_line
        self.symbols.append(
            SymbolContract(
                f"symbol:{self.repository_id}:{self.file_path}:{qualified_name}",
                self.repository_id,
                name,
                kind,
                self.file_path,
                start_line,
                end_line,
            )
        )


def _target_names(target: ast.expr) -> tuple[str, ...]:
    if isinstance(target, ast.Name):
        return (target.id,)
    if isinstance(target, (ast.Tuple, ast.List)):
        names: list[str] = []
        for element in target.elts:
            names.extend(_target_names(element))
        return tuple(names)
    return ()
