from functools import lru_cache
from pathlib import Path

import pandas as pd
from sqlalchemy.orm import Session

from backend.app.models.cricket import Player
from backend.app.schemas.player_intelligence import (
    PlayerInsight,
    PlayerIntelligenceResponse,
)


DATASET_PATH = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "historical"
    / "player_delivery_history.csv"
)


@lru_cache(maxsize=1)
def load_historical_data() -> pd.DataFrame:
    """Load the Cricsheet historical player delivery dataset once."""
    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Historical player dataset not found: {DATASET_PATH}"
        )

    df = pd.read_csv(DATASET_PATH)

    df["batter"] = df["batter"].fillna("").astype(str)
    df["bowler"] = df["bowler"].fillna("").astype(str)
    df["over"] = pd.to_numeric(df["over"], errors="coerce").fillna(0)
    df["runs_batter"] = pd.to_numeric(
        df["runs_batter"], errors="coerce"
    ).fillna(0)
    df["runs_extras"] = pd.to_numeric(
        df["runs_extras"], errors="coerce"
    ).fillna(0)
    df["runs_total"] = pd.to_numeric(
        df["runs_total"], errors="coerce"
    ).fillna(0)

    return df


def get_phase(over: int) -> str:
    """Classify a T20 over into a cricket phase."""
    if over < 6:
        return "powerplay"
    if over < 15:
        return "middle"
    return "death"


