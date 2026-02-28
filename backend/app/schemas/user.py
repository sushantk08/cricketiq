from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr
from backend.app.models.user import UserRole


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    role: Optional[UserRole] = UserRole.FAN


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str] = None
    role: UserRole
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True