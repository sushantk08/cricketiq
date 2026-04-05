from typing import Any, Dict, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.api.deps import require_roles
from backend.app.database.session import get_db
from backend.app.integrations.cricket_api import cricket_adapter
from backend.app.models.user import User
from backend.app.schemas.cricket import MatchBrief

router = APIRouter(prefix="/api/sync", tags=["Cricket API Sync"])


@router.get("/external-live", response_model=List[Dict[str, Any]])
def get_external_live_matches():
  return cricket_adapter.fetch_live_fixtures()


@router.post("/matches", response_model=List[MatchBrief])
def sync_external_matches(
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_roles(["ADMIN"])),
):
  """Only users with the ADMIN role can trigger database synchronization."""
  fixtures = cricket_adapter.fetch_live_fixtures()
  synced = []
  for f in fixtures:
    m = cricket_adapter.sync_match_to_database(db, f)
    synced.append(m)
  return synced