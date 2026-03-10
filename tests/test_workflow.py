from pathlib import Path

from paper_reach.models import QueryInput
from paper_reach.workflow import review_workflow, run_workflow, screen_workflow


def test_workflow_with_mock_source() -> None:
    query = QueryInput(
        topic="Driving attention prediction with BDD-100K",
        keywords=["BDD-100K", "driving attention", "gaze prediction", "attention map"],
        inclusion_criteria=["uses attention map or gaze supervision"],
        exclusion_criteria=[
            "generic saliency detection only",
            "no explicit attention supervision",
            "pure behavior prediction",
        ],
        must_include=["uses attention map or gaze supervision"],
        must_exclude=["pure behavior prediction"],
        year_range=(2021, 2026),
        max_results=10,
        need_gap_analysis=True,
        mode="auto",
        require_fulltext_for_selection=False,
    )
    result = run_workflow(query, channel_names=["mock_source"], fetch_fulltext=False)
    assert len(result.screening_candidates) == 2
    assert "search_plan" in result.query_summary
    assert "must_include" in result.query_summary["search_plan"]
    assert len(result.selected) == 1
    assert len(result.ambiguous) == 1
    assert len(result.rejected) == 1


def test_workflow_with_local_text_file() -> None:
    fixture = Path(__file__).parent / "fixtures" / "sample_paper.txt"
    query = QueryInput(
        topic="Driving attention prediction with BDD-100K",
        keywords=["BDD-100K", "driving attention", "gaze prediction", "attention map"],
        inclusion_criteria=["uses attention map or gaze supervision"],
        exclusion_criteria=["pure behavior prediction"],
        year_range=(2021, 2026),
        max_results=10,
        need_gap_analysis=True,
        mode="offline",
        local_paths=[str(fixture)],
        require_fulltext_for_selection=True,
    )
    result = run_workflow(query)
    assert len(result.selected) == 1
    assert result.selected[0].evidence[-1].section == "full_text"
    assert result.selected[0].stage == "review"


def test_screen_then_review_split() -> None:
    query = QueryInput(
        topic="Driving attention prediction with BDD-100K",
        keywords=["BDD-100K", "driving attention", "gaze prediction", "attention map"],
        inclusion_criteria=["uses attention map or gaze supervision"],
        exclusion_criteria=["pure behavior prediction"],
        year_range=(2021, 2026),
        max_results=10,
        need_gap_analysis=True,
        mode="auto",
        require_fulltext_for_selection=False,
    )
    screen_output, papers = screen_workflow(query, channel_names=["mock_source"])
    assert len(screen_output.screening_candidates) == 2
    assert screen_output.screening_candidates[0].stage == "screen"
    assert screen_output.screening_candidates[0].screening_dimensions
    assert "matched_must_include" in screen_output.screening_candidates[0].abstract_findings
    reviewed = review_workflow(query, screen_output=screen_output, papers=papers)
    assert len(reviewed.selected) == 1


def test_high_recall_screen_limits_review_queue() -> None:
    query = QueryInput(
        topic="Driving attention prediction with BDD-100K",
        keywords=["BDD-100K", "driving attention", "gaze prediction", "attention map"],
        inclusion_criteria=["uses attention map or gaze supervision"],
        exclusion_criteria=["pure behavior prediction"],
        year_range=(2021, 2026),
        max_results=1,
        need_gap_analysis=True,
        mode="auto",
        require_fulltext_for_selection=False,
    )
    screen_output, papers = screen_workflow(
        query,
        channel_names=["mock_source"],
        high_recall=True,
        retrieval_limit=10,
    )
    assert len(screen_output.screening_candidates) >= 1
    assert len(papers) == 1
    assert screen_output.query_summary["high_recall"] is True
