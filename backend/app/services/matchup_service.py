from functools import lru_cache
from pathlib import Path

import pandas as pd
from sqlalchemy.orm import Session

from backend.app.models.cricket import Player
from backend.app.schemas.matchup import (
    MatchupInsight,
    MatchupResponse,
)


DATASET_PATH = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "historical"
    / "player_delivery_history.csv"
)


def normalize_player_name(name: str) -> str:
    
    return (
        str(name)
        .lower()
        .replace(".", "")
        .replace("-", " ")
        .replace("_", " ")
        .strip()
    )


def player_name_matches(
    dataset_name: str,
    database_name: str,
) -> bool:
    
    dataset = normalize_player_name(dataset_name)
    database = normalize_player_name(database_name)

    if not dataset or not database:
        return False

    if dataset == database:
        return True

    dataset_parts = dataset.split()
    database_parts = database.split()

    if not dataset_parts or not database_parts:
        return False

    if dataset_parts[-1] != database_parts[-1]:
        return False

    return dataset_parts[0][0] == database_parts[0][0]


@lru_cache(maxsize=64)
def load_matchup_data(
    batter_name: str,
    bowler_name: str,
) -> pd.DataFrame:
    
    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Historical player dataset not found: {DATASET_PATH}"
        )

    required_columns = [
        "match_id",
        "match_date",
        "innings_number",
        "batting_team",
        "batter",
        "bowler",
        "over",
        "ball",
        "runs_batter",
        "runs_extras",
        "runs_total",
        "extra_type",
        "is_legal",
        "is_wicket",
        "player_dismissed",
        "dismissal_type",
        "winner",
        "teams",
    ]

    matching_chunks = []

    for chunk in pd.read_csv(
        DATASET_PATH,
        usecols=required_columns,
        chunksize=50_000,
    ):
        chunk["batter"] = chunk["batter"].fillna("").astype(str)
        chunk["bowler"] = chunk["bowler"].fillna("").astype(str)

        batter_match = chunk["batter"].apply(
            lambda name: player_name_matches(
                name,
                batter_name,
            )
        )

        bowler_match = chunk["bowler"].apply(
            lambda name: player_name_matches(
                name,
                bowler_name,
            )
        )

        matched = chunk[batter_match & bowler_match]

        if not matched.empty:
            matching_chunks.append(matched)

    if not matching_chunks:
        return pd.DataFrame(columns=required_columns)

    return pd.concat(
        matching_chunks,
        ignore_index=True,
    )


def _safe_ratio(
    numerator: float,
    denominator: float,
) -> float:
    if denominator == 0:
        return 0.0

    return numerator / denominator


def _phase(over: int) -> str:
    if over < 6:
        return "powerplay"

    if over < 15:
        return "middle"

    return "death"


