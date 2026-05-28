import zipfile
from pathlib import Path
import csv

import yaml


DOWNLOADS_DIR = Path.home() / "Downloads"
T20_ZIP_PATH = DOWNLOADS_DIR / "t20s.zip"


def get_match_files() -> list[str]:
    """Return all Cricsheet T20 match YAML files from the downloaded archive."""
    if not T20_ZIP_PATH.exists():
        raise FileNotFoundError(
            f"Cricsheet archive not found: {T20_ZIP_PATH}"
        )

    with zipfile.ZipFile(T20_ZIP_PATH, "r") as archive:
        return [
            name
            for name in archive.namelist()
            if name.endswith(".yaml") and not name.endswith("_info.yaml")
        ]


def load_match(match_file: str) -> dict:
    """Load one Cricsheet match YAML file from the T20 archive."""
    with zipfile.ZipFile(T20_ZIP_PATH, "r") as archive:
        raw_data = archive.read(match_file)

    data = yaml.safe_load(raw_data)

    if not isinstance(data, dict):
        raise ValueError(f"Invalid Cricsheet match data: {match_file}")

    return data


def extract_match_metadata(match_file: str) -> dict:
    """Extract basic metadata needed for the CricketIQ ML dataset."""
    data = load_match(match_file)
    info = data.get("info", {})

    teams = info.get("teams", [])
    outcome = info.get("outcome", {})

    return {
        "external_id": Path(match_file).stem,
        "match_date": info.get("dates", [None])[0],
        "match_type": info.get("match_type"),
        "teams": teams,
        "winner": outcome.get("winner"),
        "gender": info.get("gender"),
        "team_type": info.get("team_type"),
    }


def get_sample_metadata(limit: int = 10) -> list[dict]:
    """Return metadata for a small number of Cricsheet matches."""
    files = get_match_files()[:limit]
    return [extract_match_metadata(match_file) for match_file in files]


def is_male_international_t20(match_file: str) -> bool:
    """Check whether a Cricsheet match is a male international T20."""
    metadata = extract_match_metadata(match_file)

    return (
        metadata["match_type"] == "T20"
        and metadata["gender"] == "male"
        and metadata["team_type"] == "international"
        and len(metadata["teams"]) == 2
        and bool(metadata["winner"])
    )


def extract_second_innings_deliveries(match_file: str) -> list[dict]:
    """Extract second-innings delivery data for win-probability training."""
    data = load_match(match_file)

    if not is_male_international_t20(match_file):
        return []

    innings = data.get("innings", [])

    if len(innings) < 2:
        return []

    second_innings = innings[1]
    innings_key = next(iter(second_innings))
    innings_data = second_innings[innings_key]

    batting_team = innings_data.get("team")

    first_innings = innings[0]
    first_innings_key = next(iter(first_innings))
    first_innings_data = first_innings[first_innings_key]

    target_runs = sum(
        delivery_block[next(iter(delivery_block))]
        .get("runs", {})
        .get("total", 0)
        for delivery_block in first_innings_data.get("deliveries", [])
    )
    target_runs += 1
    match_date = extract_match_metadata(match_file)["match_date"]
    deliveries = []
    total_runs = 0
    wickets_lost = 0

    for delivery_block in innings_data.get("deliveries", []):
        delivery_key = next(iter(delivery_block))
        delivery = delivery_block[delivery_key]

        runs = delivery.get("runs", {})
        wicket_data = delivery.get("wicket")

        total_runs += runs.get("total", 0)

        if wicket_data:
            wickets_lost += 1

        is_wicket = bool(wicket_data)

        delivery_number = float(delivery_key)

        over_number = int(delivery_number)
        ball_number = int(round((delivery_number % 1) * 10))

        balls_bowled_after = (
            over_number * 6 + ball_number
        )

        balls_remaining_after = max(
            0,
            120 - balls_bowled_after,
        )

        runs_required_after = max(
            0,
            target_runs - total_runs,
        )

        wickets_in_hand_after = max(
            0,
            10 - wickets_lost,
        )

        required_run_rate_after = (
            round(
                runs_required_after
                / (balls_remaining_after / 6),
                2,
            )
            if balls_remaining_after > 0
            else 0.0
        )

        deliveries.append(
            {
                "match_id": Path(match_file).stem,
                "match_date": match_date,
                "batting_team": batting_team,
                "delivery": delivery_key,
                "over": over_number,
                "ball": ball_number,
                "batter": delivery.get("batsman"),
                "bowler": delivery.get("bowler"),
                "runs_batter": runs.get("batsman", 0),
                "runs_extras": runs.get("extras", 0),
                "runs_total": runs.get("total", 0),
                "runs_required_before": max(
                    0,
                    target_runs
                    - total_runs
                    + runs.get("total", 0),
                ),
                "runs_required_after": runs_required_after,
                "balls_remaining_after": balls_remaining_after,
                "wickets_in_hand_after": wickets_in_hand_after,
                "required_run_rate_after": required_run_rate_after,
                "is_wicket": is_wicket,
            }
        )

    return deliveries

