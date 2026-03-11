"""Two-stage literature screening workflow."""

from __future__ import annotations

from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Iterable, List, Sequence

from .channels.arxiv import ArxivChannel
from .channels.base import SearchChannel
from .channels.local_files import LocalFilesChannel
from .channels.mock_source import MockSourceChannel
from .channels.openalex import OpenAlexChannel
from .config import DEFAULT_CONFIG
from .fetchers.open_access import OpenAccessFetcher
from .fetchers.utils import FetchContext
from .models import PaperEvidence, PaperMetadata, QueryInput, ScreeningResult, WorkflowOutput
from .parsers.pymupdf_parser import PyMuPDFParser
from .parsers.simple_text_parser import SimpleTextParser
from .retrieval import (
    build_search_plan,
    evaluate_criteria_match,
    extract_abstract_findings,
    screen_dimension_scores,
)
from .ranking.rubric import score_paper


def available_channels() -> dict[str, SearchChannel]:
    """Return built-in channels."""
    return {
        "openalex": OpenAlexChannel(),
        "arxiv": ArxivChannel(),
        "local_files": LocalFilesChannel(),
        "mock_source": MockSourceChannel(),
    }


def run_workflow(
    query: QueryInput,
    channel_names: Sequence[str] | None = None,
    *,
    fetch_fulltext: bool = True,
    download_dir: Path | None = None,
    high_recall: bool = False,
    retrieval_limit: int | None = None,
    fetch_context: FetchContext | None = None,
    workers: int | None = None,
) -> WorkflowOutput:
    """Run screen, optional fetch, and review as a single command."""
    screen_output, screened_papers = screen_workflow(
        query,
        channel_names=channel_names,
        high_recall=high_recall,
        retrieval_limit=retrieval_limit,
        workers=workers,
    )
    review_input = screened_papers
    if fetch_fulltext:
        review_input = fetch_fulltexts(
            screened_papers,
            download_dir=download_dir,
            context=fetch_context,
            workers=workers,
        )
    return review_workflow(
        query,
        screen_output=screen_output,
        papers=review_input,
        workers=workers,
    )


def screen_workflow(
    query: QueryInput,
    channel_names: Sequence[str] | None = None,
    *,
    high_recall: bool = False,
    retrieval_limit: int | None = None,
    workers: int | None = None,
) -> tuple[WorkflowOutput, List[PaperMetadata]]:
    """Run initial abstract-level screening and return review candidates."""
    channels_map = available_channels()
    names = list(channel_names or _default_channel_names(query))
    candidates = _collect_candidates(
        query,
        [channels_map[name] for name in names if name in channels_map],
        high_recall=high_recall,
        retrieval_limit=retrieval_limit,
    )
    hydrated = [_attach_local_text(candidate) for candidate in candidates]

    screening_candidates: List[ScreeningResult] = []
    rejected: List[ScreeningResult] = []
    review_ready: List[PaperMetadata] = []

    for paper, result in _screen_candidates(hydrated, query, workers=workers):
        if result.decision == "rejected":
            rejected.append(result)
        else:
            screening_candidates.append(result)
            review_ready.append(paper)
    screening_candidates.sort(key=lambda item: item.relevance_score, reverse=True)
    rejected.sort(key=lambda item: item.relevance_score, reverse=True)
    review_ready_ids = {item.id for item in screening_candidates[: query.max_results]}
    review_ready = [paper for paper in review_ready if paper.id in review_ready_ids]

    output = WorkflowOutput(
        query_summary={
            "topic": query.topic,
            "mode": query.mode,
            "channels_used": names,
            "search_plan": build_search_plan(query, high_recall=high_recall),
            "total_candidates": len(candidates),
            "high_recall": high_recall,
            "retrieval_limit": retrieval_limit or len(candidates),
            "screening_candidates_count": len(screening_candidates),
            "review_queue_count": len(review_ready),
            "rejected_at_screening_count": len(rejected),
        },
        screening_candidates=screening_candidates,
        top_ranked=[],
        rejected=rejected,
        gap_analysis=[],
        recommended_next_queries=[],
    )
    return output, review_ready


def fetch_fulltexts(
    papers: Sequence[PaperMetadata],
    *,
    download_dir: Path | None = None,
    context: FetchContext | None = None,
    workers: int | None = None,
) -> List[PaperMetadata]:
    """Attempt to fetch full text for screened papers."""
    fetcher = OpenAccessFetcher()
    worker_count = _normalized_workers(workers, len(papers))
    if worker_count == 1:
        return [
            _fetch_single_paper(fetcher, paper, download_dir=download_dir, context=context)
            for paper in papers
        ]
    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        return list(
            executor.map(
                lambda item: _fetch_single_paper(
                    fetcher,
                    item,
                    download_dir=download_dir,
                    context=context,
                ),
                papers,
            )
        )


