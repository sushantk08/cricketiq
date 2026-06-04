from backend.app.ml.historical_win_probability import historical_win_predictor
from backend.app.schemas.scenario import (
    ScenarioInsight,
    ScenarioSimulateRequest,
    ScenarioSimulateResponse,
)


def _get_win_probability(
    runs_required: int,
    balls_remaining: int,
    wickets_in_hand: int,
) -> float:
    """
    Return the batting team's modeled win probability.

    Terminal match states are handled explicitly.
    """
    if runs_required <= 0:
        return 100.0

    if balls_remaining <= 0:
        return 0.0

    if wickets_in_hand <= 0:
        return 0.0

    return historical_win_predictor.predict(
        runs_required=runs_required,
        balls_remaining=balls_remaining,
        wickets_in_hand=wickets_in_hand,
    )


def _build_chase_insights(
    runs_required: int,
    balls_remaining: int,
    wickets_in_hand: int,
    required_run_rate: float,
    win_probability: float,
) -> list[ScenarioInsight]:
    """Build decision-oriented insights for a chase."""
    insights: list[ScenarioInsight] = []

    if balls_remaining <= 0:
        insights.append(
            ScenarioInsight(
                category="match_state",
                title="Innings complete",
                detail=(
                    "No deliveries remain, so the current score is the "
                    "terminal state for this scenario."
                ),
            )
        )
        return insights

    if runs_required <= 0:
        insights.append(
            ScenarioInsight(
                category="match_state",
                title="Target reached",
                detail=(
                    "The batting side has already reached the supplied "
                    "target."
                ),
            )
        )
        return insights

    if required_run_rate >= 14:
        insights.append(
            ScenarioInsight(
                category="pressure",
                title="Very high required rate",
                detail=(
                    f"The chase requires {required_run_rate:.2f} runs per "
                    "over, creating substantial scoring pressure."
                ),
            )
        )
    elif required_run_rate >= 10:
        insights.append(
            ScenarioInsight(
                category="pressure",
                title="High required rate",
                detail=(
                    f"The required rate is {required_run_rate:.2f} runs "
                    "per over, so sustained boundary scoring may be needed."
                ),
            )
        )
    elif required_run_rate <= 7:
        insights.append(
            ScenarioInsight(
                category="opportunity",
                title="Manageable required rate",
                detail=(
                    f"The required rate is {required_run_rate:.2f} runs "
                    "per over, leaving room for controlled strike rotation."
                ),
            )
        )

    if wickets_in_hand <= 2:
        insights.append(
            ScenarioInsight(
                category="resources",
                title="Wickets are a major constraint",
                detail=(
                    f"Only {wickets_in_hand} wickets remain, so preserving "
                    "the remaining batting resources is critical."
                ),
            )
        )
    elif wickets_in_hand >= 7:
        insights.append(
            ScenarioInsight(
                category="resources",
                title="Strong wicket cushion",
                detail=(
                    f"{wickets_in_hand} wickets remain, giving the batting "
                    "side greater freedom to attack."
                ),
            )
        )

    if win_probability >= 70:
        insights.append(
            ScenarioInsight(
                category="probability",
                title="Batting side currently favored",
                detail=(
                    f"The historical model estimates a "
                    f"{win_probability:.1f}% batting win probability."
                ),
            )
        )
    elif win_probability <= 30:
        insights.append(
            ScenarioInsight(
                category="probability",
                title="Batting side currently under pressure",
                detail=(
                    f"The historical model estimates a "
                    f"{win_probability:.1f}% batting win probability."
                ),
            )
        )

    if not insights:
        insights.append(
            ScenarioInsight(
                category="match_state",
                title="Balanced scenario",
                detail=(
                    "The current run requirement, remaining balls and "
                    "wickets indicate a relatively balanced situation."
                ),
            )
        )

    return insights


def _build_innings_insights(
    wickets_in_hand: int,
    overs_completed: float,
    current_run_rate: float,
    projected_score: int,
) -> list[ScenarioInsight]:
    """Build decision-oriented insights for the first innings."""
    insights: list[ScenarioInsight] = []

    if wickets_in_hand <= 3:
        insights.append(
            ScenarioInsight(
                category="resources",
                title="Wicket preservation is important",
                detail=(
                    f"Only {wickets_in_hand} wickets remain, so protecting "
                    "resources may be more valuable than taking excessive risk."
                ),
            )
        )
    elif wickets_in_hand >= 7 and overs_completed >= 14:
        insights.append(
            ScenarioInsight(
                category="opportunity",
                title="Strong platform for acceleration",
                detail=(
                    f"{wickets_in_hand} wickets remain with the death overs "
                    "approaching or underway, creating room for increased "
                    "scoring intent."
                ),
            )
        )

    if current_run_rate >= 10:
        insights.append(
            ScenarioInsight(
                category="batting",
                title="Above-ten run-rate trajectory",
                detail=(
                    f"The current run rate is {current_run_rate:.2f}, "
                    f"supporting a projected total around {projected_score}."
                ),
            )
        )
    elif current_run_rate < 7 and overs_completed >= 6:
        insights.append(
            ScenarioInsight(
                category="batting",
                title="Scoring rate needs attention",
                detail=(
                    f"The current run rate is {current_run_rate:.2f}, "
                    "which may require improved scoring tempo."
                ),
            )
        )

    if not insights:
        insights.append(
            ScenarioInsight(
                category="match_state",
                title="Stable innings progression",
                detail=(
                    f"The innings is tracking toward approximately "
                    f"{projected_score} runs under the current projection."
                ),
            )
        )

    return insights


