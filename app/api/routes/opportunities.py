

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.taxonomy import validate_disjoint_skill_groups
from app.db.database import get_db
from app.models.enums import (
    OpportunityFormat,
    OpportunityLevel,
    OpportunityType,
)
from app.models.opportunity import Opportunity
from app.schemas.opportunity import (
    OpportunityCreate,
    OpportunityRead,
    OpportunityUpdate,
    OpportunityWithMatch,
)
from datetime import datetime, timezone

from app.api.dependencies.auth import get_optional_current_user
from app.models.student_profile import StudentProfile
from app.models.user import User
from app.services.matching.engine import match_opportunity


router = APIRouter(prefix="/opportunities", tags=["opportunities"])

def get_opportunity_or_404(
    db: Session,
    opportunity_id: int,
    *,
    include_inactive: bool = False,
) -> Opportunity:
    opportunity = db.get(Opportunity, opportunity_id)

    if opportunity is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity не найдена",
        )

    if not include_inactive and not opportunity.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity не найдена",
        )

    return opportunity


def convert_urls_to_strings(data: dict) -> dict:
    for field_name in ("source_url", "image_url"):
        value = data.get(field_name)

        if value is not None:
            data[field_name] = str(value)

    return data


@router.post(
    "",
    response_model=OpportunityRead,
    status_code=status.HTTP_201_CREATED,
)
def create_opportunity(
    opportunity_data: OpportunityCreate,
    db: Session = Depends(get_db),
) -> Opportunity:
    data = convert_urls_to_strings(
        opportunity_data.model_dump()
    )

    opportunity = Opportunity(**data)

    db.add(opportunity)
    db.commit()
    db.refresh(opportunity)

    return opportunity


@router.get(
    "",
    response_model=list[OpportunityWithMatch],
)
def get_opportunities(
    opportunity_type: OpportunityType | None = Query(
        default=None,
        alias="type",
    ),
    opportunity_format: OpportunityFormat | None = Query(
        default=None,
        alias="format",
    ),
    level: OpportunityLevel | None = None,
    field: str | None = None,
    search: str | None = Query(
        default=None,
        max_length=255,
    ),
    include_inactive: bool = False,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    current_user: User | None = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
) -> list[OpportunityWithMatch]:
    statement = select(Opportunity)

    if not include_inactive:
        statement = statement.where(
            Opportunity.is_active.is_(True)
        )

    if opportunity_type is not None:
        statement = statement.where(
            Opportunity.type == opportunity_type
        )

    if opportunity_format is not None:
        statement = statement.where(
            Opportunity.format == opportunity_format
        )

    if level is not None:
        statement = statement.where(
            Opportunity.level == level
        )

    if field is not None:
        statement = statement.where(
            Opportunity.field == field
        )

    if search is not None and search.strip():
        statement = statement.where(
            Opportunity.title.ilike(
                f"%{search.strip()}%"
            )
        )

    statement = (
        statement
        .order_by(Opportunity.created_at.desc())
        .offset(offset)
        .limit(limit)
    )

    # Здесь пока действительно ORM-объекты.
    opportunities = db.scalars(statement).all()

    profile = get_profile_for_user(
        db,
        current_user,
    )
    calculation_time = datetime.now(timezone.utc)

    # А здесь ORM преобразуется в API-схемы с optional matching.
    return [
        build_opportunity_response(
            opportunity,
            profile=profile,
            now=calculation_time,
        )
        for opportunity in opportunities
    ]

def get_profile_for_user(
    db: Session,
    current_user: User | None,
) -> StudentProfile | None:
    if current_user is None:
        return None

    return db.scalar(
        select(StudentProfile).where(
            StudentProfile.user_id == current_user.id
        )
    )


def build_opportunity_response(
    opportunity: Opportunity,
    *,
    profile: StudentProfile | None,
    now: datetime,
) -> OpportunityWithMatch:
    response = OpportunityWithMatch.model_validate(opportunity)

    if profile is not None:
        response.match = match_opportunity(
            profile,
            opportunity,
            now=now,
        )

    return response

@router.get(
    "/{opportunity_id}",
    response_model=OpportunityWithMatch,
)
def get_opportunity(
    opportunity_id: int,
    current_user: User | None = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
) -> OpportunityWithMatch:
    opportunity = get_opportunity_or_404(
        db,
        opportunity_id,
    )

    profile = get_profile_for_user(
        db,
        current_user,
    )

    return build_opportunity_response(
        opportunity,
        profile=profile,
        now=datetime.now(timezone.utc),
    )


@router.patch(
    "/{opportunity_id}",
    response_model=OpportunityRead,
)
def update_opportunity(
    opportunity_id: int,
    opportunity_data: OpportunityUpdate,
    db: Session = Depends(get_db),
) -> Opportunity:

    opportunity = get_opportunity_or_404(
        db,
        opportunity_id,
        include_inactive=True,
    )

    update_data = opportunity_data.model_dump(
        exclude_unset=True,
    )
    update_data = convert_urls_to_strings(update_data)

    new_start_date = update_data.get(
        "start_date",
        opportunity.start_date,
    )
    new_end_date = update_data.get(
        "end_date",
        opportunity.end_date,
    )

    final_required_skills = update_data.get(
        "required_skills",
        opportunity.required_skills,
    )
    final_nice_to_have_skills = update_data.get(
        "nice_to_have_skills",
        opportunity.nice_to_have_skills,
    )

    try:
        validate_disjoint_skill_groups(
            required_skills=final_required_skills,
            nice_to_have_skills=final_nice_to_have_skills,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    if (
        new_start_date is not None
        and new_end_date is not None
        and new_end_date < new_start_date
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="end_date не может быть раньше start_date",
        )

    for field_name, value in update_data.items():
        setattr(opportunity, field_name, value)

    db.commit()
    db.refresh(opportunity)

    return opportunity


@router.delete(
    "/{opportunity_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_opportunity(
    opportunity_id: int,
    db: Session = Depends(get_db),
) -> None:
    opportunity = get_opportunity_or_404(
        db,
        opportunity_id,
        include_inactive=True,
    )

    opportunity.is_active = False

    db.commit()
