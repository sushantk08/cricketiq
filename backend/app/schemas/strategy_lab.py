from typing import List, Optional

from pydantic import BaseModel, Field


class StrategyLabRequest(BaseModel):
    batter_id: int = Field(
        ...,
        description="Current batter ID",
    )

    bowling_team_id: int = Field(
        ...,
        description="Bowling team ID",
    )

    current_score: int = Field(
        ...,
        ge=0,
        description="Current score",
    )

    overs_completed: float = Field(
        ...,
        ge=0.0,
        le=50.0,
        description="Overs completed",
    )

    wickets_lost: int = Field(
        ...,
        ge=0,
        le=10,
        description="Wickets lost",
    )

    target_runs: Optional[int] = Field(
        None,
        ge=0,
        description="Target score when chasing",
    )

    total_overs: int = Field(
        20,
        ge=5,
        le=50,
        description="Total match overs",
    )

    match_phase: str = Field(
        "middle",
        description="Match phase: powerplay, middle, or death",
    )


class StrategyOption(BaseModel):
    rank: int

    bowler_id: int
    bowler_name: str

    recommendation_score: float
    matchup_advantage: str
    phase_economy: float

    projected_batting_win_probability: Optional[float] = None

    risk_level: str

    tactical_directive: str
    rationale: str


class StrategyLabResponse(BaseModel):
    batter_id: int
    batter_name: str

    current_score: int
    overs_completed: float
    wickets_lost: int

    target_runs: Optional[int] = None

    match_phase: str

    options: List[StrategyOption]

    recommended_option: Optional[StrategyOption] = None

    decision_summary: str

    uncertainty_note: str = (
        "Strategy options use CricketIQ model estimates and historical "
        "evidence. They are decision-support signals, not guarantees."
    )