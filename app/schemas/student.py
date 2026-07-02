from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class StudentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    year_of_study: int = Field(ge=1, le=6)
    degree_direction: str = Field(min_length=1, max_length=150)

    country: str | None = Field(default=None, max_length=100)
    city: str | None = Field(default=None, max_length=100)

    experience_level: str = Field(pattern="^(beginner|intermediate|advanced)$")
    available_hours_per_week: int = Field(ge=0, le=80)


class StudentRead(BaseModel):
    id: int
    name: str
    year_of_study: int
    degree_direction: str
    country: str | None
    city: str | None
    experience_level: str
    available_hours_per_week: int
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }