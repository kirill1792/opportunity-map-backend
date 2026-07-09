from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.student_profile import StudentProfile
from app.models.user import User
from app.schemas.auth import AuthSessionRead, DevLoginRequest
from app.schemas.student_profile import StudentProfileCreate

router = APIRouter(prefix="/dev/auth", tags=["dev-auth"])


@router.post("/register-profile", response_model=AuthSessionRead, status_code=201)
def register_profile(profile_data: StudentProfileCreate, db: Session = Depends(get_db)):
    user = User(
        auth_provider="dev_id"
    )

    db.add(user)
    db.flush()

    profile = StudentProfile(
        user_id=user.id,
        **profile_data.model_dump(),
    )

    db.add(profile)
    db.commit()
    db.refresh(user)
    db.refresh(profile)

    return AuthSessionRead(
        user_id=user.id,
        student_profile_id=profile.id
    )


@router.post("/login-by-id", response_model=AuthSessionRead)
def login_by_id(login_data: DevLoginRequest, db: Session = Depends(get_db)):
    user = db.get(User, login_data.user_id)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    profile = (
        db.query(StudentProfile)
        .filter(StudentProfile.user_id == user.id)
        .first()
    )

    if profile is None:
        raise HTTPException(status_code=404, detail="Student profile not found")

    return AuthSessionRead(
        user_id=user.id,
        student_profile_id=profile.id,
    )