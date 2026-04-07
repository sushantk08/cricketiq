import os
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.app.api.deps import require_roles
from backend.app.database.session import get_db
from backend.app.models.user import User, VerificationStatus
from backend.app.schemas.admin import PendingUserItem, VerifyUserRequest
from backend.app.schemas.user import UserResponse

router = APIRouter(prefix="/api/admin", tags=["Admin Management"])


@router.get(
    "/pending-verifications", response_model=List[PendingUserItem]
)
def get_pending_verifications(
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_roles(["ADMIN"])),
):
    """List all users awaiting administrator approval."""
    pending_users = (
        db.query(User)
        .filter(
            User.verification_status == VerificationStatus.PENDING.value
        )
        .order_by(User.created_at.desc())
        .all()
    )

    return [
        PendingUserItem(
            id=u.id,
            email=u.email,
            full_name=u.full_name,
            role=u.role.value,
            verification_status=u.verification_status,
            has_id_document=bool(u.id_document_url),
            created_at=u.created_at,
        )
        for u in pending_users
    ]


@router.get("/users/{user_id}/document")
def view_uploaded_id_document(
    user_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_roles(["ADMIN"])),
):
    """Stream the uploaded ID document file so the admin can review it."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.id_document_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No ID document found for this user.",
        )

    if not os.path.exists(user.id_document_url):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The document file is missing on the server disk.",
        )

    return FileResponse(
        path=user.id_document_url,
        filename=f"user_{user.id}_id_document"
        + os.path.splitext(user.id_document_url)[1],
    )


@router.post("/users/{user_id}/verify", response_model=UserResponse)
def verify_user(
    user_id: int,
    req: VerifyUserRequest,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_roles(["ADMIN"])),
):
    """Approve or reject a user account."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    action_upper = req.action.upper()
    if action_upper == "APPROVE":
        user.verification_status = VerificationStatus.APPROVED.value
        user.is_active = True
    elif action_upper == "REJECT":
        user.verification_status = VerificationStatus.REJECTED.value
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Action must be either 'APPROVE' or 'REJECT'.",
        )

    db.commit()
    db.refresh(user)
    return user