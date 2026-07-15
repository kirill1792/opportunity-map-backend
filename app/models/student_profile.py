from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        unique=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(100), nullable=False)

    university: Mapped[str] = mapped_column(String(100), nullable=True)
    degree_direction: Mapped[str] = mapped_column(String(150), nullable=False)
    year_of_study: Mapped[int] = mapped_column(Integer, nullable=False)

    experience_level: Mapped[str] = mapped_column(String(50), nullable=False)
    available_hours_per_week: Mapped[int] = mapped_column(Integer, nullable=False)

    interests: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    skills: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    preferred_formats: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    goals: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    portfolio_links: Mapped[list] = mapped_column(JSON, nullable=False, default=list)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    user = relationship("User", back_populates="student_profile")