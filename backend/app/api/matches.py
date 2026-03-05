from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.models.cricket import Delivery, Match
from backend.app.schemas.cricket import (
    DeliveryItem,
    MatchBrief,
    MatchScorecardResponse,
)
from backend.app.services.match_service import compute_match_scorecard

router = APIRouter(prefix="/api/matches", tags=["Matches"])


@router.get("", response_model=List[MatchBrief])
def get_matches(db: Session = Depends(get_db)):
    return db.query(Match).order_by(Match.match_date.desc()).all()


@router.get("/{match_id}", response_model=MatchBrief)
def get_match_by_id(match_id: int, db: Session = Depends(get_db)):
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Match not found"
        )
    return match


@router.get(
    "/{match_id}/scorecard", response_model=MatchScorecardResponse
)
def get_scorecard(match_id: int, db: Session = Depends(get_db)):
    scorecard = compute_match_scorecard(db, match_id)
    if not scorecard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Match not found"
        )
    return scorecard


@router.get("/{match_id}/deliveries", response_model=List[DeliveryItem])
def get_deliveries(match_id: int, db: Session = Depends(get_db)):
    deliveries = (
        db.query(Delivery)
        .filter(Delivery.match_id == match_id)
        .order_by(
            Delivery.innings_id, Delivery.over_number, Delivery.ball_number
        )
        .all()
    )
    if not deliveries:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No deliveries found for this match",
        )

    result = []
    for d in deliveries:
        result.append(
            DeliveryItem(
                id=d.id,
                innings_number=d.innings.innings_number,
                over_number=d.over_number,
                ball_number=d.ball_number,
                batter_name=d.batter.name,
                bowler_name=d.bowler.name,
                runs_batter=d.runs_batter,
                runs_extras=d.runs_extras,
                is_wicket=d.is_wicket,
                dismissal_type=d.dismissal_type,
                cumulative_runs=d.cumulative_runs,
                cumulative_wickets=d.cumulative_wickets,
            )
        )
    return result