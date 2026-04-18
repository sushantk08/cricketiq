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
    """Translates provider-specific external payloads into CricketIQ standard structures."""

    def __init__(self):
        self.api_key = CRICKET_API_KEY
        self.base_url = CRICKET_API_BASE_URL

    def fetch_live_fixtures(self) -> List[Dict[str, Any]]:
        """Fetch live scores from CricAPI currentMatches endpoint."""
        if self.api_key and not self.api_key.startswith("your_"):
            try:
                url = f"{self.base_url}/currentMatches?apikey={self.api_key}&offset=0"
                with httpx.Client(timeout=30.0) as client:
                    response = client.get(url)
                    if response.status_code == 200:
                        data = response.json().get("data", [])
                        return [
                            self._normalize_match_payload(m) for m in data
                        ]
            except Exception as e:
                print(f"[CricketAPI] Error fetching live scores: {e}")

        # Fallback demonstration match when API key is unset or rate-limited
        return [
            {
                "external_id": "cric_live_sample_1",
                "title": (
                    "Western Australia vs New South Wales, Marsh One Day Cup"
                ),
                "match_type": "ODI",
                "status": "LIVE",
                "match_started": True,
                "match_ended": False,
                "team1_name": "Western Australia",
                "team1_short": "WA",
                "team2_name": "New South Wales",
                "team2_short": "NSW",
                "venue_name": "WACA Ground, Perth",
                "scores": [
                    {
                        "inning": "Western Australia Inning 1",
                        "runs": 207,
                        "wickets": 10,
                        "overs": 46.3,
                    },
                    {
                        "inning": "New South Wales Inning 1",
                        "runs": 182,
                        "wickets": 6,
                        "overs": 42.0,
                    },
                ],
                "formatted_score": "WA 207/10 (46.3 ov) vs NSW 182/6 (42.0 ov)",
                "status_note": "NSW need 26 runs in 48 balls",
            }
        ]

    def _normalize_match_payload(
        self, raw: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Normalize CricAPI's exact JSON keys including the 'score' array."""
        teams = raw.get("teams", ["Team A", "Team B"])
        team1 = teams[0] if len(teams) > 0 else "Team 1"
        team2 = teams[1] if len(teams) > 1 else "Team 2"

        team_info = raw.get("teamInfo", [])
        t1_short = (
             team_info[0].get("shortname")
             if len(team_info) > 0 and team_info[0].get("shortname")
             else team1[:3].upper()
        )

        t2_short = (
             team_info[1].get("shortname")
             if len(team_info) > 1 and team_info[1].get("shortname")
             else team2[:3].upper()
        )

        # Parse CricAPI's "score" array: [{ "r": 207, "w": 10, "o": 46.3, "inning": "..." }]
        raw_scores = raw.get("score", [])
        parsed_scores = []
        formatted_innings = []

        for s in raw_scores:
            runs = s.get("r", 0)
            wickets = s.get("w", 0)
            overs = s.get("o", 0.0)
            inn_name = s.get("inning", "")

            parsed_scores.append(
                {
                    "inning": inn_name,
                    "runs": runs,
                    "wickets": wickets,
                    "overs": overs,
                }
            )

            # Create short readable score e.g. "WA 207/10 (46.3 ov)"
            short_prefix = (
                t1_short
                if team1.lower() in inn_name.lower()
                else (
                    t2_short
                    if team2.lower() in inn_name.lower()
                    else inn_name[:4]
                )
            )
            formatted_innings.append(
                f"{short_prefix} {runs}/{wickets} ({overs} ov)"
            )

        formatted_score_str = (
            " vs ".join(formatted_innings)
            if formatted_innings
            else "Scores updating..."
        )

        is_live = raw.get("matchStarted", False) and not raw.get(
            "matchEnded", False
        )

        return {
            "external_id": str(raw.get("id", "cric_id")),
            "title": raw.get("name", f"{team1} vs {team2}"),
            "match_type": (raw.get("matchType", "T20")).upper(),
            "status": "LIVE" if is_live else raw.get("status", "UPCOMING"),
            "match_started": raw.get("matchStarted", False),
            "match_ended": raw.get("matchEnded", False),
            "team1_name": team1,
            "team1_short": t1_short,
            "team2_name": team2,
            "team2_short": t2_short,
            "venue_name": raw.get("venue", "International Stadium"),
            "scores": parsed_scores,
            "formatted_score": formatted_score_str,
            "status_note": raw.get("status", ""),
        }

    def sync_match_to_database(
        self, db: Session, match_data: Dict[str, Any]
    ) -> Match:
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

        venue = (
            db.query(Venue)
            .filter(Venue.name == match_data["venue_name"])
            .first()
        )
        if not venue:
            venue = Venue(
                name=match_data["venue_name"],
                city="Host City",
                country="International",
            )
            db.add(venue)
            db.commit()
            db.refresh(venue)

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


cricket_adapter = CricketAPIAdapter()