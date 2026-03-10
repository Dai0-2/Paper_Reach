"""Optional PyMuPDF-based PDF parser."""

from __future__ import annotations

from pathlib import Path

from .base import DocumentParser

try:
    import fitz  # type: ignore
except ImportError:  # pragma: no cover
    fitz = None


class PyMuPDFParser(DocumentParser):
    """Parse local PDFs when PyMuPDF is installed."""

    name = "pymupdf"

    def can_parse(self, path: Path) -> bool:
        return path.suffix.lower() == ".pdf" and fitz is not None

    def parse(self, path: Path) -> str | None:
        if fitz is None:
            return None
        try:
            with fitz.open(path) as document:
                return "\n".join(page.get_text("text") for page in document)
        except Exception:
            return None

