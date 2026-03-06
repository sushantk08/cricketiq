import random
from sqlalchemy import text
from backend.app.database.session import SessionLocal
from backend.app.models.cricket import (
    Delivery,
    Innings,
    Match,
    Player,
    Team,
    Venue,
)


def seed_cricket_data():
    db = SessionLocal()
    try:
        print("Resetting database and re-seeding with ID sequences at 1...")
        db.execute(
            text(
                "TRUNCATE TABLE deliveries, innings, matches, players, teams,"
                " venues RESTART IDENTITY CASCADE;"
            )
        )
        db.commit()

        # 1. Create Teams
        ind = Team(name="India", short_name="IND")
        aus = Team(name="Australia", short_name="AUS")
        db.add_all([ind, aus])
        db.commit()
        db.refresh(ind)
        db.refresh(aus)

        # 2. Create Players
        ind_players = [
            Player(
                name="Rohit Sharma",
                role="BATTER",
                batting_style="Right-hand bat",
                bowling_style="Right-arm offbreak",
                team_id=ind.id,
            ),
            Player(
                name="Virat Kohli",
                role="BATTER",
                batting_style="Right-hand bat",
                bowling_style="Right-arm medium",
                team_id=ind.id,
            ),
            Player(
                name="Suryakumar Yadav",
                role="BATTER",
                batting_style="Right-hand bat",
                bowling_style="Right-arm offbreak",
                team_id=ind.id,
            ),
            Player(
                name="Rishabh Pant",
                role="WICKETKEEPER",
                batting_style="Left-hand bat",
                team_id=ind.id,
            ),
            Player(
                name="Hardik Pandya",
                role="ALL_ROUNDER",
                batting_style="Right-hand bat",
                bowling_style="Right-arm fast-medium",
                team_id=ind.id,
            ),
            Player(
                name="Ravindra Jadeja",
                role="ALL_ROUNDER",
                batting_style="Left-hand bat",
                bowling_style="Slow left-arm orthodox",
                team_id=ind.id,
            ),
            Player(
                name="Axar Patel",
                role="ALL_ROUNDER",
                batting_style="Left-hand bat",
                bowling_style="Slow left-arm orthodox",
                team_id=ind.id,
            ),
            Player(
                name="Kuldeep Yadav",
                role="BOWLER",
                batting_style="Left-hand bat",
                bowling_style="Left-arm wrist-spin",
                team_id=ind.id,
            ),
            Player(
                name="Jasprit Bumrah",
                role="BOWLER",
                batting_style="Right-hand bat",
                bowling_style="Right-arm fast",
                team_id=ind.id,
            ),
            Player(
                name="Arshdeep Singh",
                role="BOWLER",
                batting_style="Left-hand bat",
                bowling_style="Left-arm fast-medium",
                team_id=ind.id,
            ),
            Player(
                name="Mohammed Siraj",
                role="BOWLER",
                batting_style="Right-hand bat",
                bowling_style="Right-arm fast",
                team_id=ind.id,
            ),
        ]

        aus_players = [
            Player(
                name="Travis Head",
                role="BATTER",
                batting_style="Left-hand bat",
                bowling_style="Right-arm offbreak",
                team_id=aus.id,
            ),
            Player(
                name="David Warner",
                role="BATTER",
                batting_style="Left-hand bat",
                bowling_style="Right-arm legbreak",
                team_id=aus.id,
            ),
            Player(
                name="Mitchell Marsh",
                role="ALL_ROUNDER",
                batting_style="Right-hand bat",
                bowling_style="Right-arm medium",
                team_id=aus.id,
            ),
            Player(
                name="Glenn Maxwell",
                role="ALL_ROUNDER",
                batting_style="Right-hand bat",
                bowling_style="Right-arm offbreak",
                team_id=aus.id,
            ),
            Player(
                name="Marcus Stoinis",
                role="ALL_ROUNDER",
                batting_style="Right-hand bat",
                bowling_style="Right-arm medium",
                team_id=aus.id,
            ),
            Player(
                name="Tim David",
                role="BATTER",
                batting_style="Right-hand bat",
                bowling_style="Right-arm offbreak",
                team_id=aus.id,
            ),
            Player(
                name="Matthew Wade",
                role="WICKETKEEPER",
                batting_style="Left-hand bat",
                team_id=aus.id,
            ),
            Player(
                name="Pat Cummins",
                role="BOWLER",
                batting_style="Right-hand bat",
                bowling_style="Right-arm fast",
                team_id=aus.id,
            ),
            Player(
                name="Mitchell Starc",
                role="BOWLER",
                batting_style="Left-hand bat",
                bowling_style="Left-arm fast",
                team_id=aus.id,
            ),
            Player(
                name="Adam Zampa",
                role="BOWLER",
                batting_style="Right-hand bat",
                bowling_style="Right-arm legbreak",
                team_id=aus.id,
            ),
            Player(
                name="Josh Hazlewood",
                role="BOWLER",
                batting_style="Left-hand bat",
                bowling_style="Right-arm fast-medium",
                team_id=aus.id,
            ),
        ]

        db.add_all(ind_players + aus_players)
        db.commit()

        # 3. Create Venue
        venue = Venue(name="Wankhede Stadium", city="Mumbai", country="India")
        db.add(venue)
        db.commit()
        db.refresh(venue)

        # 4. Create Match
        match = Match(
            title="India vs Australia - T20 Super Series",
            match_type="T20",
            status="COMPLETED",
            team1_id=ind.id,
            team2_id=aus.id,
            venue_id=venue.id,
            toss_winner_id=ind.id,
            toss_decision="bat",
            winner_id=ind.id,
        )
        db.add(match)
        db.commit()
        db.refresh(match)

        # 5. Innings and Delivery Generator
        def generate_innings(
            innings_no,
            batting_team_id,
            bowling_team_id,
            batting_squad,
            bowling_squad,
            target_runs=None,
        ):
            innings = Innings(
                match_id=match.id,
                innings_number=innings_no,
                batting_team_id=batting_team_id,
                bowling_team_id=bowling_team_id,
                total_runs=0,
                total_wickets=0,
                total_overs=20.0,
            )
            db.add(innings)
            db.commit()
            db.refresh(innings)

            bowlers = [
                p for p in bowling_squad if p.role in ["BOWLER", "ALL_ROUNDER"]
            ]
            striker_idx = 0
            non_striker_idx = 1
            next_batter_idx = 2

            curr_runs = 0
            curr_wickets = 0
            deliveries = []

            rng = random.Random(100 + innings_no)

            for over in range(20):
                bowler = bowlers[over % len(bowlers)]
                for ball in range(1, 7):
                    if (
                        target_runs
                        and curr_runs > target_runs
                        or curr_wickets >= 10
                    ):
                        break

                    rand_val = rng.random()
                    is_wicket = False
                    dismissal = None
                    runs = 0
                    current_striker = batting_squad[striker_idx]
                    player_out_id = None

                    if rand_val < 0.045 and curr_wickets < 10:
                        is_wicket = True
                        dismissal = rng.choice(["caught", "bowled", "lbw"])
                        player_out_id = current_striker.id
                        curr_wickets += 1
                    elif rand_val < 0.38:
                        runs = 0  # Dot ball
                    elif rand_val < 0.70:
                        runs = 1  # Single
                    elif rand_val < 0.83:
                        runs = 2  # Two runs
                    elif rand_val < 0.94:
                        runs = 4  # Four
                    else:
                        runs = 6  # Six

                    curr_runs += runs

                    deliv = Delivery(
                        match_id=match.id,
                        innings_id=innings.id,
                        over_number=over,
                        ball_number=ball,
                        batter_id=current_striker.id,
                        bowler_id=bowler.id,
                        non_striker_id=batting_squad[non_striker_idx].id,
                        runs_batter=runs,
                        runs_extras=0,
                        is_wicket=is_wicket,
                        dismissal_type=dismissal,
                        player_dismissed_id=player_out_id,
                        cumulative_runs=curr_runs,
                        cumulative_wickets=curr_wickets,
                    )
                    deliveries.append(deliv)

                    # Update striker AFTER delivery has been created
                    if is_wicket:
                        if next_batter_idx < len(batting_squad):
                            striker_idx = next_batter_idx
                            next_batter_idx += 1
                    else:
                        if runs in [1, 3]:
                            striker_idx, non_striker_idx = (
                                non_striker_idx,
                                striker_idx,
                            )

                # End of over strike rotation
                striker_idx, non_striker_idx = non_striker_idx, striker_idx

            db.add_all(deliveries)
            innings.total_runs = curr_runs
            innings.total_wickets = curr_wickets
            db.commit()
            return curr_runs

        # Generate both innings
        ind_score = generate_innings(
            1, ind.id, aus.id, ind_players, aus_players
        )
        generate_innings(
            2,
            aus.id,
            ind.id,
            aus_players,
            ind_players,
            target_runs=ind_score,
        )

        print("Seeded successfully with ID sequences reset to 1!")
    finally:
        db.close()


if __name__ == "__main__":
    seed_cricket_data()