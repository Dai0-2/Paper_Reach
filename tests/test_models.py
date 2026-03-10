from paper_reach.models import PaperEvidence, QueryInput, WorkflowOutput


def test_query_input_serialization() -> None:
    query = QueryInput(
        topic="Driving attention prediction with BDD-100K",
        keywords=["BDD-100K", "gaze prediction"],
        inclusion_criteria=["uses attention map or gaze supervision"],
        exclusion_criteria=["pure behavior prediction"],
        must_include=["uses attention map or gaze supervision"],
        soft_include=["preferably real driving scene"],
        must_exclude=["pure behavior prediction"],
        year_range=(2021, 2026),
        max_results=10,
        need_gap_analysis=True,
        mode="auto",
        local_paths=["tests/fixtures/sample_paper.txt"],
        require_fulltext_for_selection=False,
    )
    payload = query.model_dump(mode="json")
    assert payload["topic"] == "Driving attention prediction with BDD-100K"
    assert payload["year_range"] == [2021, 2026]
    assert payload["must_include"] == ["uses attention map or gaze supervision"]


def test_workflow_output_round_trip() -> None:
    output = WorkflowOutput(
        query_summary={"topic": "demo"},
        screening_candidates=[],
        selected=[],
        ambiguous=[],
        rejected=[],
        gap_analysis=["Need stronger full-text evidence."],
        recommended_next_queries=["demo gaze supervision"],
    )
    dumped = output.model_dump(mode="json")
    restored = WorkflowOutput.model_validate(dumped)
    assert restored.gap_analysis[0] == "Need stronger full-text evidence."


def test_evidence_defaults() -> None:
    evidence = PaperEvidence(section="abstract", note="Coarse signal only.")
    assert evidence.confidence == "low"
