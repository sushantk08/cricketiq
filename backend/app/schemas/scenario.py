from typing import Optional
from pydantic import BaseModel, Field


class ScenarioSimulateRequest(BaseModel):
    current_score: int = Field(..., ge=0, description="Current runs scored")
    overs_completed: float = Field(
        ..., ge=0.0, le=20.0, description="Overs completed (e.g., 14.2)"
    )
    wickets_lost: int = Field(
        ..., ge=0, le=10, description="Wickets fallen (0-10)"
    )
    target_runs: Optional[int] = Field(
        None,
        ge=0,
        description="Target score if chasing (omit for 1st innings)",
    )
    total_overs: int = Field(
        20, ge=5, le=50, description="Total match overs (default 20)"
    )


class ScenarioSimulateResponse(BaseModel):
    current_score: int
    overs_completed: float
    balls_bowled: int
    balls_remaining: int
    wickets_lost: int
    wickets_in_hand: int
    current_run_rate: float
    projected_score: int
    target_runs: Optional[int] = None
    runs_required: Optional[int] = None
    required_run_rate: Optional[float] = None
    win_probability_batting: Optional[float] = None
    win_probability_bowling: Optional[float] = None
    risk_level: str  # 'LOW', 'MODERATE', 'HIGH', 'EXTREME'
    tactical_outlook: str