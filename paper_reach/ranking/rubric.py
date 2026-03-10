"""Conservative literature-screening rubric."""

from __future__ import annotations

from typing import Dict, List

from ..models import PaperMetadata, QueryInput, RankingResult, RubricProfile, VenuePolicy
from .profiles import get_builtin_profile


def score_paper(paper: PaperMetadata, query: QueryInput) -> RankingResult:
    """Score a paper conservatively against screening criteria."""
    profile = query.rubric_profile or get_builtin_profile(query.rubric_profile_name)
    if profile is not None:
        return _score_with_profile(paper, query, profile)
    return _score_with_legacy_rubric(paper, query)


def _score_with_profile(
    paper: PaperMetadata,
    query: QueryInput,
    profile: RubricProfile,
) -> RankingResult:
    text = _combined_text(paper)
    dimension_scores = {
        dimension.name: _score_profile_dimension(dimension.name, paper, text, query)
        for dimension in profile.dimensions
    }
    weighted_total = sum(
        dimension_scores[dimension.name] * dimension.weight
        for dimension in profile.dimensions
    )
    reasons = _profile_reasons(dimension_scores, profile)
    violated = _profile_hard_gate_violations(paper, text, query, profile)
    insufficient_evidence = not bool(paper.abstract or paper.full_text)
    venue_verdict = _apply_venue_policy(paper, query.venue_policy)
    if venue_verdict["decision"] == "rejected":
        violated.append(venue_verdict["reason"])
    elif venue_verdict["reason"]:
        reasons.append(venue_verdict["reason"])

    decision = _decide_profile(
        profile=profile,
        total=weighted_total,
        violated=violated,
        insufficient_evidence=insufficient_evidence,
        has_fulltext=bool(paper.full_text),
        require_fulltext=query.require_fulltext_for_selection,
        venue_decision=venue_verdict["decision"],
    )

    if paper.full_text:
        reasons.append("Full-text evidence is available, improving confidence.")
    elif paper.abstract:
        reasons.append("Only abstract-level evidence is available.")
    else:
        reasons.append("Only metadata is available; evidence remains weak.")
    if violated:
        reasons.append(f"Hard-gate failure: {violated[0]}.")

    return RankingResult(
        topic_relevance=dimension_scores.get("scope_match", 0),
        method_match=dimension_scores.get("method_match", 0),
        dataset_match=dimension_scores.get("input_data_match", 0),
        supervision_match=dimension_scores.get("outcome_match", 0),
        evidence_confidence=_score_evidence_confidence(paper),
        total=weighted_total,
        decision=decision,
        reasons=reasons,
        violated_criteria=violated,
        insufficient_evidence=insufficient_evidence,
        dimension_scores=dimension_scores,
        venue_tier_inferred=venue_verdict["tier"],
        venue_tier_confidence=venue_verdict["confidence"],
    )


def _score_with_legacy_rubric(paper: PaperMetadata, query: QueryInput) -> RankingResult:
    title = paper.title.lower()
    abstract = (paper.abstract or "").lower()
    full_text = (paper.full_text or "").lower()
    combined = " ".join(part for part in [title, abstract, full_text] if part)

    violated = _violated_criteria(combined, query.exclusion_criteria)
    insufficient_evidence = not bool(paper.abstract or paper.full_text)

    topic_relevance = _score_topic(combined, query.keywords, query.topic)
    method_match = _score_method(combined)
    dataset_match = _score_dataset(combined)
    supervision_match = _score_supervision(combined)
    evidence_confidence = _score_evidence_confidence(paper)
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
        reasons.append("Dataset evidence mentions a relevant setting or data source.")
    if supervision_match >= 1:
        reasons.append("Outcome evidence suggests relevant task supervision or target variables.")
    if insufficient_evidence:
        reasons.append("Evidence is limited because abstract and full text are missing.")
    if paper.full_text:
        reasons.append("Full-text evidence is available, improving confidence.")
    elif paper.abstract:
        reasons.append("Only abstract-level evidence is available.")
    if violated:
        reasons.append("One or more exclusion criteria appear to be triggered.")

    decision = _decide_legacy(
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
        dimension_scores={},
        venue_tier_inferred=None,
        venue_tier_confidence=None,
    )


def _combined_text(paper: PaperMetadata) -> str:
    return " ".join(
        part.lower() for part in [paper.title, paper.abstract or "", paper.full_text or ""] if part
    )