def generate_matchup_intelligence(
    db: Session,
    batter_id: int,
    bowler_id: int,
) -> MatchupResponse | None:
    """Generate historical batter-vs-bowler intelligence."""
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

    df = load_matchup_data(
        batter.name,
        bowler.name,
    ).copy()

    # ---------------------------------------------------------
    # Basic matchup statistics
    # ---------------------------------------------------------

    if df.empty:
        return MatchupResponse(
            batter_id=batter.id,
            batter_name=batter.name,
            bowler_id=bowler.id,
            bowler_name=bowler.name,
            matches=0,
            balls=0,
            runs=0,
            strike_rate=0.0,
            dot_ball_percentage=0.0,
            fours=0,
            sixes=0,
            dismissals=0,
            phase_stats={
                "powerplay": {
                    "balls": 0,
                    "runs": 0,
                    "strike_rate": 0.0,
                    "dot_ball_percentage": 0.0,
                },
                "middle": {
                    "balls": 0,
                    "runs": 0,
                    "strike_rate": 0.0,
                    "dot_ball_percentage": 0.0,
                },
                "death": {
                    "balls": 0,
                    "runs": 0,
                    "strike_rate": 0.0,
                    "dot_ball_percentage": 0.0,
                },
            },
            assessment=(
                "No historical Cricsheet deliveries were found for "
                "this batter-bowler combination."
            ),
            insights=[
                MatchupInsight(
                    category="data",
                    title="Insufficient matchup evidence",
                    detail=(
                        "There are not enough recorded head-to-head "
                        "deliveries to make a meaningful historical "
                        "matchup assessment."
                    ),
                )
            ],
        )

    df["over"] = pd.to_numeric(
        df["over"],
        errors="coerce",
    ).fillna(0)

    df["runs_batter"] = pd.to_numeric(
        df["runs_batter"],
        errors="coerce",
    ).fillna(0)

    legal = df.loc[
        df["is_legal"] == True  # noqa: E712
    ].copy()

    balls = len(legal)
    runs = int(legal["runs_batter"].sum())

    strike_rate = round(
        _safe_ratio(runs, balls) * 100,
        2,
    )

    dot_balls = int(
        (
            legal["runs_batter"] == 0
        ).sum()
    )

    dot_ball_percentage = round(
        _safe_ratio(dot_balls, balls) * 100,
        2,
    )

    fours = int(
        (legal["runs_batter"] == 4).sum()
    )

    sixes = int(
        (legal["runs_batter"] == 6).sum()
    )

    dismissals = int(
        (
            (df["is_wicket"] == True)  # noqa: E712
            & (
                df["player_dismissed"]
                .fillna("")
                .astype(str)
                .apply(
                    lambda name: player_name_matches(
                        name,
                        batter.name,
                    )
                )
            )
            & (
                ~df["dismissal_type"]
                .fillna("")
                .astype(str)
                .str.casefold()
                .eq("run out")
            )
        ).sum()
    )

    matches = int(
        df["match_id"].nunique()
    )

    # ---------------------------------------------------------
    # Phase statistics
    # ---------------------------------------------------------

    df["phase"] = df["over"].apply(_phase)

    phase_stats = {}

    for phase_name in (
        "powerplay",
        "middle",
        "death",
    ):
        phase_df = df[
            (df["phase"] == phase_name)
            & (
                df["is_legal"] == True  # noqa: E712
            )
        ]

        phase_balls = len(phase_df)
        phase_runs = int(
            phase_df["runs_batter"].sum()
        )

        phase_dots = int(
            (
                phase_df["runs_batter"] == 0
            ).sum()
        )

        phase_stats[phase_name] = {
            "balls": phase_balls,
            "runs": phase_runs,
            "strike_rate": round(
                _safe_ratio(
                    phase_runs,
                    phase_balls,
                )
                * 100,
                2,
            ),
            "dot_ball_percentage": round(
                _safe_ratio(
                    phase_dots,
                    phase_balls,
                )
                * 100,
                2,
            ),
        }

    # ---------------------------------------------------------
    # Matchup insights
    # ---------------------------------------------------------

    insights: list[MatchupInsight] = []

    if strike_rate >= 140:
        insights.append(
            MatchupInsight(
                category="batting",
                title="Batter scores quickly",
                detail=(
                    f"{batter.name} has scored at a {strike_rate:.1f} "
                    f"strike rate against {bowler.name}."
                ),
            )
        )
    elif strike_rate < 100:
        insights.append(
            MatchupInsight(
                category="bowling",
                title="Bowler suppresses scoring",
                detail=(
                    f"{batter.name} has a strike rate of "
                    f"{strike_rate:.1f} against {bowler.name}, "
                    "indicating strong historical scoring control."
                ),
            )
        )

    if dismissals >= 2:
        insights.append(
            MatchupInsight(
                category="bowling",
                title="Repeated dismissals",
                detail=(
                    f"{bowler.name} has dismissed {batter.name} "
                    f"{dismissals} times in the recorded matchup."
                ),
            )
        )

    if dot_ball_percentage >= 45:
        insights.append(
            MatchupInsight(
                category="bowling",
                title="High dot-ball pressure",
                detail=(
                    f"{bowler.name} has kept {dot_ball_percentage:.1f}% "
                    "of legal matchup deliveries to zero batter runs."
                ),
            )
        )

    if fours + sixes >= 8:
        insights.append(
            MatchupInsight(
                category="batting",
                title="Boundary threat exists",
                detail=(
                    f"The matchup has produced {fours} fours and "
                    f"{sixes} sixes from the batter."
                ),
            )
        )

    death_stats = phase_stats["death"]

    if (
        death_stats["balls"] >= 20
        and death_stats["strike_rate"] >= 140
    ):
        insights.append(
            MatchupInsight(
                category="phase",
                title="Strong death-phase matchup",
                detail=(
                    f"The batter has a {death_stats['strike_rate']:.1f} "
                    "strike rate against this bowler in the death phase."
                ),
            )
        )

    # ---------------------------------------------------------
    # Overall assessment
    # ---------------------------------------------------------

    if dismissals >= 2 and strike_rate < 120:
        assessment = (
            f"{bowler.name} has historically held an advantage over "
            f"{batter.name}, combining wicket-taking success with "
            f"scoring suppression."
        )

    elif strike_rate >= 140 and dismissals == 0:
        assessment = (
            f"{batter.name} has historically enjoyed this matchup, "
            f"scoring at {strike_rate:.1f} without a recorded dismissal."
        )

    elif strike_rate >= 125:
        assessment = (
            f"The matchup leans toward {batter.name} historically, "
            f"although the available evidence is context-dependent."
        )

    elif strike_rate < 100:
        assessment = (
            f"The historical evidence favors {bowler.name}, with "
            f"{batter.name} scoring at only {strike_rate:.1f}."
        )

    else:
        assessment = (
            "The historical matchup appears relatively balanced, "
            "so phase and match context should influence the decision."
        )

    if not insights:
        insights.append(
            MatchupInsight(
                category="context",
                title="Context matters",
                detail=(
                    "The recorded matchup does not show a dominant "
                    "historical signal, so current match conditions "
                    "should be considered."
                ),
            )
        )

    return MatchupResponse(
        batter_id=batter.id,
        batter_name=batter.name,
        bowler_id=bowler.id,
        bowler_name=bowler.name,
        matches=matches,
        balls=balls,
        runs=runs,
        strike_rate=strike_rate,
        dot_ball_percentage=dot_ball_percentage,
        fours=fours,
        sixes=sixes,
        dismissals=dismissals,
        phase_stats=phase_stats,
        assessment=assessment,
        insights=insights,
    )