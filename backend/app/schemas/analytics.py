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