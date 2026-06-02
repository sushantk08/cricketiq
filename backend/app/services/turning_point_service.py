from typing import List

from sqlalchemy.orm import Session

from backend.app.ml.historical_win_probability import historical_win_predictor
from backend.app.models.cricket import Delivery, Innings, Match
from backend.app.schemas.analytics import (
    MatchTurningPointsResponse,
    TurningPointItem,
)


TOTAL_T20_BALLS = 120

# Delivery-level thresholds.
DELIVERY_SWING_THRESHOLD = 8.0
WICKET_SWING_THRESHOLD = 5.0

# Stronger thresholds for final classification.
CRITICAL_SWING_THRESHOLD = 18.0
MAJOR_SWING_THRESHOLD = 10.0

# Over-level threshold.
OVER_SWING_THRESHOLD = 12.0


def _is_legal_delivery(delivery: Delivery) -> bool:
    """Return whether a delivery counts as a legal ball."""
    return delivery.extra_type not in {"wide", "noball"}


def _safe_player_name(player) -> str:
    """Safely return a player's name for event descriptions."""
    return player.name if player else "Unknown player"


def _classify_swing(
    abs_delta: float,
    is_wicket: bool,
) -> str | None:
    """
    Classify the importance of a probability swing.

    Returns None when the event is not significant enough.
    """
    if abs_delta >= CRITICAL_SWING_THRESHOLD:
        return "CRITICAL_TURNING_POINT"

    if abs_delta >= MAJOR_SWING_THRESHOLD:
        return "MAJOR_SWING"

    if abs_delta >= DELIVERY_SWING_THRESHOLD:
        return "MODERATE_SHIFT"

    if is_wicket and abs_delta >= WICKET_SWING_THRESHOLD:
        return "MODERATE_SHIFT"

    return None


def _build_event_summary(
    delivery: Delivery,
    balls_remaining_after: int,
) -> str:
    """Create a human-readable explanation for a turning-point event."""
    batter_name = _safe_player_name(delivery.batter)
    bowler_name = _safe_player_name(delivery.bowler)

    if delivery.is_wicket:
        dismissed_name = _safe_player_name(
            delivery.player_dismissed
        )

        dismissal_desc = (
            f"{delivery.dismissal_type} out"
            if delivery.dismissal_type
            else "dismissed"
        )

        return (
            f"Wicket: {dismissed_name} {dismissal_desc} by "
            f"{bowler_name}"
        )

    if delivery.runs_batter == 6:
        return (
            f"Six: {batter_name} strikes maximum off "
            f"{bowler_name}"
        )

    if delivery.runs_batter == 4:
        return (
            f"Boundary: {batter_name} hits four off "
            f"{bowler_name}"
        )

    if (
        delivery.runs_batter == 0
        and delivery.runs_extras == 0
        and balls_remaining_after <= 24
    ):
        return (
            f"Crucial dot ball: {bowler_name} to "
            f"{batter_name}"
        )

    return (
        f"{delivery.runs_batter} runs scored by "
        f"{batter_name} off {bowler_name}"
    )


def _get_win_probability(
    runs_required: int,
    balls_remaining: int,
    wickets_in_hand: int,
) -> float:
    """
    Return the batting team's win probability.

    Terminal match states are handled explicitly instead of
    passing zero-ball states to the historical ML model.
    """
    if runs_required <= 0:
        return 100.0

    if balls_remaining <= 0:
        return 0.0

    if wickets_in_hand <= 0:
        return 0.0

    return historical_win_predictor.predict(
        runs_required,
        balls_remaining,
        wickets_in_hand,
    )

