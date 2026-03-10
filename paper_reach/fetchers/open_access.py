"""Conservative open-access full-text fetcher."""

from __future__ import annotations

from pathlib import Path

import requests

from ..config import DEFAULT_CONFIG
from ..models import PaperMetadata
from .base import FulltextFetcher


class OpenAccessFetcher(FulltextFetcher):
    """Attempt to download openly accessible PDFs when a direct link is available."""

    name = "open_access"

    def fetch(self, paper: PaperMetadata, download_dir: Path | None = None) -> PaperMetadata:
        if paper.full_text or paper.pdf_path:
            paper.fulltext_status = "available" if paper.full_text else "local_only"
            return paper
        if not paper.download_url:
            paper.fulltext_status = "not_found"
            paper.access_notes = paper.access_notes or "No direct download URL is available."
            return paper
        if not download_dir:
            paper.fulltext_status = "not_found"
            paper.access_notes = "Download URL exists, but no download directory was provided."
            return paper
        try:
            response = requests.get(
                paper.download_url,
                timeout=DEFAULT_CONFIG.request_timeout_seconds,
                headers={"User-Agent": DEFAULT_CONFIG.user_agent},
            )
            response.raise_for_status()
        except requests.RequestException:
            paper.fulltext_status = "restricted"
            paper.access_notes = "Download failed or remote access is restricted."
            return paper
        download_dir.mkdir(parents=True, exist_ok=True)
        target = download_dir / f"{paper.id.replace('/', '_')}.pdf"
        target.write_bytes(response.content)
        paper.pdf_path = str(target)
        paper.local_path = str(target)
        paper.fulltext_status = "available"
        paper.access_notes = "Downloaded via open-access URL."
        return paper