def review_workflow(
    query: QueryInput,
    *,
    screen_output: WorkflowOutput,
    papers: Sequence[PaperMetadata],
    workers: int | None = None,
) -> WorkflowOutput:
    """Run final review and ranking for screened papers."""
    selected: List[ScreeningResult] = []
    ambiguous: List[ScreeningResult] = []
    review_rejected: List[ScreeningResult] = []
    reviewed_results: List[ScreeningResult] = []

    for result in _review_candidates(query, papers, workers=workers):
        reviewed_results.append(result)
        if result.decision == "selected":
            selected.append(result)
        elif result.decision == "ambiguous":
            ambiguous.append(result)
        else:
            review_rejected.append(result)

    rejected = [*screen_output.rejected, *review_rejected]
    downloaded_reviewed = [
        result
        for result in reviewed_results
        if result.fulltext_status in {"available", "local_only"} or result.pdf_path
    ]
    top_ranked = _build_adaptive_shortlist(reviewed_results, min_items=10, max_items=20)
    query_summary = {
        "topic": query.topic,
        "mode": query.mode,
        "channels_used": screen_output.query_summary.get("channels_used", []),
        "search_plan": screen_output.query_summary.get("search_plan", {}),
        "total_candidates": screen_output.query_summary.get("total_candidates", 0),
        "screening_candidates_count": len(screen_output.screening_candidates),
        "review_attempted_count": len(papers),
        "downloaded_fulltext_count": len(downloaded_reviewed),
        "top_ranked_count": len(top_ranked),
        "selected_count": len(selected),
        "ambiguous_count": len(ambiguous),
        "rejected_count": len(rejected),
    }
    gap_analysis = _gap_analysis(query, selected, ambiguous, rejected)
    recommended_next_queries = _recommended_next_queries(query, ambiguous, rejected)
    return WorkflowOutput(
        query_summary=query_summary,
        screening_candidates=screen_output.screening_candidates,
        top_ranked=top_ranked,
        selected=selected,
        ambiguous=ambiguous,
        rejected=rejected,
        gap_analysis=gap_analysis if query.need_gap_analysis else [],
        recommended_next_queries=recommended_next_queries,
    )


def _build_adaptive_shortlist(
    reviewed_results: Sequence[ScreeningResult],
    *,
    min_items: int = 10,
    max_items: int = 20,
) -> List[ScreeningResult]:
    strict = [
        item for item in reviewed_results
        if item.hard_filter_passed and item.venue_tier_inferred != "excluded"
    ]
    near_miss = [
        item for item in reviewed_results
        if item.venue_tier_inferred != "excluded"
        and not item.hard_filter_passed
        and len(item.violated_criteria) <= 1
        and item.relevance_score >= 5
    ]
    high_score = [
        item for item in reviewed_results
        if item.venue_tier_inferred != "excluded"
        and item.relevance_score >= 4
    ]

    ordered: List[ScreeningResult] = []
    seen: set[str] = set()

    def add_pool(pool: Sequence[ScreeningResult], tier: str) -> None:
        for item in sorted(
            pool,
            key=lambda result: (
                result.relevance_score,
                1 if (result.fulltext_status in {"available", "local_only"} or result.pdf_path) else 0,
                -len(result.violated_criteria),
            ),
            reverse=True,
        ):
            if item.id in seen:
                continue
            seen.add(item.id)
            ordered.append(
                item.model_copy(
                    update={
                        "shortlist_tier": tier,
                        "shortlist_reason": _shortlist_reason(item, tier),
                    }
                )
            )
            if len(ordered) >= max_items:
                return

    add_pool(strict, "strict_match")
    if len(ordered) < min_items:
        add_pool(near_miss, "near_miss")
    if len(ordered) < min_items:
        add_pool(high_score, "score_fill")

    return ordered[:max_items]


def _shortlist_reason(item: ScreeningResult, tier: str) -> str:
    if tier == "strict_match":
        return "Passed hard filters and ranked highly by the composite score."
    if tier == "near_miss":
        if item.violated_criteria:
            return f"Included as a near miss with one recoverable gap: {item.violated_criteria[0]}."
        return "Included as a near miss because the paper scored well despite a minor gap."
    if item.fulltext_status in {"available", "local_only"} or item.pdf_path:
        return "Included to fill the shortlist based on high score and available full text."
    return "Included to fill the shortlist based on high relevance score."


