from typing import List, Tuple

import numpy as np
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.app.ml.historical_win_probability import historical_win_predictor
from backend.app.utils.cricket_rules import get_format_rules
from backend.app.models.cricket import (
    DecisionReplayRecord,
    Delivery,
    Innings,
    Match,
    Player,
)
from backend.app.schemas.replay import (
    DecisionPoint,
    DecisionReplayRequest,
    DecisionReplayResponse,
)
from backend.app.services.player_service import get_phase_label


NEUTRAL_ECONOMY = 8.5
FULL_RELIABILITY_BALLS = 36


def get_match_decision_points(
    db: Session, match_id: int
) -> List[DecisionPoint]:
    inn2 = (
        db.query(Innings)
        .filter(
            Innings.match_id == match_id,
            Innings.innings_number == 2,
        )
        .first()
    )

    inn1 = (
        db.query(Innings)
        .filter(
            Innings.match_id == match_id,
            Innings.innings_number == 1,
        )
        .first()
    )

    if not inn2 or not inn1:
        return []

    match = (
        db.query(Match)
        .filter(Match.id == match_id)
        .first()
    )

    if not match:
        return []

    format_rules = get_format_rules(match.match_type)
    max_balls = format_rules["max_balls"]

    target = inn1.total_runs + 1

    critical_overs = (
        db.query(Delivery)
        .filter(
            Delivery.innings_id == inn2.id,
            Delivery.ball_number == 1,
            Delivery.over_number >= 10,
        )
        .order_by(Delivery.over_number)
        .all()
    )

    points = []

    for delivery in critical_overs:
        balls_bowled = delivery.over_number * 6
        balls_remaining = max(0, max_balls - balls_bowled)
        runs_required = max(
            0,
            target - delivery.cumulative_runs,
        )

        phase = get_phase_label(
            delivery.over_number
        ).capitalize()

        reason = (
            f"{phase} phase bowling decision with "
            f"{runs_required} runs required off "
            f"{balls_remaining} balls."
        )

        points.append(
            DecisionPoint(
                over_number=delivery.over_number,
                display_over=f"{delivery.over_number}.1",
                batter_id=delivery.batter_id,
                batter_name=delivery.batter.name,
                actual_bowler_id=delivery.bowler_id,
                actual_bowler_name=delivery.bowler.name,
                score_at_time=delivery.cumulative_runs,
                wickets_at_time=delivery.cumulative_wickets,
                runs_required=runs_required,
                balls_remaining=balls_remaining,
                context_reason=reason,
            )
        )

    return points


def estimate_alternative_bowler_outcome(
    db: Session,
    bowler_id: int,
    phase_label: str,
) -> Tuple[float, float, int, int]:
    """
    Estimate an alternative bowler's expected runs and wickets
    for one over using phase-specific historical evidence.

    Small samples are shrunk toward a neutral economy baseline
    rather than being treated as fully reliable.

    Returns:
        expected_runs,
        expected_wickets,
        phase_legal_balls,
        phase_matches
    """

    deliveries = (
        db.query(Delivery)
        .filter(Delivery.bowler_id == bowler_id)
        .all()
    )

    phase_deliveries = [
        delivery
        for delivery in deliveries
        if get_phase_label(delivery.over_number) == phase_label
    ]

    if not phase_deliveries:
        return NEUTRAL_ECONOMY, 0.0, 0, 0

    legal_deliveries = [
        delivery
        for delivery in phase_deliveries
        if delivery.extra_type not in ["wide", "noball"]
    ]

    legal_balls = len(legal_deliveries)

    if legal_balls == 0:
        return NEUTRAL_ECONOMY, 0.0, 0, 0

    phase_runs = sum(
        delivery.runs_batter
        + (
            delivery.runs_extras
            if delivery.extra_type in ["wide", "noball"]
            else 0
        )
        for delivery in phase_deliveries
    )

    phase_wickets = sum(
        1
        for delivery in phase_deliveries
        if delivery.is_wicket
        and delivery.dismissal_type != "runout"
    )

    phase_matches = len(
        {
            delivery.match_id
            for delivery in phase_deliveries
            if delivery.match_id is not None
        }
    )

    observed_economy = (
        phase_runs / (legal_balls / 6.0)
        if legal_balls > 0
        else NEUTRAL_ECONOMY
    )

    # Up to 36 legal balls gives full weight to the observed
    # phase economy. Smaller samples are blended with the
    # neutral baseline of 8.5 runs per over.
    reliability_weight = min(
        legal_balls / FULL_RELIABILITY_BALLS,
        1.0,
    )

    expected_runs = (
        observed_economy * reliability_weight
        + NEUTRAL_ECONOMY * (1.0 - reliability_weight)
    )

    # Convert the observed wicket rate into expected wickets
