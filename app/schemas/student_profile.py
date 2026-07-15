from datetime import datetime
from typing import Optional, Literal

from pydantic import BaseModel, Field

class StudentSkill(BaseModel):
    skill: str
    level: Literal["novice", "beginner", "intermediate", "advanced", "expert"]

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