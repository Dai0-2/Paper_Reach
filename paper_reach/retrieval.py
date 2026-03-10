"""Helpers for high-recall literature retrieval and coarse screening."""

from __future__ import annotations

import re
from typing import Dict, Iterable, List, Sequence

from .models import QueryInput

_HAZARD_TERMS = {
    "disaster",
    "hazard",
    "flood",
    "flooding",
    "earthquake",
    "landslide",
    "typhoon",
    "storm",
    "precipitation",
    "rainfall",
    "heatwave",
    "drought",
    "coastal flooding",
    "sea-level rise",
}
_POPULATION_TERMS = {
    "population",
    "static population",
    "gridded population",
    "population density",
    "worldpop",
    "landscan",
    "exposure population",
}
_EXPOSURE_TERMS = {
    "exposure",
    "risk",
    "risk assessment",
    "exposure assessment",
    "vulnerability",
    "susceptibility",
}
_CHINA_TERMS = {
    "china",
    "chinese",
    "yangtze river delta",
    "pearl river delta",
    "poyang lake",
    "beijing",
    "shanghai",
    "guangdong",
    "sichuan",
    "yunnan",
    "tibet",
    "hubei",
    "henan",
}


def build_search_phrases(query: QueryInput, *, high_recall: bool = False) -> List[str]:
    """Build a small family of retrieval phrases for multi-round search."""
    seed_terms = _dedupe_preserve(
        [query.topic, *query.keywords, *query.inclusion_criteria]
    )
    hazard_terms = _matching_terms(seed_terms, _HAZARD_TERMS) or ["disaster"]
    population_terms = _matching_terms(seed_terms, _POPULATION_TERMS) or ["population"]
    exposure_terms = _matching_terms(seed_terms, _EXPOSURE_TERMS) or ["exposure"]
    geography_terms = _matching_terms(seed_terms, _CHINA_TERMS)

    phrases = [
        query.topic,
        " ".join(query.keywords[:5]).strip(),
        " ".join([population_terms[0], exposure_terms[0], *geography_terms[:1]]).strip(),
        " ".join([hazard_terms[0], population_terms[0], exposure_terms[0], *geography_terms[:1]]).strip(),
    ]

    if high_recall:
        for hazard in hazard_terms[:4]:
            phrases.append(" ".join([hazard, population_terms[0], exposure_terms[0], *geography_terms[:1]]).strip())
        for geography in geography_terms[:4]:
            phrases.append(" ".join([population_terms[0], exposure_terms[0], geography]).strip())
        for population in population_terms[:3]:
            phrases.append(" ".join([population, hazard_terms[0], *geography_terms[:1]]).strip())
        phrases.extend(query.inclusion_criteria[:3])

    return [phrase for phrase in _dedupe_preserve(phrases) if phrase]


def build_search_plan(query: QueryInput, *, high_recall: bool = False) -> Dict[str, object]:
    """Return a compact, explainable retrieval plan."""
    seed_terms = [query.topic, *query.keywords, *query.inclusion_criteria]
    hazard_terms = _matching_terms(seed_terms, _HAZARD_TERMS)
    population_terms = _matching_terms(seed_terms, _POPULATION_TERMS)
    exposure_terms = _matching_terms(seed_terms, _EXPOSURE_TERMS)
    geography_terms = _matching_terms(seed_terms, _CHINA_TERMS)
    criteria = split_criteria(query)
    return {
        "query_family_count": len(build_search_phrases(query, high_recall=high_recall)),
        "hazard_terms": hazard_terms,
        "population_terms": population_terms,
        "exposure_terms": exposure_terms,
        "geography_terms": geography_terms,
        "must_include": criteria["must_include"],
        "soft_include": criteria["soft_include"],
        "must_exclude": criteria["must_exclude"],
        "high_recall": high_recall,
    }


def screen_dimension_scores(text: str, query: QueryInput) -> dict[str, int]:
    """Score how well a text matches core screening dimensions."""
    lowered = normalize_text(text)
    phrase_hits = sum(1 for keyword in query.keywords if normalize_text(keyword) in lowered)
    token_hits = sum(
        1 for token in _significant_tokens([query.topic, *query.keywords]) if token in lowered
    )
    keyword_hits = max(phrase_hits, min(token_hits, 3))
    geography_hits = _term_hits(lowered, _matching_terms([query.topic, *query.keywords, *query.inclusion_criteria], _CHINA_TERMS))
    population_hits = _term_hits(lowered, _matching_terms([query.topic, *query.keywords, *query.inclusion_criteria], _POPULATION_TERMS))
    exposure_hits = _term_hits(lowered, _matching_terms([query.topic, *query.keywords, *query.inclusion_criteria], _EXPOSURE_TERMS))
    hazard_hits = _term_hits(lowered, _matching_terms([query.topic, *query.keywords, *query.inclusion_criteria], _HAZARD_TERMS))

    return {
        "keyword": min(keyword_hits, 3),
        "geography": min(geography_hits, 2),
        "population": min(population_hits, 2),
        "exposure": min(exposure_hits, 2),
        "hazard": min(hazard_hits, 2),
    }