def _score_profile_dimension(
    name: str,
    paper: PaperMetadata,
    text: str,
    query: QueryInput,
) -> int:
    if name == "scope_match":
        return _score_scope_match(text)
    if name == "input_data_match":
        return _score_input_data_match(text)
    if name == "outcome_match":
        return _score_outcome_match(text)
    if name == "reusability":
        return _score_reusability(text)
    if name == "method_match":
        return _score_method(text)
    if name == "evidence_strength":
        return _score_evidence_confidence(paper)
    if name == "topic_match":
        return _score_topic(text, query.keywords, query.topic)
    return 0


def _score_scope_match(text: str) -> int:
    chinese_regions = [
        "china",
        "chinese",
        "beijing",
        "shanghai",
        "sichuan",
        "wuhan",
        "tianjin",
        "guangdong",
        "yangtze",
        "poyang",
        "hong kong",
        "chongqing",
        "wrenchuan",
        "wenchuan",
    ]
    if "china" in text and any(region in text for region in chinese_regions if region != "china"):
        return 2
    if "china" in text or "chinese" in text:
        return 1
    return 0


def _score_input_data_match(text: str) -> int:
    if any(term in text for term in ["worldpop", "landscan", "gpw", "gridded population", "static population", "census population"]):
        return 3
    if any(term in text for term in ["population distribution", "spatial population", "population density"]):
        return 2
    if "population" in text:
        return 1
    return 0


def _score_outcome_match(text: str) -> int:
    if any(term in text for term in ["population exposure", "affected population", "population at risk", "exposure risk"]):
        return 3
    if any(term in text for term in ["risk assessment", "exposure assessment", "at risk"]):
        return 2
    if any(term in text for term in ["vulnerability", "risk", "exposure"]):
        return 1
    return 0


def _score_reusability(text: str) -> int:
    if _score_input_data_match(text) >= 3 and _score_outcome_match(text) >= 3 and _score_scope_match(text) >= 1:
        return 2
    if _score_input_data_match(text) >= 2 and _score_outcome_match(text) >= 2:
        return 1
    return 0


def _profile_hard_gate_violations(
    paper: PaperMetadata,
    text: str,
    query: QueryInput,
    profile: RubricProfile,
) -> List[str]:
    violations: List[str] = []
    for gate in profile.hard_gates:
        gate_l = gate.lower()
        if "china" in gate_l and _score_scope_match(text) == 0:
            violations.append(gate)
        elif "static or gridded population" in gate_l and _score_input_data_match(text) < 2:
            violations.append(gate)
        elif "exposure or population-at-risk" in gate_l and _score_outcome_match(text) < 2:
            violations.append(gate)
        elif "not generic epidemiology or a broad review" in gate_l and _looks_generic_or_review(text):
            violations.append(gate)
    for criterion in query.must_exclude:
        if criterion.lower() in text:
            violations.append(criterion)
    return violations


def _looks_generic_or_review(text: str) -> bool:
    review_terms = ["systematic review", "review article", "scoping review", "broad review"]
    epidemiology_terms = ["prevalence", "risk factors", "cohort study", "mental health", "clinical outcome"]
    return any(term in text for term in review_terms) or any(term in text for term in epidemiology_terms)


def _profile_reasons(scores: Dict[str, int], profile: RubricProfile) -> List[str]:
    label_map = {
        "scope_match": "study scope",
        "input_data_match": "input data",
        "outcome_match": "outcome or exposure target",
        "reusability": "baseline reusability",
        "method_match": "method alignment",
        "topic_match": "topic alignment",
        "evidence_strength": "evidence strength",
    }
    reasons = []
    for dimension in profile.dimensions:
        score = scores.get(dimension.name, 0)
        label = label_map.get(dimension.name, dimension.name)
        if score > 0:
            reasons.append(f"{label} score is {score}/{dimension.weight}.")
    if not reasons:
        reasons.append("Profile-driven rubric found very limited support in the available evidence.")
    return reasons


def _decide_profile(
    *,
    profile: RubricProfile,
    total: int,
    violated: List[str],
    insufficient_evidence: bool,
    has_fulltext: bool,
    require_fulltext: bool,
    venue_decision: str,
) -> str:
    if violated:
        return "rejected"
    if venue_decision == "rejected":
        return "rejected"
    if venue_decision == "ambiguous" and total >= profile.thresholds.selected:
        return "ambiguous"
    if not has_fulltext and total >= profile.thresholds.selected:
        return "ambiguous"
    if require_fulltext and not has_fulltext and total >= profile.thresholds.selected:
        return "ambiguous"
    if total >= profile.thresholds.selected and not insufficient_evidence:
        return "selected"
    if total >= profile.thresholds.ambiguous:
        return "ambiguous"
    return "rejected"


