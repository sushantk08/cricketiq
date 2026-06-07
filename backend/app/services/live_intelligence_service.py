from typing import Any, Dict, List, Optional

from backend.app.schemas.live_intelligence import (
    LiveInsight,
    LiveMatchIntelligence,
)


def _safe_float(value: Any) -> Optional[float]:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _extract_current_innings(
    match: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """
    Return the latest innings entry from the normalized live-score feed.
    """
    scores = match.get("scores") or []

    if not scores:
        return None

    return scores[-1]


def _build_live_insights(
    match: Dict[str, Any],
    current_innings: Optional[Dict[str, Any]],
) -> List[LiveInsight]:
    """Create simple decision-oriented insights from the live feed."""
    insights: List[LiveInsight] = []

    if not current_innings:
        insights.append(
            LiveInsight(
                category="data",
                title="Waiting for score update",
                detail=(
                    "The live provider has not yet supplied enough innings "
                    "information for deeper scenario analysis."
                ),
            )
        )
        return insights

    runs = int(current_innings.get("runs", 0) or 0)
    wickets = int(current_innings.get("wickets", 0) or 0)
    overs = _safe_float(current_innings.get("overs"))

    if overs is not None and overs > 0:
        run_rate = runs / overs

        if run_rate >= 10:
            insights.append(
                LiveInsight(
                    category="momentum",
                    title="Fast scoring rate",
                    detail=(
                        f"The current innings is scoring at approximately "
                        f"{run_rate:.2f} runs per over."
                    ),
                )
            )
        elif run_rate < 6:
            insights.append(
                LiveInsight(
                    category="pressure",
                    title="Scoring rate under pressure",
                    detail=(
                        f"The current scoring rate is approximately "
                        f"{run_rate:.2f} runs per over."
                    ),
                )
            )

    if wickets >= 7:
        insights.append(
            LiveInsight(
                category="resources",
                title="Limited batting resources",
                detail=(
                    f"{wickets} wickets have fallen, leaving "
                    f"{10 - wickets} wickets in hand."
                ),
            )
        )
    elif wickets <= 2:
        insights.append(
            LiveInsight(
                category="resources",
                title="Strong wicket cushion",
                detail=(
                    f"Only {wickets} wickets have fallen, leaving "
                    f"{10 - wickets} wickets in hand."
                ),
            )
        )

    if not insights:
        insights.append(
            LiveInsight(
                category="match_state",
                title="Match progressing normally",
                detail=(
                    "The available live score does not currently indicate "
                    "an extreme scoring or wicket-pressure signal."
                ),
            )
        )

    return insights


def _build_decision_summary(
    match: Dict[str, Any],
    current_innings: Optional[Dict[str, Any]],
) -> str:
    if not current_innings:
        return (
            "Live decision intelligence is waiting for a current innings "
            "score from the provider."
        )

    runs = int(current_innings.get("runs", 0) or 0)
    wickets = int(current_innings.get("wickets", 0) or 0)
    overs = current_innings.get("overs", 0.0)
    innings_name = current_innings.get("inning", "Current innings")

    return (
        f"{innings_name}: {runs}/{wickets} after {overs} overs. "
        "Use the current score, resources and live status as the immediate "
        "match-state reference."
    )


def build_live_match_intelligence(
    match: Dict[str, Any],
) -> LiveMatchIntelligence:
    """
    Convert one normalized CricAPI match into CricketIQ live intelligence.

    This first version intentionally uses only fields already normalized
    by the existing CricketAPIAdapter.
    """
    current_innings = _extract_current_innings(match)

    current_score = None
    current_wickets = None
    current_overs = None

    if current_innings:
        current_score = int(
            current_innings.get("runs", 0) or 0
        )

        current_wickets = int(
            current_innings.get("wickets", 0) or 0
        )

        current_overs = _safe_float(
            current_innings.get("overs")
        )

    insights = _build_live_insights(
        match,
        current_innings,
    )

    decision_summary = _build_decision_summary(
        match,
        current_innings,
    )

    return LiveMatchIntelligence(
        external_id=str(
            match.get("external_id", "")
        ),
        title=match.get(
            "title",
            "Live Match",
        ),
        match_type=match.get(
            "match_type",
            "T20",
        ),
        status=match.get(
            "status",
            "LIVE",
        ),
        team1_name=match.get(
            "team1_name",
            "Team 1",
        ),
        team2_name=match.get(
            "team2_name",
            "Team 2",
        ),
        formatted_score=match.get(
            "formatted_score",
            "Scores updating...",
        ),
        status_note=match.get(
            "status_note",
            "",
        ),
        venue_name=match.get(
            "venue_name",
            "Unknown venue",
        ),
        current_innings=(
            current_innings.get("inning")
            if current_innings
            else None
        ),
        current_score=current_score,
        current_wickets=current_wickets,
        current_overs=current_overs,
        projected_score=None,
        required_run_rate=None,
        win_probability_batting=None,
        win_probability_bowling=None,
        insights=insights,
        decision_summary=decision_summary,
    )


def build_live_intelligence_feed(
    matches: List[Dict[str, Any]],
) -> List[LiveMatchIntelligence]:
    """Build intelligence objects for all live matches."""
    live_matches = []

    for match in matches:
        if not match.get("match_started", False):
            continue

        if match.get("match_ended", False):
            continue

        live_matches.append(
            build_live_match_intelligence(match)
        )

    return live_matches