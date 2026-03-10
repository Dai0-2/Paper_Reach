"""Lightweight arXiv backend."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import List

import requests

from ..config import DEFAULT_CONFIG
from ..models import PaperMetadata, QueryInput
from ..retrieval import build_search_phrases
from .base import SearchChannel


class ArxivChannel(SearchChannel):
    """Query arXiv Atom API with conservative parsing."""

    name = "arxiv"
    supports_online = True
    supports_offline = False
    endpoint = "http://export.arxiv.org/api/query"

    def search(
        self,
        query: QueryInput,
        *,
        high_recall: bool = False,
        retrieval_limit: int | None = None,
    ) -> List[PaperMetadata]:
        if query.mode == "offline":
            return []
        limit = retrieval_limit or (max(query.max_results * 4, 40) if high_recall else max(query.max_results * 2, 20))
        phrases = build_search_phrases(query, high_recall=high_recall)
        results: dict[str, PaperMetadata] = {}
        batch_size = 20 if high_recall else min(query.max_results, 10)

        for phrase in phrases[: (8 if high_recall else 3)]:
            search_query = " AND ".join(f'all:"{term}"' for term in phrase.split()[:8])
            params = {"search_query": search_query, "start": 0, "max_results": batch_size}
            try:
                response = requests.get(
                    self.endpoint,
                    params=params,
                    timeout=DEFAULT_CONFIG.request_timeout_seconds,
                    headers={"User-Agent": DEFAULT_CONFIG.user_agent},
                )
                response.raise_for_status()
            except requests.RequestException:
                continue
            try:
                root = ET.fromstring(response.text)
            except ET.ParseError:
                continue
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            for entry in root.findall("atom:entry", ns):
                title = _text(entry, "atom:title", ns)
                summary = _text(entry, "atom:summary", ns)
                year = None
                published = _text(entry, "atom:published", ns)
                if published:
                    try:
                        year = int(published[:4])
                    except ValueError:
                        year = None
                if year is not None and not (query.year_range[0] <= year <= query.year_range[1]):
                    continue
                authors = [
                    author.findtext("{http://www.w3.org/2005/Atom}name", "")
                    for author in entry.findall("atom:author", ns)
                ]
                paper = PaperMetadata(
                    id=_text(entry, "atom:id", ns) or title or "",
                    title=(title or "Untitled").strip(),
                    authors=[author for author in authors if author],
                    year=year,
                    venue="arXiv",
                    abstract=(summary or "").strip() or None,
                    source=self.name,
                    url=_text(entry, "atom:id", ns),
                )
                results.setdefault(paper.id or paper.title.lower(), paper)
                if len(results) >= limit:
                    return list(results.values())[:limit]
        return list(results.values())[:limit]


def _text(entry: ET.Element, path: str, ns: dict[str, str]) -> str | None:
    node = entry.find(path, ns)
    return node.text if node is not None else None
