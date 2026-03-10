"""Lightweight OpenAlex backend."""

from __future__ import annotations

from typing import List

import requests

from ..config import DEFAULT_CONFIG
from ..models import PaperMetadata, QueryInput
from ..retrieval import build_search_phrases
from .base import SearchChannel


class OpenAlexChannel(SearchChannel):
    """Query OpenAlex defensively and normalize a small result set."""

    name = "openalex"
    supports_online = True
    supports_offline = False
    endpoint = "https://api.openalex.org/works"

    def search(
        self,
        query: QueryInput,
        *,
        high_recall: bool = False,
        retrieval_limit: int | None = None,
    ) -> List[PaperMetadata]:
        if query.mode == "offline":
            return []
        limit = retrieval_limit or (max(query.max_results * 8, 100) if high_recall else max(query.max_results * 2, 25))
        phrases = build_search_phrases(query, high_recall=high_recall)
        page_size = 25
        pages_per_phrase = 2 if high_recall else 1
        deduped: dict[str, PaperMetadata] = {}

        for phrase in phrases:
            for page in range(1, pages_per_phrase + 1):
                params = {
                    "search": phrase,
                    "per-page": page_size,
                    "page": page,
                    "sort": "relevance_score:desc",
                }
                try:
                    response = requests.get(
                        self.endpoint,
                        params=params,
                        timeout=DEFAULT_CONFIG.request_timeout_seconds,
                        headers={"User-Agent": DEFAULT_CONFIG.user_agent},
                    )
                    response.raise_for_status()
                    payload = response.json()
                except requests.RequestException:
                    break
                for item in payload.get("results", []):
                    paper = _to_paper(item, self.name, query)
                    if paper is None:
                        continue
                    deduped.setdefault(paper.id or paper.title.lower(), paper)
                    if len(deduped) >= limit:
                        return list(deduped.values())[:limit]
                if not payload.get("results"):
                    break
        return list(deduped.values())[:limit]


def _to_paper(item: dict, source_name: str, query: QueryInput) -> PaperMetadata | None:
    year = item.get("publication_year")
    if year is not None and not (query.year_range[0] <= year <= query.year_range[1]):
        return None
    primary_location = item.get("primary_location") or {}
    source = primary_location.get("source") or {}
    authors = [
        authorship.get("author", {}).get("display_name", "")
        for authorship in item.get("authorships", [])
        if authorship.get("author", {}).get("display_name")
    ]
    abstract = _openalex_abstract(item)
    return PaperMetadata(
        id=item.get("id", ""),
        title=item.get("title") or "Untitled",
        authors=authors,
        year=year,
        venue=source.get("display_name"),
        abstract=abstract,
        source=source_name,
        url=primary_location.get("landing_page_url"),
        download_url=((item.get("open_access") or {}).get("oa_url")),
    )


def _openalex_abstract(item: dict) -> str | None:
    inverted = item.get("abstract_inverted_index")
    if not inverted:
        return None
    positions = []
    for token, idxs in inverted.items():
        for idx in idxs:
            positions.append((idx, token))
    return " ".join(token for _, token in sorted(positions))
