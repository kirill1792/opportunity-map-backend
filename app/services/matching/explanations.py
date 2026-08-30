from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Mapping

from app.schemas.matching import EligibilityStatus, SkillRequirement
from app.services.matching.deadline import DeadlineScoreResult
from app.services.matching.skills import SkillScoreResult

if TYPE_CHECKING:
    from app.models.opportunity import Opportunity
    from app.models.student_profile import StudentProfile


@dataclass(frozen=True)
class ExplanationResult:
    reasons: tuple[str, ...]
    warnings: tuple[str, ...]
    next_steps: tuple[str, ...]


def generate_explanations(
    *,
    profile: StudentProfile,
    opportunity: Opportunity,
    scores: Mapping[str, int | None],
    skill_result: SkillScoreResult,
    deadline_result: DeadlineScoreResult,
    eligibility_status: EligibilityStatus,
) -> ExplanationResult:
    reasons = _generate_reasons(
        profile=profile,
        opportunity=opportunity,
        scores=scores,
        skill_result=skill_result,
    )
    warnings = _generate_warnings(
        opportunity=opportunity,
        scores=scores,
        skill_result=skill_result,
        deadline_result=deadline_result,
        eligibility_status=eligibility_status,
    )
    next_steps = _generate_next_steps(
        skill_result=skill_result,
        deadline_result=deadline_result,
    )

    return ExplanationResult(
        reasons=tuple(reasons),
        warnings=tuple(warnings),
        next_steps=tuple(next_steps),
    )


def _generate_reasons(
    *,
    profile: StudentProfile,
    opportunity: Opportunity,
    scores: Mapping[str, int | None],
    skill_result: SkillScoreResult,
) -> list[str]:
    reasons: list[str] = []
    interests = _normalised_values(profile.interests or [])
    opportunity_field = _normalise_value(opportunity.field)
    tags = _normalised_values(opportunity.tags or [])

    if opportunity_field in interests:
        reasons.append(
            f"Совпадает с вашим интересом: {_label(opportunity_field)}"
        )
    else:
        matching_interests = sorted(interests & tags)

        if matching_interests:
            reasons.append(
                "Совпадает с вашими интересами "
                f"{_join_labels(matching_interests[:3])}"
            )

    required_matches = [
        skill.skill
        for skill in skill_result.matched_skills
        if skill.requirement == SkillRequirement.REQUIRED
    ]

    if required_matches:
        reasons.append(
            f"Ваш навык: {_join_labels(required_matches[:3])} удовлетворяет требованиям "
        )

    format_score = scores.get("format")

    if format_score == 100:
        opportunity_format = _normalise_value(opportunity.format)
        reasons.append(
            f"{_label(opportunity_format)} - этот формат подходит вам"
        )
    elif format_score is not None and format_score >= 70:
        reasons.append("Этот формат соответствует вашим предпочтениям.")

    level_score = scores.get("level")

    if level_score is not None and level_score >= 85:
        reasons.append("Сложность соответствует вашему текущему уровню опыта")

    goal_score = scores.get("goal")

    if goal_score is not None and goal_score >= 70:
        reasons.append("Удовлетворяет вашим целям")

    effort_score = scores.get("effort")

    if effort_score is not None and effort_score >= 80:
        reasons.append("Нагрузка допустима в рамках вашего доступного времени")

    return reasons[:5]


def _generate_warnings(
    *,
    opportunity: Opportunity,
    scores: Mapping[str, int | None],
    skill_result: SkillScoreResult,
    deadline_result: DeadlineScoreResult,
    eligibility_status: EligibilityStatus,
) -> list[str]:
    warnings: list[str] = []

    if deadline_result.is_expired:
        warnings.append("Дедлайн уже прошел")
    elif deadline_result.is_urgent:
        warnings.append(_deadline_warning(deadline_result.days_left))

    if (
        eligibility_status == EligibilityStatus.UNKNOWN
        and opportunity.eligibility
    ):
        warnings.append(
            "Ознакомьтесь с требованиями, прежде чем подавать заявку."
        )

    if skill_result.missing_skills:
        gaps = [
            f"{_label(skill.skill)} "
            f"({skill.current_level} to {skill.required_level})"
            for skill in skill_result.missing_skills[:3]
        ]
        warnings.append(f"Нехватка обязательных навыков: {', '.join(gaps)}")

    level_score = scores.get("level")

    if level_score is not None and level_score <= 25:
        warnings.append(
            "Требования возможности существенно выше вашего текущего уровня"
        )

    effort_score = scores.get("effort")

    if effort_score is not None and effort_score < 60:
        warnings.append(
            "Объем работы превышает имеющееся у вас время"
        )

    return warnings[:5]


def _generate_next_steps(
    *,
    skill_result: SkillScoreResult,
    deadline_result: DeadlineScoreResult,
) -> list[str]:
    next_steps: list[str] = []

    for missing_skill in skill_result.missing_skills[:2]:
        skill_label = _label(missing_skill.skill)

        if missing_skill.current_level == 0:
            next_steps.append(
                f"Освоить {skill_label} на уровне "
                f"{missing_skill.required_level}"
            )
        else:
            next_steps.append(
                f"Подтянуть {skill_label} от уровня "
                f"{missing_skill.current_level} до "
                f"{missing_skill.required_level}"
            )

    if deadline_result.is_expired:
        next_steps.append(
            "Проверьте официальную страницу на предмет продления срока подачи заявок "
            "или информации о следующем наборе."
        )
    elif deadline_result.is_urgent:
        next_steps.append(
            "Ознакомьтесь с требованиями и подайте заявку как можно скорее"
        )
    else:
        next_steps.append(
            "Откройте официальную страницу и ознакомьтесь с требованиями к заявке"
        )

    if (
        not skill_result.missing_skills
        and skill_result.nice_missing_skills
    ):
        nice_skill = skill_result.nice_missing_skills[0]
        next_steps.append(
            f"По возможности прокачайте {_label(nice_skill.skill)}, чтобы "
            "ваш уровень готовности"
        )

    return next_steps[:4]


def _deadline_warning(days_left: int | None) -> str:
    if days_left == 0:
        return "Дедлайн - сегодня"
    if days_left == 1:
        return "До дедлайна - 1 день"

    return f"Дней до дедлайна: {days_left}"


def _normalised_values(values: list[Any]) -> set[str]:
    return {
        normalised
        for value in values
        if (normalised := _normalise_value(value)) is not None
    }


def _normalise_value(value: Any) -> str | None:
    enum_value = getattr(value, "value", value)

    if not isinstance(enum_value, str):
        return None

    normalised = enum_value.strip().lower().replace("-", "_")

    return normalised or None


def _label(value: str | None) -> str:
    if value is None:
        return "Возможность"

    return value.replace("_", " ").title()


def _join_labels(values: list[str]) -> str:
    labels = [_label(value) for value in values]

    if len(labels) <= 1:
        return "".join(labels)
    if len(labels) == 2:
        return f"{labels[0]} и {labels[1]}"

    return f"{', '.join(labels[:-1])}, и {labels[-1]}"
