from statistics import mean

from sqlalchemy.orm import Session

from backend.app.models.cricket import Player
from backend.app.schemas.scenario import ScenarioSimulateRequest
from backend.app.schemas.strategy import (
    BattingStrategyRequest,
    BowlingStrategyRequest,
)
from backend.app.schemas.strategy_lab import (
    StrategyLabRequest,
    StrategyLabResponse,
    StrategyOption,
)
from backend.app.services.scenario_service import run_scenario_simulation
from backend.app.services.strategy_service import (
    recommend_batting_strategy,
    recommend_bowling_options,
)


def _clamp_probability(value: float) -> float:
    return round(max(0.0, min(100.0, value)), 2)


def _calculate_required_run_rate(req: StrategyLabRequest):
    if req.target_runs is None:
        return None

    full_overs = int(req.overs_completed)

    partial_balls = int(
        round(
            (req.overs_completed - full_overs) * 10
        )
    )

    partial_balls = min(
        max(partial_balls, 0),
        5,
    )

    balls_bowled = min(
        req.total_overs * 6,
        (full_overs * 6) + partial_balls,
    )

    balls_remaining = max(
        0,
        req.total_overs * 6 - balls_bowled,
    )

    runs_required = max(
        0,
        req.target_runs - req.current_score,
    )

    if balls_remaining <= 0:
        return None

    return (runs_required / balls_remaining) * 6.0


def _build_strategy_option(
    recommendation,
    batting_strategy,
    scenario_result,
    baseline_score: float,
    average_score: float,
    rank: int,
) -> StrategyOption:
    score_delta = recommendation.recommendation_score - average_score

    # Convert the recommendation score difference into a
    # small model adjustment around the baseline scenario.
    probability_adjustment = score_delta * 0.12

    adjusted_probability = _clamp_probability(
        baseline_score + probability_adjustment
    )

    return StrategyOption(
        rank=rank,
        bowler_id=recommendation.bowler_id,
        bowler_name=recommendation.bowler_name,
        recommendation_score=recommendation.recommendation_score,
        matchup_advantage=recommendation.matchup_advantage,
        phase_economy=recommendation.phase_economy,
        projected_batting_win_probability=adjusted_probability,
        risk_level=(
            batting_strategy.risk_level
            if batting_strategy
            else "MODERATE"
        ),
        tactical_directive=(
            batting_strategy.tactical_directive
            if batting_strategy
            else "Assess this bowler using matchup and phase conditions."
        ),
        rationale=recommendation.rationale,
    )


def run_strategy_lab(
    db: Session,
    req: StrategyLabRequest,
) -> StrategyLabResponse:

    batter = (
        db.query(Player)
        .filter(Player.id == req.batter_id)
        .first()
    )

    if not batter:
        raise ValueError("Batter not found")

    bowling_result = recommend_bowling_options(
        db,
        BowlingStrategyRequest(
            batter_id=req.batter_id,
            bowling_team_id=req.bowling_team_id,
            match_phase=req.match_phase,
        ),
    )

    if not bowling_result or not bowling_result.recommendations:
        return StrategyLabResponse(
            batter_id=batter.id,
            batter_name=batter.name,
            current_score=req.current_score,
            overs_completed=req.overs_completed,
            wickets_lost=req.wickets_lost,
            target_runs=req.target_runs,
            match_phase=req.match_phase.lower(),
            options=[],
            recommended_option=None,
            decision_summary=(
                "No eligible bowling options were found for this scenario."
            ),
        )

    scenario_result = run_scenario_simulation(
        ScenarioSimulateRequest(
            current_score=req.current_score,
            overs_completed=req.overs_completed,
            wickets_lost=req.wickets_lost,
            target_runs=req.target_runs,
            total_overs=req.total_overs,
        )
    )

    baseline_probability = (
        scenario_result.win_probability_batting
        if scenario_result.win_probability_batting is not None
        else 50.0
    )

    recommendation_scores = [
        item.recommendation_score
        for item in bowling_result.recommendations
    ]

    average_score = mean(recommendation_scores)

    required_run_rate = _calculate_required_run_rate(req)

    options = []

    for recommendation in bowling_result.recommendations:

        batting_strategy = recommend_batting_strategy(
            db,
            BattingStrategyRequest(
                bowler_id=recommendation.bowler_id,
                match_phase=req.match_phase,
                required_run_rate=required_run_rate,
            ),
        )

        options.append(
            _build_strategy_option(
                recommendation=recommendation,
                batting_strategy=batting_strategy,
                scenario_result=scenario_result,
                baseline_score=baseline_probability,
                average_score=average_score,
                rank=recommendation.rank,
            )
        )

    options.sort(
        key=lambda option: option.projected_batting_win_probability,
        reverse=False,
    )

    for index, option in enumerate(options, start=1):
        option.rank = index

    # Lowest projected batting probability represents the strongest
    # bowling-side option under this heuristic.
    recommended = options[0] if options else None

    if recommended:
        decision_summary = (
            f"Strategy Lab identifies {recommended.bowler_name} as the "
            f"top bowling option against {batter.name}. "
            f"Its recommendation score is "
            f"{recommended.recommendation_score:.1f}/100, with "
            f"{recommended.matchup_advantage.replace('_', ' ').title()} "
            f"head-to-head evidence and {recommended.phase_economy:.1f} "
            f"RPO in the selected phase. "
            f"The baseline batting win probability is "
            f"{baseline_probability:.1f}%, while this option's "
            f"decision-adjusted estimate is "
            f"{recommended.projected_batting_win_probability:.1f}%."
        )
    else:
        decision_summary = (
            "Strategy Lab could not produce a ranked decision."
        )

    return StrategyLabResponse(
        batter_id=batter.id,
        batter_name=batter.name,
        current_score=req.current_score,
        overs_completed=req.overs_completed,
        wickets_lost=req.wickets_lost,
        target_runs=req.target_runs,
        match_phase=req.match_phase.lower(),
        options=options,
        recommended_option=recommended,
        decision_summary=decision_summary,
        uncertainty_note=(
            "The baseline probability comes from CricketIQ's historical "
            "scenario model. Option-level probability is a decision-"
            "adjusted heuristic derived from the bowling recommendation "
            "score and should not be interpreted as a separately trained "
            "win-probability model."
        ),
    )