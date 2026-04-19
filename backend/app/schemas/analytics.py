from typing import List
from pydantic import BaseModel


class TurningPointItem(BaseModel):
    over_number: int
    ball_number: int
    display_over: str  # e.g., "16.4"
    batter_name: str
    bowler_name: str
    event_summary: str
    win_prob_before: float
    win_prob_after: float
    win_prob_delta: float  # Positive = batting swing, Negative = bowling swing
    classification: (
        str  # CRITICAL_TURNING_POINT, MAJOR_SWING, MODERATE_SHIFT
    )


class MatchTurningPointsResponse(BaseModel):
    match_id: int
    chasing_team: str
    defending_team: str
    total_turning_points: int
    turning_points: List[TurningPointItem]

class PhaseAnalytics(BaseModel):
    runs: int
    balls: int
    run_rate: float


class InningsAnalytics(BaseModel):
    innings_number: int
    batting_team: str
    bowling_team: str
    runs: int
    wickets: int
    legal_balls: int
    run_rate: float
    fours: int
    sixes: int
    boundaries: int
    dot_balls: int
    dot_ball_percentage: float
    boundary_percentage: float
    phases: dict[str, PhaseAnalytics]


class MatchAnalyticsResponse(BaseModel):
    match_id: int
    title: str
    match_type: str
    status: str
    innings: List[InningsAnalytics]