def extract_abstract_findings(text: str, query: QueryInput) -> Dict[str, List[str]]:
    """Extract explainable abstract-level findings for screening."""
    lowered = normalize_text(text)
    seed_terms = [query.topic, *query.keywords, *query.inclusion_criteria]
    structured = extract_structured_abstract_fields(text)
    findings = {
        "keywords": [term for term in query.keywords if normalize_text(term) in lowered][:6],
        "hazards": [term for term in _matching_terms(seed_terms, _HAZARD_TERMS) if term in lowered][:6],
        "population_signals": [term for term in _matching_terms(seed_terms, _POPULATION_TERMS) if term in lowered][:6],
        "exposure_signals": [term for term in _matching_terms(seed_terms, _EXPOSURE_TERMS) if term in lowered][:6],
        "geography_signals": [term for term in _matching_terms(seed_terms, _CHINA_TERMS) if term in lowered][:6],
        "task": structured["task"],
        "dataset": structured["dataset"],
        "method": structured["method"],
        "supervision": structured["supervision"],
        "study_area": structured["study_area"],
    }
    return findings


def split_criteria(query: QueryInput) -> Dict[str, List[str]]:
    """Split query criteria into must/soft/exclude buckets."""
    must_include = list(query.must_include)
    soft_include = list(query.soft_include)
    must_exclude = list(query.must_exclude or query.exclusion_criteria)
    if not must_include and not soft_include:
        for criterion in query.inclusion_criteria:
            lowered = normalize_text(criterion)
            if any(token in lowered for token in ["must", "require", "uses", "study area is", "explicit"]):
                must_include.append(criterion)
            else:
                soft_include.append(criterion)
    return {
        "must_include": _dedupe_preserve(must_include),
        "soft_include": _dedupe_preserve(soft_include),
        "must_exclude": _dedupe_preserve(must_exclude),
    }


def evaluate_criteria_match(text: str, query: QueryInput) -> Dict[str, List[str]]:
    """Evaluate which criteria appear matched or still missing from abstract-level evidence."""
    criteria = split_criteria(query)
    lowered = normalize_text(text)
    matched_must = [criterion for criterion in criteria["must_include"] if _criterion_matches(lowered, criterion)]
    matched_soft = [criterion for criterion in criteria["soft_include"] if _criterion_matches(lowered, criterion)]
    violated = [criterion for criterion in criteria["must_exclude"] if _criterion_matches(lowered, criterion)]
    missing_must = [criterion for criterion in criteria["must_include"] if criterion not in matched_must]
    return {
        "matched_must_include": matched_must,
        "missing_must_include": missing_must,
        "matched_soft_include": matched_soft,
        "violated_exclude": violated,
    }


def extract_structured_abstract_fields(text: str) -> Dict[str, List[str]]:
    """Extract lightweight structured fields from an abstract."""
    lowered = normalize_text(text)
    patterns = {
        "task": ["exposure assessment", "risk assessment", "population exposure", "flood exposure", "earthquake exposure"],
        "dataset": ["bdd-100k", "worldpop", "landscan", "census", "survey", "gridded population"],
        "method": ["gis", "remote sensing", "spatial analysis", "model", "regression", "machine learning"],
        "supervision": ["annotation", "labeled", "survey-based", "human gaze", "manual interpretation"],
        "study_area": list(_CHINA_TERMS),
    }
    return {
        key: [term for term in terms if term in lowered][:6]
        for key, terms in patterns.items()
    }


def normalize_text(text: str) -> str:
    """Normalize text for loose term matching."""
    return re.sub(r"\s+", " ", text.lower()).strip()


def _matching_terms(terms: Sequence[str], lexicon: set[str]) -> List[str]:
    lowered_terms = [normalize_text(term) for term in terms if term]
    hits: List[str] = []
    for lex in lexicon:
        if any(lex in term for term in lowered_terms):
            hits.append(lex)
    return _dedupe_preserve(hits)


def _term_hits(text: str, terms: Iterable[str]) -> int:
    return sum(1 for term in terms if term and term in text)


def _criterion_matches(text: str, criterion: str) -> bool:
    normalized = normalize_text(criterion)
    if normalized in text:
        return True
    tokens = _significant_tokens([criterion])
    if not tokens:
        return False
    hits = sum(1 for token in tokens if token in text)
    return hits >= min(2, len(tokens))


def _dedupe_preserve(items: Sequence[str]) -> List[str]:
    seen = set()
    ordered: List[str] = []
    for item in items:
        if item and item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered


def _significant_tokens(texts: Sequence[str]) -> List[str]:
    tokens: List[str] = []
    for text in texts:
        for token in re.findall(r"[a-z0-9-]{3,}", normalize_text(text)):
            if token not in {"and", "the", "with", "using", "for", "from"}:
                tokens.append(token)
    return _dedupe_preserve(tokens)
