from typing import List
from sqlalchemy.orm import Session
from backend.app.ml.historical_win_probability import historical_win_predictor
from backend.app.models.cricket import Delivery, Innings, Match
from backend.app.schemas.analytics import (
    MatchTurningPointsResponse,
    TurningPointItem,
)


def detect_turning_points(
    db: Session, match_id: int
) -> MatchTurningPointsResponse:
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        return None

    inn1 = (
        db.query(Innings)
        .filter(Innings.match_id == match_id, Innings.innings_number == 1)
        .first()
    )
    inn2 = (
        db.query(Innings)
        .filter(Innings.match_id == match_id, Innings.innings_number == 2)
        .first()
    )
    if not inn1 or not inn2:
        return None

    target = inn1.total_runs + 1
    deliveries = (
        db.query(Delivery)
        .filter(Delivery.innings_id == inn2.id)
        .order_by(Delivery.over_number, Delivery.ball_number)
        .all()
    )

    total_balls = 120
    legal_balls_bowled = 0
    cumulative_runs = 0
    cumulative_wickets = 0

    candidates: List[TurningPointItem] = []

    for d in deliveries:
        # Match state BEFORE this delivery
        balls_rem_before = max(0, total_balls - legal_balls_bowled)
        runs_req_before = max(0, target - cumulative_runs)
        wkts_hand_before = max(0, 10 - cumulative_wickets)

        prob_before = historical_win_predictor.predict(
             runs_req_before, balls_rem_before, wkts_hand_before
        )

        # Update state WITH this delivery
        if d.extra_type not in ["wide", "noball"]:
            legal_balls_bowled += 1

        cumulative_runs = d.cumulative_runs
        cumulative_wickets = d.cumulative_wickets

        # Match state AFTER this delivery
        balls_rem_after = max(0, total_balls - legal_balls_bowled)
        runs_req_after = max(0, target - cumulative_runs)
        wkts_hand_after = max(0, 10 - cumulative_wickets)

        prob_after = historical_win_predictor.predict(
            runs_req_after, balls_rem_after, wkts_hand_after
        )

        # Calculate probability swing for the batting team
        delta = round(prob_after - prob_before, 2)
        abs_delta = abs(delta)

        # Classify turning points
        if abs_delta >= 12.0 or (d.is_wicket and abs_delta >= 6.0):
            if abs_delta >= 18.0:
                classification = "CRITICAL_TURNING_POINT"
            elif abs_delta >= 10.0:
                classification = "MAJOR_SWING"
            else:
                classification = "MODERATE_SHIFT"

            # Formulate human-readable description
            if d.is_wicket:
                dismissal_desc = (
                    f"{d.dismissal_type} out"
                    if d.dismissal_type
                    else "dismissed"
                )
                desc = (
                    f"Wicket: {d.player_dismissed.name} {dismissal_desc} by"
                    f" {d.bowler.name}"
                )
            elif d.runs_batter == 6:
                desc = f"Six: {d.batter.name} strikes maximum off {d.bowler.name}"
            elif d.runs_batter == 4:
                desc = (
                    f"Boundary: {d.batter.name} hits four off"
                    f" {d.bowler.name}"
                )
            elif d.runs_batter == 0 and balls_rem_after <= 24:
                desc = f"Crucial Dot Ball bowled by {d.bowler.name} to {d.batter.name}"
            else:
                desc = (
                    f"{d.runs_batter} runs scored by {d.batter.name} off"
                    f" {d.bowler.name}"
                )

            candidates.append(
                TurningPointItem(
                    over_number=d.over_number,
                    ball_number=d.ball_number,
                    display_over=f"{d.over_number}.{d.ball_number}",
                    batter_name=d.batter.name,
                    bowler_name=d.bowler.name,
                    event_summary=desc,
                    win_prob_before=round(prob_before, 2),
                    win_prob_after=round(prob_after, 2),
                    win_prob_delta=delta,
                    classification=classification,
                )
            )

    # Rank by highest absolute probability shift
    candidates.sort(key=lambda x: abs(x.win_prob_delta), reverse=True)

    return MatchTurningPointsResponse(
        match_id=match.id,
        chasing_team=inn2.batting_team.name,
        defending_team=inn2.bowling_team.name,
        total_turning_points=len(candidates),
        turning_points=candidates,
    )