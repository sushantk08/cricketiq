from typing import List, Optional
from pydantic import BaseModel, Field


class MatchAnalysisRequest(BaseModel):
    match_id: int = Field(..., description="ID of the match to analyze")


class MatchAnalysisResponse(BaseModel):
    match_id: int
    match_title: str
    winner: str
    summary: str
    best_batter: str
    best_bowler: str
    turning_point_insights: List[str]
    tactical_verdict: str
    grounded_in_database_facts: bool


class PlayerAnalysisRequest(BaseModel):
    player_id: int = Field(..., description="ID of the player")


class PlayerAnalysisResponse(BaseModel):
    player_id: int
    player_name: str
    role: str
    scouting_report: str
    strengths: List[str]
    tactical_recommendations: List[str]


class AskAnalystRequest(BaseModel):
    match_id: Optional[int] = Field(
        None, description="Optional match context"
    )
    question: str = Field(
        ..., min_length=5, description="Cricket strategy question"
    )


class AskAnalystResponse(BaseModel):
    question: str
    answer: str
    referenced_data: List[str]