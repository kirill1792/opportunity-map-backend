from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator, field_validator

from app.models.enums import (
    OpportunityFormat,
    OpportunityLevel,
    OpportunityType,
)

from app.core.taxonomy import (
    ALLOWED_FIELDS,
    validate_allowed_value,
    validate_disjoint_skill_groups,
    validate_skill_requirements,
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

    field: str = Field(
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

    @field_validator("field")
    @classmethod
    def validate_field(cls, value: str) -> str:
        return validate_allowed_value(
            value=value,
            allowed_values=ALLOWED_FIELDS,
            field_name="field",
        )

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
    def validate_skill_requirements_data(self) -> "OpportunityBase":
        self.required_skills = validate_skill_requirements(
            skills=self.required_skills,
            field_name="required_skills",
        )

        self.nice_to_have_skills = validate_skill_requirements(
            skills=self.nice_to_have_skills,
            field_name="nice_to_have_skills",
        )

        validate_disjoint_skill_groups(
            required_skills=self.required_skills,
            nice_to_have_skills=self.nice_to_have_skills,
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

    @field_validator("field")
    @classmethod
    def validate_field(cls, value: str | None) -> str | None:
        if value is None:
            return value

        return validate_allowed_value(
            value=value,
            allowed_values=ALLOWED_FIELDS,
            field_name="field",
        )

    @model_validator(mode="after")
    def validate_skill_requirements_data(self) -> "OpportunityUpdate":
        if self.required_skills is not None:
            self.required_skills = validate_skill_requirements(
                skills=self.required_skills,
                field_name="required_skills",
            )

        if self.nice_to_have_skills is not None:
            self.nice_to_have_skills = validate_skill_requirements(
                skills=self.nice_to_have_skills,
                field_name="nice_to_have_skills",
            )

        if (
                self.required_skills is not None
                and self.nice_to_have_skills is not None
        ):
            validate_disjoint_skill_groups(
                required_skills=self.required_skills,
                nice_to_have_skills=self.nice_to_have_skills,
            )

        return self


class OpportunityRead(OpportunityBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime