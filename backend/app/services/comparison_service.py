from sqlalchemy.orm import Session

from backend.app.models.cricket import Player
from backend.app.services.player_service import compute_player_analytics


def _get_batting_score(stats: dict | None) -> float:
    if not stats:
        return 0.0

    return (
        stats.get("total_runs", 0) * 0.35
        + stats.get("strike_rate", 0) * 0.35
        + stats.get("average", 0) * 0.20
        + stats.get("boundary_run_pct", 0) * 0.10
    )


def _get_bowling_score(stats: dict | None) -> float:
    if not stats:
        return 0.0

    economy = stats.get("economy", 0)
    wickets = stats.get("wickets", 0)
    dot_ball_pct = stats.get("dot_ball_pct", 0)

    economy_score = max(0.0, 12.0 - economy) * 8.0

    return (
        economy_score * 0.35
        + wickets * 6.0 * 0.40
        + dot_ball_pct * 0.25
    )


def _build_summary(
    player1_name: str,
    player2_name: str,
    better_batter: str | None,
    better_bowler: str | None,
) -> str:
    parts = []

    if better_batter:
        parts.append(
            f"{better_batter} has the stronger historical batting profile "
            "based on the available CricketIQ statistics."
        )

    if better_bowler:
        parts.append(
            f"{better_bowler} has the stronger historical bowling profile "
            "based on the available CricketIQ statistics."
        )

    if not parts:
        parts.append(
            f"{player1_name} and {player2_name} have insufficient "
            "role-specific historical data for a meaningful comparison."
        )

    return " ".join(parts)


def generate_player_comparison(
    db: Session,
    player1_id: int,
    player2_id: int,
) -> dict | None:
    if player1_id == player2_id:
        return None

    player1 = db.query(Player).filter(Player.id == player1_id).first()
    player2 = db.query(Player).filter(Player.id == player2_id).first()

    if not player1 or not player2:
        return None

    stats1 = compute_player_analytics(db, player1_id)
    stats2 = compute_player_analytics(db, player2_id)

    better_batter = None
    better_bowler = None

    batting1 = stats1.get("batting")
    batting2 = stats2.get("batting")

    if batting1 and batting2:
        score1 = _get_batting_score(batting1)
        score2 = _get_batting_score(batting2)

        if score1 > score2:
            better_batter = player1.name
        elif score2 > score1:
            better_batter = player2.name

    bowling1 = stats1.get("bowling")
    bowling2 = stats2.get("bowling")

    if bowling1 and bowling2:
        score1 = _get_bowling_score(bowling1)
        score2 = _get_bowling_score(bowling2)

        if score1 > score2:
            better_bowler = player1.name
        elif score2 > score1:
            better_bowler = player2.name

    return {
        "player1_id": player1.id,
        "player1_name": player1.name,
        "player1_role": player1.role,
        "player1_team": player1.team.name if player1.team else None,
        "player2_id": player2.id,
        "player2_name": player2.name,
        "player2_role": player2.role,
        "player2_team": player2.team.name if player2.team else None,
        "player1_stats": stats1,
        "player2_stats": stats2,
        "better_batter": better_batter,
        "better_bowler": better_bowler,
        "comparison_summary": _build_summary(
            player1.name,
            player2.name,
            better_batter,
            better_bowler,
        ),
    }