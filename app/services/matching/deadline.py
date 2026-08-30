from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from math import ceil
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.opportunity import Opportunity


@dataclass(frozen=True)
class DeadlineScoreResult:
    score: int | None
    days_left: int | None
    is_urgent: bool
    is_expired: bool


def calculate_deadline_score(
    opportunity: Opportunity,
    *,
    now: datetime | None = None,
) -> DeadlineScoreResult:
    deadline = opportunity.deadline

    if not isinstance(deadline, datetime):
        return DeadlineScoreResult(
            score=None,
            days_left=None,
            is_urgent=False,
            is_expired=False,
        )

    current_time = _as_utc(now or datetime.now(timezone.utc))
    deadline_time = _as_utc(deadline)
    seconds_left = (deadline_time - current_time).total_seconds()

    if seconds_left < 0:
        days_left = -max(1, ceil(abs(seconds_left) / 86_400))

        return DeadlineScoreResult(
            score=0,
            days_left=days_left,
            is_urgent=False,
            is_expired=True,
        )

    days_left = ceil(seconds_left / 86_400)

    if days_left >= 14:
        score = 100
    elif days_left >= 7:
        score = 90
    elif days_left >= 3:
        score = 65
    elif days_left >= 1:
        score = 35
    else:
        score = 15

    return DeadlineScoreResult(
        score=score,
        days_left=days_left,
        is_urgent=days_left <= 3,
        is_expired=False,
    )


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)

    return value.astimezone(timezone.utc)
