from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class TeamBrief(BaseModel):
    id: int
    name: str
    short_name: str

    class Config:
        from_attributes = True


class VenueBrief(BaseModel):
    id: int
    name: str
    city: str
    country: str

    class Config:
        from_attributes = True


class MatchBrief(BaseModel):
    id: int
    title: str
    match_type: str
    status: str
    match_date: datetime
    team1: TeamBrief
    team2: TeamBrief
    venue: Optional[VenueBrief] = None
    winner_id: Optional[int] = None

    class Config:
        from_attributes = True


class BatterScorecard(BaseModel):
    player_id: int
    name: str
    runs: int
    balls: int
    fours: int
    sixes: int
    strike_rate: float
    dismissal: str


class BowlerScorecard(BaseModel):
    player_id: int
    name: str
    overs: float
    maidens: int
    runs_conceded: int
    wickets: int
    economy: float


class InningsScorecard(BaseModel):
    innings_number: int
    batting_team: str
    bowling_team: str
    total_runs: int
    total_wickets: int
    total_overs: float
    batting: List[BatterScorecard]
    bowling: List[BowlerScorecard]


class MatchScorecardResponse(BaseModel):
    match_id: int
    title: str
    status: str
    innings: List[InningsScorecard]


class DeliveryItem(BaseModel):
    id: int
    innings_number: int
    over_number: int
    ball_number: int
    batter_name: str
    bowler_name: str
    runs_batter: int
    runs_extras: int
    is_wicket: bool
    dismissal_type: Optional[str] = None
    cumulative_runs: int
    cumulative_wickets: int