# over a six-ball counterfactual over.
#
# Small samples are shrunk toward the overall death-phase
# baseline of 0.20 wickets per over.
    observed_wickets_per_over = (
        (phase_wickets / legal_balls) * 6.0
         if legal_balls > 0
         else 0.20
    )

    baseline_wickets_per_over = 0.20

    expected_wickets = (
        observed_wickets_per_over * reliability_weight
        + baseline_wickets_per_over * (1.0 - reliability_weight)
    )

    expected_wickets = min(
       max(expected_wickets, 0.0),
       1.0,
    )

    expected_wickets = round(
       expected_wickets,
        2,
    )

    return (
        round(expected_runs, 1),
        round(expected_wickets, 2),
        legal_balls,
        phase_matches,
    )


def calculate_counterfactual_win_probability(
    runs_required_before: int,
    balls_remaining_before: int,
    wickets_in_hand_before: int,
    expected_runs: float,
    expected_wickets: float,
    over_balls: int = 6,
) -> float:

    run_floor = max(
        0,
        int(np.floor(expected_runs)) - 2,
    )
    run_ceiling = int(
        np.ceil(expected_runs)
    ) + 2

    run_values = list(
        range(
            run_floor,
            run_ceiling + 1,
        )
    )

    run_weights = np.array(
        [
            np.exp(
                -0.5
                * ((runs - expected_runs) / 1.5) ** 2
            )
            for runs in run_values
        ],
        dtype=float,
    )

    run_weights /= run_weights.sum()

    wicket_probability = float(
        np.clip(
            expected_wickets,
            0.0,
            1.0,
        )
    )

    weighted_probability = 0.0

    for runs, run_weight in zip(
        run_values,
        run_weights,
    ):
        runs_required_after = max(
            0,
            runs_required_before - runs,
        )

        balls_remaining_after = max(
            0,
            balls_remaining_before - over_balls,
        )

        win_prob_no_wicket = historical_win_predictor.predict(
            runs_required_after,
            balls_remaining_after,
            wickets_in_hand_before,
        )

        win_prob_one_wicket = historical_win_predictor.predict(
            runs_required_after,
            balls_remaining_after,
            max(
                0,
                wickets_in_hand_before - 1,
            ),
        )

        expected_probability_for_runs = (
            win_prob_no_wicket
            * (1.0 - wicket_probability)
            + win_prob_one_wicket
            * wicket_probability
        )

        weighted_probability += (
            expected_probability_for_runs
            * run_weight
        )

    return float(
        round(
            weighted_probability,
            2,
        )
    )

