import os
from typing import Any, Dict, List, Optional
import httpx
from sqlalchemy.orm import Session

from backend.app.models.cricket import Match, Team, Venue

CRICKET_API_KEY = os.getenv("CRICKET_API_KEY", "")
CRICKET_API_BASE_URL = os.getenv(
    "CRICKET_API_BASE_URL", "https://api.cricapi.com/v1"
)


class CricketAPIAdapter:
    """Translates provider-specific external payloads into CricketIQ internal data structures."""

    def __init__(self):
        self.api_key = CRICKET_API_KEY
        self.base_url = CRICKET_API_BASE_URL

    def fetch_live_fixtures(self) -> List[Dict[str, Any]]:
        """Fetch current match fixtures from provider or return normalized sample if key is unconfigured."""
        if self.api_key and not self.api_key.startswith("your_"):
            try:
                url = f"{self.base_url}/currentMatches?apikey={self.api_key}"
                with httpx.Client(timeout=8.0) as client:
                    response = client.get(url)
                    if response.status_code == 200:
                        data = response.json().get("data", [])
                        return [self._normalize_match_payload(m) for m in data]
            except Exception as e:
                print(
                    f"[CricketAPI] Provider unreachable: {e}. Using"
                    " fallback adapter."
                )

        # Resilient fallback fixture when external API is offline or without key
        return [
            {
                "external_id": "cric_live_101",
                "title": "England vs South Africa - 2nd T20I",
                "match_type": "T20",
                "status": "LIVE",
                "team1_name": "England",
                "team1_short": "ENG",
                "team2_name": "South Africa",
                "team2_short": "SA",
                "venue_name": "Lord's Cricket Ground",
                "venue_city": "London",
                "venue_country": "England",
            }
        ]

    def _normalize_match_payload(
        self, raw: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Normalize vendor-specific keys to CricketIQ standard keys."""
        teams = raw.get("teams", ["Team A", "Team B"])
        team1 = teams[0] if len(teams) > 0 else "Team 1"
        team2 = teams[1] if len(teams) > 1 else "Team 2"

        return {
            "external_id": str(raw.get("id", "cric_ext")),
            "title": raw.get("name", f"{team1} vs {team2}"),
            "match_type": (raw.get("matchType", "T20")).upper(),
            "status": (
                "LIVE" if raw.get("matchStarted") else "UPCOMING"
            ),
            "team1_name": team1,
            "team1_short": team1[:3].upper(),
            "team2_name": team2,
            "team2_short": team2[:3].upper(),
            "venue_name": raw.get("venue", "International Stadium"),
            "venue_city": "Host City",
            "venue_country": "International",
        }

    def sync_match_to_database(
        self, db: Session, match_data: Dict[str, Any]
    ) -> Match:
        """Idempotently ingest a normalized match into PostgreSQL."""
        # 1. Resolve or create Team 1
        t1 = (
            db.query(Team)
            .filter(Team.name == match_data["team1_name"])
            .first()
        )
        if not t1:
            t1 = Team(
                name=match_data["team1_name"],
                short_name=match_data["team1_short"],
            )
            db.add(t1)
            db.commit()
            db.refresh(t1)

        # 2. Resolve or create Team 2
        t2 = (
            db.query(Team)
            .filter(Team.name == match_data["team2_name"])
            .first()
        )
        if not t2:
            t2 = Team(
                name=match_data["team2_name"],
                short_name=match_data["team2_short"],
            )
            db.add(t2)
            db.commit()
            db.refresh(t2)

        # 3. Resolve or create Venue
        venue = (
            db.query(Venue)
            .filter(Venue.name == match_data["venue_name"])
            .first()
        )
        if not venue:
            venue = Venue(
                name=match_data["venue_name"],
                city=match_data["venue_city"],
                country=match_data["venue_country"],
            )
            db.add(venue)
            db.commit()
            db.refresh(venue)

        # 4. Check existing Match
        match = (
            db.query(Match)
            .filter(Match.title == match_data["title"])
            .first()
        )
        if not match:
            match = Match(
                title=match_data["title"],
                match_type=match_data["match_type"],
                status=match_data["status"],
                team1_id=t1.id,
                team2_id=t2.id,
                venue_id=venue.id,
            )
            db.add(match)
            db.commit()
            db.refresh(match)
        else:
            match.status = match_data["status"]
            db.commit()

        return match


# Shared singleton
cricket_adapter = CricketAPIAdapter()