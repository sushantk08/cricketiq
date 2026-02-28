import enum
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Enum, Integer, String
from backend.app.database.session import Base


class UserRole(str, enum.Enum):
    FAN = "FAN"
    ANALYST = "ANALYST"
    COACH = "COACH"
    ADMIN = "ADMIN"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    role = Column(
        Enum(UserRole, name="user_roles"),
        default=UserRole.FAN,
        nullable=False,
    )
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)