def _default_channel_names(query: QueryInput) -> List[str]:
    if query.mode == "offline":
        return ["local_files"]
    if query.mode == "online":
        return ["openalex", "arxiv"]
    return ["openalex", "arxiv", "local_files"]


def _collect_candidates(
    query: QueryInput,
    channels: Iterable[SearchChannel],
    *,
    high_recall: bool = False,
    retrieval_limit: int | None = None,
) -> List[PaperMetadata]:
    deduped: dict[str, PaperMetadata] = {}
    limit = retrieval_limit or (max(query.max_results * 8, 100) if high_recall else query.max_results)
    for channel in channels:
        for paper in channel.search(query, high_recall=high_recall, retrieval_limit=limit):
            if paper.year is not None and not (query.year_range[0] <= paper.year <= query.year_range[1]):
                continue
            key = _dedupe_key(paper)
            deduped.setdefault(key, paper)
            if len(deduped) >= limit:
                break
    return list(deduped.values())[:limit]


def _dedupe_key(paper: PaperMetadata) -> str:
    return paper.id or paper.title.strip().lower()


def _attach_local_text(paper: PaperMetadata) -> PaperMetadata:
    if paper.full_text or not paper.local_path:
        return paper
    path = Path(paper.local_path)
    text = _parse_local_path(path)
    if text:
        paper.full_text = text
        paper.fulltext_status = "available"
        if not paper.abstract:
            paper.abstract = text[:500]
    return paper


def _parse_local_path(path: Path) -> str | None:
    parsers = [PyMuPDFParser(), SimpleTextParser()]
    for parser in parsers:
        if parser.can_parse(path):
            return parser.parse(path)
    return None


def _screen_candidates(
    papers: Sequence[PaperMetadata],
    query: QueryInput,
    *,
    workers: int | None = None,
) -> List[tuple[PaperMetadata, ScreeningResult]]:
    worker_count = _normalized_workers(workers, len(papers))
    if worker_count == 1:
        return [_screen_single_paper(paper, query) for paper in papers]
    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        return list(executor.map(lambda item: _screen_single_paper(item, query), papers))


def _screen_single_paper(
    paper: PaperMetadata,
    query: QueryInput,
) -> tuple[PaperMetadata, ScreeningResult]:
    enriched = _enrich_paper(paper)
    return enriched, _screen_paper(enriched, query)


def _fetch_single_paper(
    fetcher: OpenAccessFetcher,
    paper: PaperMetadata,
    *,
    download_dir: Path | None = None,
    context: FetchContext | None = None,
) -> PaperMetadata:
    if paper.local_path or paper.pdf_path or paper.full_text:
        if paper.full_text:
            paper.fulltext_status = "available"
        elif paper.pdf_path:
            paper.fulltext_status = "local_only"
        return _attach_local_text(paper)
    return fetcher.fetch(paper, download_dir=download_dir, context=context)


def _review_candidates(
    query: QueryInput,
    papers: Sequence[PaperMetadata],
    *,
    workers: int | None = None,
) -> List[ScreeningResult]:
    worker_count = _normalized_workers(workers, len(papers))
    if worker_count == 1:
        return [_review_single_paper(query, paper) for paper in papers]
    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        return list(executor.map(lambda item: _review_single_paper(query, item), papers))


def _review_single_paper(query: QueryInput, paper: PaperMetadata) -> ScreeningResult:
    paper = _attach_local_text(paper)
    paper = _enrich_paper(paper)
    ranking = score_paper(paper, query)
    need_fulltext = not bool(paper.full_text) and ranking.decision != "rejected"
    return ScreeningResult(
        id=paper.id,
        title=paper.title,
        authors=paper.authors,
        year=paper.year,
        venue=paper.venue,
        abstract=paper.abstract,
        abstract_summary=paper.abstract_summary or _summarize_abstract(paper.abstract),
        source=paper.source,
        url=paper.url,
        pdf_path=paper.pdf_path,
        download_url=paper.download_url,
        relevance_score=ranking.total,
        decision=ranking.decision,
        reasons=ranking.reasons,
        evidence=paper.evidence,
        screening_dimensions={},
        abstract_findings={},
        need_fulltext=need_fulltext,
        fulltext_status=paper.fulltext_status,
        access_notes=paper.access_notes,
        review_ready=True,
        stage="review",
        venue_tier_inferred=ranking.venue_tier_inferred,
        venue_tier_confidence=ranking.venue_tier_confidence,
        violated_criteria=ranking.violated_criteria,
        hard_filter_passed=not bool(ranking.violated_criteria),
    )


