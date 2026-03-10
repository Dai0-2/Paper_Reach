"""Base parser contract."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path


class DocumentParser(ABC):
    """Abstract parser for local documents."""

    name: str

    @abstractmethod
    def can_parse(self, path: Path) -> bool:
        """Return whether this parser can handle the path."""

    @abstractmethod
    def parse(self, path: Path) -> str | None:
        """Return extracted text or None if parsing fails."""

