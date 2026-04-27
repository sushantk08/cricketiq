from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class PendingUserItem(BaseModel):
    id: int
    email: str
    full_name: Optional[str] = None
    role: str
    verification_status: str
    has_id_document: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class VerifyUserRequest(BaseModel):
    action: str = Field(..., description="'APPROVE' or 'REJECT'")
    rejection_reason: Optional[str] = Field(
        None, description="Optional explanation if rejected"
    )