from typing import List

from sqlalchemy.orm import Session

from backend.app.models.cricket import Delivery, Player
from backend.app.schemas.strategy import (
    BattingStrategyRequest,
    BattingStrategyResponse,
    BowlerRecommendation,
    BowlingStrategyRequest,
    BowlingStrategyResponse,
    MatchupStats,
)
from backend.app.services.player_intelligence_service import (
    load_player_historical_data,
    normalize_player_name,
    player_name_matches,
)
from backend.app.services.player_service import compute_player_analytics


def _build_matchup_stats(
    batter: Player,
    bowler: Player,
    deliveries,
) -> MatchupStats | None:
    if not deliveries:
        return None

    balls_faced = len(deliveries)
    runs_scored = sum(
        int(getattr(d, "runs_batter", 0) or 0)
        for d in deliveries
    )

    dismissals = sum(
        1
        for d in deliveries
        if bool(getattr(d, "is_wicket", False))
        and getattr(d, "player_dismissed_id", None) == batter.id
        and getattr(d, "dismissal_type", None) != "runout"
    )

    fours = sum(
        1
        for d in deliveries
        if int(getattr(d, "runs_batter", 0) or 0) == 4
    )

    sixes = sum(
        1
        for d in deliveries
        if int(getattr(d, "runs_batter", 0) or 0) == 6
    )

    dots = sum(
        1
        for d in deliveries
        if int(getattr(d, "runs_batter", 0) or 0) == 0
    )

    strike_rate = (
        round((runs_scored / balls_faced) * 100, 2)
        if balls_faced > 0
        else 0.0
    )

    dot_ball_pct = (
        round((dots / balls_faced) * 100, 2)
        if balls_faced > 0
        else 0.0
    )

    if dismissals >= 1 and strike_rate <= 115.0:
        advantage = "BOWLER_FAVORED"
    elif strike_rate >= 140.0 and dismissals == 0:
        advantage = "BATTER_FAVORED"
    else:
        advantage = "BALANCED"

    return MatchupStats(
        batter_id=batter.id,
        batter_name=batter.name,
        bowler_id=bowler.id,
        bowler_name=bowler.name,
        balls_faced=balls_faced,
        runs_scored=runs_scored,
        dismissals=dismissals,
        strike_rate=strike_rate,
        dot_ball_pct=dot_ball_pct,
        fours=fours,
        sixes=sixes,
        advantage=advantage,
    )


def _get_historical_matchup(
    batter: Player,
    bowler: Player,
) -> MatchupStats | None:
    """
    Build batter-vs-bowler matchup statistics from Cricsheet
    when PostgreSQL does not contain direct delivery history.
    """

    batter_name = normalize_player_name(batter.name)
    bowler_name = normalize_player_name(bowler.name)

    df = load_player_historical_data(batter.name)

    if df.empty:
        return None

    batter_mask = df["batter"].fillna("").apply(
        lambda name: player_name_matches(
            str(name),
            batter_name,
        )
    )

    bowler_mask = df["bowler"].fillna("").apply(
        lambda name: player_name_matches(
            str(name),
            bowler_name,
        )
    )

    matchup_df = df[batter_mask & bowler_mask].copy()

    if matchup_df.empty:
        return None

    legal_mask = matchup_df["is_legal"].fillna(True).astype(bool)
    legal_balls = matchup_df[legal_mask]

    balls_faced = len(legal_balls)

    runs_scored = int(
        legal_balls["runs_batter"].sum()
    )

    wickets_df = matchup_df[
        matchup_df["is_wicket"].fillna(False).astype(bool)
    ].copy()

    wickets_df = wickets_df[
        wickets_df["dismissal_type"]
        .fillna("")
        .astype(str)
        .str.lower()
        != "runout"
    ]

    wickets_df = wickets_df[
        wickets_df["player_dismissed"]
        .fillna("")
        .apply(
            lambda name: player_name_matches(
                str(name),
                batter_name,
            )
        )
    ]

    dismissals = len(wickets_df)

    fours = int(
        (legal_balls["runs_batter"] == 4).sum()
    )

    sixes = int(
        (legal_balls["runs_batter"] == 6).sum()
    )

    dots = int(
        (legal_balls["runs_batter"] == 0).sum()
    )

    strike_rate = (
        round((runs_scored / balls_faced) * 100, 2)
        if balls_faced > 0
        else 0.0
    )

    dot_ball_pct = (
        round((dots / balls_faced) * 100, 2)
        if balls_faced > 0
        else 0.0
    )

    if dismissals >= 1 and strike_rate <= 115.0:
        advantage = "BOWLER_FAVORED"
    elif strike_rate >= 140.0 and dismissals == 0:
        advantage = "BATTER_FAVORED"
    else:
        advantage = "BALANCED"

    return MatchupStats(
        batter_id=batter.id,
        batter_name=batter.name,
        bowler_id=bowler.id,
        bowler_name=bowler.name,
        balls_faced=balls_faced,
        runs_scored=runs_scored,
        dismissals=dismissals,
        strike_rate=strike_rate,
        dot_ball_pct=dot_ball_pct,
        fours=fours,
        sixes=sixes,
        advantage=advantage,
    )


