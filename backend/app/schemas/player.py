from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class PlayerBrief(BaseModel):
    id: int
    name: str
    role: str
    batting_style: Optional[str] = None
    bowling_style: Optional[str] = None
    team_id: Optional[int] = None

    class Config:
        from_attributes = True


class PhaseStats(BaseModel):
    runs: int
    balls: int
    strike_rate: float
    wickets: int


class BattingAnalytics(BaseModel):
    innings_batted: int
    total_runs: int
    balls_faced: int
    average: float
    strike_rate: float
    fours: int
    sixes: int
    dot_ball_pct: float
    boundary_run_pct: float
    phases: Dict[str, Dict[str, Any]]


class BowlingAnalytics(BaseModel):
    innings_bowled: int
    overs_bowled: float
    runs_conceded: int
    wickets: int
    economy: float
    bowling_strike_rate: Optional[float] = None
    dot_ball_pct: float
    phases: Dict[str, Dict[str, Any]]


class PlayerStatsResponse(BaseModel):
    player_id: int
    name: str
    role: str
    team_name: Optional[str] = None
    batting: Optional[BattingAnalytics] = None
    bowling: Optional[BowlingAnalytics] = None