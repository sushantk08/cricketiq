from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.ml.historical_win_probability import historical_win_predictor
from backend.app.models.cricket import Delivery, Innings, Match
from backend.app.schemas.prediction import (
    BallProbabilityPoint,
    HistoricalModelEvaluationResponse,
    MatchWinProbabilityCurve,
    WinProbabilityRequest,
    WinProbabilityResponse,
)

router = APIRouter(prefix="/api/predictions", tags=["Predictions"])

@router.get(
    "/historical-model/evaluation",
    response_model=HistoricalModelEvaluationResponse,
)
def get_historical_model_evaluation():
    """Return evaluation metrics for the historical win-probability model."""
    evaluation = historical_win_predictor.evaluate()

    return HistoricalModelEvaluationResponse(**evaluation)


@router.post(
    "/win-probability",
    response_model=WinProbabilityResponse,
)
def predict_win_probability(
    request: WinProbabilityRequest,
    db: Session = Depends(get_db),
):
    """
    Predict the chasing team's win probability using the
    historical Cricsheet-trained model.
    """

    required_run_rate = (
        (request.runs_required / request.balls_remaining) * 6
        if request.balls_remaining > 0
        else 0.0
    )

    batting_probability = historical_win_predictor.predict(
        request.runs_required,
        request.balls_remaining,
        request.wickets_in_hand,
    )

    batting_probability = round(batting_probability, 2)
    bowling_probability = round(100.0 - batting_probability, 2)

    return WinProbabilityResponse(
        runs_required=request.runs_required,
        balls_remaining=request.balls_remaining,
        wickets_in_hand=request.wickets_in_hand,
        required_run_rate=round(required_run_rate, 2),
        win_probability_batting=batting_probability,
        win_probability_bowling=bowling_probability,
    )


@router.get(
    "/match/{match_id}/win-probability",
    response_model=MatchWinProbabilityCurve,
)
def get_match_win_probability_curve(
    match_id: int,
    db: Session = Depends(get_db),
):
    """
    Generate a ball-by-ball win probability curve for a match.

    The second innings is treated as the chasing innings.
    Historical ML probability is calculated after each delivery.
    """

    match = db.query(Match).filter(Match.id == match_id).first()

    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found",
        )

    innings_list = (
        db.query(Innings)
        .filter(Innings.match_id == match_id)
        .order_by(Innings.innings_number)
        .all()
    )

    if len(innings_list) < 2:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match does not contain two innings",
        )

    first_innings = innings_list[0]
    second_innings = innings_list[1]

    first_innings_deliveries = (
        db.query(Delivery)
        .filter(Delivery.innings_id == first_innings.id)
        .order_by(Delivery.over, Delivery.ball)
        .all()
    )

    second_innings_deliveries = (
        db.query(Delivery)
        .filter(Delivery.innings_id == second_innings.id)
        .order_by(Delivery.over, Delivery.ball)
        .all()
    )

    if not first_innings_deliveries or not second_innings_deliveries:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match does not contain delivery data",
        )

    target = sum(
        (delivery.runs_batter or 0) + (delivery.runs_extras or 0)
        for delivery in first_innings_deliveries
    ) + 1

    chasing_team = second_innings.batting_team
    defending_team = first_innings.batting_team

    curve = []
    current_score = 0
    wickets_lost = 0

    for delivery in second_innings_deliveries:
        current_score += (
            (delivery.runs_batter or 0)
            + (delivery.runs_extras or 0)
        )

        if delivery.is_wicket:
            wickets_lost += 1

        runs_required = max(0, target - current_score)

        balls_completed = (
            delivery.over * 6
            + delivery.ball
        )

        balls_remaining = max(0, 120 - balls_completed)
        wickets_in_hand = max(0, 10 - wickets_lost)

        batting_probability = historical_win_predictor.predict(
            runs_required,
            balls_remaining,
            wickets_in_hand,
        )

        batting_probability = round(batting_probability, 2)
        bowling_probability = round(
            100.0 - batting_probability,
            2,
        )

        curve.append(
            BallProbabilityPoint(
                over=delivery.over,
                ball=delivery.ball,
                score=current_score,
                wickets=wickets_lost,
                runs_required=runs_required,
                balls_remaining=balls_remaining,
                batting_win_prob=batting_probability,
                bowling_win_prob=bowling_probability,
            )
        )

    return MatchWinProbabilityCurve(
        match_id=match_id,
        chasing_team=chasing_team,
        defending_team=defending_team,
        target=target,
        curve=curve,
    )