def get_head_to_head_matchup(
    db: Session,
    batter_id: int,
    bowler_id: int,
) -> MatchupStats:
    batter = (
        db.query(Player)
        .filter(Player.id == batter_id)
        .first()
    )

    bowler = (
        db.query(Player)
        .filter(Player.id == bowler_id)
        .first()
    )

    if not batter or not bowler:
        return None

    deliveries = (
        db.query(Delivery)
        .filter(
            Delivery.batter_id == batter_id,
            Delivery.bowler_id == bowler_id,
        )
        .all()
    )

    # Use the PostgreSQL delivery history first.
    if deliveries:
        legal_balls = [
            d
            for d in deliveries
            if d.extra_type != "wide"
        ]

        matchup = _build_matchup_stats(
            batter,
            bowler,
            legal_balls,
        )

        if matchup:
            return matchup

    # Fall back to Cricsheet historical delivery data.
    return _get_historical_matchup(
        batter,
        bowler,
    )


def recommend_bowling_options(
    db: Session,
    req: BowlingStrategyRequest,
) -> BowlingStrategyResponse:
    batter = (
        db.query(Player)
        .filter(Player.id == req.batter_id)
        .first()
    )

    if not batter:
        return None

    bowlers = (
        db.query(Player)
        .filter(
            Player.team_id == req.bowling_team_id,
            Player.role.in_(
                ["BOWLER", "ALL_ROUNDER"]
            ),
        )
        .all()
    )

    ranked_candidates = []
    phase_key = req.match_phase.lower()

    for bowler in bowlers:
        analytics = compute_player_analytics(
            db,
            bowler.id,
        )

        phase_economy = 8.5
        phase_wickets = 0

        if analytics and analytics.get("bowling"):
            phases = analytics["bowling"].get(
                "phases",
                {},
            )

            phase_stats = phases.get(
                phase_key,
                {},
            )

            if (
                phase_stats
                and phase_stats.get("economy", 0) > 0
            ):
                phase_economy = phase_stats["economy"]
                phase_wickets = phase_stats.get(
                    "wickets",
                    0,
                )

            elif analytics["bowling"].get(
                "economy",
                0,
            ) > 0:
                phase_economy = analytics["bowling"][
                    "economy"
                ]

        matchup = get_head_to_head_matchup(
            db,
            req.batter_id,
            bowler.id,
        )

        matchup_edge = (
            matchup.advantage
            if matchup
            else "BALANCED"
        )

        score = (
            60.0
            - (phase_economy * 3.0)
            + (phase_wickets * 8.0)
        )

        if matchup_edge == "BOWLER_FAVORED":
            score += 18.0

        elif matchup_edge == "BATTER_FAVORED":
            score -= 12.0

        score = round(
            max(10.0, min(95.0, score)),
            1,
        )

        rationale = (
            f"{bowler.name} concedes "
            f"{phase_economy:.1f} RPO in "
            f"{phase_key} phase. "
            f"Matchup vs {batter.name}: "
            f"{matchup_edge.replace('_', ' ').title()}."
        )

        ranked_candidates.append(
            {
                "bowler_id": bowler.id,
                "bowler_name": bowler.name,
                "phase_economy": phase_economy,
                "matchup_advantage": matchup_edge,
                "recommendation_score": score,
                "rationale": rationale,
            }
        )

    ranked_candidates.sort(
        key=lambda item: item["recommendation_score"],
        reverse=True,
    )

    recommendations = [
        BowlerRecommendation(
            bowler_id=item["bowler_id"],
            bowler_name=item["bowler_name"],
            rank=index + 1,
            phase_economy=item["phase_economy"],
            matchup_advantage=item["matchup_advantage"],
            recommendation_score=item["recommendation_score"],
            rationale=item["rationale"],
        )
        for index, item in enumerate(
            ranked_candidates
        )
    ]

    return BowlingStrategyResponse(
        batter_id=batter.id,
        batter_name=batter.name,
        match_phase=phase_key,
        recommendations=recommendations,
    )


def recommend_batting_strategy(
    db: Session,
    req: BattingStrategyRequest,
) -> BattingStrategyResponse:
    bowler = (
        db.query(Player)
        .filter(Player.id == req.bowler_id)
        .first()
    )

    if not bowler:
        return None

    analytics = compute_player_analytics(
        db,
        req.bowler_id,
    )

    economy = (
        analytics["bowling"]["economy"]
        if analytics
        and analytics.get("bowling")
        else 8.0
    )

    required_run_rate = (
        req.required_run_rate
        if req.required_run_rate is not None
        else 8.0
    )

    if required_run_rate >= 11.5:
        approach = "AGGRESSIVE_ATTACK"
        risk = "HIGH"

        directive = (
            "Target boundaries off early deliveries "
            "in the over; force bowler off length."
        )

        insight = (
            f"Required rate is critical "
            f"({required_run_rate:.1f}). "
            f"Must take calculated risks against "
            f"{bowler.name}."
        )

    elif economy <= 6.5 and required_run_rate <= 8.5:
        approach = "STRIKE_ROTATION"
        risk = "LOW"

        directive = (
            "Prioritize singles and twos; preserve "
            "wickets against high-value bowler."
        )

        insight = (
            f"{bowler.name} operates at an economical "
            f"{economy:.1f} RPO. Avoid unnecessary "
            "boundary hunting."
        )

    else:
        approach = "CONTROLLED_ACCELERATION"
        risk = "MODERATE"

        directive = (
            "Capitalize on loose deliveries while "
            "maintaining run-a-ball floor."
        )

        insight = (
            f"Standard phase balance against "
            f"{bowler.bowling_style or 'bowling attack'}."
        )

    return BattingStrategyResponse(
        bowler_id=bowler.id,
        bowler_name=bowler.name,
        bowling_style=bowler.bowling_style,
        recommended_approach=approach,
        risk_level=risk,
        tactical_directive=directive,
        supporting_insight=insight,
    )