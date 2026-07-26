from datetime import date, datetime
from typing import Any, Optional

from sqlalchemy import Boolean, Date, DateTime, Enum, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.enums import (
    OpportunityFormat,
    OpportunityLevel,
    OpportunityType,
)


class Opportunity(Base):
    __tablename__ = "opportunities"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    source_url: Mapped[str] = mapped_column(
        String(2048),
        nullable=False,
    )

    type: Mapped[OpportunityType] = mapped_column(
        Enum(
            OpportunityType,
            name="opportunity_type",
            values_callable=lambda enum_class: [
                item.value for item in enum_class
            ],
        ),
        nullable=False,
        index=True,
    )

    field: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    level: Mapped[OpportunityLevel] = mapped_column(
        Enum(
            OpportunityLevel,
            name="opportunity_level",
            values_callable=lambda enum_class: [
                item.value for item in enum_class
            ],
        ),
        nullable=False,
        default=OpportunityLevel.ANY,
        index=True,
    )

    image_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )


    format: Mapped[OpportunityFormat] = mapped_column(
        Enum(
            OpportunityFormat,
            name="opportunity_format",
            values_callable=lambda enum_class: [
                item.value for item in enum_class
            ],
        ),
        nullable=False,
        index=True,
    )

    location: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    deadline: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )

    start_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
    )

    end_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
    )

    language: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )

    is_paid: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        nullable=True,
    )

    estimated_effort: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    eligibility: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    required_skills: Mapped[dict[str, int]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )

    nice_to_have_skills: Mapped[dict[str, int]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )

    tags: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )