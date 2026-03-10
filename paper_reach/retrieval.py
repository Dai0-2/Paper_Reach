"""Helpers for high-recall literature retrieval and coarse screening."""

from __future__ import annotations

import re
from typing import Iterable, List, Sequence

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