def build_training_rows(limit: int = 100) -> list[dict]:
    """Build win-probability training rows from a limited set of matches."""
    training_rows = []

    for match_file in get_match_files()[:limit]:
        rows = extract_second_innings_deliveries(match_file)

        if not rows:
            continue

        data = load_match(match_file)
        winner = data.get("info", {}).get("outcome", {}).get("winner")

        for row in rows:
            row["winner"] = winner
            row["chasing_team_won"] = int(
                winner == row["batting_team"]
            )

        training_rows.extend(rows)

    return training_rows


def write_training_dataset(output_path: Path, limit: int | None = None) -> int:
    """Write historical win-probability rows to a CSV file."""
    files = get_match_files()

    if limit is not None:
        files = files[:limit]

    columns = [
        "match_id",
        "match_date",
        "batting_team",
        "delivery",
        "over",
        "ball",
        "batter",
        "bowler",
        "runs_batter",
        "runs_extras",
        "runs_total",
        "runs_required_before",
        "runs_required_after",
        "balls_remaining_after",
        "wickets_in_hand_after",
        "required_run_rate_after",
        "is_wicket",
        "winner",
        "chasing_team_won",
    ]

    row_count = 0

    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=columns)
        writer.writeheader()

        for match_file in files:
            rows = extract_second_innings_deliveries(match_file)

            if not rows:
                continue

            data = load_match(match_file)
            winner = data.get("info", {}).get("outcome", {}).get("winner")

            if not winner:
                continue

            for row in rows:
                row["winner"] = winner
                row["chasing_team_won"] = int(
                    winner == row["batting_team"]
                )

                writer.writerow(row)
                row_count += 1

    return row_count

def build_player_historical_rows(limit: int | None = None) -> list[dict]:
    """
    Build player-level historical delivery rows from the full
    Cricsheet men's international T20 dataset.

    Each row represents one delivery and contains both batter
    and bowler information so downstream analytics can aggregate
    player performance without relying on the small PostgreSQL seed.
    """
    files = get_match_files()

    if limit is not None:
        files = files[:limit]

    rows = []

    for match_file in files:
        if not is_male_international_t20(match_file):
            continue

        data = load_match(match_file)
        info = data.get("info", {})

        match_date = info.get("dates", [None])[0]
        teams = info.get("teams", [])
        winner = info.get("outcome", {}).get("winner")

        for innings_number, innings_block in enumerate(
            data.get("innings", []),
            start=1,
        ):
            innings_key = next(iter(innings_block))
            innings_data = innings_block[innings_key]

            batting_team = innings_data.get("team")

            for delivery_block in innings_data.get("deliveries", []):
                delivery_key = next(iter(delivery_block))
                delivery = delivery_block[delivery_key]

                runs = delivery.get("runs", {})
                extras = delivery.get("extras", {})
                over_number = int(float(delivery_key))
                ball_number = int(
                     round((float(delivery_key) % 1) * 10)
                )


                wicket_data = delivery.get("wicket")

                if isinstance(wicket_data, list):
                     wickets = wicket_data
                elif isinstance(wicket_data, dict):
                     wickets = [wicket_data]
                else:
                     wickets = delivery.get("wickets", [])

                player_dismissed = None
                dismissal_type = None

                if wickets:
                    wicket = wickets[0]

                    if isinstance(wicket, dict):
                        player_dismissed = (
                             wicket.get("player_out")
                             or wicket.get("player_dismissed")
                        )
                        dismissal_type = (
                            wicket.get("kind")
                            or wicket.get("dismissal_type")
                        )

                rows.append(
                    {
                        "match_id": Path(match_file).stem,
                        "match_date": match_date,
                        "innings_number": innings_number,
                        "batting_team": batting_team,
                        "batter": delivery.get("batter") or delivery.get("batsman"),
                        "bowler": delivery.get("bowler"),
                        "over": over_number,
                        "ball": ball_number,
                        "runs_batter": runs.get("batter", 0),
                        "runs_extras": runs.get("extras", 0),
                        "runs_total": runs.get("total", 0),
                        "extra_type": (
                            next(iter(extras))
                            if extras
                            else None
                        ),
                        "is_legal": not any(
                            extra_type in extras
                            for extra_type in [
                                "wides",
                                "noballs",
                            ]
                        ),
                        "is_wicket": bool(wickets),
                        "player_dismissed": player_dismissed,
                        "dismissal_type": dismissal_type,
                        "winner": winner,
                        "teams": "|".join(teams),
                    }
                )

    return rows

def write_player_historical_dataset(
    output_path: Path,
    limit: int | None = None,
) -> int:
    """Write Cricsheet player-level historical delivery data to CSV."""
    rows = build_player_historical_rows(limit=limit)

    columns = [
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

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=columns,
        )

        writer.writeheader()

        for row in rows:
            writer.writerow(row)

    return len(rows)