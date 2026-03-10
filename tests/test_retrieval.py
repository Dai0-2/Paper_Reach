from paper_reach.models import QueryInput
from paper_reach.retrieval import (
    build_search_phrases,
    build_search_plan,
    evaluate_criteria_match,
    extract_abstract_findings,
    screen_dimension_scores,
    split_criteria,
)


def test_build_search_phrases_high_recall_expands_queries() -> None:
    query = QueryInput(
        topic="disaster exposure assessment using static population in China",
        keywords=["static population", "disaster exposure", "China", "flood exposure"],
        inclusion_criteria=[
            "uses static population data or gridded population as exposure input",
            "assesses disaster exposure or risk exposure",
            "study area is in China",
        ],
        exclusion_criteria=[],
        year_range=(2010, 2026),
        max_results=20,
        need_gap_analysis=True,
        mode="online",
        require_fulltext_for_selection=False,
    )
    normal = build_search_phrases(query, high_recall=False)
    expanded = build_search_phrases(query, high_recall=True)
    assert len(expanded) > len(normal)
    assert any("china" in phrase.lower() for phrase in expanded)


def test_screen_dimension_scores_capture_core_dimensions() -> None:
    query = QueryInput(
        topic="disaster exposure assessment using static population in China",
        keywords=["static population", "disaster exposure", "China", "earthquake exposure"],
        inclusion_criteria=["uses gridded population", "study area is in China"],
        exclusion_criteria=[],
        year_range=(2010, 2026),
        max_results=20,
        need_gap_analysis=True,
        mode="online",
        require_fulltext_for_selection=False,
    )
    text = (
        "This study assesses earthquake exposure in China using static gridded population "
        "and risk assessment methods."
    )
    scores = screen_dimension_scores(text, query)
    assert scores["population"] >= 1
    assert scores["exposure"] >= 1
    assert scores["hazard"] >= 1
    assert scores["geography"] >= 1


def test_search_plan_and_abstract_findings_are_explainable() -> None:
    query = QueryInput(
        topic="disaster exposure assessment using static population in China",
        keywords=["static population", "disaster exposure", "China", "flood exposure"],
        inclusion_criteria=["uses gridded population", "study area is in China"],
        exclusion_criteria=["study area outside China only"],
        must_include=["uses gridded population"],
        soft_include=["study area is in China"],
        must_exclude=["study area outside China only"],
        year_range=(2010, 2026),
        max_results=20,
        need_gap_analysis=True,
        mode="online",
        require_fulltext_for_selection=False,
    )
    plan = build_search_plan(query, high_recall=True)
    findings = extract_abstract_findings(
        "This study estimates flood exposure in China using gridded population data.",
        query,
    )
    criteria = evaluate_criteria_match(
        "This study estimates flood exposure in China using gridded population data.",
        query,
    )
    split = split_criteria(query)
    assert plan["query_family_count"] >= 4
    assert split["must_include"] == ["uses gridded population"]
    assert "china" in findings["geography_signals"]
    assert "gridded population" in findings["population_signals"]
    assert criteria["matched_must_include"] == ["uses gridded population"]