def _normalized_workers(workers: int | None, item_count: int) -> int:
    if item_count <= 1:
        return 1
    base = workers or DEFAULT_CONFIG.default_workers
    return max(1, min(base, item_count))


def _enrich_paper(paper: PaperMetadata) -> PaperMetadata:
    paper.abstract_summary = paper.abstract_summary or _summarize_abstract(paper.abstract)
    paper.evidence = _extract_evidence(paper)
    if paper.local_path and paper.fulltext_status == "not_requested":
        paper.fulltext_status = "local_only"
    return paper


def _screen_paper(paper: PaperMetadata, query: QueryInput) -> ScreeningResult:
    screening_text = paper.abstract or (paper.full_text[:1200] if paper.full_text else "")
    combined = " ".join(part.lower() for part in [paper.title, screening_text] if part)
    title_only = not screening_text
    exclusion_hit = _screen_exclusions(combined, query.exclusion_criteria)
    dimension_scores = screen_dimension_scores(combined, query)
    findings = extract_abstract_findings(screening_text or paper.title, query)
    criteria_match = evaluate_criteria_match(screening_text or paper.title, query)
    findings.update(
        {
            "matched_must_include": criteria_match["matched_must_include"],
            "missing_must_include": criteria_match["missing_must_include"],
            "matched_soft_include": criteria_match["matched_soft_include"],
        }
    )
    relevance_hits = sum(dimension_scores.values())
    if exclusion_hit or criteria_match["violated_exclude"]:
        decision = "rejected"
        violated = exclusion_hit or criteria_match["violated_exclude"][0]
        reasons = [f"Screening rejected the paper because it matched exclusion criterion: {violated}."]
    elif title_only and relevance_hits:
        decision = "ambiguous"
        reasons = ["Title suggests relevance, but abstract or readable local text is missing so the paper must not be selected yet."]
    elif criteria_match["missing_must_include"] and _is_high_priority_screen_match(dimension_scores):
        decision = "ambiguous"
        reasons = [
            _screen_reason(dimension_scores, strong=False),
            f"Abstract is still missing hard criteria: {', '.join(criteria_match['missing_must_include'][:2])}.",
        ]
    elif _is_high_priority_screen_match(dimension_scores):
        decision = "ambiguous"
        reasons = [_screen_reason(dimension_scores, strong=True)]
    elif _is_partial_screen_match(dimension_scores):
        decision = "ambiguous"
        reasons = [_screen_reason(dimension_scores, strong=False)]
    else:
        decision = "rejected"
        reasons = ["Abstract-level screening did not provide enough support for the inclusion criteria."]
    need_fulltext = decision != "rejected"
    return ScreeningResult(
        id=paper.id,
        title=paper.title,
        authors=paper.authors,
        year=paper.year,
        venue=paper.venue,
        abstract=paper.abstract or _summarize_abstract(screening_text),
        abstract_summary=paper.abstract_summary or _summarize_abstract(screening_text),
        source=paper.source,
        url=paper.url,
        pdf_path=paper.pdf_path,
        download_url=paper.download_url,
        relevance_score=min(relevance_hits + (0 if title_only else 1), 12),
        decision=decision,
        reasons=reasons,
        evidence=paper.evidence,
        screening_dimensions=dimension_scores,
        abstract_findings=findings,
        need_fulltext=need_fulltext,
        fulltext_status=paper.fulltext_status,
        access_notes=paper.access_notes,
        review_ready=need_fulltext,
        stage="screen",
    )
def _is_high_priority_screen_match(scores: dict[str, int]) -> bool:
    return (
        scores["population"] >= 1
        and scores["exposure"] >= 1
        and (scores["hazard"] >= 1 or scores["geography"] >= 1)
    ) or scores["keyword"] >= 3


def _is_partial_screen_match(scores: dict[str, int]) -> bool:
    return (
        scores["population"] >= 1 and scores["exposure"] >= 1
    ) or (
        scores["hazard"] >= 1 and scores["geography"] >= 1
    ) or scores["keyword"] >= 2


