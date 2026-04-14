from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.models.cricket import Team
from backend.app.schemas.cricket import TeamBrief


router = APIRouter(prefix="/api/teams", tags=["Teams"])


@router.get("", response_model=List[TeamBrief])
def list_teams(db: Session = Depends(get_db)):
    return db.query(Team).order_by(Team.name).all()