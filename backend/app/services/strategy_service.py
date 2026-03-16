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
from backend.app.services.player_service import compute_player_analytics


def get_head_to_head_matchup(
    db: Session, batter_id: int, bowler_id: int
) -> MatchupStats:
    batter = db.query(Player).filter(Player.id == batter_id).first()
    bowler = db.query(Player).filter(Player.id == bowler_id).first()
    if not batter or not bowler:
        return None

    deliveries = (
        db.query(Delivery)
        .filter(
            Delivery.batter_id == batter_id, Delivery.bowler_id == bowler_id
        )
        .all()
    )

    legal_balls = [d for d in deliveries if d.extra_type != "wide"]
    balls_faced = len(legal_balls)
    runs_scored = sum(d.runs_batter for d in legal_balls)
    dismissals = sum(
        1
        for d in deliveries
        if d.is_wicket
        and d.player_dismissed_id == batter_id
        and d.dismissal_type != "runout"
    )

    fours = sum(1 for d in legal_balls if d.runs_batter == 4)
    sixes = sum(1 for d in legal_balls if d.runs_batter == 6)
    dots = sum(1 for d in legal_balls if d.runs_batter == 0)

    sr = (
        round((runs_scored / balls_faced) * 100, 2)
        if balls_faced > 0
        else 0.0
    )
    dot_pct = (
        round((dots / balls_faced) * 100, 2) if balls_faced > 0 else 0.0
    )

    # Advantage classification
    if dismissals >= 1 and sr <= 115.0:
        advantage = "BOWLER_FAVORED"
    elif sr >= 140.0 and dismissals == 0:
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
        strike_rate=sr,
        dot_ball_pct=dot_pct,
        fours=fours,
        sixes=sixes,
        advantage=advantage,
    )


def recommend_bowling_options(
    db: Session, req: BowlingStrategyRequest
) -> BowlingStrategyResponse:
    batter = db.query(Player).filter(Player.id == req.batter_id).first()
    if not batter:
        return None

    bowlers = (
        db.query(Player)
        .filter(
            Player.team_id == req.bowling_team_id,
            Player.role.in_(["BOWLER", "ALL_ROUNDER"]),
        )
        .all()
    )

    ranked_candidates = []
    phase_key = req.match_phase.lower()

    for b in bowlers:
        analytics = compute_player_analytics(db, b.id)
        phase_econ = 8.5
        phase_wkts = 0

        if analytics and analytics.get("bowling"):
            ph = analytics["bowling"]["phases"].get(phase_key, {})
            if ph and ph.get("economy", 0) > 0:
                phase_econ = ph["economy"]
                phase_wkts = ph.get("wickets", 0)
            elif analytics["bowling"].get("economy", 0) > 0:
                phase_econ = analytics["bowling"]["economy"]

        matchup = get_head_to_head_matchup(db, req.batter_id, b.id)
        matchup_edge = matchup.advantage if matchup else "BALANCED"

        # Scoring formula: lower economy + wickets + head-to-head advantage
        score = 60.0 - (phase_econ * 3.0) + (phase_wkts * 8.0)
        if matchup_edge == "BOWLER_FAVORED":
            score += 18.0
        elif matchup_edge == "BATTER_FAVORED":
            score -= 12.0

        score = round(max(10.0, min(95.0, score)), 1)

        rationale = (
            f"{b.name} concedes {phase_econ:.1f} RPO in {phase_key} phase. "
            f"Matchup vs {batter.name}: {matchup_edge.replace('_', ' ').title()}."
        )

        ranked_candidates.append(
            {
                "bowler_id": b.id,
                "bowler_name": b.name,
                "phase_economy": phase_econ,
                "matchup_advantage": matchup_edge,
                "recommendation_score": score,
                "rationale": rationale,
            }
        )

    ranked_candidates.sort(
        key=lambda x: x["recommendation_score"], reverse=True
    )

    recommendations = [
        BowlerRecommendation(
            bowler_id=item["bowler_id"],
            bowler_name=item["bowler_name"],
            rank=idx + 1,
            phase_economy=item["phase_economy"],
            matchup_advantage=item["matchup_advantage"],
            recommendation_score=item["recommendation_score"],
            rationale=item["rationale"],
        )
        for idx, item in enumerate(ranked_candidates)
    ]

    return BowlingStrategyResponse(
        batter_id=batter.id,
        batter_name=batter.name,
        match_phase=phase_key,
        recommendations=recommendations,
    )


def recommend_batting_strategy(
    db: Session, req: BattingStrategyRequest
) -> BattingStrategyResponse:
    bowler = db.query(Player).filter(Player.id == req.bowler_id).first()
    if not bowler:
        return None

    analytics = compute_player_analytics(db, req.bowler_id)
    econ = (
        analytics["bowling"]["economy"]
        if analytics and analytics.get("bowling")
        else 8.0
    )

    rrr = req.required_run_rate or 8.0

    if rrr >= 11.5:
        approach = "AGGRESSIVE_ATTACK"
        risk = "HIGH"
        directive = "Target boundaries off early deliveries in the over; force bowler off length."
        insight = f"Required rate is critical ({rrr:.1f}). Must take calculated risks against {bowler.name}."
    elif econ <= 6.5 and rrr <= 8.5:
        approach = "STRIKE_ROTATION"
        risk = "LOW"
        directive = (
            "Prioritize singles and twos; preserve wickets against high-value"
            " bowler."
        )
        insight = f"{bowler.name} operates at an economical {econ:.1f} RPO. Avoid unnecessary boundary hunting."
    else:
        approach = "CONTROLLED_ACCELERATION"
        risk = "MODERATE"
        directive = (
            "Capitalize on loose deliveries while maintaining run-a-ball"
            " floor."
        )
        insight = f"Standard phase balance against {bowler.bowling_style or 'bowling attack'}."

    return BattingStrategyResponse(
        bowler_id=bowler.id,
        bowler_name=bowler.name,
        bowling_style=bowler.bowling_style,
        recommended_approach=approach,
        risk_level=risk,
        tactical_directive=directive,
        supporting_insight=insight,
    )