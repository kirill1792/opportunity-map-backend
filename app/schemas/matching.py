from enum import Enum

from pydantic import BaseModel, Field


class MatchCategory(str, Enum):
    READY_NOW = "ready_now"
    ALMOST_READY = "almost_ready"
    LONG_TERM = "long_term"
    NOT_RECOMMENDED = "not_recommended"


class EligibilityStatus(str, Enum):
    ELIGIBLE = "eligible"
    INELIGIBLE = "ineligible"
    UNKNOWN = "unknown"


class SkillRequirement(str, Enum):
    REQUIRED = "required"
    NICE_TO_HAVE = "nice_to_have"


class MatchedSkill(BaseModel):
    skill: str
    current_level: int = Field(ge=1, le=5)
    required_level: int = Field(ge=1, le=5)
    requirement: SkillRequirement


class MissingSkill(BaseModel):
    skill: str
    current_level: int = Field(ge=0, le=5)
    required_level: int = Field(ge=1, le=5)
    gap: int = Field(ge=1, le=5)
    requirement: SkillRequirement


class MatchingResult(BaseModel):
    total_score: int = Field(ge=0, le=100)

    category: MatchCategory
    eligibility_status: EligibilityStatus

    skill_score: int | None = Field(default=None, ge=0, le=100)
    interest_score: int | None = Field(default=None, ge=0, le=100)
    level_score: int | None = Field(default=None, ge=0, le=100)
    format_score: int | None = Field(default=None, ge=0, le=100)
    deadline_score: int | None = Field(default=None, ge=0, le=100)
    goal_score: int | None = Field(default=None, ge=0, le=100)
    effort_score: int | None = Field(default=None, ge=0, le=100)

    matched_skills: list[MatchedSkill] = Field(default_factory=list)
    missing_skills: list[MissingSkill] = Field(default_factory=list)
    nice_missing_skills: list[MissingSkill] = Field(default_factory=list)

    reasons: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    next_steps: list[str] = Field(default_factory=list)

    days_left: int | None = None
    is_urgent: bool = False