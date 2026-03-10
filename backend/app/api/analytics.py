from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.schemas.analytics import MatchTurningPointsResponse
from backend.app.services.turning_point_service import detect_turning_points

router = APIRouter(prefix="/api/matches", tags=["Analytics"])


@router.get(
    "/{match_id}/turning-points", response_model=MatchTurningPointsResponse
)
def get_match_turning_points(match_id: int, db: Session = Depends(get_db)):
    result = detect_turning_points(db, match_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "Match not found or incomplete innings for turning point"
                " analysis"
            ),
        )
    return result