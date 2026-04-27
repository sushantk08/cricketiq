from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class DecisionPoint(BaseModel):
    over_number: int
    display_over: str
    batter_id: int
    batter_name: str
    actual_bowler_id: int
    actual_bowler_name: str
    score_at_time: int
    wickets_at_time: int
    runs_required: int
    balls_remaining: int
    context_reason: str


class DecisionReplayRequest(BaseModel):
    match_id: int = Field(..., description="ID of the match")
    over_number: int = Field(
        ..., ge=0, le=19, description="Over to replay (0-19)"
    )
    alternative_bowler_id: int = Field(
        ..., description="Player ID of the alternative bowler"
    )


class DecisionReplayResponse(BaseModel):
    replay_id: int
    match_id: int
    over_number: int
    display_over: str
    batter_name: str
    actual_bowler_name: str
    alternative_bowler_name: str
    actual_win_prob: float
    alternative_win_prob: float
    decision_impact: float  # Difference in percentage points
    expected_runs_actual: float
    expected_runs_alternative: float
    decision_quality_score: float  # 0 to 100
    tactical_verdict: str
    explanation: str
    uncertainty_disclaimer: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)