def _screen_reason(scores: dict[str, int], *, strong: bool) -> str:
    matched = [name for name, value in scores.items() if value > 0]
    prefix = (
        "Abstract-level screening shows strong support across"
        if strong
        else "Only partial abstract-level support is available across"
    )
    label_map = {
        "keyword": "query keywords",
        "geography": "study-area geography",
        "population": "population terms",
        "exposure": "exposure or risk terms",
        "hazard": "hazard terms",
    }
    readable = ", ".join(label_map[item] for item in matched) if matched else "few dimensions"
    suffix = "and the paper should move to full-text review." if strong else "so keep it for conservative review."
    return f"{prefix} {readable}, {suffix}"


def _screen_exclusions(text: str, exclusion_criteria: Sequence[str]) -> str | None:
    for criterion in exclusion_criteria:
        criterion_l = criterion.lower()
        if "behavior prediction" in criterion_l and "behavior prediction" in text:
            return criterion
        if "generic saliency" in criterion_l and "generic saliency" in text:
            return criterion
    return None


def _summarize_abstract(abstract: str | None) -> str | None:
    if not abstract:
        return None
    compact = " ".join(abstract.split())
    return compact[:157] + "..." if len(compact) > 160 else compact


def _extract_evidence(paper: PaperMetadata) -> List[PaperEvidence]:
    evidence: List[PaperEvidence] = []
    if paper.abstract:
        evidence.append(
            PaperEvidence(
                section="abstract",
                excerpt=_best_excerpt(paper.abstract),
                note=_abstract_note(paper.abstract),
                confidence="medium" if paper.full_text else "low",
            )
        )
    if paper.full_text:
        evidence.append(
            PaperEvidence(
                section="full_text",
                excerpt=_best_excerpt(paper.full_text),
                note="Full text is available for detailed review.",
                confidence="high",
            )
        )
    if not evidence:
        evidence.append(
            PaperEvidence(
                section="metadata",
                excerpt=paper.title,
                note="Only metadata is available; evidence remains weak.",
                confidence="low",
            )
        )
    return evidence


def _best_excerpt(text: str) -> str:
    normalized = " ".join(text.split())
    return normalized[:197] + "..." if len(normalized) > 200 else normalized


def _abstract_note(text: str) -> str:
    lowered = text.lower()
    findings = []
    if any(token in lowered for token in ["gaze", "attention map", "attention supervision"]):
        findings.append("Abstract contains attention supervision cues.")
    if "bdd-100k" in lowered:
        findings.append("Abstract mentions BDD-100K.")
    if any(token in lowered for token in ["real traffic", "driving videos", "real scenes"]):
        findings.append("Abstract suggests real driving data.")
    return " ".join(findings) or "Abstract provides coarse evidence only."


def _gap_analysis(
    query: QueryInput,
    selected: List[ScreeningResult],
    ambiguous: List[ScreeningResult],
    rejected: List[ScreeningResult],
) -> List[str]:
    notes: List[str] = []
    if ambiguous:
        restricted = sum(1 for paper in ambiguous if paper.fulltext_status in {"restricted", "not_found"})
        notes.append(f"{len(ambiguous)} papers remain ambiguous and would benefit from stronger full-text evidence.")
        if restricted:
            notes.append(f"{restricted} ambiguous papers could not be fully reviewed because full text was unavailable.")
    if not selected:
        notes.append("No paper reached a strong selected status under the current conservative rubric.")
    dataset_mentions = Counter(
        "bdd-100k" in ((paper.abstract or "") + " " + (paper.abstract_summary or "")).lower()
        for paper in selected + ambiguous
    )
    if dataset_mentions.get(True, 0) < max(1, len(selected) // 2):
        notes.append("Direct dataset matches are sparse; broaden dataset synonyms or related benchmarks.")
    if rejected:
        notes.append("Rejected items suggest exclusion criteria are filtering out behavior-prediction papers.")
    if query.require_fulltext_for_selection:
        notes.append("Full-text gating is enabled, so abstract-only candidates will remain ambiguous.")
    return notes


def _recommended_next_queries(
    query: QueryInput,
    ambiguous: List[ScreeningResult],
    rejected: List[ScreeningResult],
) -> List[str]:
    suggestions = [
        " ".join([query.topic, "gaze supervision"]).strip(),
        " ".join([query.topic, "BDD-100K attention map"]).strip(),
    ]
    if ambiguous:
        suggestions.append("driving attention prediction full text gaze supervision dataset")
    if any("behavior prediction" in " ".join(item.reasons).lower() for item in rejected):
        suggestions.append("driving attention prediction not behavior prediction")
    seen = set()
    ordered = []
    for item in suggestions:
        if item and item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered[:5]
