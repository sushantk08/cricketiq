from typing import Dict, List

from sqlalchemy.orm import Session

from backend.app.services.player_service import compute_player_analytics


def _build_insight(
    category: str,
    title: str,
    detail: str,
) -> Dict[str, str]:
    return {
        "category": category,
        "title": title,
        "detail": detail,
    }


def generate_player_intelligence(
    db: Session,
    player_id: int,
) -> dict | None:
    """
    Generate decision-oriented player intelligence from
    existing database-derived player analytics.

    This layer does not invent statistics. All observations
    are derived from the existing player analytics service.
    """

    analytics = compute_player_analytics(db, player_id)

    if not analytics:
        return None

    batting = analytics.get("batting")
    bowling = analytics.get("bowling")

    strengths: List[Dict[str, str]] = []
    weaknesses: List[Dict[str, str]] = []
    recommendations: List[Dict[str, str]] = []

    # -------------------------
    # Batting intelligence
    # -------------------------
    if batting:
        phases = batting.get("phases", {})

        phase_strike_rates = {
            phase: data.get("strike_rate", 0.0)
            for phase, data in phases.items()
            if data.get("balls", 0) > 0
        }

        if phase_strike_rates:
            best_phase = max(
                phase_strike_rates,
                key=phase_strike_rates.get,
            )

            best_phase_rate = phase_strike_rates[best_phase]

            strengths.append(
                _build_insight(
                    "BATTING",
                    f"Strongest batting phase: {best_phase}",
                    (
                        f"The player records a strike rate of "
                        f"{best_phase_rate:.2f} in the {best_phase} phase."
                    ),
                )
            )

        if batting["strike_rate"] >= 130:
            strengths.append(
                _build_insight(
                    "BATTING",
                    "High scoring rate",
                    (
                        f"Overall strike rate is "
                        f"{batting['strike_rate']:.2f}, indicating "
                        "an aggressive scoring profile."
                    ),
                )
            )

        if batting["boundary_run_pct"] >= 45:
            strengths.append(
                _build_insight(
                    "BATTING",
                    "Boundary-driven scoring",
                    (
                        f"{batting['boundary_run_pct']:.2f}% of batting "
                        "runs come from boundaries."
                    ),
                )
            )

        if batting["dot_ball_pct"] >= 45:
            weaknesses.append(
                _build_insight(
                    "BATTING",
                    "High dot-ball exposure",
                    (
                        f"The player's dot-ball percentage is "
                        f"{batting['dot_ball_pct']:.2f}%, suggesting "
                        "potential pressure during scoring sequences."
                    ),
                )
            )

            recommendations.append(
                _build_insight(
                    "BATTING",
                    "Target strike rotation",
                    (
                        "Prioritize singles and twos when boundary "
                        "options are limited to reduce dot-ball pressure."
                    ),
                )
            )

        if phase_strike_rates:
            weakest_phase = min(
                phase_strike_rates,
                key=phase_strike_rates.get,
            )

            weakest_rate = phase_strike_rates[weakest_phase]

            if weakest_phase != best_phase:
                weaknesses.append(
                    _build_insight(
                        "BATTING",
                        f"Lower-output phase: {weakest_phase}",
                        (
                            f"Strike rate is {weakest_rate:.2f} in this phase "
                            f"compared with {best_phase_rate:.2f} in the "
                            f"{best_phase} phase."
                        ),
                    )
                )

                recommendations.append(
                    _build_insight(
                        "BATTING",
                        f"Manage {weakest_phase} phase better",
                        (
                            f"Plan batting resources around improving scoring "
                            f"efficiency during the {weakest_phase} phase."
                        ),
                    )
                )

    # -------------------------
    # Bowling intelligence
    # -------------------------
    if bowling:
        phases = bowling.get("phases", {})

        phase_economies = {
            phase: data.get("economy", 0.0)
            for phase, data in phases.items()
            if data.get("overs", 0) > 0
        }

        if phase_economies:
            best_phase = min(
                phase_economies,
                key=phase_economies.get,
            )

            best_economy = phase_economies[best_phase]

            strengths.append(
                _build_insight(
                    "BOWLING",
                    f"Best bowling phase: {best_phase}",
                    (
                        f"The player's economy is "
                        f"{best_economy:.2f} during the {best_phase} phase."
                    ),
                )
            )

            worst_phase = max(
                phase_economies,
                key=phase_economies.get,
            )

            worst_economy = phase_economies[worst_phase]

            if worst_phase != best_phase:
                weaknesses.append(
                    _build_insight(
                        "BOWLING",
                        f"Higher-risk phase: {worst_phase}",
                        (
                            f"Economy rises to {worst_economy:.2f} "
                            f"in the {worst_phase} phase versus "
                            f"{best_economy:.2f} in the {best_phase} phase."
                        ),
                    )
                )

                recommendations.append(
                    _build_insight(
                        "BOWLING",
                        f"Review {worst_phase} usage",
                        (
                            f"Consider matchup and game-state factors before "
                            f"using the player heavily in the {worst_phase} phase."
                        ),
                    )
                )

        if bowling["dot_ball_pct"] >= 40:
            strengths.append(
                _build_insight(
                    "BOWLING",
                    "Creates dot-ball pressure",
                    (
                        f"Dot-ball percentage is "
                        f"{bowling['dot_ball_pct']:.2f}%, indicating "
                        "the ability to restrict scoring opportunities."
                    ),
                )
            )
        if bowling["wickets"] >= 2:
            strengths.append(
                _build_insight(
                    "BOWLING",
                    "Wicket-taking contribution",
                    (
                        f"The player has recorded "
                        f"{bowling['wickets']} wickets in the "
                        "available bowling data."
                    ),
                )
            )
        if bowling["economy"] >= 9:
            weaknesses.append(
                _build_insight(
                    "BOWLING",
                    "Elevated overall economy",
                    (
                        f"Overall economy is "
                        f"{bowling['economy']:.2f} runs per over."
                    ),
                )
            )
            recommendations.append(
                    _build_insight(
                        "BOWLING",
                        "Use matchup-aware deployment",
                        (
                            "Consider using the bowler in phases or "
                            "matchups where their historical economy is strongest."
                        ),
                    )
                )
    # -------------------------
    # Role-based assessment
    # -------------------------
    role = analytics["role"].replace("_", " ").title()

    if batting and bowling:
        overall_assessment = (
            f"{analytics['name']} profiles as a two-way "
            f"{role} contributor. The available data should be used "
            "to select phases where the player has shown stronger "
            "historical output."
        )
    elif batting:
        overall_assessment = (
            f"{analytics['name']} profiles primarily as an "
            f"{role} with measurable bowling performance."
        )
    elif bowling:
        overall_assessment = (
            f"{analytics['name']} profiles primarily as an "
            f"{role} with measurable bowling performance."
        )
    else:
        overall_assessment = (
            f"Insufficient performance data is available to build "
            f"a detailed assessment for {analytics['name']}."
        )

    if not strengths:
        strengths.append(
            _build_insight(
                "DATA",
                "Limited positive evidence",
                "The available sample does not support a strong statistical strength.",
            )
        )

    if not weaknesses:
        weaknesses.append(
            _build_insight(
                "DATA",
                "No major weakness identified",
                (
                    "The available sample does not reveal a clear weakness "
                    "using the current intelligence rules."
                ),
            )
        )

    if not recommendations:
        recommendations.append(
            _build_insight(
                "GENERAL",
                "Use context with player statistics",
                (
                    "Combine player trends with match state, opponent "
                    "matchups, and phase-specific conditions before making decisions."
                ),
            )
        )

    evidence_parts = []

    if batting:
        evidence_parts.append(
            f"batting sample: {batting['innings_batted']} innings, "
            f"{batting['balls_faced']} balls"
        )

    if bowling:
        evidence_parts.append(
            f"bowling sample: {bowling['innings_bowled']} innings, "
            f"{bowling['overs_bowled']} overs"
        )

    evidence_summary = (
        "Intelligence derived from database-backed player analytics "
        f"({'; '.join(evidence_parts)})."
    )

    return {
        "player_id": analytics["player_id"],
        "player_name": analytics["name"],
        "role": analytics["role"],
        "team_name": analytics["team_name"],
        "overall_assessment": overall_assessment,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "recommendations": recommendations,
        "evidence_summary": evidence_summary,
    }