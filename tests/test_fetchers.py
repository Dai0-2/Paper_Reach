from pathlib import Path

from paper_reach.fetchers.utils import (
    FetchContext,
    build_session,
    classify_response,
    discover_pdf_url,
    load_cookies,
    load_headers,
)


class DummyResponse:
    def __init__(self, status_code: int, text: str, content_type: str = "text/html") -> None:
        self.status_code = status_code
        self.text = text
        self.headers = {"content-type": content_type}


def test_discover_pdf_url_from_meta() -> None:
    html = '<meta name="citation_pdf_url" content="/paper.pdf">'
    assert discover_pdf_url("https://example.org/article", html) == "https://example.org/paper.pdf"


def test_classify_cloudflare_challenge() -> None:
    response = DummyResponse(403, "Just a moment... cloudflare challenge")
    status, note = classify_response(response)  # type: ignore[arg-type]
    assert status == "challenge"
    assert "challenge" in note.lower()


def test_load_json_headers_and_cookies(tmp_path: Path) -> None:
    header_path = tmp_path / "headers.json"
    cookie_path = tmp_path / "cookies.json"
    header_path.write_text('{"Authorization": "Bearer demo"}', encoding="utf-8")
    cookie_path.write_text('{"sessionid": "abc"}', encoding="utf-8")
    assert load_headers(header_path)["Authorization"] == "Bearer demo"
    assert load_cookies(cookie_path)["sessionid"] == "abc"
    session = build_session(FetchContext(cookie_file=cookie_path, header_file=header_path))
    assert session.headers["Authorization"] == "Bearer demo"
    assert session.cookies.get("sessionid") == "abc"

