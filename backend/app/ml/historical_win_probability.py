from pathlib import Path
import joblib
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

MODEL_PATH = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "historical"
    / "win_probability_model.joblib"
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

    def save_model(self) -> None:
        MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, MODEL_PATH)


    def load_model(self) -> bool:
        if not MODEL_PATH.exists():
            return False
        self.model = joblib.load(MODEL_PATH)
        self.is_trained = True
        return True

    def train(self) -> dict:
        df = self.load_dataset()

        df["match_date"] = pd.to_datetime(df["match_date"])
        df = df.sort_values("match_date").reset_index(drop=True)

        X = df[FEATURE_COLUMNS]
        y = df[TARGET_COLUMN]

        unique_dates = df["match_date"].drop_duplicates().sort_values()
        cutoff_index = int(len(unique_dates) * 0.8)
        cutoff_date = unique_dates.iloc[cutoff_index]

        train_mask = df["match_date"] <= cutoff_date
        test_mask = df["match_date"] > cutoff_date

        X_train = X.loc[train_mask]
        X_test = X.loc[test_mask]
        y_train = y.loc[train_mask]
        y_test = y.loc[test_mask]

        self.model.fit(X_train, y_train)
        self.is_trained = True
        self.save_model()

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


    def evaluate(self) -> dict:
        df = self.load_dataset()
        
        df["match_date"] = pd.to_datetime(df["match_date"])
        df = df.sort_values("match_date").reset_index(drop=True)
        
        X = df[FEATURE_COLUMNS]
        y = df[TARGET_COLUMN]
        
        unique_dates = df["match_date"].drop_duplicates().sort_values()
        cutoff_index = int(len(unique_dates) * 0.8)
        cutoff_date = unique_dates.iloc[cutoff_index]
        
        train_mask = df["match_date"] <= cutoff_date
        test_mask = df["match_date"] > cutoff_date
        
        X_train = X.loc[train_mask]
        X_test = X.loc[test_mask]
        y_train = y.loc[train_mask]
        y_test = y.loc[test_mask]
        
        evaluation_model = LogisticRegression(max_iter=1000)
        evaluation_model.fit(X_train, y_train)
        
        predictions = evaluation_model.predict(X_test)
        probabilities = evaluation_model.predict_proba(X_test)[:, 1]
        
        return {
            "rows": len(df),
            "accuracy": accuracy_score(y_test, predictions),
            "brier_score": brier_score_loss(y_test, probabilities),
            "train_start_date": df.loc[train_mask, "match_date"].min().date().isoformat(),
            "train_end_date": df.loc[train_mask, "match_date"].max().date().isoformat(),
            "test_start_date": df.loc[test_mask, "match_date"].min().date().isoformat(),
            "test_end_date": df.loc[test_mask, "match_date"].max().date().isoformat(),
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

if not historical_win_predictor.load_model():
    historical_win_predictor.train()