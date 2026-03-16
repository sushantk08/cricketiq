from typing import List, Optional
from pydantic import BaseModel, Field


class MatchupStats(BaseModel):
    batter_id: int
    batter_name: str
    bowler_id: int
    bowler_name: str
    balls_faced: int
    runs_scored: int
    dismissals: int
    strike_rate: float
    dot_ball_pct: float
    fours: int
    sixes: int
    advantage: str  # 'BATTER_FAVORED', 'BOWLER_FAVORED', 'BALANCED'


class BowlingStrategyRequest(BaseModel):
    batter_id: int = Field(..., description="ID of the batter at crease")
    bowling_team_id: int = Field(
        ..., description="Team ID of the bowling team"
    )
    match_phase: str = Field(
        "middle", description="Phase: 'powerplay', 'middle', or 'death'"
    )


class BowlerRecommendation(BaseModel):
    bowler_id: int
    bowler_name: str
    rank: int
    phase_economy: float
    matchup_advantage: str
    recommendation_score: float  # 0 to 100
    rationale: str


class BowlingStrategyResponse(BaseModel):
    batter_id: int
    batter_name: str
    match_phase: str
    recommendations: List[BowlerRecommendation]


class BattingStrategyRequest(BaseModel):
    bowler_id: int = Field(..., description="ID of the active bowler")
    match_phase: str = Field(
        "middle", description="'powerplay', 'middle', or 'death'"
    )
    required_run_rate: Optional[float] = Field(
        None, description="Current RRR if chasing"
    )


class BattingStrategyResponse(BaseModel):
    bowler_id: int
    bowler_name: str
    bowling_style: Optional[str] = None
    recommended_approach: (
        str  # 'AGGRESSIVE_ATTACK', 'STRIKE_ROTATION', 'CONSOLIDATION'
    )
    risk_level: str
    tactical_directive: str
    supporting_insight: str