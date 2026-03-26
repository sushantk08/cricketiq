from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.models.cricket import DecisionReplayRecord
from backend.app.schemas.replay import (
    DecisionPoint,
    DecisionReplayRequest,
    DecisionReplayResponse,
)
from backend.app.services.replay_service import (
    get_match_decision_points,
    simulate_decision_replay,
)

router = APIRouter(tags=["Decision Replay"])


@router.get(
    "/api/matches/{match_id}/decision-points",
    response_model=List[DecisionPoint],
)
def list_decision_points(match_id: int, db: Session = Depends(get_db)):
    return get_match_decision_points(db, match_id)


@router.post("/api/replay/simulate", response_model=DecisionReplayResponse)
def run_replay(req: DecisionReplayRequest, db: Session = Depends(get_db)):
    return simulate_decision_replay(db, req)


@router.get("/api/replay/{replay_id}", response_model=DecisionReplayResponse)
def get_saved_replay(replay_id: int, db: Session = Depends(get_db)):
    rec = (
        db.query(DecisionReplayRecord)
        .filter(DecisionReplayRecord.id == replay_id)
        .first()
    )
    if not rec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Replay record not found",
        )

    disclaimer = (
        "Statistical estimate derived from historical phase distributions and"
        " model predictions; does not guarantee counterfactual certainty."
    )

    return DecisionReplayResponse(
        replay_id=rec.id,
        match_id=rec.match_id,
        over_number=rec.over_number,
        display_over=f"{rec.over_number}.0",
        batter_name=rec.batter.name,
        actual_bowler_name=rec.actual_bowler.name,
        alternative_bowler_name=rec.alternative_bowler.name,
        actual_win_prob=rec.actual_win_prob,
        alternative_win_prob=rec.alternative_win_prob,
        decision_impact=rec.decision_impact,
        expected_runs_actual=rec.expected_runs_actual,
        expected_runs_alternative=rec.expected_runs_alternative,
        decision_quality_score=rec.decision_quality_score,
        tactical_verdict=(
            f"Saved Analysis: Decision Impact {rec.decision_impact:+.1f} pts"
        ),
        explanation=rec.explanation,
        uncertainty_disclaimer=disclaimer,
        created_at=rec.created_at,
    )