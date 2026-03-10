from paper_reach.models import PaperMetadata, QueryInput, VenuePolicy
from paper_reach.ranking.profiles import STATIC_POPULATION_EXPOSURE_BASELINE
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


def test_profile_selected_for_static_population_baseline_paper() -> None:
    query = QueryInput(
        topic="China static population disaster exposure baseline",
        keywords=["China", "gridded population", "population exposure"],
        inclusion_criteria=["study area is in China"],
        exclusion_criteria=["generic epidemiology"],
        rubric_profile_name=STATIC_POPULATION_EXPOSURE_BASELINE.name,
    )
    paper = PaperMetadata(
        id="p4",
        title="Flood population exposure assessment in Sichuan, China using WorldPop",
        abstract=(
            "This study assesses population exposure and population at risk for flood hazards "
            "in Sichuan, China using WorldPop gridded population data."
        ),
        source="mock",
    )
    result = score_paper(paper, query)
    assert result.total >= 8
    assert result.decision == "ambiguous"
    assert result.dimension_scores["scope_match"] == 2
    assert result.dimension_scores["input_data_match"] == 3


def test_profile_rejects_generic_epidemiology_paper() -> None:
    query = QueryInput(
        topic="China static population infectious disease exposure baseline",
        keywords=["China", "population at risk"],
        inclusion_criteria=["study area is in China"],
        exclusion_criteria=[],
        rubric_profile_name=STATIC_POPULATION_EXPOSURE_BASELINE.name,
    )
    paper = PaperMetadata(
        id="p5",
        title="Prevalence and risk factors of influenza in the Chinese population",
        abstract="A nationwide cohort study of prevalence and risk factors in China.",
        source="mock",
    )
    result = score_paper(paper, query)
    assert result.decision == "rejected"
    assert result.violated_criteria


def test_venue_policy_rejects_mdpi() -> None:
    query = QueryInput(
        topic="China static population disaster exposure baseline",
        keywords=["China", "population exposure"],
        rubric_profile_name=STATIC_POPULATION_EXPOSURE_BASELINE.name,
        venue_policy=VenuePolicy(
            exclude_publishers=["MDPI"],
            elite_journals=["Nature", "Science", "PNAS"],
            allow_journal_quartiles=["Q1", "Q2"],
            allow_conference_tiers=["A*", "A"],
        ),
    )
    paper = PaperMetadata(
        id="p6",
        title="Flood population exposure in China",
        abstract="This study assesses population exposure in China using WorldPop gridded population data.",
        venue="Remote Sensing",
        source="openalex",
    )
    result = score_paper(paper, query)
    assert result.decision == "rejected"
    assert any("MDPI" in item for item in result.violated_criteria)


def test_venue_policy_accepts_elite_journal() -> None:
    query = QueryInput(
        topic="China static population disaster exposure baseline",
        keywords=["China", "population exposure"],
        rubric_profile_name=STATIC_POPULATION_EXPOSURE_BASELINE.name,
        venue_policy=VenuePolicy(
            exclude_publishers=["MDPI"],
            elite_journals=["Nature", "Science", "PNAS"],
            allow_journal_quartiles=["Q1", "Q2"],
            allow_conference_tiers=["A*", "A"],
        ),
    )
    paper = PaperMetadata(
        id="p7",
        title="Population exposure to flooding in China",
        abstract="This study assesses population exposure and population at risk in China using WorldPop gridded population data.",
        venue="Nature Communications",
        source="openalex",
    )
    result = score_paper(paper, query)
    assert result.decision == "ambiguous"
    assert result.total >= 8
