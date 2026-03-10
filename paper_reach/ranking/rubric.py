"""Conservative literature-screening rubric."""

from __future__ import annotations

from typing import List

from ..models import PaperMetadata, QueryInput, RankingResult


def score_paper(paper: PaperMetadata, query: QueryInput) -> RankingResult:
    """Score a paper conservatively against screening criteria."""
    title = paper.title.lower()
    abstract = (paper.abstract or "").lower()
    full_text = (paper.full_text or "").lower()
    combined = " ".join(part for part in [title, abstract, full_text] if part)
    evidence_source = full_text or abstract or title

    violated = _violated_criteria(combined, query.exclusion_criteria)
    insufficient_evidence = not bool(paper.abstract or paper.full_text)

    topic_relevance = _score_topic(combined, query.keywords, query.topic)
    method_match = _score_method(combined)
    dataset_match = _score_dataset(combined)
    supervision_match = _score_supervision(combined)
    evidence_confidence = _score_evidence_confidence(paper, evidence_source)
    evidence_gap = not paper.full_text and topic_relevance >= 2 and supervision_match == 0

    total = (
        topic_relevance
        + method_match
        + dataset_match
        + supervision_match
        + evidence_confidence
    )
    reasons: List[str] = []

    if topic_relevance >= 2:
        reasons.append("Topic relevance is supported by title or abstract cues.")
    if method_match >= 2:
        reasons.append("Method or task framing appears aligned with the query.")
    if dataset_match >= 1:
        reasons.append("Dataset evidence mentions a relevant driving dataset or real-scene setting.")
    if supervision_match >= 1:
        reasons.append("Supervision evidence suggests attention maps, gaze, or explicit annotation.")
    if insufficient_evidence:
        reasons.append("Evidence is limited because abstract and full text are missing.")
    if paper.full_text:
        reasons.append("Full-text evidence is available, improving confidence.")
    elif paper.abstract:
        reasons.append("Only abstract-level evidence is available.")
    if violated:
        reasons.append("One or more exclusion criteria appear to be triggered.")

    decision = _decide(
        total=total,
        violated=violated,
        insufficient_evidence=insufficient_evidence,
        evidence_gap=evidence_gap,
        require_fulltext=query.require_fulltext_for_selection,
        has_fulltext=bool(paper.full_text),
    )

    if decision == "ambiguous" and not paper.full_text and (topic_relevance >= 2 or supervision_match >= 1):
        reasons.append("Full text would help resolve an otherwise plausible match.")
    if decision == "rejected" and not violated and total < 5:
        reasons.append("Overall score is too weak for selection.")

    return RankingResult(
        topic_relevance=topic_relevance,
        method_match=method_match,
        dataset_match=dataset_match,
        supervision_match=supervision_match,
        evidence_confidence=evidence_confidence,
        total=total,
        decision=decision,
        reasons=reasons,
        violated_criteria=violated,
        insufficient_evidence=insufficient_evidence,
    )


def _score_topic(text: str, keywords: List[str], topic: str) -> int:
    topic_terms = [term.lower() for term in keywords] + topic.lower().split()
    hits = sum(1 for term in topic_terms if term and term in text)
    if hits >= 3:
        return 3
    if hits >= 1:
        return 2
    if any(term in text for term in ["attention", "gaze", "driving"]):
        return 1
    return 0


def _score_method(text: str) -> int:
    if any(term in text for term in ["attention prediction", "gaze prediction", "attention map"]):
        return 3
    if any(term in text for term in ["predict attention", "attention", "gaze"]):
        return 2
    if any(term in text for term in ["saliency", "visual prediction"]):
        return 1
    return 0


def _score_dataset(text: str) -> int:
    if "bdd-100k" in text:
        return 2
    if any(term in text for term in ["real traffic", "real driving", "driving videos"]):
        return 1
    return 0


def _score_supervision(text: str) -> int:
    if any(term in text for term in ["gaze supervision", "attention supervision", "gaze maps"]):
        return 2
    if any(term in text for term in ["gaze", "attention map", "eye tracking", "human attention"]):
        return 1
    return 0


def _score_evidence_confidence(paper: PaperMetadata, evidence_source: str) -> int:
    if paper.full_text and len(evidence_source) > 200:
        return 2
    if paper.abstract:
        return 1
    return 0


def _violated_criteria(text: str, exclusion_criteria: List[str]) -> List[str]:
    violations = []
    for criterion in exclusion_criteria:
        criterion_l = criterion.lower()
        if "generic saliency" in criterion_l and "saliency" in text and "attention supervision" not in text:
            violations.append(criterion)
        if "pure behavior prediction" in criterion_l and "behavior prediction" in text:
            violations.append(criterion)
    return violations


def _decide(
    *,
    total: int,
    violated: List[str],
    insufficient_evidence: bool,
    evidence_gap: bool,
    require_fulltext: bool,
    has_fulltext: bool,
) -> str:
    if violated:
        return "rejected"
    if evidence_gap:
        return "ambiguous"
    if require_fulltext and not has_fulltext and total >= 7:
        return "ambiguous"
    if insufficient_evidence:
        return "ambiguous" if total >= 4 else "rejected"
    if total >= 8:
        return "selected"
    if total >= 5:
        return "ambiguous"
    return "rejected"
