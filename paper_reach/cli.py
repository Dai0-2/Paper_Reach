"""Typer CLI for Paper-Reach."""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

import typer

from . import __version__
from .config import DEFAULT_CONFIG
from .fetchers.utils import FetchContext
from .io_utils import load_query, print_json, write_json
from .models import QueryInput
from .parsers.pymupdf_parser import fitz
from .workflow import (
    available_channels,
    fetch_fulltexts,
    review_workflow,
    run_workflow,
    screen_workflow,
)

app = typer.Typer(help="Give your AI agent a rigorous literature review workflow.")


@app.command("run")
def run_command(
    input: Path = typer.Option(..., "--input", exists=True, readable=True, help="Path to query JSON."),
    output: Path = typer.Option(..., "--output", help="Path to write result JSON."),
    mode: Optional[str] = typer.Option(None, "--mode", help="Override query mode."),
    channel: Optional[List[str]] = typer.Option(None, "--channel", help="Explicit channel names."),
    local_path: Optional[List[Path]] = typer.Option(None, "--local-path", help="Additional local paths."),
    no_fetch_fulltext: bool = typer.Option(False, "--no-fetch-fulltext", help="Skip the fetch stage."),
    download_dir: Optional[Path] = typer.Option(None, "--download-dir", help="Directory for downloaded full texts."),
    cookie_file: Optional[Path] = typer.Option(None, "--cookie-file", exists=True, readable=True, help="Cookie file for user-authorized sessions."),
    header_file: Optional[Path] = typer.Option(None, "--header-file", exists=True, readable=True, help="JSON header file for user-authorized sessions."),
    high_recall: bool = typer.Option(False, "--high-recall", help="Use broader multi-query retrieval."),
    retrieval_limit: Optional[int] = typer.Option(None, "--retrieval-limit", help="Maximum initial retrieval size."),
) -> None:
    """Run screen + optional fetch + review."""
    query = _load_query_with_overrides(input, mode, local_path)
    result = run_workflow(
        query,
        channel_names=channel,
        fetch_fulltext=not no_fetch_fulltext,
        download_dir=download_dir,
        high_recall=high_recall,
        retrieval_limit=retrieval_limit,
        fetch_context=_fetch_context(cookie_file, header_file),
    )
    write_json(output, result.model_dump(mode="json"))
    typer.echo(f"Wrote result to {output}")


@app.command("screen")
def screen_command(
    input: Path = typer.Option(..., "--input", exists=True, readable=True, help="Path to query JSON."),
    output: Path = typer.Option(..., "--output", help="Path to write result JSON."),
    mode: Optional[str] = typer.Option(None, "--mode", help="Override query mode."),
    channel: Optional[List[str]] = typer.Option(None, "--channel", help="Explicit channel names."),
    local_path: Optional[List[Path]] = typer.Option(None, "--local-path", help="Additional local paths."),
    high_recall: bool = typer.Option(False, "--high-recall", help="Use broader multi-query retrieval."),
    retrieval_limit: Optional[int] = typer.Option(None, "--retrieval-limit", help="Maximum initial retrieval size."),
) -> None:
    """Run initial abstract-level screening only."""
    query = _load_query_with_overrides(input, mode, local_path)
    result, _ = screen_workflow(
        query,
        channel_names=channel,
        high_recall=high_recall,
        retrieval_limit=retrieval_limit,
    )
    write_json(output, result.model_dump(mode="json"))
    typer.echo(f"Wrote screening result to {output}")


