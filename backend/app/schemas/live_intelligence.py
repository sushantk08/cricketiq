from typing import List, Optional

from pydantic import BaseModel


class LiveInsight(BaseModel):
    category: str
    title: str
    detail: str


class LiveMatchIntelligence(BaseModel):
    external_id: str
    title: str
    match_type: str
    status: str

    team1_name: str
    team2_name: str

    formatted_score: str
    status_note: str
    venue_name: str

    current_innings: Optional[str] = None
    current_score: Optional[int] = None
    current_wickets: Optional[int] = None
    current_overs: Optional[float] = None

    projected_score: Optional[int] = None
    required_run_rate: Optional[float] = None

    win_probability_batting: Optional[float] = None
    win_probability_bowling: Optional[float] = None

    insights: List[LiveInsight]

    decision_summary: str

    uncertainty_note: str = (
        "Live intelligence is based on the currently available score feed "
        "and CricketIQ models. Probabilities and projections are estimates, "
        "not guarantees."
    )