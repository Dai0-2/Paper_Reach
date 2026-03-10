"""Helpers for exporting compact human-readable views of workflow output."""

from __future__ import annotations

from typing import Dict, List, Literal

from .models import ScreeningResult, WorkflowOutput


SummaryFormat = Literal["titles", "brief"]
DecisionFilter = Literal["all", "selected", "ambiguous", "rejected"]


def summarize_workflow_output(
    workflow: WorkflowOutput,
    *,
    format: SummaryFormat = "titles",
    include_rejected: bool = False,
    decision: DecisionFilter = "all",
    top_k: int | None = None,
) -> List[Dict[str, object]]:
    """Return a compact list view of selected workflow results."""
    papers = list(workflow.top_ranked) or (list(workflow.selected) + list(workflow.ambiguous))
    if include_rejected:
        papers.extend(workflow.rejected)
    papers.sort(key=lambda paper: paper.relevance_score, reverse=True)
    if decision != "all":
        papers = [paper for paper in papers if paper.decision == decision]
    if top_k is not None:
        papers = papers[:top_k]
    if format == "titles":
        return [_to_title_item(paper) for paper in papers]
    return [_to_brief_item(paper) for paper in papers]


def _to_title_item(paper: ScreeningResult) -> Dict[str, object]:
    return {
        "title": paper.title,
        "url": paper.url,
    }


def _to_brief_item(paper: ScreeningResult) -> Dict[str, object]:
    findings = paper.abstract_findings or {}
    return {
        "title": paper.title,
        "url": paper.url,
        "year": paper.year,
        "decision": paper.decision,
        "source": paper.source,
        "venue": paper.venue,
        "venue_tier_inferred": paper.venue_tier_inferred,
        "venue_tier_confidence": paper.venue_tier_confidence,
        "study_area": findings.get("study_area", []),
        "dataset": findings.get("dataset", []),
        "task": findings.get("task", []),
        "reasons": paper.reasons,
        "fulltext_status": paper.fulltext_status,
        "pdf_path": paper.pdf_path,
    }
