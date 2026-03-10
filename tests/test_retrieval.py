from paper_reach.models import QueryInput
from paper_reach.retrieval import build_search_phrases, screen_dimension_scores


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

