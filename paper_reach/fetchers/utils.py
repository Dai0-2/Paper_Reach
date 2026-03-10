"""Helpers for authenticated or semi-automated full-text retrieval."""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from http.cookiejar import MozillaCookieJar
from pathlib import Path
from typing import Dict, Iterable
from urllib.parse import urljoin

import requests

from ..config import DEFAULT_CONFIG


@dataclass(slots=True)
class FetchContext:
    """Runtime options for full-text fetching."""

    cookie_file: Path | None = None
    header_file: Path | None = None


def get_openalex_api_key() -> str | None:
    """Return an OpenAlex content API key from the environment if configured."""
    return os.getenv("OPENALEX_API_KEY") or os.getenv("OPENALEX_CONTENT_API_KEY")


def build_session(context: FetchContext | None = None) -> requests.Session:
    """Build a requests session with optional user-supplied auth state."""
    session = requests.Session()
    session.headers.update({"User-Agent": DEFAULT_CONFIG.user_agent})
    if context is None:
        return session
    if context.header_file:
        session.headers.update(load_headers(context.header_file))
    if context.cookie_file:
        for name, value in load_cookies(context.cookie_file).items():
            session.cookies.set(name, value)
    return session


def load_headers(path: Path) -> Dict[str, str]:
    """Load headers from a JSON file."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("header file must contain a JSON object")
    return {str(key): str(value) for key, value in data.items()}


def load_cookies(path: Path) -> Dict[str, str]:
    """Load cookies from JSON or Netscape/Mozilla cookiejar."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except UnicodeDecodeError:
        data = None
    except json.JSONDecodeError:
        data = None

    if isinstance(data, dict):
        return {str(key): str(value) for key, value in data.items()}
    if isinstance(data, list):
        cookies: Dict[str, str] = {}
        for item in data:
            if isinstance(item, dict) and "name" in item and "value" in item:
                cookies[str(item["name"])] = str(item["value"])
        if cookies:
            return cookies

    jar = MozillaCookieJar(str(path))
    jar.load(ignore_expires=True, ignore_discard=True)
    return {cookie.name: cookie.value for cookie in jar}


def classify_response(response: requests.Response) -> tuple[str | None, str | None]:
    """Classify common access failure modes from a response."""
    content_type = (response.headers.get("content-type") or "").lower()
    body = response.text[:4000].lower() if "text" in content_type else ""
    if response.status_code in {401, 407}:
        return "login_required", "Remote site requires authentication."
    if response.status_code == 403:
        if "just a moment" in body or "cf-challenge" in body or "cloudflare" in body:
            return "challenge", "Remote site returned an anti-bot challenge page."
        return "restricted", "Remote site denied automated access."
    if response.status_code >= 400:
        return "restricted", f"Remote site returned HTTP {response.status_code}."
    return None, None


def discover_pdf_url(base_url: str, html: str) -> str | None:
    """Extract a likely PDF URL from an HTML page."""
    patterns = [
        r'<meta[^>]+name=["\']citation_pdf_url["\'][^>]+content=["\']([^"\']+)["\']',
        r'<meta[^>]+property=["\']og:pdf["\'][^>]+content=["\']([^"\']+)["\']',
        r'href=["\']([^"\']+\.pdf(?:\?[^"\']*)?)["\']',
    ]
    for pattern in patterns:
        match = re.search(pattern, html, re.IGNORECASE)
        if match:
            return urljoin(base_url, match.group(1))
    return None


def looks_like_pdf(response: requests.Response) -> bool:
    """Heuristically detect a PDF response."""
    content_type = (response.headers.get("content-type") or "").lower()
    if "application/pdf" in content_type:
        return True
    content = response.content[:5]
    return content == b"%PDF-"


def candidate_urls(download_url: str | None, landing_url: str | None) -> Iterable[str]:
    """Yield candidate URLs to try for full-text retrieval."""
    seen = set()
    for value in [download_url, landing_url]:
        if value and value not in seen:
            seen.add(value)
            yield value