def simulate_decision_replay(
    db: Session,
    req: DecisionReplayRequest,
) -> DecisionReplayResponse:
    print(
        f"[Decision Replay] Received request: "
        f"match_id={req.match_id}, "
        f"over_number={req.over_number}, "
        f"alternative_bowler_id={req.alternative_bowler_id}"
    )

    inn2 = (
        db.query(Innings)
        .filter(
            Innings.match_id == req.match_id,
            Innings.innings_number == 2,
        )
        .first()
    )

    inn1 = (
        db.query(Innings)
        .filter(
            Innings.match_id == req.match_id,
            Innings.innings_number == 1,
        )
        .first()
    )

    if not inn2 or not inn1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Match {req.match_id} does not have both "
                f"completed innings in the database."
            ),
        )

    match = (
        db.query(Match)
        .filter(Match.id == req.match_id)
        .first()
    )

    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Match {req.match_id} not found.",
        )

    format_rules = get_format_rules(match.match_type)
    max_balls = format_rules["max_balls"]

    over_delivs = (
        db.query(Delivery)
        .filter(
            Delivery.innings_id == inn2.id,
            Delivery.over_number == req.over_number,
        )
        .order_by(Delivery.ball_number)
        .all()
    )

    if not over_delivs:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"No deliveries found for match {req.match_id}, "
                f"innings {inn2.id}, over {req.over_number}."
            ),
        )

    first_ball = over_delivs[0]
    target = inn1.total_runs + 1

    runs_before = (
        first_ball.cumulative_runs
        - first_ball.runs_batter
        - first_ball.runs_extras
    )

    wickets_before = (
        first_ball.cumulative_wickets
        - (1 if first_ball.is_wicket else 0)
    )

    balls_bowled_before = req.over_number * 6

    balls_rem_before = max(
        0,
        max_balls - balls_bowled_before,
    )

    runs_req_before = max(
        0,
        target - runs_before,
    )

    wkts_hand_before = max(
        0,
        10 - wickets_before,
    )

    actual_runs_scored = sum(
        delivery.runs_batter
        + delivery.runs_extras
        for delivery in over_delivs
    )

    actual_wickets_taken = sum(
        1
        for delivery in over_delivs
        if delivery.is_wicket
        and delivery.dismissal_type != "runout"
    )

    legal_balls_in_over = sum(
        1
        for delivery in over_delivs
        if delivery.extra_type not in ["wide", "noball"]
    )

    balls_rem_after = max(
        0,
        balls_rem_before - legal_balls_in_over,
    )

    runs_req_actual_after = max(
        0,
        runs_req_before - actual_runs_scored,
    )

    wkts_hand_actual_after = max(
        0,
        wkts_hand_before - actual_wickets_taken,
    )

    actual_win_prob = historical_win_predictor.predict(
        runs_req_actual_after,
        balls_rem_after,
        wkts_hand_actual_after,
    )

    alt_bowler = (
        db.query(Player)
        .filter(Player.id == req.alternative_bowler_id)
        .first()
    )

    if not alt_bowler:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Bowler with ID "
                f"{req.alternative_bowler_id} not found."
            ),
        )

    if alt_bowler.id == first_ball.bowler_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "The alternative bowler must be different "
                "from the actual bowler."
            ),
        )

    phase_label = get_phase_label(
        req.over_number
    )

    (
        exp_runs_alt,
        exp_wkts_alt,
        sample_balls,
        sample_matches,
    ) = estimate_alternative_bowler_outcome(
        db=db,
        bowler_id=alt_bowler.id,
        phase_label=phase_label,
    )


    alt_win_prob = calculate_counterfactual_win_probability(
      runs_required_before=runs_req_before,
       balls_remaining_before=balls_rem_before,
       wickets_in_hand_before=wkts_hand_before,
       expected_runs=exp_runs_alt,
       expected_wickets=exp_wkts_alt,
    )

    actual_bowling_prob = round(
        100.0 - actual_win_prob,
        2,
    )

    alt_bowling_prob = round(
        100.0 - alt_win_prob,
        2,
    )

    impact = round(
        alt_bowling_prob - actual_bowling_prob,
        2,
    )

    quality_score = float(
        np.clip(
            50.0 - (impact * 1.5),
            5.0,
            95.0,
        )
    )

    if impact > 5.0:
        verdict = (
            f"Suboptimal Choice: "
            f"{alt_bowler.name} was statistically favored"
        )

        explanation = (
            f"Bowling {alt_bowler.name} in over "
            f"{req.over_number} was estimated at "
            f"{exp_runs_alt:.1f} runs and "
            f"{exp_wkts_alt:.2f} wickets for the over. "
            f"The estimate uses {sample_balls} legal "
            f"{phase_label} deliveries across "
            f"{sample_matches} recorded match(es). "
            f"The observed evidence is therefore treated "
            f"with sample-size adjustment. "
            f"{first_ball.bowler.name}'s actual over conceded "
            f"{actual_runs_scored} runs and took "
            f"{actual_wickets_taken} wickets. "
            f"The model estimates defensive win "
            f"probability would have changed by "
            f"{impact:+.1f} percentage points."
        )

    elif impact < -5.0:
        verdict = (
            f"Sound Decision: "
            f"{first_ball.bowler.name} was the superior option"
        )

        explanation = (
            f"{first_ball.bowler.name} delivered an effective "
            f"over with {actual_runs_scored} runs and "
            f"{actual_wickets_taken} wickets. "
            f"Substituting {alt_bowler.name} was projected "
            f"at {exp_runs_alt:.1f} runs and "
            f"{exp_wkts_alt:.2f} wickets, based on "
            f"{sample_balls} legal {phase_label} deliveries "
            f"across {sample_matches} recorded match(es). "
            f"The estimated defensive win probability "
            f"would have changed by "
            f"{impact:+.1f} percentage points."
        )

    else:
        verdict = (
            "Neutral Impact: "
            "Comparable tactical options"
        )

        explanation = (
            f"Both {first_ball.bowler.name} and "
            f"{alt_bowler.name} produced comparable "
            f"projected match equity. "
            f"The alternative was estimated at "
            f"{exp_runs_alt:.1f} runs and "
            f"{exp_wkts_alt:.2f} wickets using "
            f"{sample_balls} legal {phase_label} deliveries "
            f"across {sample_matches} recorded match(es). "
            f"The estimated defensive win probability "
            f"difference was {impact:+.1f} percentage points."
        )

    disclaimer = (
        "Counterfactual result is a statistical estimate, "
        "not a reconstruction of what would certainly have happened. "
        "Alternative-bowler projections are adjusted for historical "
        "sample size and use the historical win-probability model."
    )

    record = DecisionReplayRecord(
        match_id=req.match_id,
        over_number=req.over_number,
        actual_bowler_id=first_ball.bowler_id,
        alternative_bowler_id=alt_bowler.id,
        batter_id=first_ball.batter_id,
        actual_win_prob=actual_bowling_prob,
        alternative_win_prob=alt_bowling_prob,
        decision_impact=impact,
        expected_runs_actual=float(actual_runs_scored),
        expected_runs_alternative=exp_runs_alt,
        decision_quality_score=round(
            quality_score,
            1,
        ),
        explanation=explanation,
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return DecisionReplayResponse(
        replay_id=record.id,
        match_id=record.match_id,
        over_number=record.over_number,
        display_over=f"{record.over_number}.0",
        batter_name=first_ball.batter.name,
        actual_bowler_name=first_ball.bowler.name,
        alternative_bowler_name=alt_bowler.name,
        actual_win_prob=actual_bowling_prob,
        alternative_win_prob=alt_bowling_prob,
        decision_impact=impact,
        expected_runs_actual=float(
            actual_runs_scored
        ),
        expected_runs_alternative=exp_runs_alt,
        decision_quality_score=round(
            quality_score,
            1,
        ),
        tactical_verdict=verdict,
        explanation=explanation,
        uncertainty_disclaimer=disclaimer,
        created_at=record.created_at,
    )