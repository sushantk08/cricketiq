import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, brier_score_loss
from sklearn.model_selection import train_test_split


class WinProbabilityModel:

    def __init__(self):
        self.model = LogisticRegression(max_iter=1000)
        self.is_trained = False
        self._train_default_model()

    def _train_default_model(self):
        """Generate representative T20 chase scenarios and train a calibrated Logistic Regression model."""
        rng = np.random.RandomState(42)
        n_samples = 4000

        # Synthesize realistic chase situations
        balls_remaining = rng.randint(1, 121, size=n_samples)
        wickets_lost = rng.randint(0, 10, size=n_samples)
        wickets_in_hand = 10 - wickets_lost

        # Runs required depends on balls remaining (averaging 6 to 12 RRR)
        target_avg = (balls_remaining / 6.0) * rng.uniform(
            6.0, 10.5, size=n_samples
        )
        runs_required = np.clip(
            target_avg + rng.normal(0, 15, size=n_samples), 1, 250
        ).astype(int)

        # Required Run Rate
        rrr = np.where(
            balls_remaining > 0, (runs_required / balls_remaining) * 6.0, 36.0
        )

        # Feature matrix: [runs_required, balls_remaining, wickets_in_hand, required_run_rate]
        X = np.column_stack(
            [runs_required, balls_remaining, wickets_in_hand, rrr]
        )

        # True cricket formula for win probability label:
        # Higher wickets in hand & lower RRR -> high win chance
        logit = (
            (wickets_in_hand * 0.55)
            - (rrr * 0.42)
            + (balls_remaining * 0.015)
            - (runs_required * 0.01)
        )
        prob = 1.0 / (1.0 + np.exp(-logit))
        y = (rng.uniform(0, 1, size=n_samples) < prob).astype(int)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        self.model.fit(X_train, y_train)
        self.is_trained = True

        # Evaluate baseline
        preds = self.model.predict(X_test)
        probs = self.model.predict_proba(X_test)[:, 1]
        acc = accuracy_score(y_test, preds)
        brier = brier_score_loss(y_test, probs)
        print(
            f"[CricketIQ ML] Win Probability Model trained. Accuracy:"
            f" {acc:.2%}, Brier Score: {brier:.4f}"
        )

    def predict(
        self, runs_required: int, balls_remaining: int, wickets_in_hand: int
    ) -> float:
        """Return win probability (0.0 to 1.0) for the chasing team."""
        if wickets_in_hand <= 0:
            return 0.0
        if runs_required <= 0:
            return 1.0
        if balls_remaining <= 0:
            return 0.0 if runs_required > 0 else 1.0

        rrr = (runs_required / balls_remaining) * 6.0
        features = np.array(
            [[runs_required, balls_remaining, wickets_in_hand, rrr]]
        )
        prob = self.model.predict_proba(features)[0][1]
        return float(np.clip(prob, 0.01, 0.99))


# Global singleton instance for API usage
win_predictor = WinProbabilityModel()