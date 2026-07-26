from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator

from app.models.enums import (
    OpportunityFormat,
    OpportunityLevel,
    OpportunityType,
)


class OpportunityBase(BaseModel):
    title: str = Field(
        min_length=2,
        max_length=255,
    )

    description: str | None = None

    source_url: HttpUrl

    type: OpportunityType

    image_url: HttpUrl | None = None

    field: str | None = Field(
        default=None,
        max_length=100,
    )

    level: OpportunityLevel = OpportunityLevel.ANY

    format: OpportunityFormat

    location: str | None = Field(
        default=None,
        max_length=255,
    )

    deadline: datetime | None = None

    start_date: date | None = None
    end_date: date | None = None

    language: str | None = Field(
        default=None,
        max_length=50,
    )

    is_paid: bool | None = None

    estimated_effort: int | None = Field(
        default=None,
        ge=0,
        description="Ожидаемая нагрузка в часах в неделю",
    )

    eligibility: str | None = None

    required_skills: dict[str, int] = Field(default_factory=dict)
    nice_to_have_skills: dict[str, int] = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_dates(self) -> "OpportunityBase":
        if (
            self.start_date is not None
            and self.end_date is not None
            and self.end_date < self.start_date
        ):
            raise ValueError(
                "end_date не может быть раньше start_date"
            )

        return self

    @model_validator(mode="after")
    def validate_skill_levels(self) -> "OpportunityBase":
        skill_groups = {
            "required_skills": self.required_skills,
            "nice_to_have_skills": self.nice_to_have_skills,
        }

        for field_name, skills in skill_groups.items():
            for skill_name, level in skills.items():
                if not skill_name.strip():
                    raise ValueError(
                        f"{field_name} не может содержать пустое название навыка"
                    )

                if not 0 <= level <= 5:
                    raise ValueError(
                        f"Уровень навыка '{skill_name}' должен быть от 0 до 5"
                    )

        return self


class OpportunityCreate(OpportunityBase):
    pass


class OpportunityUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=2,
        max_length=255,
    )

    description: str | None = None
    source_url: HttpUrl | None = None

    type: OpportunityType | None = None

    field: str | None = Field(
        default=None,
        max_length=100,
    )

    level: OpportunityLevel | None = None
    format: OpportunityFormat | None = None

    location: str | None = Field(
        default=None,
        max_length=255,
    )

    deadline: datetime | None = None
    start_date: date | None = None
    end_date: date | None = None

    language: str | None = Field(
        default=None,
        max_length=50,
    )

    is_paid: bool | None = None

    estimated_effort: int | None = Field(
        default=None,
        ge=0,
    )

    eligibility: str | None = None

    required_skills: dict[str, int] | None = None
    nice_to_have_skills: dict[str, int] | None = None
    tags: list[str] | None = None

    is_active: bool | None = None

    image_url: HttpUrl | None = None


class OpportunityRead(OpportunityBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime