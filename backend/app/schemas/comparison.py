from typing import Any, Dict, Optional

from pydantic import BaseModel


class PlayerComparisonResponse(BaseModel):
    player1_id: int
    player1_name: str
    player1_role: str
    player1_team: Optional[str] = None

    player2_id: int
    player2_name: str
    player2_role: str
    player2_team: Optional[str] = None

    player1_stats: Dict[str, Any]
    player2_stats: Dict[str, Any]

    better_batter: Optional[str] = None
    better_bowler: Optional[str] = None

    comparison_summary: str

    uncertainty_note: str = (
        "Player comparison is based on available CricketIQ "
        "historical statistics and should be treated as evidence, "
        "not a guarantee of future performance."
    )