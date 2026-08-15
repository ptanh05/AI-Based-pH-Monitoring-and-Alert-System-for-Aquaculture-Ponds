"""
Forecasting Engine for AI Aquaculture Guardian.

Multi-step pH forecasting using Random Forest with recursive prediction.
Includes a persistence baseline for honest model comparison.
"""

import numpy as np
import pickle
import os
from typing import List, Tuple, Optional, Dict
from datetime import datetime
from collections import deque

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from ai.features import FeatureEngineer


class PersistenceBaseline:
    """
    Naive persistence baseline: predict latest observed value.

    For multi-step, the prediction for every horizon step is the
    last known value. This is the minimum bar any model must beat.
    """

    def predict(self, latest_value: float, n_steps: int = 1) -> List[float]:
        return [latest_value] * n_steps


class ForecastingEngine:
    """
    Multi-step pH forecasting engine.

    Uses Random Forest (scikit-learn) with recursive multi-step prediction.
    Recursive strategy: predict step t+1, feed it back as input to
    predict t+2, and so on. This is documented — error can accumulate
    over longer horizons.

    Attributes:
        feature_engineer: Feature extraction pipeline.
        model: Trained RandomForestRegressor or None.
        baseline: PersistenceBaseline for comparison.
    """

    def __init__(
        self,
        window_size: int = 20,
        min_train_samples: int = 50,
        retrain_interval: int = 50,
        n_estimators: int = 100,
        max_depth: int = 12,
        random_state: int = 42,
    ):
        self.window_size = window_size
        self.min_train_samples = min_train_samples
        self.retrain_interval = retrain_interval
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.random_state = random_state

        self.feature_engineer = FeatureEngineer(window_size=window_size)
        self.model: Optional[RandomForestRegressor] = None
        self.baseline = PersistenceBaseline()

        self._history: deque = deque(maxlen=2000)
        self._read_count: int = 0
        self._is_trained: bool = False
        self._train_metrics: Optional[Dict] = None
        self._feature_importance: Optional[List[float]] = None
        self._total_retrains: int = 0
        self._last_retrain_at: Optional[str] = None

    # ------------------------------------------------------------------
    # Data ingestion
    # ------------------------------------------------------------------

    def add_reading(self, value: float, timestamp: Optional[datetime] = None):
        """Add a new pH reading to the history buffer."""
        self._history.append(value)
        self._read_count += 1

        # Auto-train / retrain
        if len(self._history) >= self.min_train_samples:
            if not self._is_trained:
                self.train()
                if self._is_trained:
                    self._total_retrains += 1
                    self._last_retrain_at = (
                        timestamp.isoformat() if timestamp else datetime.now().isoformat()
                    )
            elif self.retrain_interval > 0 and self._read_count % self.retrain_interval == 0:
                self.train()
                if self._is_trained:
                    self._total_retrains += 1
                    self._last_retrain_at = (
                        timestamp.isoformat() if timestamp else datetime.now().isoformat()
                    )

    # ------------------------------------------------------------------
    # Training
    # ------------------------------------------------------------------

    def train(self) -> bool:
        """
        Train the Random Forest model on accumulated history.

        Uses chronological split: first 80% train, last 20% validation.
        Never shuffles time-series data.

        Returns:
            True if training succeeded.
        """
        values = list(self._history)
        X, y = self.feature_engineer.extract_batch(values, target_offset=1)

        if len(X) < 10:
            return False

        # Chronological split — no shuffling
        split = int(len(X) * 0.8)
        if split < 5 or (len(X) - split) < 2:
            split = max(5, len(X) - 2)

        X_train, X_val = X[:split], X[split:]
        y_train, y_val = y[:split], y[split:]

        self.model = RandomForestRegressor(
            n_estimators=self.n_estimators,
            max_depth=self.max_depth,
            random_state=self.random_state,
            n_jobs=-1,
        )
        self.model.fit(X_train, y_train)
        self._is_trained = True

        # Feature importance
        self._feature_importance = self.model.feature_importances_.tolist()

        # Validation metrics
        y_pred = self.model.predict(X_val)
        mae = float(mean_absolute_error(y_val, y_pred))
        rmse = float(np.sqrt(mean_squared_error(y_val, y_pred)))
        ss_res = float(np.sum((y_val - y_pred) ** 2))
        ss_tot = float(np.sum((y_val - np.mean(y_val)) ** 2))
        r2 = float(1 - ss_res / ss_tot) if ss_tot > 0 else 0.0

        self._train_metrics = {
            "mae": round(mae, 6),
            "rmse": round(rmse, 6),
            "r2": round(r2, 6),
            "train_samples": len(X_train),
            "val_samples": len(X_val),
        }
        return True

    # ------------------------------------------------------------------
    # Prediction
    # ------------------------------------------------------------------

    def predict_single(self, hour_of_day: Optional[float] = None) -> Tuple[float, bool]:
        """
        Predict the next single value.

        Returns:
            (predicted_value, is_model_trained)
        """
        values = list(self._history)
        if not values:
            return 7.5, False  # safe default

        if self._is_trained and self.model is not None:
            features = self.feature_engineer.extract(values, hour_of_day)
            pred = float(self.model.predict(features.reshape(1, -1))[0])
            return round(pred, 4), True

        # Fallback: persistence baseline
        return round(values[-1], 4), False

    def predict_multistep(
        self,
        n_steps: int = 5,
        hour_of_day: Optional[float] = None,
    ) -> Dict:
        """
        Multi-step recursive forecast.

        Strategy: predict step t+1, append to synthetic history,
        then predict t+2, etc. Error can accumulate — this is
        documented and expected for recursive multi-step forecasting.

        Args:
            n_steps: Number of steps to forecast.
            hour_of_day: Current hour for time features.

        Returns:
            Dictionary with model predictions, baseline predictions, and metadata.
        """
        values = list(self._history)
        if not values:
            return {
                "model_predictions": [7.5] * n_steps,
                "baseline_predictions": [7.5] * n_steps,
                "is_model_trained": False,
                "strategy": "persistence_fallback",
                "n_steps": n_steps,
            }

        baseline_preds = self.baseline.predict(values[-1], n_steps)

        if not self._is_trained or self.model is None:
            return {
                "model_predictions": baseline_preds,
                "baseline_predictions": baseline_preds,
                "is_model_trained": False,
                "strategy": "persistence_baseline",
                "n_steps": n_steps,
            }

        # Recursive multi-step
        synthetic_history = list(values)
        model_preds = []

        for step in range(n_steps):
            features = self.feature_engineer.extract(synthetic_history, hour_of_day)
            pred = float(self.model.predict(features.reshape(1, -1))[0])
            pred = round(pred, 4)
            model_preds.append(pred)
            synthetic_history.append(pred)

        return {
            "model_predictions": model_preds,
            "baseline_predictions": baseline_preds,
            "is_model_trained": True,
            "strategy": "recursive_random_forest",
            "n_steps": n_steps,
        }

    # ------------------------------------------------------------------
    # Evaluation
    # ------------------------------------------------------------------

    def evaluate(self, horizon_steps: List[int] = None) -> Dict:
        """
        Evaluate forecasting accuracy at multiple horizons.

        Uses chronological split (last 20% as test).

        Returns:
            Evaluation results per horizon.
        """
        if horizon_steps is None:
            horizon_steps = [1, 5, 15, 30]

        values = list(self._history)
        results = {}

        for h in horizon_steps:
            X, y = self.feature_engineer.extract_batch(values, target_offset=h)
            if len(X) < 10:
                results[f"{h}_step"] = {"error": "Insufficient data"}
                continue

            split = int(len(X) * 0.8)
            if split < 5 or (len(X) - split) < 2:
                results[f"{h}_step"] = {"error": "Insufficient data for split"}
                continue

            X_train, X_test = X[:split], X[split:]
            y_train, y_test = y[:split], y[split:]

            # Train a fresh model for this horizon
            model = RandomForestRegressor(
                n_estimators=self.n_estimators,
                max_depth=self.max_depth,
                random_state=self.random_state,
                n_jobs=-1,
            )
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)

            # Baseline: persistence (last value from features = current_value = X[:, 0])
            y_baseline = X_test[:, 0]

            mae_model = float(mean_absolute_error(y_test, y_pred))
            rmse_model = float(np.sqrt(mean_squared_error(y_test, y_pred)))
            ss_res = float(np.sum((y_test - y_pred) ** 2))
            ss_tot = float(np.sum((y_test - np.mean(y_test)) ** 2))
            r2_model = float(1 - ss_res / ss_tot) if ss_tot > 0 else 0.0

            mae_base = float(mean_absolute_error(y_test, y_baseline))
            rmse_base = float(np.sqrt(mean_squared_error(y_test, y_baseline)))
            ss_res_b = float(np.sum((y_test - y_baseline) ** 2))
            r2_base = float(1 - ss_res_b / ss_tot) if ss_tot > 0 else 0.0

            results[f"{h}_step"] = {
                "horizon_steps": h,
                "model": {
                    "mae": round(mae_model, 6),
                    "rmse": round(rmse_model, 6),
                    "r2": round(r2_model, 6),
                },
                "baseline_persistence": {
                    "mae": round(mae_base, 6),
                    "rmse": round(rmse_base, 6),
                    "r2": round(r2_base, 6),
                },
                "train_samples": len(X_train),
                "test_samples": len(X_test),
                "data_source": "synthetic",
            }

        return results

    # ------------------------------------------------------------------
    # Model info / export
    # ------------------------------------------------------------------

    def get_model_info(self) -> Dict:
        return {
            "is_trained": self._is_trained,
            "model_type": "RandomForest" if self._is_trained else "PersistenceBaseline",
            "history_size": len(self._history),
            "window_size": self.window_size,
            "train_metrics": self._train_metrics,
            "feature_importance": self._feature_importance,
            "feature_names": FeatureEngineer.FEATURE_NAMES,
            "total_retrains": self._total_retrains,
            "last_retrain_at": self._last_retrain_at,
            "n_estimators": self.n_estimators,
            "max_depth": self.max_depth,
        }

    def get_sklearn_model(self):
        """Return the raw sklearn model (for OpenVINO export)."""
        return self.model

    @property
    def is_trained(self) -> bool:
        return self._is_trained

    @property
    def total_retrains(self) -> int:
        return self._total_retrains

    @property
    def history(self) -> list:
        return list(self._history)
