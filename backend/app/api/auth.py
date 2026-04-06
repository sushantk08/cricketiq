import os
import shutil
import uuid
from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from backend.app.api.deps import get_current_user
from backend.app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from backend.app.database.session import get_db
from backend.app.models.user import User, UserRole, VerificationStatus
from backend.app.schemas.user import (
    Token,
    UserLogin,
    UserResponse,
)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

UPLOAD_DIR = os.path.join("backend", "uploads", "id_documents")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    email: str = Form(...),
    password: str = Form(...),
    full_name: str = Form(None),
    role: str = Form("FAN"),
    id_document: UploadFile = File(None),
    db: Session = Depends(get_db),
):
    role_upper = role.upper()

    # Prevent self-registration as ADMIN
    if role_upper == UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Admin accounts cannot be self-registered. Contact an"
                " existing administrator."
            ),
        )

    # Validate role
    if role_upper not in [r.value for r in UserRole]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role: {role}",
        )

    # Analysts and Coaches MUST upload an ID document
    if role_upper in [UserRole.ANALYST.value, UserRole.COACH.value]:
        if not id_document or not id_document.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Registration as {role_upper} requires uploading an ID"
                    " verification document."
                ),
            )

    # Check if email is taken
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists.",
        )

    # Save uploaded ID document if present
    saved_file_path = None
    if id_document and id_document.filename:
        file_ext = os.path.splitext(id_document.filename)[1]
        unique_filename = f"{uuid.uuid4().hex}{file_ext}"
        saved_file_path = os.path.join(UPLOAD_DIR, unique_filename)
        with open(saved_file_path, "wb") as buffer:
            shutil.copyfileobj(id_document.file, buffer)

    # Determine verification status
    if role_upper in [UserRole.ANALYST.value, UserRole.COACH.value]:
        status_val = VerificationStatus.PENDING.value
    else:
        status_val = VerificationStatus.APPROVED.value

    new_user = User(
        email=email,
        hashed_password=hash_password(password),
        full_name=full_name,
        role=UserRole(role_upper),
        verification_status=status_val,
        id_document_url=saved_file_path,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(
        credentials.password, user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
        )

    # Check verification status
    if user.verification_status == VerificationStatus.PENDING.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Your account is pending verification by an administrator."
                " Access will be granted once your ID document is reviewed."
            ),
        )
    elif user.verification_status == VerificationStatus.REJECTED.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Your account verification was rejected. Please contact"
                " support."
            ),
        )

    access_token = create_access_token(
        data={"sub": user.email, "role": user.role.value}
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    return current_user