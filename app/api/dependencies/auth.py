from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User


def get_optional_current_user(
    x_dev_user_id: int | None = Header(
        default=None,
        alias="X-Dev-User-Id",
    ),
    db: Session = Depends(get_db),
) -> User | None:
    if x_dev_user_id is None:
        return None

    user = db.get(User, x_dev_user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid dev user",
        )

    return user


def get_current_user(
    current_user: User | None = Depends(get_optional_current_user),
) -> User:
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    return current_user