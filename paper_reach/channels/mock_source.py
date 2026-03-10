"""Mock source used by tests and demos."""

from __future__ import annotations

from typing import List

from ..models import PaperMetadata, QueryInput
from .base import SearchChannel


class MockSourceChannel(SearchChannel):
    """Return deterministic sample papers."""

    name = "mock_source"
    supports_online = True
    supports_offline = True

    def search(
        self,
        query: QueryInput,
        *,
        high_recall: bool = False,
        retrieval_limit: int | None = None,
    ) -> List[PaperMetadata]:
        return [
            PaperMetadata(
                id="mock-001",
                title="Driving Attention Maps with Human Gaze Supervision in Real Traffic",
                authors=["A. Lee", "B. Kumar"],
                year=2023,
                venue="CVPR Workshops",
                abstract=(
                    "We study driving attention prediction in real scenes with human gaze "
                    "maps collected on BDD-100K-like videos."
                ),
                source=self.name,
                url="https://example.org/mock-001",
            ),
            PaperMetadata(
                id="mock-002",
                title="Attention Prediction for Driving Videos",
                authors=["C. Zhang"],
                year=2022,
                venue="ArXiv",
                abstract="We predict attention in driving videos using multimodal inputs.",
                source=self.name,
                url="https://example.org/mock-002",
            ),
            PaperMetadata(
                id="mock-003",
                title="Behavior Prediction for Autonomous Driving",
                authors=["D. Smith"],
                year=2024,
                venue="IV",
                abstract="We predict driving maneuvers from egocentric video.",
                source=self.name,
                url="https://example.org/mock-003",
            ),
        ][: (retrieval_limit or query.max_results)]
