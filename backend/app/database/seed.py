import random
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
        # Check if already seeded to prevent duplicates
        if db.query(Match).first():
            print("Database already contains match data. Skipping seeding.")
            return

        print("Seeding sample cricket data...")

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
        venue = Venue(
            name="Wankhede Stadium", city="Mumbai", country="India"
        )
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

        # 5. Helper function to generate 20 overs of ball-by-ball deliveries
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
                p
                for p in bowling_squad
                if p.role in ["BOWLER", "ALL_ROUNDER"]
            ]
            striker_idx = 0
            non_striker_idx = 1
            next_batter_idx = 2

            curr_runs = 0
            curr_wickets = 0
            deliveries = []

            # Seed random generator for predictable realistic stats
            rng = random.Random(42 + innings_no)

            for over in range(20):
                bowler = bowlers[over % len(bowlers)]
                for ball in range(1, 7):
                    if (
                        target_runs
                        and curr_runs > target_runs
                        or curr_wickets >= 10
                    ):
                        break

                    # Simulate delivery event
                    rand_val = rng.random()
                    is_wicket = False
                    dismissal = None
                    runs = 0
                    player_out_id = None

                    if rand_val < 0.05 and curr_wickets < 10:
                        # Wicket
                        is_wicket = True
                        dismissal = rng.choice(["caught", "bowled", "lbw"])
                        player_out_id = batting_squad[striker_idx].id
                        curr_wickets += 1
                        if next_batter_idx < len(batting_squad):
                            striker_idx = next_batter_idx
                            next_batter_idx += 1
                    elif rand_val < 0.40:
                        runs = 0  # Dot ball
                    elif rand_val < 0.72:
                        runs = 1  # Single
                    elif rand_val < 0.85:
                        runs = 2  # Two
                    elif rand_val < 0.95:
                        runs = 4  # Boundary
                    else:
                        runs = 6  # Six

                    curr_runs += runs

                    deliv = Delivery(
                        match_id=match.id,
                        innings_id=innings.id,
                        over_number=over,
                        ball_number=ball,
                        batter_id=batting_squad[striker_idx].id,
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

                    # Rotate strike on odd runs
                    if runs in [1, 3]:
                        striker_idx, non_striker_idx = (
                            non_striker_idx,
                            striker_idx,
                        )

                # End of over: rotate strike
                striker_idx, non_striker_idx = non_striker_idx, striker_idx

            db.add_all(deliveries)
            innings.total_runs = curr_runs
            innings.total_wickets = curr_wickets
            db.commit()
            return curr_runs

        # Innings 1: India batting, Australia bowling
        ind_score = generate_innings(
            1, ind.id, aus.id, ind_players, aus_players
        )
        # Innings 2: Australia chasing India's target
        generate_innings(
            2,
            aus.id,
            ind.id,
            aus_players,
            ind_players,
            target_runs=ind_score,
        )

        print("Sample cricket data seeded successfully!")
    finally:
        db.close()


if __name__ == "__main__":
    seed_cricket_data()