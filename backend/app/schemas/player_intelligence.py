from typing import List, Optional

from pydantic import BaseModel


class PlayerInsight(BaseModel):
    category: str
    title: str
    detail: str


class PlayerIntelligenceResponse(BaseModel):
    player_id: int
    player_name: str
    role: str
    team_name: Optional[str] = None

    overall_assessment: str

    strengths: List[PlayerInsight]
    weaknesses: List[PlayerInsight]
    recommendations: List[PlayerInsight]

    evidence_summary: str