from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.student_profile import StudentProfile
from app.models.user import User
from app.schemas.student_profile import StudentProfileRead, StudentProfileUpdate

router = APIRouter(prefix="/profile", tags=["profile"])


def get_current_dev_user(
    x_dev_user_id: int = Header(alias="X-Dev-User-Id"),
    db: Session = Depends(get_db),
) -> User:
    user = db.get(User, x_dev_user_id)

    if user is None:
        raise HTTPException(status_code=401, detail="Invalid dev user")

    return user


@router.get("/me", response_model=StudentProfileRead)
def get_my_profile(
    current_user: User = Depends(get_current_dev_user),
    db: Session = Depends(get_db),
):
    profile = (
        db.query(StudentProfile)
        .filter(StudentProfile.user_id == current_user.id)
        .first()
    )

    if profile is None:
        raise HTTPException(status_code=404, detail="Student profile not found")

    return profile


@router.put("/me", response_model=StudentProfileRead)
def update_my_profile(
    profile_data: StudentProfileUpdate,
    current_user: User = Depends(get_current_dev_user),
    db: Session = Depends(get_db),
):
    profile = (
        db.query(StudentProfile)
        .filter(StudentProfile.user_id == current_user.id)
        .first()
    )

    if profile is None:
        raise HTTPException(status_code=404, detail="Student profile not found")

    for field, value in profile_data.model_dump().items():
        setattr(profile, field, value)

    #current_user.display_name = profile_data.name

    db.commit()
    db.refresh(profile)

    return profile