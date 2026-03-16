from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.schemas.strategy import (
    BattingStrategyRequest,
    BattingStrategyResponse,
    BowlingStrategyRequest,
    BowlingStrategyResponse,
    MatchupStats,
)
from backend.app.services.strategy_service import (
    get_head_to_head_matchup,
    recommend_batting_strategy,
    recommend_bowling_options,
)

router = APIRouter(tags=["Strategy & Matchups"])


@router.get("/api/matchups", response_model=MatchupStats)
def get_matchup(
    batter_id: int = Query(..., description="ID of batter"),
    bowler_id: int = Query(..., description="ID of bowler"),
    db: Session = Depends(get_db),
):
    matchup = get_head_to_head_matchup(db, batter_id, bowler_id)
    if not matchup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batter or Bowler not found",
        )
    return matchup


@router.post(
    "/api/strategy/bowling", response_model=BowlingStrategyResponse
)
def get_bowling_strategy(
    req: BowlingStrategyRequest, db: Session = Depends(get_db)
):
    res = recommend_bowling_options(db, req)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Batter not found"
        )
    return res


@router.post(
    "/api/strategy/batting", response_model=BattingStrategyResponse
)
def get_batting_strategy(
    req: BattingStrategyRequest, db: Session = Depends(get_db)
):
    res = recommend_batting_strategy(db, req)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Bowler not found"
        )
    return res