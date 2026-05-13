from pathlib import Path

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, brier_score_loss
from sklearn.model_selection import GroupShuffleSplit


DATASET_PATH = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "historical"
    / "win_probability.csv"
)

FEATURE_COLUMNS = [
    "runs_required_after",
    "balls_remaining_after",
    "wickets_in_hand_after",
    "required_run_rate_after",
]

TARGET_COLUMN = "chasing_team_won"


class HistoricalWinProbabilityModel:
    """Win-probability model trained on historical CricketIQ data."""

    def __init__(self):
        self.model = LogisticRegression(max_iter=1000)
        self.is_trained = False

    def load_dataset(self) -> pd.DataFrame:
        if not DATASET_PATH.exists():
            raise FileNotFoundError(
                f"Historical dataset not found: {DATASET_PATH}"
            )

        df = pd.read_csv(DATASET_PATH)

        required_columns = FEATURE_COLUMNS + [TARGET_COLUMN]

        missing_columns = [
            column for column in required_columns if column not in df.columns
        ]

        if missing_columns:
            raise ValueError(
                f"Dataset is missing columns: {missing_columns}"
            )

        return df

    def train(self) -> dict:
        df = self.load_dataset()

        X = df[FEATURE_COLUMNS]
        y = df[TARGET_COLUMN]

        groups = df["match_id"]

        splitter = GroupShuffleSplit(
            n_splits=1,
            test_size=0.2,
            random_state=42,
        )

        train_indices, test_indices = next(
               splitter.split(X, y, groups=groups)
        )

        X_train = X.iloc[train_indices]
        X_test = X.iloc[test_indices]
        y_train = y.iloc[train_indices]
        y_test = y.iloc[test_indices]

        self.model.fit(X_train, y_train)
        self.is_trained = True

        predictions = self.model.predict(X_test)
        probabilities = self.model.predict_proba(X_test)[:, 1]

        return {
            "rows": len(df),
            "accuracy": accuracy_score(y_test, predictions),
            "brier_score": brier_score_loss(
                y_test,
                probabilities,
            ),
        }

    def predict(
        self,
        runs_required: int,
        balls_remaining: int,
        wickets_in_hand: int,
    ) -> float:
        """Return historical win probability as a percentage."""
        if not self.is_trained:
            raise RuntimeError("Model must be trained before prediction.")

        rrr = (
            (runs_required / balls_remaining) * 6
            if balls_remaining > 0
            else 0.0
        )

        features = pd.DataFrame(
            [
                {
                    "runs_required_after": runs_required,
                    "balls_remaining_after": balls_remaining,
                    "wickets_in_hand_after": wickets_in_hand,
                    "required_run_rate_after": rrr,
                }
            ],
            columns=FEATURE_COLUMNS,
        )

        probability = self.model.predict_proba(features)[0][1]

        return float(probability * 100)

historical_win_predictor = HistoricalWinProbabilityModel()
historical_win_predictor.train()