from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from app.core.taxonomy import SKILL_LEVEL_TO_SCORE
from app.schemas.matching import (
    MatchedSkill,
    MissingSkill,
    SkillRequirement,
)

if TYPE_CHECKING:
    from app.models.opportunity import Opportunity
    from app.models.student_profile import StudentProfile


@dataclass(frozen=True)
class SkillScoreResult:
    score: int | None
    matched_skills: tuple[MatchedSkill, ...]
    missing_skills: tuple[MissingSkill, ...]
    nice_missing_skills: tuple[MissingSkill, ...]


def calculate_skill_score(
    profile: StudentProfile,
    opportunity: Opportunity,
) -> SkillScoreResult:
    student_skills = _student_skill_levels(profile.skills or [])
    required_skills = opportunity.required_skills or {}
    nice_to_have_skills = opportunity.nice_to_have_skills or {}

    required_score, required_matched, required_missing = _score_skill_group(
        student_skills=student_skills,
        requirements=required_skills,
        requirement=SkillRequirement.REQUIRED,
    )
    nice_score, nice_matched, nice_missing = _score_skill_group(
        student_skills=student_skills,
        requirements=nice_to_have_skills,
        requirement=SkillRequirement.NICE_TO_HAVE,
    )

    if required_score is None and nice_score is None:
        score = None
    elif required_score is None:
        score = _round_score(nice_score)
    elif nice_score is None:
        score = _round_score(required_score)
    else:
        score = _round_score(
            required_score * 0.85
            + nice_score * 0.15
        )

    return SkillScoreResult(
        score=score,
        matched_skills=tuple(required_matched + nice_matched),
        missing_skills=tuple(required_missing),
        nice_missing_skills=tuple(nice_missing),
    )


def _student_skill_levels(skills: list[Any]) -> dict[str, int]:
    result: dict[str, int] = {}

    for item in skills:
        if isinstance(item, dict):
            skill_name = item.get("skill")
            raw_level = item.get("level")
        else:
            skill_name = getattr(item, "skill", None)
            raw_level = getattr(item, "level", None)

        if not isinstance(skill_name, str) or not skill_name:
            raise ValueError("Student skill must contain a non-empty 'skill'")

        if (
            not isinstance(raw_level, str)
            or raw_level not in SKILL_LEVEL_TO_SCORE
        ):
            raise ValueError(
                f"Unknown level '{raw_level}' for student skill "
                f"'{skill_name}'"
            )

        if skill_name in result:
            raise ValueError(
                f"Student profile contains duplicate skill '{skill_name}'"
            )

        result[skill_name] = SKILL_LEVEL_TO_SCORE[raw_level]

    return result


def _score_skill_group(
    *,
    student_skills: dict[str, int],
    requirements: dict[str, int],
    requirement: SkillRequirement,
) -> tuple[float | None, list[MatchedSkill], list[MissingSkill]]:
    if not requirements:
        return None, [], []

    coverage_sum = 0.0
    matched_skills: list[MatchedSkill] = []
    missing_skills: list[MissingSkill] = []

    for skill_name, required_level in sorted(requirements.items()):
        if not isinstance(required_level, int) or not 1 <= required_level <= 5:
            raise ValueError(
                f"Required level for skill '{skill_name}' must be between 1 and 5"
            )

        current_level = student_skills.get(skill_name, 0)
        coverage_sum += min(current_level / required_level, 1.0)

        if current_level >= required_level:
            matched_skills.append(
                MatchedSkill(
                    skill=skill_name,
                    current_level=current_level,
                    required_level=required_level,
                    requirement=requirement,
                )
            )
        else:
            missing_skills.append(
                MissingSkill(
                    skill=skill_name,
                    current_level=current_level,
                    required_level=required_level,
                    gap=required_level - current_level,
                    requirement=requirement,
                )
            )

    score = coverage_sum / len(requirements) * 100

    return score, matched_skills, missing_skills


def _round_score(score: float) -> int:
    return int(score + 0.5)