def _apply_venue_policy(paper: PaperMetadata, policy: VenuePolicy | None) -> Dict[str, str]:
    if policy is None:
        return {"decision": "pass", "reason": "", "tier": "unknown", "confidence": "low"}
    venue = (paper.venue or "").lower()
    title = (paper.title or "").lower()
    source = (paper.source or "").lower()
    haystack = " ".join(part for part in [venue, title, source] if part)

    for publisher in policy.exclude_publishers:
        if publisher.lower() in haystack or _matches_known_publisher_venue(publisher, venue):
            return {
                "decision": "rejected",
                "reason": f"Venue policy excluded publisher or venue match: {publisher}.",
                "tier": "excluded",
                "confidence": "high",
            }

    if _matches_any(haystack, policy.elite_journals) or _matches_any(haystack, policy.elite_conferences):
        return {
            "decision": "pass",
            "reason": "Venue heuristic matched an elite journal or conference.",
            "tier": "Q1-like",
            "confidence": "high",
        }

    quartile = _infer_journal_quartile(venue)
    if quartile and quartile in {item.upper() for item in policy.allow_journal_quartiles}:
        return {
            "decision": "pass",
            "reason": f"Venue heuristic inferred journal tier {quartile}-like.",
            "tier": f"{quartile}-like",
            "confidence": "medium" if quartile == "Q2" else "high",
        }

    tier = _infer_conference_tier(venue)
    if tier and tier in {item.upper() for item in policy.allow_conference_tiers}:
        return {
            "decision": "pass",
            "reason": f"Venue heuristic inferred conference tier {tier}.",
            "tier": "Q1-like" if tier == "A*" else "Q2-like",
            "confidence": "high" if tier == "A*" else "medium",
        }

    if not venue:
        if policy.reject_unknown_venue_rank:
            return {
                "decision": "rejected",
                "reason": "Venue policy rejected a paper with unknown venue rank.",
                "tier": "unknown",
                "confidence": "low",
            }
        return {
            "decision": "pass",
            "reason": "Venue tier is unknown; keeping the paper based on content and treating the venue tier as heuristic only.",
            "tier": "unknown",
            "confidence": "low",
        }

    if policy.reject_unknown_venue_rank:
        return {
            "decision": "rejected",
            "reason": "Venue did not match elite/Q1/Q2/A/A* rules.",
            "tier": "unknown",
            "confidence": "low",
        }
    return {
        "decision": "pass",
        "reason": "Venue did not match the built-in elite/Q1-like/Q2-like heuristics; keeping it unless other rules reject it.",
        "tier": "unknown",
        "confidence": "low",
    }


def _matches_any(text: str, candidates: List[str]) -> bool:
    return any(candidate.lower() in text for candidate in candidates)


def _matches_known_publisher_venue(publisher: str, venue: str) -> bool:
    publisher_l = publisher.lower()
    venue_l = venue.lower()
    known = {
        "mdpi": {
            "remote sensing",
            "sustainability",
            "ijerph",
            "international journal of environmental research and public health",
            "atmosphere",
            "water",
            "sensors",
            "applied sciences",
            "electronics",
            "isprs international journal of geo-information",
        }
    }
    return venue_l in known.get(publisher_l, set())


def _infer_journal_quartile(venue: str) -> str | None:
    q1_patterns = [
        "nature",
        "science",
        "pnas",
        "lancet",
        "jama",
        "nejm",
        "nature communications",
        "proceedings of the national academy of sciences",
    ]
    q2_patterns = [
        "environmental research",
        "international journal of disaster risk reduction",
        "natural hazards",
        "science of the total environment",
        "journal of hydrology",
        "health & place",
    ]
    if any(pattern in venue for pattern in q1_patterns):
        return "Q1"
    if any(pattern in venue for pattern in q2_patterns):
        return "Q2"
    return None


def _infer_conference_tier(venue: str) -> str | None:
    a_star_patterns = ["cvpr", "iccv", "eccv", "neurips", "iclr"]
    a_patterns = ["aaai", "ijcai", "acm mm", "kdd"]
    if any(pattern in venue for pattern in a_star_patterns):
        return "A*"
    if any(pattern in venue for pattern in a_patterns):
        return "A"
    return None


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


def _score_evidence_confidence(paper: PaperMetadata) -> int:
    if paper.full_text:
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


def _decide_legacy(
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
