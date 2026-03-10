from paper_reach.models import PaperMetadata, QueryInput
from paper_reach.ranking.rubric import score_paper


def build_query(require_fulltext: bool = False) -> QueryInput:
    return QueryInput(
        topic="Driving attention prediction with BDD-100K",
        keywords=["BDD-100K", "driving attention", "gaze prediction", "attention map"],
        inclusion_criteria=[
            "uses attention map or gaze supervision",
            "preferably real driving scene",
        ],
        exclusion_criteria=[
            "generic saliency detection only",
            "no explicit attention supervision",
            "pure behavior prediction",
        ],
        year_range=(2021, 2026),
        max_results=10,
        need_gap_analysis=True,
        mode="auto",
        require_fulltext_for_selection=require_fulltext,
    )


def test_selected_when_evidence_is_strong() -> None:
    paper = PaperMetadata(
        id="p1",
        title="Driving Attention Maps with Gaze Supervision",
        abstract="We use BDD-100K and gaze supervision for driving attention prediction.",
        full_text="Full text confirms attention map supervision on BDD-100K real driving scenes.",
        source="mock",
    )
    result = score_paper(paper, build_query())
    assert result.decision == "selected"
    assert result.total >= 8


def test_ambiguous_when_fulltext_required_but_missing() -> None:
    paper = PaperMetadata(
        id="p2",
        title="Driving Attention Maps with Gaze Supervision",
        abstract="We use BDD-100K and gaze supervision for driving attention prediction.",
        source="mock",
    )
    result = score_paper(paper, build_query(require_fulltext=True))
    assert result.decision == "ambiguous"


def test_rejected_on_exclusion_signal() -> None:
    paper = PaperMetadata(
        id="p3",
        title="Behavior Prediction for Autonomous Driving",
        abstract="This paper focuses on behavior prediction from video.",
        source="mock",
    )
    result = score_paper(paper, build_query())
    assert result.decision == "rejected"
    assert result.violated_criteria

