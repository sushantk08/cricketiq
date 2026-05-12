from backend.app.ml.historical_win_probability import historical_win_predictor
from backend.app.schemas.scenario import (
    ScenarioSimulateRequest,
    ScenarioSimulateResponse,
)


def run_scenario_simulation(
    req: ScenarioSimulateRequest,
) -> ScenarioSimulateResponse:
    # Convert overs (e.g. 14.2) into discrete legal deliveries
    full_overs = int(req.overs_completed)
    partial_balls = int(round((req.overs_completed - full_overs) * 10))
    balls_bowled = min(
        req.total_overs * 6, (full_overs * 6) + partial_balls
    )
    total_balls = req.total_overs * 6
    balls_remaining = max(0, total_balls - balls_bowled)

    wickets_in_hand = max(0, 10 - req.wickets_lost)

    # Current Run Rate (CRR)
    crr = (
        round((req.current_score / balls_bowled) * 6.0, 2)
        if balls_bowled > 0
        else 0.0
    )

    # 1. Score Projection Calculation
    if wickets_in_hand == 0 or balls_remaining == 0:
        projected_score = req.current_score
    else:
        # Resource weighting based on remaining wickets
        resource_factor = wickets_in_hand / 10.0
        overs_left = balls_remaining / 6.0

        if req.overs_completed >= 15:  # Death phase acceleration
            projected_rr = max(6.5, crr * 1.1) * (
                0.65 + 0.35 * resource_factor
            )
        elif req.overs_completed >= 6:  # Middle overs consolidation
            projected_rr = max(6.0, crr) * (0.70 + 0.30 * resource_factor)
        else:  # Powerplay
            projected_rr = max(7.0, crr) * (0.80 + 0.20 * resource_factor)

        projected_runs = overs_left * projected_rr
        projected_score = int(round(req.current_score + projected_runs))

    # 2. Chase Metrics (if target provided)
    runs_required = None
    rrr = None
    win_prob_bat = None
    win_prob_bowl = None

    if req.target_runs is not None:
        runs_required = max(0, req.target_runs - req.current_score)
        rrr = (
            round((runs_required / balls_remaining) * 6.0, 2)
            if balls_remaining > 0
            else (0.0 if runs_required == 0 else 99.0)
        )

        prob = historical_win_predictor.predict(
           runs_required=runs_required,
           balls_remaining=balls_remaining,
           wickets_in_hand=wickets_in_hand,
        )

        win_prob_bat = round(prob, 2)
        win_prob_bowl = round(100.0 - prob, 2)

        # Risk Tier Classification
        if wickets_in_hand <= 2 or rrr >= 14.0:
            risk = "EXTREME"
            outlook = f"Extreme pressure: RRR at {rrr:.1f} with only {wickets_in_hand} wickets in hand. Boundaries mandatory every over."
        elif wickets_in_hand <= 4 or rrr >= 11.0:
            risk = "HIGH"
            outlook = f"High risk: Chasing team requires {runs_required} off {balls_remaining} balls (RRR {rrr:.1f}). Bowling team controls leverage."
        elif rrr >= 8.5:
            risk = "MODERATE"
            outlook = f"Balanced contest: Target reachable with disciplined strike rotation and preserving remaining {wickets_in_hand} wickets."
        else:
            risk = "LOW"
            outlook = f"Comfortable chase: Required rate is manageable ({rrr:.1f} RPO). Batting team strongly favored ({win_prob_bat}% win probability)."
    else:
        # 1st Innings outlook
        if wickets_in_hand <= 3:
            risk = "HIGH"
            outlook = f"Wickets depleted: Team projected to reach {projected_score}. Batters must protect wickets to bat out full 20 overs."
        elif wickets_in_hand >= 7 and req.overs_completed >= 14:
            risk = "LOW"
            outlook = f"Aggressive launchpad: {wickets_in_hand} wickets remaining entering death overs. High boundary potential to exceed {projected_score}."
        else:
            risk = "MODERATE"
            outlook = f"Par progression: Score tracking toward {projected_score} based on current run rate of {crr:.2f}."

    return ScenarioSimulateResponse(
        current_score=req.current_score,
        overs_completed=req.overs_completed,
        balls_bowled=balls_bowled,
        balls_remaining=balls_remaining,
        wickets_lost=req.wickets_lost,
        wickets_in_hand=wickets_in_hand,
        current_run_rate=crr,
        projected_score=projected_score,
        target_runs=req.target_runs,
        runs_required=runs_required,
        required_run_rate=rrr,
        win_probability_batting=win_prob_bat,
        win_probability_bowling=win_prob_bowl,
        risk_level=risk,
        tactical_outlook=outlook,
    )