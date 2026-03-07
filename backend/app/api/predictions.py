from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.ml.win_probability import win_predictor
from backend.app.models.cricket import Delivery, Innings, Match
from backend.app.schemas.prediction import (
    BallProbabilityPoint,
    MatchWinProbabilityCurve,
    WinProbabilityRequest,
    WinProbabilityResponse,
)

router = APIRouter(prefix="/api/predictions", tags=["Predictions"])


@router.post("/win-probability", response_model=WinProbabilityResponse)
def calculate_win_probability(req: WinProbabilityRequest):
    prob_batting = win_predictor.predict(
        runs_required=req.runs_required,
        balls_remaining=req.balls_remaining,
        wickets_in_hand=req.wickets_in_hand,
    )
    rrr = (
        round((req.runs_required / req.balls_remaining) * 6.0, 2)
        if req.balls_remaining > 0
        else 0.0
    )

    return {
        "runs_required": req.runs_required,
        "balls_remaining": req.balls_remaining,
        "wickets_in_hand": req.wickets_in_hand,
        "required_run_rate": rrr,
        "win_probability_batting": round(prob_batting * 100, 2),
        "win_probability_bowling": round((1.0 - prob_batting) * 100, 2),
    }


@router.get(
    "/matches/{match_id}/curve", response_model=MatchWinProbabilityCurve
)
def get_match_probability_curve(
    match_id: int, db: Session = Depends(get_db)
):
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Match not found"
        )

    inn1 = (
        db.query(Innings)
        .filter(Innings.match_id == match_id, Innings.innings_number == 1)
        .first()
    )
    inn2 = (
        db.query(Innings)
        .filter(Innings.match_id == match_id, Innings.innings_number == 2)
        .first()
    )
    if not inn1 or not inn2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Match does not have both innings recorded",
        )

    target = inn1.total_runs + 1
    deliveries = (
        db.query(Delivery)
        .filter(Delivery.innings_id == inn2.id)
        .order_by(Delivery.over_number, Delivery.ball_number)
        .all()
    )

    curve = []
    total_balls = 120
    legal_balls_bowled = 0

    for d in deliveries:
        if d.extra_type not in ["wide", "noball"]:
            legal_balls_bowled += 1

        balls_remaining = max(0, total_balls - legal_balls_bowled)
        runs_required = max(0, target - d.cumulative_runs)
        wickets_in_hand = max(0, 10 - d.cumulative_wickets)

        batting_prob = win_predictor.predict(
            runs_required=runs_required,
            balls_remaining=balls_remaining,
            wickets_in_hand=wickets_in_hand,
        )

        curve.append(
            BallProbabilityPoint(
                over=d.over_number,
                ball=d.ball_number,
                score=d.cumulative_runs,
                wickets=d.cumulative_wickets,
                runs_required=runs_required,
                balls_remaining=balls_remaining,
                batting_win_prob=round(batting_prob * 100, 2),
                bowling_win_prob=round((1.0 - batting_prob) * 100, 2),
            )
        )

    return {
        "match_id": match.id,
        "chasing_team": inn2.batting_team.name,
        "defending_team": inn2.bowling_team.name,
        "target": target,
        "curve": curve,
    }