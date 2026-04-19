from collections import defaultdict
from sqlalchemy.orm import Session

from backend.app.models.cricket import Delivery, Innings, Match


def compute_match_analytics(db: Session, match_id: int) -> dict | None:
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        return None

    innings_list = (
        db.query(Innings)
        .filter(Innings.match_id == match_id)
        .order_by(Innings.innings_number)
        .all()
    )

    if not innings_list:
        return None

    innings_analytics = []

    for innings in innings_list:
        deliveries = (
            db.query(Delivery)
            .filter(Delivery.innings_id == innings.id)
            .order_by(Delivery.over_number, Delivery.ball_number)
            .all()
        )

        if not deliveries:
            continue

        legal_balls = sum(
            1
            for d in deliveries
            if d.extra_type not in ["wide", "noball"]
        )

        total_runs = innings.total_runs
        total_wickets = innings.total_wickets

        boundaries = sum(
            1 for d in deliveries if d.runs_batter in [4, 6]
        )

        fours = sum(
            1 for d in deliveries if d.runs_batter == 4
        )

        sixes = sum(
            1 for d in deliveries if d.runs_batter == 6
        )

        dot_balls = sum(
            1
            for d in deliveries
            if d.runs_batter == 0
            and d.runs_extras == 0
            and d.extra_type is None
        )

        run_rate = (
            round(total_runs / (legal_balls / 6), 2)
            if legal_balls > 0
            else 0.0
        )

        dot_ball_percentage = (
            round((dot_balls / legal_balls) * 100, 2)
            if legal_balls > 0
            else 0.0
        )

        boundary_percentage = (
            round((boundaries / legal_balls) * 100, 2)
            if legal_balls > 0
            else 0.0
        )

        phase_runs = defaultdict(int)
        phase_balls = defaultdict(int)

        for delivery in deliveries:
            if delivery.over_number < 6:
                phase = "POWERPLAY"
            elif delivery.over_number < 15:
                phase = "MIDDLE"
            else:
                phase = "DEATH"

            phase_runs[phase] += (
                delivery.runs_batter + delivery.runs_extras
            )

            if delivery.extra_type not in ["wide", "noball"]:
                phase_balls[phase] += 1

        phases = {}

        for phase in ["POWERPLAY", "MIDDLE", "DEATH"]:
            balls = phase_balls[phase]
            runs = phase_runs[phase]

            phases[phase] = {
                "runs": runs,
                "balls": balls,
                "run_rate": round(runs / (balls / 6), 2)
                if balls > 0
                else 0.0,
            }

        innings_analytics.append(
            {
                "innings_number": innings.innings_number,
                "batting_team": innings.batting_team.name,
                "bowling_team": innings.bowling_team.name,
                "runs": total_runs,
                "wickets": total_wickets,
                "legal_balls": legal_balls,
                "run_rate": run_rate,
                "fours": fours,
                "sixes": sixes,
                "boundaries": boundaries,
                "dot_balls": dot_balls,
                "dot_ball_percentage": dot_ball_percentage,
                "boundary_percentage": boundary_percentage,
                "phases": phases,
            }
        )

    return {
        "match_id": match.id,
        "title": match.title,
        "match_type": match.match_type,
        "status": match.status,
        "innings": innings_analytics,
    }