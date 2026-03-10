"""Base interface for full-text fetchers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from ..models import PaperMetadata
from .utils import FetchContext


class FulltextFetcher(ABC):
    """Abstract full-text fetcher."""

    name: str

    @abstractmethod
    def fetch(
        self,
        paper: PaperMetadata,
        download_dir: Path | None = None,
        context: FetchContext | None = None,
    ) -> PaperMetadata:
        """Return updated paper metadata after attempting full-text retrieval."""
