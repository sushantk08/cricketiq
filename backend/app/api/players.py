from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.models.cricket import Player
from backend.app.schemas.player import PlayerBrief, PlayerStatsResponse
from backend.app.services.player_service import compute_player_analytics
from backend.app.schemas.player_intelligence import PlayerIntelligenceResponse
from backend.app.services.player_intelligence_service import (
    generate_player_intelligence,
)

router = APIRouter(prefix="/api/players", tags=["Players"])


@router.get("", response_model=List[PlayerBrief])
def list_players(
    team_id: Optional[int] = Query(None, description="Filter by team ID"),
    role: Optional[str] = Query(None, description="Filter by player role"),
    db: Session = Depends(get_db),
):
    query = db.query(Player)
    if team_id:
        query = query.filter(Player.team_id == team_id)
    if role:
        query = query.filter(Player.role == role.upper())
    return query.order_by(Player.name).all()


@router.get("/{player_id}", response_model=PlayerBrief)
def get_player(player_id: int, db: Session = Depends(get_db)):
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Player not found"
        )
    return player


@router.get("/{player_id}/stats", response_model=PlayerStatsResponse)
def get_player_statistics(player_id: int, db: Session = Depends(get_db)):
    stats = compute_player_analytics(db, player_id)
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Player not found"
        )
    return stats

@router.get(
    "/{player_id}/intelligence",
    response_model=PlayerIntelligenceResponse,
)
def get_player_intelligence(
    player_id: int,
    db: Session = Depends(get_db),
):
    intelligence = generate_player_intelligence(db, player_id)

    if not intelligence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found",
        )

    return intelligence