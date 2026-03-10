from paper_reach.models import ScreeningResult, WorkflowOutput
from paper_reach.summarize import summarize_workflow_output


def test_titles_summary_keeps_only_title_and_url() -> None:
    workflow = WorkflowOutput(
        query_summary={"topic": "demo"},
        top_ranked=[],
        ambiguous=[
            ScreeningResult(
                id="p1",
                title="Demo Paper",
                source="openalex",
                url="https://example.org/p1",
                relevance_score=4,
                decision="ambiguous",
            )
        ],
    )
    payload = summarize_workflow_output(workflow, format="titles")
    assert payload == [{"title": "Demo Paper", "url": "https://example.org/p1"}]


def test_brief_summary_includes_core_screening_fields() -> None:
    workflow = WorkflowOutput(
        query_summary={"topic": "demo"},
        top_ranked=[],
        selected=[
            ScreeningResult(
                id="p2",
                title="Selected Paper",
                source="openalex",
                url="https://example.org/p2",
                year=2024,
                relevance_score=8,
                decision="selected",
                reasons=["Abstract matches the target workflow."],
                abstract_findings={"study_area": ["China"], "dataset": ["WorldPop"], "task": ["risk assessment"]},
                fulltext_status="available",
                pdf_path="/tmp/p2.pdf",
            )
        ],
    )
    payload = summarize_workflow_output(workflow, format="brief")
    assert payload[0]["title"] == "Selected Paper"
    assert payload[0]["study_area"] == ["China"]
    assert payload[0]["dataset"] == ["WorldPop"]
    assert payload[0]["pdf_path"] == "/tmp/p2.pdf"


def test_summary_can_filter_and_limit() -> None:
    workflow = WorkflowOutput(
        query_summary={"topic": "demo"},
        top_ranked=[],
        selected=[
            ScreeningResult(
                id="p1",
                title="Selected Paper",
                source="openalex",
                url="https://example.org/p1",
                relevance_score=9,
                decision="selected",
            )
        ],
        ambiguous=[
            ScreeningResult(
                id="p2",
                title="Ambiguous Paper",
                source="openalex",
                url="https://example.org/p2",
                relevance_score=6,
                decision="ambiguous",
            )
        ],
    )
    payload = summarize_workflow_output(workflow, format="titles", decision="ambiguous", top_k=1)
    assert payload == [{"title": "Ambiguous Paper", "url": "https://example.org/p2"}]


def test_summary_sorts_by_score_descending() -> None:
    workflow = WorkflowOutput(
        query_summary={"topic": "demo"},
        top_ranked=[],
        ambiguous=[
            ScreeningResult(
                id="p1",
                title="Lower Score",
                source="openalex",
                url="https://example.org/p1",
                relevance_score=3,
                decision="ambiguous",
            ),
            ScreeningResult(
                id="p2",
                title="Higher Score",
                source="openalex",
                url="https://example.org/p2",
                relevance_score=9,
                decision="ambiguous",
            ),
        ],
    )
    payload = summarize_workflow_output(workflow, format="titles")
    assert payload[0]["title"] == "Higher Score"


def test_summary_prefers_top_ranked_when_present() -> None:
    workflow = WorkflowOutput(
        query_summary={"topic": "demo"},
        top_ranked=[
            ScreeningResult(
                id="p9",
                title="Downloaded Winner",
                source="openalex",
                url="https://example.org/p9",
                relevance_score=10,
                decision="ambiguous",
                fulltext_status="available",
            )
        ],
        ambiguous=[
            ScreeningResult(
                id="p8",
                title="Other Paper",
                source="openalex",
                url="https://example.org/p8",
                relevance_score=9,
                decision="ambiguous",
            )
        ],
    )
    payload = summarize_workflow_output(workflow, format="titles")
    assert payload == [{"title": "Downloaded Winner", "url": "https://example.org/p9"}]
