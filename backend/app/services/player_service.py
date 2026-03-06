import numpy as np
import pandas as pd
from sqlalchemy.orm import Session
from backend.app.models.cricket import Delivery, Player


def get_phase_label(over: int) -> str:
    if over < 6:
        return "powerplay"  # Overs 0-5
    elif over < 15:
        return "middle"  # Overs 6-14
    return "death"  # Overs 15-19


def compute_player_analytics(db: Session, player_id: int) -> dict:
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        return None

    # Fetch all deliveries involving this player
    bat_delivs = (
        db.query(Delivery).filter(Delivery.batter_id == player_id).all()
    )
    bowl_delivs = (
        db.query(Delivery).filter(Delivery.bowler_id == player_id).all()
    )
    out_delivs = (
        db.query(Delivery)
        .filter(
            Delivery.player_dismissed_id == player_id,
            Delivery.is_wicket == True,
        )
        .all()
    )

    batting_stats = None
    bowling_stats = None

    # 1. Batting Computation
    if bat_delivs:
        df_bat = pd.DataFrame(
            [
                {
                    "match_id": d.match_id,
                    "innings_id": d.innings_id,
                    "over": d.over_number,
                    "runs": d.runs_batter,
                    "is_wide": d.extra_type == "wide",
                    "phase": get_phase_label(d.over_number),
                }
                for d in bat_delivs
            ]
        )

        legal_balls = df_bat[~df_bat["is_wide"]]
        total_runs = int(df_bat["runs"].sum())
        balls_faced = len(legal_balls)
        dismissals = len(out_delivs)

        batting_avg = (
            round(total_runs / dismissals, 2)
            if dismissals > 0
            else float(total_runs)
        )
        strike_rate = (
            round((total_runs / balls_faced) * 100, 2)
            if balls_faced > 0
            else 0.0
        )
        fours = int((legal_balls["runs"] == 4).sum())
        sixes = int((legal_balls["runs"] == 6).sum())
        dots = int((legal_balls["runs"] == 0).sum())

        dot_pct = (
            round((dots / balls_faced) * 100, 2) if balls_faced > 0 else 0.0
        )
        boundary_runs = (fours * 4) + (sixes * 6)
        boundary_pct = (
            round((boundary_runs / total_runs) * 100, 2)
            if total_runs > 0
            else 0.0
        )

        # Phase breakdown
        phases = {}
        for ph in ["powerplay", "middle", "death"]:
            ph_df = legal_balls[legal_balls["phase"] == ph]
            ph_runs = int(ph_df["runs"].sum())
            ph_balls = len(ph_df)
            phases[ph] = {
                "runs": ph_runs,
                "balls": ph_balls,
                "strike_rate": (
                    round((ph_runs / ph_balls) * 100, 2)
                    if ph_balls > 0
                    else 0.0
                ),
            }

        batting_stats = {
            "innings_batted": df_bat["innings_id"].nunique(),
            "total_runs": total_runs,
            "balls_faced": balls_faced,
            "average": batting_avg,
            "strike_rate": strike_rate,
            "fours": fours,
            "sixes": sixes,
            "dot_ball_pct": dot_pct,
            "boundary_run_pct": boundary_pct,
            "phases": phases,
        }

    # 2. Bowling Computation
    if bowl_delivs:
        df_bowl = pd.DataFrame(
            [
                {
                    "match_id": d.match_id,
                    "innings_id": d.innings_id,
                    "over": d.over_number,
                    "runs_conceded": d.runs_batter
                    + (
                        d.runs_extras
                        if d.extra_type in ["wide", "noball"]
                        else 0
                    ),
                    "is_legal": d.extra_type not in ["wide", "noball"],
                    "is_wicket": d.is_wicket and d.dismissal_type != "runout",
                    "phase": get_phase_label(d.over_number),
                }
                for d in bowl_delivs
            ]
        )

        legal_deliveries = df_bowl[df_bowl["is_legal"]]
        total_legal_balls = len(legal_deliveries)
        runs_conceded = int(df_bowl["runs_conceded"].sum())
        wickets = int(df_bowl["is_wicket"].sum())

        overs_int = total_legal_balls // 6
        overs_remainder = total_legal_balls % 6
        overs_float = float(f"{overs_int}.{overs_remainder}")

        economy = (
            round(runs_conceded / (total_legal_balls / 6.0), 2)
            if total_legal_balls > 0
            else 0.0
        )
        bowling_sr = (
            round(total_legal_balls / wickets, 2) if wickets > 0 else None
        )
        dot_balls = int((legal_deliveries["runs_conceded"] == 0).sum())
        dot_pct = (
            round((dot_balls / total_legal_balls) * 100, 2)
            if total_legal_balls > 0
            else 0.0
        )

        # Phase breakdown
        phases = {}
        for ph in ["powerplay", "middle", "death"]:
            ph_df = df_bowl[df_bowl["phase"] == ph]
            ph_legal = ph_df[ph_df["is_legal"]]
            ph_runs = int(ph_df["runs_conceded"].sum())
            ph_wkts = int(ph_df["is_wicket"].sum())
            ph_legal_balls = len(ph_legal)
            phases[ph] = {
                "overs": float(
                    f"{ph_legal_balls // 6}.{ph_legal_balls % 6}"
                ),
                "runs": ph_runs,
                "wickets": ph_wkts,
                "economy": (
                    round(ph_runs / (ph_legal_balls / 6.0), 2)
                    if ph_legal_balls > 0
                    else 0.0
                ),
            }

        bowling_stats = {
            "innings_bowled": df_bowl["innings_id"].nunique(),
            "overs_bowled": overs_float,
            "runs_conceded": runs_conceded,
            "wickets": wickets,
            "economy": economy,
            "bowling_strike_rate": bowling_sr,
            "dot_ball_pct": dot_pct,
            "phases": phases,
        }

    return {
        "player_id": player.id,
        "name": player.name,
        "role": player.role,
        "team_name": player.team.name if player.team else None,
        "batting": batting_stats,
        "bowling": bowling_stats,
    }