def detect_turning_points(
    db: Session,
    match_id: int,
) -> MatchTurningPointsResponse | None:

    match = (
        db.query(Match)
        .filter(Match.id == match_id)
        .first()
    )

    if not match:
        return None

    inn1 = (
        db.query(Innings)
        .filter(
            Innings.match_id == match_id,
            Innings.innings_number == 1,
        )
        .first()
    )

    inn2 = (
        db.query(Innings)
        .filter(
            Innings.match_id == match_id,
            Innings.innings_number == 2,
        )
        .first()
    )

    if not inn1 or not inn2:
        return None

    target = inn1.total_runs + 1

    deliveries = (
        db.query(Delivery)
        .filter(Delivery.innings_id == inn2.id)
        .order_by(
            Delivery.over_number,
            Delivery.ball_number,
        )
        .all()
    )

    if not deliveries:
        return MatchTurningPointsResponse(
            match_id=match.id,
            chasing_team=inn2.batting_team.name,
            defending_team=inn2.bowling_team.name,
            total_turning_points=0,
            turning_points=[],
        )

    legal_balls_bowled = 0
    cumulative_runs = 0
    cumulative_wickets = 0

    candidates: List[TurningPointItem] = []

    # Track the probability state at the start of each over.
    current_over = None
    over_start_probability = None
    over_end_probability = None
    over_start_ball = None

    for delivery in deliveries:

        # ---------------------------------------------------------
        # State BEFORE delivery
        # ---------------------------------------------------------

        balls_remaining_before = max(
            0,
            TOTAL_T20_BALLS - legal_balls_bowled,
        )

        runs_required_before = max(
            0,
            target - cumulative_runs,
        )

        wickets_in_hand_before = max(
            0,
            10 - cumulative_wickets,
        )

        # Avoid feeding an impossible zero-ball state into the model
        # unless the innings has already effectively finished.
        probability_before = _get_win_probability(
            runs_required_before,
            balls_remaining_before,
            wickets_in_hand_before,
        )

        # ---------------------------------------------------------
        # Start-of-over tracking
        # ---------------------------------------------------------

        if current_over != delivery.over_number:
            current_over = delivery.over_number
            over_start_probability = probability_before
            over_start_ball = delivery

        # ---------------------------------------------------------
        # Apply delivery
        # ---------------------------------------------------------

        if _is_legal_delivery(delivery):
            legal_balls_bowled += 1

        cumulative_runs = delivery.cumulative_runs
        cumulative_wickets = delivery.cumulative_wickets

        # ---------------------------------------------------------
        # State AFTER delivery
        # ---------------------------------------------------------

        balls_remaining_after = max(
            0,
            TOTAL_T20_BALLS - legal_balls_bowled,
        )

        runs_required_after = max(
            0,
            target - cumulative_runs,
        )

        wickets_in_hand_after = max(
            0,
            10 - cumulative_wickets,
        )

        probability_after = _get_win_probability(
            runs_required_after,
            balls_remaining_after,
            wickets_in_hand_after,
        )

        over_end_probability = probability_after

        # ---------------------------------------------------------
        # Delivery-level swing
        # ---------------------------------------------------------

        delta = round(
            probability_after - probability_before,
            2,
        )

        abs_delta = abs(delta)

        classification = _classify_swing(
            abs_delta,
            delivery.is_wicket,
        )

        if classification:
            candidates.append(
                TurningPointItem(
                    over_number=delivery.over_number,
                    ball_number=delivery.ball_number,
                    display_over=(
                        f"{delivery.over_number}."
                        f"{delivery.ball_number}"
                    ),
                    batter_name=_safe_player_name(
                        delivery.batter
                    ),
                    bowler_name=_safe_player_name(
                        delivery.bowler
                    ),
                    event_summary=_build_event_summary(
                        delivery,
                        balls_remaining_after,
                    ),
                    win_prob_before=round(
                        probability_before,
                        2,
                    ),
                    win_prob_after=round(
                        probability_after,
                        2,
                    ),
                    win_prob_delta=delta,
                    classification=classification,
                )
            )

        # ---------------------------------------------------------
        # End-of-over momentum detection
        # ---------------------------------------------------------

        is_end_of_over = (
            delivery.ball_number >= 6
            or delivery == deliveries[-1]
        )

        if is_end_of_over and over_start_probability is not None:

            over_delta = round(
                over_end_probability - over_start_probability,
                2,
            )

            abs_over_delta = abs(over_delta)

            # Only add an over-level event when:
            # 1. no individual delivery in that over already
            #    represents essentially the same event, and
            # 2. the complete over produced a meaningful shift.
            existing_same_over = any(
                item.over_number == delivery.over_number
                for item in candidates
            )

            if (
                abs_over_delta >= OVER_SWING_THRESHOLD
                and not existing_same_over
                and over_start_ball is not None
            ):
                if abs_over_delta >= CRITICAL_SWING_THRESHOLD:
                    over_classification = (
                        "CRITICAL_TURNING_POINT"
                    )
                else:
                    over_classification = "MAJOR_SWING"

                over_event = (
                    "Momentum swing: over "
                    f"{delivery.over_number} changed the "
                    "modeled win probability by "
                    f"{over_delta:+.1f} percentage points."
                )

                candidates.append(
                    TurningPointItem(
                        over_number=delivery.over_number,
                        ball_number=delivery.ball_number,
                        display_over=(
                            f"{delivery.over_number}."
                            f"{delivery.ball_number}"
                        ),
                        batter_name=_safe_player_name(
                            delivery.batter
                        ),
                        bowler_name=_safe_player_name(
                            delivery.bowler
                        ),
                        event_summary=over_event,
                        win_prob_before=round(
                            over_start_probability,
                            2,
                        ),
                        win_prob_after=round(
                            over_end_probability,
                            2,
                        ),
                        win_prob_delta=over_delta,
                        classification=over_classification,
                    )
                )

    # -------------------------------------------------------------
    # Rank by magnitude of win probability impact.
    # -------------------------------------------------------------

    candidates.sort(
        key=lambda item: abs(item.win_prob_delta),
        reverse=True,
    )

    return MatchTurningPointsResponse(
        match_id=match.id,
        chasing_team=inn2.batting_team.name,
        defending_team=inn2.bowling_team.name,
        total_turning_points=len(candidates),
        turning_points=candidates,
    )