def run_scenario_simulation(
    req: ScenarioSimulateRequest,
) -> ScenarioSimulateResponse:
    """
    Simulate the current match scenario and provide
    decision-oriented intelligence.
    """

    # ---------------------------------------------------------
    # Convert overs into legal deliveries
    # ---------------------------------------------------------

    full_overs = int(req.overs_completed)

    partial_balls = int(
        round(
            (req.overs_completed - full_overs) * 10
        )
    )

    # Keep malformed decimal values such as 14.7 from
    # producing more than six balls in the partial over.
    partial_balls = min(
        max(partial_balls, 0),
        5,
    )

    balls_bowled = min(
        req.total_overs * 6,
        (full_overs * 6) + partial_balls,
    )

    total_balls = req.total_overs * 6

    balls_remaining = max(
        0,
        total_balls - balls_bowled,
    )

    wickets_in_hand = max(
        0,
        10 - req.wickets_lost,
    )

    # ---------------------------------------------------------
    # Current Run Rate
    # ---------------------------------------------------------

    crr = (
        round(
            (req.current_score / balls_bowled) * 6.0,
            2,
        )
        if balls_bowled > 0
        else 0.0
    )

    # ---------------------------------------------------------
    # Score Projection
    # ---------------------------------------------------------

    if (
        wickets_in_hand == 0
        or balls_remaining == 0
    ):
        projected_score = req.current_score

    else:
        resource_factor = wickets_in_hand / 10.0
        overs_left = balls_remaining / 6.0

        if req.overs_completed >= 15:
            projected_rr = max(
                6.5,
                crr * 1.1,
            ) * (
                0.65 + 0.35 * resource_factor
            )

        elif req.overs_completed >= 6:
            projected_rr = max(
                6.0,
                crr,
            ) * (
                0.70 + 0.30 * resource_factor
            )

        else:
            projected_rr = max(
                7.0,
                crr,
            ) * (
                0.80 + 0.20 * resource_factor
            )

        projected_runs = (
            overs_left * projected_rr
        )

        projected_score = int(
            round(
                req.current_score + projected_runs
            )
        )

    # ---------------------------------------------------------
    # Defaults
    # ---------------------------------------------------------

    runs_required = None
    required_run_rate = None
    win_prob_bat = None
    win_prob_bowl = None

    key_insights: list[ScenarioInsight] = []

    # ---------------------------------------------------------
    # Chase scenario
    # ---------------------------------------------------------

    if req.target_runs is not None:

        runs_required = max(
            0,
            req.target_runs - req.current_score,
        )

        if balls_remaining > 0:
            required_run_rate = round(
                (runs_required / balls_remaining) * 6.0,
                2,
            )
        else:
            required_run_rate = (
                0.0
                if runs_required == 0
                else 99.0
            )

        prob = _get_win_probability(
            runs_required=runs_required,
            balls_remaining=balls_remaining,
            wickets_in_hand=wickets_in_hand,
        )

        win_prob_bat = round(
            prob,
            2,
        )

        win_prob_bowl = round(
            100.0 - prob,
            2,
        )

        # -----------------------------------------------------
        # Risk classification
        # -----------------------------------------------------

        if (
            wickets_in_hand <= 2
            or required_run_rate >= 14.0
        ):
            risk = "EXTREME"

            outlook = (
                f"Extreme pressure: {runs_required} runs are required "
                f"from {balls_remaining} balls at "
                f"{required_run_rate:.2f} RPO with only "
                f"{wickets_in_hand} wickets in hand."
            )

        elif (
            wickets_in_hand <= 4
            or required_run_rate >= 11.0
        ):
            risk = "HIGH"

            outlook = (
                f"High-pressure chase: {runs_required} runs are required "
                f"from {balls_remaining} balls at "
                f"{required_run_rate:.2f} RPO."
            )

        elif required_run_rate >= 8.5:
            risk = "MODERATE"

            outlook = (
                f"Competitive chase: {runs_required} runs are required "
                f"from {balls_remaining} balls at "
                f"{required_run_rate:.2f} RPO."
            )

        else:
            risk = "LOW"

            outlook = (
                f"Manageable chase: {runs_required} runs are required "
                f"from {balls_remaining} balls at "
                f"{required_run_rate:.2f} RPO, with a modeled batting "
                f"win probability of {win_prob_bat:.1f}%."
            )

        key_insights = _build_chase_insights(
            runs_required=runs_required,
            balls_remaining=balls_remaining,
            wickets_in_hand=wickets_in_hand,
            required_run_rate=required_run_rate,
            win_probability=win_prob_bat,
        )

        decision_summary = (
            f"Decision view: the batting side needs {runs_required} runs "
            f"from {balls_remaining} balls while retaining "
            f"{wickets_in_hand} wickets. The historical model estimates "
            f"{win_prob_bat:.1f}% batting win probability."
        )

    # ---------------------------------------------------------
    # First innings scenario
    # ---------------------------------------------------------

    else:

        if wickets_in_hand <= 3:
            risk = "HIGH"

            outlook = (
                f"Wickets depleted: {wickets_in_hand} wickets remain and "
                f"the current projection is approximately "
                f"{projected_score} runs."
            )

        elif (
            wickets_in_hand >= 7
            and req.overs_completed >= 14
        ):
            risk = "LOW"

            outlook = (
                f"Strong launchpad: {wickets_in_hand} wickets remain "
                f"with the death phase approaching or underway. "
                f"Projected score is {projected_score}."
            )

        else:
            risk = "MODERATE"

            outlook = (
                f"Current progression points toward approximately "
                f"{projected_score} runs at a current run rate of "
                f"{crr:.2f}."
            )

        key_insights = _build_innings_insights(
            wickets_in_hand=wickets_in_hand,
            overs_completed=req.overs_completed,
            current_run_rate=crr,
            projected_score=projected_score,
        )

        decision_summary = (
            f"Decision view: the innings is currently {req.current_score} "
            f"after {req.overs_completed:.1f} overs, with "
            f"{wickets_in_hand} wickets in hand and a projected total "
            f"of approximately {projected_score}."
        )

    # ---------------------------------------------------------
    # Response
    # ---------------------------------------------------------

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
        required_run_rate=required_run_rate,
        win_probability_batting=win_prob_bat,
        win_probability_bowling=win_prob_bowl,
        risk_level=risk,
        tactical_outlook=outlook,
        key_insights=key_insights,
        decision_summary=decision_summary,
        uncertainty_note=(
            "All projections and probabilities are model-based estimates, "
            "not guarantees of match outcomes."
        ),
    )