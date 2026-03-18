from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.schemas.ai import (
    AskAnalystRequest,
    AskAnalystResponse,
    MatchAnalysisRequest,
    MatchAnalysisResponse,
    PlayerAnalysisRequest,
    PlayerAnalysisResponse,
)
from backend.app.services.ai_service import (
    answer_analyst_question,
    generate_match_analysis,
    generate_player_analysis,
)

router = APIRouter(prefix="/api/ai", tags=["AI Analyst"])


@router.post("/analyze-match", response_model=MatchAnalysisResponse)
def analyze_match(req: MatchAnalysisRequest, db: Session = Depends(get_db)):
    report = generate_match_analysis(db, req.match_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Match not found"
        )
    return report


@router.post("/analyze-player", response_model=PlayerAnalysisResponse)
def analyze_player(
    req: PlayerAnalysisRequest, db: Session = Depends(get_db)
):
    report = generate_player_analysis(db, req.player_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Player not found"
        )
    return report


@router.post("/ask", response_model=AskAnalystResponse)
def ask_cricketiq_analyst(
    req: AskAnalystRequest, db: Session = Depends(get_db)
):
    return answer_analyst_question(db, req)