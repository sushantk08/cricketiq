from collections import defaultdict
from sqlalchemy.orm import Session
from backend.app.models.cricket import Delivery, Innings, Match, Player


def compute_match_scorecard(db: Session, match_id: int) -> dict:
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        return None

    innings_list = (
        db.query(Innings)
        .filter(Innings.match_id == match_id)
        .order_by(Innings.innings_number)
        .all()
    )

    innings_result = []

    for inn in innings_list:
        deliveries = (
            db.query(Delivery)
            .filter(Delivery.innings_id == inn.id)
            .order_by(Delivery.over_number, Delivery.ball_number)
            .all()
        )

        # Batting statistics
        batting_stats = {}
        batting_order = []
        # Bowling statistics
        bowling_stats = {}
        bowling_order = []
        # Track over-by-over runs for maidens
        bowler_overs = defaultdict(lambda: defaultdict(int))

        for d in deliveries:
            # Track Batter
            if d.batter_id not in batting_stats:
                player = (
                    db.query(Player).filter(Player.id == d.batter_id).first()
                )
                batting_stats[d.batter_id] = {
                    "player_id": d.batter_id,
                    "name": player.name if player else f"Player {d.batter_id}",
                    "runs": 0,
                    "balls": 0,
                    "fours": 0,
                    "sixes": 0,
                    "strike_rate": 0.0,
                    "dismissal": "not out",
                }
                batting_order.append(d.batter_id)

            b_entry = batting_stats[d.batter_id]
            b_entry["runs"] += d.runs_batter
            if d.extra_type != "wide":
                b_entry["balls"] += 1
            if d.runs_batter == 4:
                b_entry["fours"] += 1
            elif d.runs_batter == 6:
                b_entry["sixes"] += 1

            # Track Wickets
            if d.is_wicket and d.player_dismissed_id:
                if d.player_dismissed_id in batting_stats:
                    batting_stats[d.player_dismissed_id][
                        "dismissal"
                    ] = d.dismissal_type or "out"

            # Track Bowler
            if d.bowler_id not in bowling_stats:
                bowler = (
                    db.query(Player).filter(Player.id == d.bowler_id).first()
                )
                bowling_stats[d.bowler_id] = {
                    "player_id": d.bowler_id,
                    "name": bowler.name if bowler else f"Player {d.bowler_id}",
                    "legal_balls": 0,
                    "maidens": 0,
                    "runs_conceded": 0,
                    "wickets": 0,
                    "economy": 0.0,
                }
                bowling_order.append(d.bowler_id)

            bw_entry = bowling_stats[d.bowler_id]
            runs_this_ball = d.runs_batter + (
                d.runs_extras if d.extra_type in ["wide", "noball"] else 0
            )
            bw_entry["runs_conceded"] += runs_this_ball
            bowler_overs[d.bowler_id][d.over_number] += runs_this_ball

            if d.extra_type not in ["wide", "noball"]:
                bw_entry["legal_balls"] += 1

            if d.is_wicket and d.dismissal_type != "runout":
                bw_entry["wickets"] += 1

        # Finalize Batting Stats
        batting_list = []
        for p_id in batting_order:
            b = batting_stats[p_id]
            b["strike_rate"] = (
                round((b["runs"] / b["balls"]) * 100, 2)
                if b["balls"] > 0
                else 0.0
            )
            batting_list.append(b)

        # Finalize Bowling Stats
        bowling_list = []
        for p_id in bowling_order:
            bw = bowling_stats[p_id]
            legal_b = bw.pop("legal_balls")
            overs_full = legal_b // 6
            overs_rem = legal_b % 6
            bw["overs"] = float(f"{overs_full}.{overs_rem}")
            bw["economy"] = (
                round((bw["runs_conceded"] / (legal_b / 6.0)), 2)
                if legal_b > 0
                else 0.0
            )
            # Calculate maidens: completed overs with 0 runs
            maidens = sum(
                1
                for ov, r in bowler_overs[p_id].items()
                if r == 0 and sum(1 for d in deliveries if d.bowler_id == p_id and d.over_number == ov and d.extra_type not in ["wide", "noball"]) == 6
            )
            bw["maidens"] = maidens
            bowling_list.append(bw)

        innings_result.append(
            {
                "innings_number": inn.innings_number,
                "batting_team": inn.batting_team.name,
                "bowling_team": inn.bowling_team.name,
                "total_runs": inn.total_runs,
                "total_wickets": inn.total_wickets,
                "total_overs": inn.total_overs,
                "batting": batting_list,
                "bowling": bowling_list,
            }
        )

    return {
        "match_id": match.id,
        "title": match.title,
        "status": match.status,
        "innings": innings_result,
    }