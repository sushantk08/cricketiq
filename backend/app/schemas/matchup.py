from typing import List, Optional

from pydantic import BaseModel


class MatchupInsight(BaseModel):
    category: str
    title: str
    detail: str


class MatchupResponse(BaseModel):
    batter_id: int
    batter_name: str

    bowler_id: int
    bowler_name: str

    matches: int
    balls: int
    runs: int
    strike_rate: float

    dot_ball_percentage: float
    fours: int
    sixes: int

    dismissals: int

    phase_stats: dict[str, dict]

    assessment: str

    insights: List[MatchupInsight]

    uncertainty_note: str = (
        "Matchup statistics are based on available historical Cricsheet "
        "delivery data and should be treated as historical evidence, "
        "not a guarantee of future performance."
    )