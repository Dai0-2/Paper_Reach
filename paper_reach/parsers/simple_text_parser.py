"""Plain text parser."""

from __future__ import annotations

from pathlib import Path

from .base import DocumentParser


class SimpleTextParser(DocumentParser):
    """Read plain text files from disk."""

    name = "simple_text"

    def can_parse(self, path: Path) -> bool:
        return path.suffix.lower() == ".txt"

    def parse(self, path: Path) -> str | None:
        try:
            return path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return None