@app.command("fetch-fulltext")
def fetch_fulltext_command(
    input: Path = typer.Option(..., "--input", exists=True, readable=True, help="Path to query JSON."),
    output: Path = typer.Option(..., "--output", help="Path to write review result JSON."),
    mode: Optional[str] = typer.Option(None, "--mode", help="Override query mode."),
    channel: Optional[List[str]] = typer.Option(None, "--channel", help="Explicit channel names."),
    local_path: Optional[List[Path]] = typer.Option(None, "--local-path", help="Additional local paths."),
    download_dir: Optional[Path] = typer.Option(None, "--download-dir", help="Directory for downloaded full texts."),
    cookie_file: Optional[Path] = typer.Option(None, "--cookie-file", exists=True, readable=True, help="Cookie file for user-authorized sessions."),
    header_file: Optional[Path] = typer.Option(None, "--header-file", exists=True, readable=True, help="JSON header file for user-authorized sessions."),
    high_recall: bool = typer.Option(False, "--high-recall", help="Use broader multi-query retrieval."),
    retrieval_limit: Optional[int] = typer.Option(None, "--retrieval-limit", help="Maximum initial retrieval size."),
) -> None:
    """Run screen, attempt full-text fetch, then emit review result."""
    query = _load_query_with_overrides(input, mode, local_path)
    screen_output, papers = screen_workflow(
        query,
        channel_names=channel,
        high_recall=high_recall,
        retrieval_limit=retrieval_limit,
    )
    fetched = fetch_fulltexts(
        papers,
        download_dir=download_dir,
        context=_fetch_context(cookie_file, header_file),
    )
    result = review_workflow(query, screen_output=screen_output, papers=fetched)
    write_json(output, result.model_dump(mode="json"))
    typer.echo(f"Wrote fetched review result to {output}")


@app.command("review")
def review_command(
    input: Path = typer.Option(..., "--input", exists=True, readable=True, help="Path to query JSON."),
    output: Path = typer.Option(..., "--output", help="Path to write result JSON."),
    mode: Optional[str] = typer.Option(None, "--mode", help="Override query mode."),
    channel: Optional[List[str]] = typer.Option(None, "--channel", help="Explicit channel names."),
    local_path: Optional[List[Path]] = typer.Option(None, "--local-path", help="Additional local paths."),
    high_recall: bool = typer.Option(False, "--high-recall", help="Use broader multi-query retrieval."),
    retrieval_limit: Optional[int] = typer.Option(None, "--retrieval-limit", help="Maximum initial retrieval size."),
) -> None:
    """Run screen and review using only already-available local full text."""
    query = _load_query_with_overrides(input, mode, local_path)
    screen_output, papers = screen_workflow(
        query,
        channel_names=channel,
        high_recall=high_recall,
        retrieval_limit=retrieval_limit,
    )
    result = review_workflow(query, screen_output=screen_output, papers=papers)
    write_json(output, result.model_dump(mode="json"))
    typer.echo(f"Wrote review result to {output}")


@app.command("doctor")
def doctor_command() -> None:
    """Print available capabilities."""
    payload = {
        "version": __version__,
        "channels": sorted(available_channels().keys()),
        "pdf_parser_available": fitz is not None,
        "authenticated_fetch_supported": True,
        "default_config": DEFAULT_CONFIG.as_dict(),
        "workflow_stages": ["screen", "fetch-fulltext", "review", "run"],
    }
    print_json(payload)


@app.command("example-query")
def example_query_command() -> None:
    """Print a sample query JSON."""
    query = QueryInput(
        topic="Driving attention prediction with BDD-100K",
        keywords=["BDD-100K", "driving attention", "gaze prediction", "attention map"],
        inclusion_criteria=[
            "uses attention map or gaze supervision",
            "preferably real driving scene",
            "preferably after 2021",
        ],
        exclusion_criteria=[
            "generic saliency detection only",
            "no explicit attention supervision",
            "pure behavior prediction",
        ],
        year_range=(2021, 2026),
        max_results=10,
        need_gap_analysis=True,
        mode="auto",
        local_paths=[],
        require_fulltext_for_selection=False,
    )
    print_json(query.model_dump(mode="json"))


@app.command("version")
def version_command() -> None:
    """Print package version."""
    typer.echo(__version__)


def _load_query_with_overrides(
    input_path: Path,
    mode: Optional[str],
    local_path: Optional[List[Path]],
) -> QueryInput:
    query = load_query(input_path)
    if mode is not None:
        query = query.model_copy(update={"mode": mode})
    if local_path:
        merged_paths = list(query.local_paths) + [str(item) for item in local_path]
        query = query.model_copy(update={"local_paths": merged_paths})
    return query


def _fetch_context(cookie_file: Optional[Path], header_file: Optional[Path]) -> FetchContext | None:
    if cookie_file is None and header_file is None:
        return None
    return FetchContext(cookie_file=cookie_file, header_file=header_file)


if __name__ == "__main__":
    app()
