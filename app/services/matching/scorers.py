from __future__ import annotations

from typing import TYPE_CHECKING, Any

from app.core.taxonomy import SKILL_LEVEL_TO_SCORE
from app.schemas.matching import EligibilityStatus

if TYPE_CHECKING:
    from app.models.opportunity import Opportunity
    from app.models.student_profile import StudentProfile


GOAL_TYPE_SCORES: dict[str, dict[str, int]] = {
    "find_internship": {"internship": 100},
    "find_research_opportunity": {
        "school": 75,
        "event": 65,
        "internship": 60,
    },
    "join_hackathon": {"hackathon": 100},
    "build_portfolio": {
        "hackathon": 100,
        "competition": 90,
        "internship": 80,
        "course": 75,
        "school": 75,
    },
    "improve_skills": {
        "course": 100,
        "school": 95,
        "hackathon": 80,
        "competition": 80,
        "internship": 75,
        "event": 65,
    },
    "find_scholarship_or_grant": {
        "school": 70,
        "course": 60,
    },
    "prepare_for_big_tech": {
        "internship": 100,
        "competition": 85,
        "course": 75,
    },
    "explore_career_direction": {
        "event": 100,
        "course": 85,
        "school": 85,
        "internship": 80,
    },
    "find_summer_school": {"school": 100},
    "find_competitions": {
        "competition": 100,
        "hackathon": 90,
    },
    "network_with_people": {
        "event": 100,
        "hackathon": 85,
        "school": 80,
    },
}

GOAL_SIGNALS: dict[str, set[str]] = {
    "find_research_opportunity": {"research"},
    "find_scholarship_or_grant": {"scholarship", "grant"},
    "contribute_to_open_source": {"open_source"},
}

UNRESTRICTED_ELIGIBILITY = {
    "all",
    "any",
    "any_student",
    "open_to_all",
    "no_restrictions",
    "без_ограничений",
    "любой_курс",
}


def calculate_interest_score(
    profile: StudentProfile,
    opportunity: Opportunity,
) -> int | None:
    interests = _normalised_values(profile.interests or [])
    opportunity_field = _normalise_value(opportunity.field)
    tags = _normalised_values(opportunity.tags or [])

    if not interests or not (opportunity_field or tags):
        return None

    if opportunity_field in interests:
        return 100

    matching_tags = interests & tags

    if matching_tags:
        coverage = len(matching_tags) / len(interests)
        return min(90, _round_score(70 + 20 * coverage))

    return 25


def calculate_level_score(
    profile: StudentProfile,
    opportunity: Opportunity,
) -> int | None:
    profile_level = _normalise_value(profile.experience_level)
    opportunity_level = _normalise_value(opportunity.level)

    if opportunity_level == "any":
        return 100

    if (
        profile_level not in SKILL_LEVEL_TO_SCORE
        or opportunity_level not in SKILL_LEVEL_TO_SCORE
    ):
        return None

    difference = (
        SKILL_LEVEL_TO_SCORE[opportunity_level]
        - SKILL_LEVEL_TO_SCORE[profile_level]
    )

    if difference == 0:
        return 100
    if difference == 1:
        return 70
    if difference == 2:
        return 25
    if difference >= 3:
        return 10
    if difference == -1:
        return 85

    return 65


def calculate_format_score(
    profile: StudentProfile,
    opportunity: Opportunity,
) -> int | None:
    preferred_formats = _normalised_values(
        profile.preferred_formats or []
    )
    opportunity_format = _normalise_value(opportunity.format)

    if not preferred_formats or opportunity_format is None:
        return None

    if opportunity_format in preferred_formats:
        return 100

    if (
        opportunity_format == "hybrid"
        or "hybrid" in preferred_formats
    ):
        return 70

    return 40


def calculate_goal_score(
    profile: StudentProfile,
    opportunity: Opportunity,
) -> int | None:
    goals = _normalised_values(profile.goals or [])
    opportunity_type = _normalise_value(opportunity.type)
    opportunity_field = _normalise_value(opportunity.field)
    signals = _normalised_values(opportunity.tags or [])

    if opportunity_field is not None:
        signals.add(opportunity_field)

    if not goals or not (opportunity_type or signals):
        return None

    best_score = 25

    for goal in goals:
        if GOAL_SIGNALS.get(goal, set()) & signals:
            best_score = max(best_score, 100)

        type_score = GOAL_TYPE_SCORES.get(goal, {}).get(
            opportunity_type,
        )

        if type_score is not None:
            best_score = max(best_score, type_score)

    return best_score


def calculate_effort_score(
    profile: StudentProfile,
    opportunity: Opportunity,
) -> int | None:
    available_hours = profile.available_hours_per_week
    estimated_effort = opportunity.estimated_effort

    if (
        not _is_non_negative_number(available_hours)
        or not _is_non_negative_number(estimated_effort)
    ):
        return None

    if estimated_effort == 0:
        return 100

    if available_hours == 0:
        return 10

    effort_ratio = estimated_effort / available_hours

    if effort_ratio <= 1:
        return 100
    if effort_ratio <= 1.25:
        return 80
    if effort_ratio <= 1.5:
        return 60
    if effort_ratio <= 2:
        return 30

    return 10


def calculate_eligibility_status(
    profile: StudentProfile,
    opportunity: Opportunity,
) -> EligibilityStatus:
    _ = profile
    eligibility = _normalise_value(opportunity.eligibility)

    if eligibility is None or eligibility in UNRESTRICTED_ELIGIBILITY:
        return EligibilityStatus.ELIGIBLE

    return EligibilityStatus.UNKNOWN


def _normalised_values(values: list[Any]) -> set[str]:
    result: set[str] = set()

    for value in values:
        normalised = _normalise_value(value)

        if normalised is not None:
            result.add(normalised)

    return result


def _normalise_value(value: Any) -> str | None:
    enum_value = getattr(value, "value", value)

    if not isinstance(enum_value, str):
        return None

    normalised = (
        enum_value.strip()
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
    )

    return normalised or None


def _is_non_negative_number(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and value >= 0
    )


def _round_score(score: float) -> int:
    return int(score + 0.5)
