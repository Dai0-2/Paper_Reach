"""Base interface for search channels."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from ..models import PaperMetadata, QueryInput


class SearchChannel(ABC):
    """Abstract search backend."""

    name: str
    supports_online: bool = False
    supports_offline: bool = False

    @abstractmethod
    def search(
        self,
        query: QueryInput,
        *,
        high_recall: bool = False,
        retrieval_limit: int | None = None,
    ) -> List[PaperMetadata]:
        """Return normalized metadata records for a query."""
