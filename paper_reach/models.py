"""Core data models used across the Paper-Reach workflow."""

from __future__ import annotations

from typing import Dict, List, Literal, Optional, Tuple

from pydantic import BaseModel, Field, field_validator


Mode = Literal["online", "offline", "auto"]
Decision = Literal["selected", "ambiguous", "rejected"]
Confidence = Literal["low", "medium", "high"]
FulltextStatus = Literal["available", "restricted", "not_found", "not_requested", "local_only"]
Stage = Literal["screen", "review"]


class QueryInput(BaseModel):
    """Structured input for literature screening."""

    topic: str
    keywords: List[str] = Field(default_factory=list)
    inclusion_criteria: List[str] = Field(default_factory=list)
    exclusion_criteria: List[str] = Field(default_factory=list)
    year_range: Tuple[int, int] = (2000, 2100)
    max_results: int = 20
    need_gap_analysis: bool = True
    mode: Mode = "auto"
    local_paths: List[str] = Field(default_factory=list)
    require_fulltext_for_selection: bool = False

    @field_validator("year_range")
    @classmethod
    def validate_year_range(cls, value: Tuple[int, int]) -> Tuple[int, int]:
        """Ensure year range is increasing."""
        start_year, end_year = value
        if start_year > end_year:
            raise ValueError("year_range start must be <= end")
        return value

    @field_validator("max_results")
    @classmethod
    def validate_max_results(cls, value: int) -> int:
        """Ensure max_results is positive."""
        if value <= 0:
            raise ValueError("max_results must be positive")
        return value


class PaperEvidence(BaseModel):
    """Single evidence item supporting or weakening a screening decision."""

    section: str
    excerpt: Optional[str] = None
    note: str
    confidence: Confidence = "low"


class PaperMetadata(BaseModel):
    """Normalized candidate paper representation."""

    id: str
    title: str
    authors: List[str] = Field(default_factory=list)
    year: Optional[int] = None
    venue: Optional[str] = None
    abstract: Optional[str] = None
    abstract_summary: Optional[str] = None
    source: str
    url: Optional[str] = None
    pdf_path: Optional[str] = None
    local_path: Optional[str] = None
    full_text: Optional[str] = None
    download_url: Optional[str] = None
    fulltext_status: FulltextStatus = "not_requested"
    access_notes: Optional[str] = None
    evidence: List[PaperEvidence] = Field(default_factory=list)


class ScreeningResult(BaseModel):
    """Decision-oriented view of a paper after screening or review."""

    id: str
    title: str
    authors: List[str] = Field(default_factory=list)
    year: Optional[int] = None
    venue: Optional[str] = None
    abstract: Optional[str] = None
    abstract_summary: Optional[str] = None
    source: str
    url: Optional[str] = None
    pdf_path: Optional[str] = None
    download_url: Optional[str] = None
    relevance_score: int
    decision: Decision
    reasons: List[str] = Field(default_factory=list)
    evidence: List[PaperEvidence] = Field(default_factory=list)
    need_fulltext: bool = False
    fulltext_status: FulltextStatus = "not_requested"
    access_notes: Optional[str] = None
    review_ready: bool = False
    stage: Stage = "screen"


class RankingResult(BaseModel):
    """Detailed rubric output."""

    topic_relevance: int
    method_match: int
    dataset_match: int
    supervision_match: int
    evidence_confidence: int
    total: int
    decision: Decision
    reasons: List[str] = Field(default_factory=list)
    violated_criteria: List[str] = Field(default_factory=list)
    insufficient_evidence: bool = False


class WorkflowOutput(BaseModel):
    """Top-level output written by the CLI."""

    query_summary: Dict[str, object]
    screening_candidates: List[ScreeningResult] = Field(default_factory=list)
    selected: List[ScreeningResult] = Field(default_factory=list)
    ambiguous: List[ScreeningResult] = Field(default_factory=list)
    rejected: List[ScreeningResult] = Field(default_factory=list)
    gap_analysis: List[str] = Field(default_factory=list)
    recommended_next_queries: List[str] = Field(default_factory=list)
