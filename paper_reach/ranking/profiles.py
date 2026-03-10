"""Built-in rubric profiles and helpers."""

from __future__ import annotations

from ..models import RubricDimension, RubricProfile, RubricThresholds


STATIC_POPULATION_EXPOSURE_BASELINE = RubricProfile(
    name="static_population_exposure_baseline",
    hard_gates=[
        "study area is in China",
        "is an exposure or population-at-risk study",
    ],
    dimensions=[
        RubricDimension(name="scope_match", weight=2),
        RubricDimension(name="input_data_match", weight=3),
        RubricDimension(name="outcome_match", weight=3),
        RubricDimension(name="reusability", weight=2),
    ],
    thresholds=RubricThresholds(selected=8, ambiguous=5),
)


BUILTIN_PROFILES = {
    STATIC_POPULATION_EXPOSURE_BASELINE.name: STATIC_POPULATION_EXPOSURE_BASELINE,
}


def get_builtin_profile(name: str | None) -> RubricProfile | None:
    """Return a built-in rubric profile by name."""
    if not name:
        return None
    return BUILTIN_PROFILES.get(name)