def safe_ratio(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


def generate_player_intelligence(
    db: Session,
    player_id: int,
) -> PlayerIntelligenceResponse | None:
    """
    Generate player intelligence from the full Cricsheet historical dataset.

    PostgreSQL is used only for player identity/role/team information.
    Performance statistics come from Cricsheet.
    """
    player = (
        db.query(Player)
        .filter(Player.id == player_id)
        .first()
    )

    if not player:
        return None

    df = load_historical_data()

    player_name = player.name.strip()

    batting_df = df[df["batter"].str.casefold() == player_name.casefold()].copy()
    bowling_df = df[df["bowler"].str.casefold() == player_name.casefold()].copy()

    strengths: list[PlayerInsight] = []
    weaknesses: list[PlayerInsight] = []
    recommendations: list[PlayerInsight] = []

    batting_runs = float(batting_df["runs_batter"].sum())
    batting_balls = int(
        batting_df.loc[batting_df["is_legal"] == True].shape[0]  # noqa: E712
    )

    batting_strike_rate = (
        batting_runs / batting_balls * 100
        if batting_balls > 0
        else 0.0
    )

    fours = int((batting_df["runs_batter"] == 4).sum())
    sixes = int((batting_df["runs_batter"] == 6).sum())

    legal_balls = batting_df.loc[
        batting_df["is_legal"] == True  # noqa: E712
    ]

    dot_balls = int(
        (
            (legal_balls["runs_batter"] == 0)
            & (legal_balls["runs_extras"] == 0)
        ).sum()
    )

    dot_ball_percentage = safe_ratio(
        dot_balls,
        batting_balls,
    ) * 100

    boundary_runs = (fours * 4) + (sixes * 6)
    boundary_run_percentage = safe_ratio(
        boundary_runs,
        batting_runs,
    ) * 100

    batting_matches = (
        batting_df["match_id"].nunique()
        if not batting_df.empty
        else 0
    )

    batting_phase = {}

    if not batting_df.empty:
        batting_df["phase"] = batting_df["over"].apply(get_phase)

        for phase in ("powerplay", "middle", "death"):
            phase_df = batting_df[batting_df["phase"] == phase]

            phase_balls = int(
                phase_df.loc[
                    phase_df["is_legal"] == True  # noqa: E712
                ].shape[0]
            )

            phase_runs = float(phase_df["runs_batter"].sum())

            batting_phase[phase] = {
                "runs": phase_runs,
                "balls": phase_balls,
                "strike_rate": (
                    phase_runs / phase_balls * 100
                    if phase_balls > 0
                    else 0.0
                ),
            }

    # ---------------------------------------------------------
    # Bowling analytics
    # ---------------------------------------------------------

    bowling_legal = bowling_df.loc[
        bowling_df["is_legal"] == True  # noqa: E712
    ].copy()

    bowling_legal_balls = len(bowling_legal)

    # Wides and no-balls are bowler-conceded runs.
    # Byes and leg-byes are not charged to the bowler.
    bowling_runs = float(bowling_df["runs_total"].sum())

    if not bowling_df.empty:
        if "extra_type" in bowling_df.columns:
            non_bowler_extras = bowling_df["extra_type"].isin(
                ["byes", "legbyes"]
            )

            bowling_runs -= float(
                bowling_df.loc[
                    non_bowler_extras,
                    "runs_extras",
                ].sum()
            )

    bowling_wickets_df = bowling_df.loc[
        (bowling_df["is_wicket"] == True)  # noqa: E712
        & (
            ~bowling_df["dismissal_type"]
            .fillna("")
            .astype(str)
            .str.casefold()
            .eq("run out")
        )
    ]

    bowling_wickets = len(bowling_wickets_df)

    bowling_overs = bowling_legal_balls / 6
    bowling_economy = (
        bowling_runs / bowling_overs
        if bowling_overs > 0
        else 0.0
    )

    bowling_dot_balls = int(
        (
            (bowling_legal["runs_total"] == 0)
        ).sum()
    )

    bowling_dot_percentage = safe_ratio(
        bowling_dot_balls,
        bowling_legal_balls,
    ) * 100

    bowling_matches = (
        bowling_df["match_id"].nunique()
        if not bowling_df.empty
        else 0
    )

    bowling_phase = {}

    if not bowling_df.empty:
        bowling_df["phase"] = bowling_df["over"].apply(get_phase)

        for phase in ("powerplay", "middle", "death"):
            phase_df = bowling_df[bowling_df["phase"] == phase]

            phase_legal = phase_df.loc[
                phase_df["is_legal"] == True  # noqa: E712
            ]

            phase_balls = len(phase_legal)

            phase_runs = float(phase_df["runs_total"].sum())

            if "extra_type" in phase_df.columns:
                non_bowler_extras = phase_df["extra_type"].isin(
                    ["byes", "legbyes"]
                )

                phase_runs -= float(
                    phase_df.loc[
                        non_bowler_extras,
                        "runs_extras",
                    ].sum()
                )

            phase_overs = phase_balls / 6

            phase_wickets = len(
                phase_df.loc[
                    (phase_df["is_wicket"] == True)  # noqa: E712
                    & (
                        ~phase_df["dismissal_type"]
                        .fillna("")
                        .astype(str)
                        .str.casefold()
                        .eq("run out")
                    )
                ]
            )

            bowling_phase[phase] = {
                "runs": phase_runs,
                "balls": phase_balls,
                "economy": (
                    phase_runs / phase_overs
                    if phase_overs > 0
                    else 0.0
                ),
                "wickets": phase_wickets,
            }

    # ---------------------------------------------------------
    # Strengths
    # ---------------------------------------------------------

    if batting_runs > 0:
        if batting_strike_rate >= 140:
            strengths.append(
                PlayerInsight(
                    category="batting",
                    title="High scoring rate",
                    detail=(
                        f"Historical batting strike rate is "
                        f"{batting_strike_rate:.1f}, indicating strong "
                        "run-scoring tempo."
                    ),
                )
            )

        if boundary_run_percentage >= 50:
            strengths.append(
                PlayerInsight(
                    category="batting",
                    title="Boundary-driven scoring",
                    detail=(
                        f"{boundary_run_percentage:.1f}% of batting runs "
                        "come from boundaries."
                    ),
                )
            )

        if dot_ball_percentage <= 35:
            strengths.append(
                PlayerInsight(
                    category="batting",
                    title="Good strike rotation",
                    detail=(
                        f"Dot-ball percentage is {dot_ball_percentage:.1f}%, "
                        "showing the ability to keep the scoreboard moving."
                    ),
                )
            )

        death_batting = batting_phase.get("death", {})

        if death_batting.get("balls", 0) >= 50 and death_batting.get(
            "strike_rate", 0
        ) >= 145:
            strengths.append(
                PlayerInsight(
                    category="batting",
                    title="Strong death-phase batting",
                    detail=(
                        f"Death-over strike rate is "
                        f"{death_batting['strike_rate']:.1f}."
                    ),
                )
            )

    if bowling_legal_balls > 0:
        if bowling_economy <= 8:
            strengths.append(
                PlayerInsight(
                    category="bowling",
                    title="Economical bowling",
                    detail=(
                        f"Historical bowling economy is "
                        f"{bowling_economy:.2f} runs per over."
                    ),
                )
            )

        if bowling_wickets >= 20:
            strengths.append(
                PlayerInsight(
                    category="bowling",
                    title="Reliable wicket contribution",
                    detail=(
                        f"Historical data contains {bowling_wickets} "
                        "credited wickets."
                    ),
                )
            )

        if bowling_dot_percentage >= 35:
            strengths.append(
                PlayerInsight(
                    category="bowling",
                    title="Creates dot-ball pressure",
                    detail=(
                        f"Dot-ball percentage is "
                        f"{bowling_dot_percentage:.1f}%."
                    ),
                )
            )

        death_bowling = bowling_phase.get("death", {})

        if (
            death_bowling.get("balls", 0) >= 50
            and death_bowling.get("economy", 99) <= 9
        ):
            strengths.append(
                PlayerInsight(
                    category="bowling",
                    title="Effective death bowling",
                    detail=(
                        f"Death-phase economy is "
                        f"{death_bowling['economy']:.2f}."
                    ),
                )
            )

    # ---------------------------------------------------------
    # Weaknesses
    # ---------------------------------------------------------

    if batting_balls > 50:
        if batting_strike_rate < 110:
            weaknesses.append(
                PlayerInsight(
                    category="batting",
                    title="Low scoring tempo",
                    detail=(
                        f"Strike rate of {batting_strike_rate:.1f} "
                        "suggests the player may need to increase scoring "
                        "speed in suitable situations."
                    ),
                )
            )

        if dot_ball_percentage >= 45:
            weaknesses.append(
                PlayerInsight(
                    category="batting",
                    title="High dot-ball percentage",
                    detail=(
                        f"{dot_ball_percentage:.1f}% of legal balls "
                        "have produced no batter runs."
                    ),
                )
            )

        death_batting = batting_phase.get("death", {})

        if (
            death_batting.get("balls", 0) >= 30
            and death_batting.get("strike_rate", 999) < 120
        ):
            weaknesses.append(
                PlayerInsight(
                    category="batting",
                    title="Death-phase scoring limitation",
                    detail=(
                        f"Death-over strike rate is "
                        f"{death_batting['strike_rate']:.1f}."
                    ),
                )
            )

    if bowling_legal_balls > 50:
        if bowling_economy >= 10:
            weaknesses.append(
                PlayerInsight(
                    category="bowling",
                    title="Expensive bowling",
                    detail=(
                        f"Historical bowling economy is "
                        f"{bowling_economy:.2f}."
                    ),
                )
            )

        death_bowling = bowling_phase.get("death", {})

        if (
            death_bowling.get("balls", 0) >= 30
            and death_bowling.get("economy", 0) >= 10
        ):
            weaknesses.append(
                PlayerInsight(
                    category="bowling",
                    title="Death-over vulnerability",
                    detail=(
                        f"Death-phase economy is "
                        f"{death_bowling['economy']:.2f}."
                    ),
                )
            )

    # ---------------------------------------------------------
    # Recommendations
    # ---------------------------------------------------------

    if batting_strike_rate > 0:
        if batting_strike_rate >= 140:
            recommendations.append(
                PlayerInsight(
                    category="strategy",
                    title="Use as a tempo accelerator",
                    detail=(
                        "Consider giving the player situations where "
                        "rapid scoring can change the innings state."
                    ),
                )
            )
        elif batting_strike_rate < 120:
            recommendations.append(
                PlayerInsight(
                    category="strategy",
                    title="Prioritize strike rotation",
                    detail=(
                        "Focus on reducing prolonged dot-ball sequences "
                        "and increasing scoring opportunities."
                    ),
                )
            )

    if bowling_legal_balls > 0:
        if bowling_economy <= 8:
            recommendations.append(
                PlayerInsight(
                    category="strategy",
                    title="Use in control phases",
                    detail=(
                        "The historical economy supports using the bowler "
                        "when run suppression is important."
                    ),
                )
            )
        elif bowling_economy >= 10:
            recommendations.append(
                PlayerInsight(
                    category="strategy",
                    title="Use matchups carefully",
                    detail=(
                        "Consider selecting favorable batting matchups "
                        "before assigning high-leverage overs."
                    ),
                )
            )

    # ---------------------------------------------------------
    # Overall assessment
    # ---------------------------------------------------------

    role = str(player.role or "UNKNOWN").upper()

    if role == "BATSMAN":
        if batting_strike_rate >= 140:
            overall_assessment = (
                "Historically, this player profiles as an aggressive "
                "T20 batter capable of maintaining a high scoring tempo."
            )
        elif batting_strike_rate >= 120:
            overall_assessment = (
                "Historically, this player profiles as a balanced T20 "
                "batter with a useful scoring rate."
            )
        else:
            overall_assessment = (
                "Historically, this player profiles as a lower-tempo "
                "batter whose value depends on building innings stability."
            )

    elif role == "BOWLER":
        if bowling_economy <= 8:
            overall_assessment = (
                "Historically, this player profiles as an economical "
                "bowler capable of creating run pressure."
            )
        else:
            overall_assessment = (
                "Historically, this player provides a bowling option "
                "but may require careful matchup and phase selection."
            )

    elif role == "ALL_ROUNDER":
        if batting_strike_rate >= 125 and bowling_economy <= 9:
            overall_assessment = (
                "Historically, this player provides balanced value across "
                "both batting and bowling phases."
            )
        elif batting_strike_rate >= 125:
            overall_assessment = (
                "Historically, this player contributes more strongly "
                "through batting while retaining bowling value."
            )
        else:
            overall_assessment = (
                "Historically, this player contributes across multiple "
                "phases, with the exact value depending on match context."
            )

    else:
        overall_assessment = (
            "Historical Cricsheet data provides a performance profile "
            "that can be evaluated across batting and bowling phases."
        )

    # ---------------------------------------------------------
    # Evidence summary
    # ---------------------------------------------------------

    evidence_summary = (
        f"Cricsheet evidence covers {batting_matches} matches as batter "
        f"and {bowling_matches} matches as bowler. "
        f"Historical batting: {int(batting_runs)} runs from "
        f"{batting_balls} legal balls at "
        f"{batting_strike_rate:.1f} strike rate. "
        f"Historical bowling: {bowling_wickets} wickets from "
        f"{bowling_legal_balls} legal balls at "
        f"{bowling_economy:.2f} economy."
    )

    # Avoid returning an empty analysis for valid historical players.
    if not strengths:
        strengths.append(
            PlayerInsight(
                category="historical",
                title="Historical profile available",
                detail=(
                    "The player has enough recorded Cricsheet events "
                    "to support further match-context analysis."
                ),
            )
        )

    if not recommendations:
        recommendations.append(
            PlayerInsight(
                category="strategy",
                title="Use match context",
                detail=(
                    "Combine the historical profile with opposition, "
                    "match phase, venue and current match state."
                ),
            )
        )

    return PlayerIntelligenceResponse(
        player_id=player.id,
        player_name=player.name,
        role=role,
        team_name=player.team.name if player.team else None,
        overall_assessment=overall_assessment,
        strengths=strengths,
        weaknesses=weaknesses,
        recommendations=recommendations,
        evidence_summary=evidence_summary,
    )