from typing import List
from pydantic import BaseModel, Field


class WinProbabilityRequest(BaseModel):
    runs_required: int = Field(
        ..., ge=0, description="Runs needed to win the match"
    )
    balls_remaining: int = Field(
        ..., ge=0, le=120, description="Legal deliveries remaining"
    )
    wickets_in_hand: int = Field(
        ..., ge=0, le=10, description="Remaining wickets"
    )


class WinProbabilityResponse(BaseModel):
    runs_required: int
    balls_remaining: int
    wickets_in_hand: int
    required_run_rate: float
    win_probability_batting: float
    win_probability_bowling: float


class BallProbabilityPoint(BaseModel):
    over: int
    ball: int
    score: int
    wickets: int
    runs_required: int
    balls_remaining: int
    batting_win_prob: float
    bowling_win_prob: float


class MatchWinProbabilityCurve(BaseModel):
    match_id: int
    chasing_team: str
    defending_team: str
    target: int
    curve: List[BallProbabilityPoint]

class HistoricalModelEvaluationResponse(BaseModel):
    rows: int
    accuracy: float
    brier_score: float
    train_start_date: str
    train_end_date: str
    test_start_date: str
    test_end_date: str