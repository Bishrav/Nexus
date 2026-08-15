"""Language parser registration and dispatch."""

from __future__ import annotations

from typing import Dict

from nexus.domain import ContractValidationError, _require_identifier
from nexus.parser import ParserAdapter, ParserInputContract, ParserOutputContract


class ParserRegistryError(ContractValidationError):
    """Raised when parser registration or selection cannot be completed."""


class ParserRegistry:
    """Dispatches parser inputs to one registered adapter per language."""

    def __init__(self) -> None:
        self._adapters: Dict[str, ParserAdapter] = {}

    @property
    def languages(self) -> tuple[str, ...]:
        """Return registered language identifiers in deterministic order."""

        return tuple(sorted(self._adapters))

    def register(self, adapter: ParserAdapter) -> None:
        """Register an adapter, rejecting invalid or duplicate languages."""

        if not isinstance(adapter, ParserAdapter):
            raise ParserRegistryError("adapter must implement ParserAdapter")
        _require_identifier(adapter.language, "adapter.language")
        language = adapter.language.lower()
        if language in self._adapters:
            raise ParserRegistryError(f"a parser is already registered for {language!r}")
        self._adapters[language] = adapter

    def get(self, language: str) -> ParserAdapter:
        """Return the adapter for a language or raise a selection error."""

        _require_identifier(language, "language")
        normalized = language.lower()
        try:
            return self._adapters[normalized]
        except KeyError as error:
            raise ParserRegistryError(f"no parser is registered for {normalized!r}") from error

    def parse(self, parser_input: ParserInputContract) -> ParserOutputContract:
        """Dispatch a validated input to the adapter matching its file language."""

        if not isinstance(parser_input, ParserInputContract):
            raise ParserRegistryError("parser_input must be a ParserInputContract")
        return self.get(parser_input.source_file.language).parse(parser_input)
