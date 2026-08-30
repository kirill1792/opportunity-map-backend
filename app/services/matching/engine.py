from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Mapping

from app.schemas.matching import (
    EligibilityStatus,
    MatchCategory,
    MatchingResult,
)
from app.services.matching.deadline import calculate_deadline_score
from app.services.matching.explanations import generate_explanations
from app.services.matching.scorers import (
    calculate_effort_score,
    calculate_eligibility_status,
    calculate_format_score,
    calculate_goal_score,
    calculate_interest_score,
    calculate_level_score,
)
from app.services.matching.skills import calculate_skill_score

if TYPE_CHECKING:
    from app.models.opportunity import Opportunity
    from app.models.student_profile import StudentProfile


SCORE_WEIGHTS = {
    "skill": 0.30,
    "interest": 0.20,
    "level": 0.15,
    "format": 0.10,
    "deadline": 0.10,
    "goal": 0.10,
    "effort": 0.05,
}


def match_opportunity(
    profile: StudentProfile,
    opportunity: Opportunity,
    *,
    now: datetime | None = None,
) -> MatchingResult:
    skill_result = calculate_skill_score(profile, opportunity)
    deadline_result = calculate_deadline_score(
        opportunity,
        now=now,
    )
    eligibility_status = calculate_eligibility_status(
        profile,
        opportunity,
    )

    scores = {
        "skill": skill_result.score,
        "interest": calculate_interest_score(profile, opportunity),
        "level": calculate_level_score(profile, opportunity),
        "format": calculate_format_score(profile, opportunity),
        "deadline": deadline_result.score,
        "goal": calculate_goal_score(profile, opportunity),
        "effort": calculate_effort_score(profile, opportunity),
    }

    total_score = calculate_weighted_total(scores)
    category = determine_match_category(
        total_score,
        eligibility_status=eligibility_status,
        is_expired=deadline_result.is_expired,
    )
    explanations = generate_explanations(
        profile=profile,
        opportunity=opportunity,
        scores=scores,
        skill_result=skill_result,
        deadline_result=deadline_result,
        eligibility_status=eligibility_status,
    )

    return MatchingResult(
        total_score=total_score,
        category=category,
        eligibility_status=eligibility_status,
        skill_score=scores["skill"],
        interest_score=scores["interest"],
        level_score=scores["level"],
        format_score=scores["format"],
        deadline_score=scores["deadline"],
        goal_score=scores["goal"],
        effort_score=scores["effort"],
        matched_skills=list(skill_result.matched_skills),
        missing_skills=list(skill_result.missing_skills),
        nice_missing_skills=list(skill_result.nice_missing_skills),
        reasons=list(explanations.reasons),
        warnings=list(explanations.warnings),
        next_steps=list(explanations.next_steps),
        days_left=deadline_result.days_left,
        is_urgent=deadline_result.is_urgent,
    )


def calculate_weighted_total(
    scores: Mapping[str, int | None],
) -> int:
    weighted_sum = 0.0
    available_weight = 0.0

    for score_name, weight in SCORE_WEIGHTS.items():
        score = scores.get(score_name)

        if score is None:
            continue

        if not 0 <= score <= 100:
            raise ValueError(
                f"Score '{score_name}' must be between 0 and 100"
            )

        weighted_sum += score * weight
        available_weight += weight

    if available_weight == 0:
        return 0

    return _round_score(weighted_sum / available_weight)


def determine_match_category(
    total_score: int,
    *,
    eligibility_status: EligibilityStatus,
    is_expired: bool,
) -> MatchCategory:
    if (
        eligibility_status == EligibilityStatus.INELIGIBLE
        or is_expired
    ):
        return MatchCategory.NOT_RECOMMENDED

    if total_score >= 80:
        return MatchCategory.READY_NOW
    if total_score >= 65:
        return MatchCategory.ALMOST_READY
    if total_score >= 45:
        return MatchCategory.LONG_TERM

    return MatchCategory.NOT_RECOMMENDED


def _round_score(score: float) -> int:
    return int(score + 0.5)
