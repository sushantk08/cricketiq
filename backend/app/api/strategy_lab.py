from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.schemas.strategy_lab import (
    StrategyLabRequest,
    StrategyLabResponse,
)
from backend.app.services.strategy_lab_service import run_strategy_lab


router = APIRouter(
    prefix="/api/strategy-lab",
    tags=["Strategy Lab"],
)


@router.post(
    "/analyze",
    response_model=StrategyLabResponse,
)
def analyze_strategy_lab(
    req: StrategyLabRequest,
    db: Session = Depends(get_db),
):
    try:
        return run_strategy_lab(db, req)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc