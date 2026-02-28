from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.security import hash_password
from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.schemas.user import UserCreate, UserResponse

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    # Check if the email is already registered
    existing_user = (
        db.query(User).filter(User.email == user_in.email).first()
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists.",
        )

    # Hash password and persist user
    new_user = User(
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        full_name=user_in.full_name,
        role=user_in.role or "FAN",
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user