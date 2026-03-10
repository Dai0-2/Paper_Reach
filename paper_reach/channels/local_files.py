"""Offline channel for local metadata and document files."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List

from ..models import PaperMetadata, QueryInput
from .base import SearchChannel


class LocalFilesChannel(SearchChannel):
    """Load candidates from local JSON, TXT, and PDF paths."""

    name = "local_files"
    supports_online = False
    supports_offline = True

    def search(
        self,
        query: QueryInput,
        *,
        high_recall: bool = False,
        retrieval_limit: int | None = None,
    ) -> List[PaperMetadata]:
        results: List[PaperMetadata] = []
        limit = retrieval_limit or query.max_results
        for path_str in query.local_paths:
            path = Path(path_str)
            for candidate in _iter_paths(path):
                loaded = self._load_candidate(candidate)
                if loaded is not None:
                    results.append(loaded)
                if len(results) >= limit:
                    return results
        return results

    def _load_candidate(self, path: Path) -> PaperMetadata | None:
        suffix = path.suffix.lower()
        if suffix == ".json":
            data = json.loads(path.read_text(encoding="utf-8"))
            return PaperMetadata(
                id=data.get("id", path.stem),
                title=data.get("title", path.stem),
                authors=data.get("authors", []),
                year=data.get("year"),
                venue=data.get("venue"),
                abstract=data.get("abstract"),
                source=self.name,
                url=data.get("url"),
                pdf_path=data.get("pdf_path"),
                local_path=str(path),
            )
        if suffix == ".txt":
            text = path.read_text(encoding="utf-8", errors="ignore")
            return PaperMetadata(
                id=path.stem,
                title=path.stem.replace("_", " "),
                source=self.name,
                local_path=str(path),
                full_text=text,
            )
        if suffix == ".pdf":
            return PaperMetadata(
                id=path.stem,
                title=path.stem.replace("_", " "),
                source=self.name,
                pdf_path=str(path),
                local_path=str(path),
            )
        return None


def _iter_paths(path: Path) -> Iterable[Path]:
    if path.is_file():
        yield path
        return
    if path.is_dir():
        for candidate in sorted(path.rglob("*")):
            if candidate.is_file():
                yield candidate
