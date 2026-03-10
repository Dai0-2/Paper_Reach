"""Conservative open-access full-text fetcher."""

from __future__ import annotations

from pathlib import Path

from ..config import DEFAULT_CONFIG
from ..models import PaperMetadata
from .base import FulltextFetcher
from .utils import (
    FetchContext,
    build_session,
    candidate_urls,
    classify_response,
    discover_pdf_url,
    looks_like_pdf,
)


class OpenAccessFetcher(FulltextFetcher):
    """Attempt to download openly accessible PDFs when a direct link is available."""

    name = "open_access"

    def fetch(
        self,
        paper: PaperMetadata,
        download_dir: Path | None = None,
        context: FetchContext | None = None,
    ) -> PaperMetadata:
        if paper.full_text or paper.pdf_path:
            paper.fulltext_status = "available" if paper.full_text else "local_only"
            return paper
        if not download_dir:
            paper.fulltext_status = "not_found"
            paper.access_notes = "A download directory is required for automatic full-text retrieval."
            return paper
        session = build_session(context)
        for url in candidate_urls(paper.download_url, paper.url):
            outcome = _attempt_url(session, url, paper, download_dir)
            if outcome:
                return paper
        if not paper.download_url and not paper.url:
            paper.fulltext_status = "not_found"
            paper.access_notes = paper.access_notes or "No download URL or landing page URL is available."
            return paper
        if paper.fulltext_status == "not_requested":
            paper.fulltext_status = "not_found"
            paper.access_notes = "No PDF link could be discovered from the available URLs."
        return paper


def _attempt_url(session, url: str, paper: PaperMetadata, download_dir: Path) -> bool:
    try:
        response = session.get(
            url,
            timeout=DEFAULT_CONFIG.request_timeout_seconds,
            allow_redirects=True,
        )
    except Exception:
        paper.fulltext_status = "restricted"
        paper.access_notes = "Download request failed or remote access is restricted."
        return False

    status, note = classify_response(response)
    if status is not None:
        paper.fulltext_status = status  # type: ignore[assignment]
        paper.access_notes = note
        return False

    if looks_like_pdf(response):
        _write_pdf(download_dir, paper, response.content)
        paper.access_notes = "Downloaded from a discovered PDF URL."
        return True

    content_type = (response.headers.get("content-type") or "").lower()
    if "html" in content_type:
        html = response.text
        pdf_url = discover_pdf_url(response.url, html)
        if pdf_url and pdf_url != url:
            paper.download_url = pdf_url
            return _attempt_url(session, pdf_url, paper, download_dir)
        if "login" in html[:4000].lower() or "sign in" in html[:4000].lower():
            paper.fulltext_status = "login_required"
            paper.access_notes = "Landing page appears to require a logged-in session."
            return False
    paper.fulltext_status = "not_found"
    paper.access_notes = "The remote page did not expose a downloadable PDF."
    return False


def _write_pdf(download_dir: Path, paper: PaperMetadata, content: bytes) -> None:
    download_dir.mkdir(parents=True, exist_ok=True)
    target = download_dir / f"{paper.id.replace('/', '_')}.pdf"
    target.write_bytes(content)
    paper.pdf_path = str(target)
    paper.local_path = str(target)
    paper.fulltext_status = "available"
