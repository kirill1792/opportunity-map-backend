from datetime import datetime
from typing import Optional, Literal

from pydantic import BaseModel, Field, field_validator, model_validator

from app.core.taxonomy import validate_allowed_value, ALLOWED_SKILLS, validate_allowed_values, ALLOWED_FIELDS, \
    ALLOWED_PREFERRED_FORMATS, ALLOWED_GOALS


class StudentSkill(BaseModel):
    skill: str
    level: Literal["novice", "beginner", "intermediate", "advanced", "expert"]

    @field_validator("skill")
    @classmethod
    def validate_skill(cls, value: str) -> str:
        return validate_allowed_value(
            value=value,
            allowed_values=ALLOWED_SKILLS,
            field_name="skill",
        )


class StudentProfileCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    university: Optional[str] = Field(default=None, max_length=150)
    year_of_study: int = Field(ge=1, le=6)
    degree_direction: str = Field(min_length=1, max_length=150)

    interests: list[str] = Field(default_factory=list)
    skills: list[StudentSkill] = Field(default_factory=list)
    preferred_formats: list[str] = Field(default_factory=list)
    available_hours_per_week: int = Field(ge=0, le=80)
    goals: list[str] = Field(default_factory=list)
    experience_level: Literal["novice", "beginner", "intermediate", "advanced", "expert"]
    portfolio_links: list[str] = Field(default_factory=list)

    @field_validator("interests")
    @classmethod
    def validate_interests(cls, values: list[str]) -> list[str]:
        return validate_allowed_values(
            values=values,
            allowed_values=ALLOWED_FIELDS,
            field_name="interests",
        )

    @field_validator("preferred_formats")
    @classmethod
    def validate_preferred_formats(cls, values: list[str]) -> list[str]:
        return validate_allowed_values(
            values=values,
            allowed_values=ALLOWED_PREFERRED_FORMATS,
            field_name="preferred_formats",
        )

    @field_validator("goals")
    @classmethod
    def validate_goals(cls, values: list[str]) -> list[str]:
        return validate_allowed_values(
            values=values,
            allowed_values=ALLOWED_GOALS,
            field_name="goals",
        )

    @model_validator(mode="after")
    def validate_unique_skills(self) -> "StudentProfileCreate":
        skill_names = [student_skill.skill for student_skill in self.skills]

        if len(skill_names) != len(set(skill_names)):
            raise ValueError(
                "Student profile cannot contain duplicate skills"
            )

        return self



class StudentProfileUpdate(StudentProfileCreate):
    pass


class StudentProfileRead(StudentProfileCreate):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }