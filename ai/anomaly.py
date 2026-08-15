"""
Anomaly Detection Engine for AI Aquaculture Guardian.

Detects unusual sensor behaviour that may indicate equipment failure,
environmental events, or data quality problems — even when pH is
still within the configured safety thresholds.

Methods:
- Rolling Z-Score: fast, statistical, good for sudden spikes.
- Isolation Forest: ML-based, learns normal patterns.
"""

import numpy as np
from typing import List, Optional, Dict, Tuple
from collections import deque

try:
    from sklearn.ensemble import IsolationForest
    ISOLATION_FOREST_AVAILABLE = True
except ImportError:
    ISOLATION_FOREST_AVAILABLE = False


class AnomalyDetector:
    """
    Hybrid anomaly detection for aquaculture sensor data.

    Combines:
    1. Rolling Z-Score for immediate spike detection.
    2. Isolation Forest for pattern-based anomaly scoring
       (trained once enough data is available).
    """

    def __init__(
        self,
        z_score_window: int = 30,
        z_score_threshold: float = 2.5,
        isolation_forest_samples: int = 100,
        contamination: float = 0.05,
        random_state: int = 42,
    ):
        """
        Args:
            z_score_window: Rolling window for Z-Score computation.
            z_score_threshold: Absolute Z-Score above which a reading
                               is flagged as anomalous.
            isolation_forest_samples: Minimum history length before
                                      Isolation Forest is trained.
            contamination: Expected proportion of anomalies.
            random_state: Random seed for reproducibility.
        """
        self.z_score_window = z_score_window
        self.z_score_threshold = z_score_threshold
        self.isolation_forest_samples = isolation_forest_samples
        self.contamination = contamination
        self.random_state = random_state

        self._history: deque = deque(maxlen=2000)
        self._if_model: Optional[object] = None
        self._if_trained: bool = False

    # ------------------------------------------------------------------
    # Rolling Z-Score
    # ------------------------------------------------------------------

    def _compute_z_score(self, values: List[float], current: float) -> float:
        """Compute Z-Score of current value relative to recent window."""
        if len(values) < 3:
            return 0.0
        window = values[-self.z_score_window:]
        mean = float(np.mean(window))
        std = float(np.std(window, ddof=1))
        if std < 1e-8:
            # If std ≈ 0 and current differs from mean, that's a huge spike
            diff = abs(current - mean)
            if diff > 0.01:
                return (current - mean) / 0.01  # large z-score
            return 0.0
        return (current - mean) / std

    # ------------------------------------------------------------------
    # Rate-of-change anomaly
    # ------------------------------------------------------------------

    def _rate_anomaly(self, values: List[float]) -> Tuple[bool, float, str]:
        """Detect abnormally rapid changes."""
        if len(values) < 3:
            return False, 0.0, ""

        diffs = np.diff(values[-self.z_score_window:])
        if len(diffs) < 2:
            return False, 0.0, ""

        mean_diff = float(np.mean(np.abs(diffs)))
        std_diff = float(np.std(np.abs(diffs), ddof=1))
        latest_diff = abs(float(diffs[-1]))

        if std_diff < 1e-8:
            return False, 0.0, ""

        rate_z = (latest_diff - mean_diff) / std_diff
        if rate_z > self.z_score_threshold:
            direction = "upward" if diffs[-1] > 0 else "downward"
            return True, float(rate_z), f"Rapid {direction} pH change"
        return False, float(rate_z), ""

    # ------------------------------------------------------------------
    # Stuck-sensor detection
    # ------------------------------------------------------------------

    def _stuck_check(self, values: List[float], tolerance: float = 0.001) -> bool:
        """Check if sensor appears stuck (constant output)."""
        if len(values) < 10:
            return False
        recent = values[-10:]
        return (max(recent) - min(recent)) < tolerance

    # ------------------------------------------------------------------
    # Isolation Forest
    # ------------------------------------------------------------------

    def _train_isolation_forest(self, values: List[float]):
        """Train Isolation Forest on accumulated history."""
        if not ISOLATION_FOREST_AVAILABLE:
            return
        if len(values) < self.isolation_forest_samples:
            return

        # Build simple features: value, diff, rolling_std
        arr = np.array(values)
        diffs = np.diff(arr)
        # Align lengths
        n = len(diffs)
        features = []
        window = min(10, n)
        for i in range(window, n):
            segment = arr[i - window + 1: i + 2]  # +2 because arr is one longer
            features.append([
                arr[i + 1],
                diffs[i],
                float(np.std(segment)),
            ])

        if len(features) < 20:
            return

        X = np.array(features)
        self._if_model = IsolationForest(
            contamination=self.contamination,
            random_state=self.random_state,
            n_estimators=100,
        )
        self._if_model.fit(X)
        self._if_trained = True

    def _isolation_forest_score(self, values: List[float], current: float) -> float:
        """
        Compute anomaly score from Isolation Forest.

        Returns a score in [0, 1] where higher = more anomalous.
        """
        if not self._if_trained or self._if_model is None:
            return 0.0

        arr = np.array(values)
        if len(arr) < 11:
            return 0.0

        diff = current - arr[-2] if len(arr) >= 2 else 0.0
        segment = arr[-10:]
        std = float(np.std(segment))

        X = np.array([[current, diff, std]])
        # decision_function: lower = more anomalous; we invert and clip to [0,1]
        raw_score = -float(self._if_model.decision_function(X)[0])
        # Normalize roughly to [0, 1]
        score = max(0.0, min(1.0, (raw_score + 0.5) / 1.0))
        return round(score, 4)

    # ------------------------------------------------------------------
    # Main API
    # ------------------------------------------------------------------

    def add_reading(self, value: float):
        """Add a new value; auto-train Isolation Forest when ready."""
        self._history.append(value)
        if (
            not self._if_trained
            and len(self._history) >= self.isolation_forest_samples
        ):
            self._train_isolation_forest(list(self._history))

    def detect(self, value: Optional[float] = None) -> Dict:
        """
        Run anomaly detection on the latest reading.

        Args:
            value: Explicit value to check. If None, uses the last
                   value in history.

        Returns:
            {
                "is_anomaly": bool,
                "anomaly_score": float (0-1),
                "reasons": [str, ...],
                "z_score": float,
                "isolation_score": float,
                "stuck_sensor": bool,
            }
        """
        values = list(self._history)
        if value is not None and (not values or values[-1] != value):
            values.append(value)

        if not values:
            return {
                "is_anomaly": False,
                "anomaly_score": 0.0,
                "reasons": [],
                "z_score": 0.0,
                "isolation_score": 0.0,
                "stuck_sensor": False,
            }

        current = values[-1]
        reasons = []

        # Z-Score
        z = self._compute_z_score(values[:-1] if len(values) > 1 else values, current)
        z_anomaly = abs(z) > self.z_score_threshold
        if z_anomaly:
            direction = "above" if z > 0 else "below"
            reasons.append(
                f"pH value is {abs(z):.1f} standard deviations {direction} recent mean"
            )

        # Rate-of-change
        rate_flag, rate_z, rate_reason = self._rate_anomaly(values)
        if rate_flag and rate_reason:
            reasons.append(rate_reason)

        # Stuck sensor
        stuck = self._stuck_check(values)
        if stuck:
            reasons.append("Sensor appears stuck — constant readings detected")

        # Isolation Forest
        if_score = self._isolation_forest_score(values, current)
        if if_score > 0.6:
            reasons.append("Isolation Forest flagged unusual pattern")

        # Composite anomaly score (0–1)
        z_contrib = min(abs(z) / (self.z_score_threshold * 2), 1.0) * 0.4
        rate_contrib = min(abs(rate_z) / (self.z_score_threshold * 2), 1.0) * 0.2
        if_contrib = if_score * 0.3
        stuck_contrib = 0.1 if stuck else 0.0

        anomaly_score = float(round(min(1.0, z_contrib + rate_contrib + if_contrib + stuck_contrib), 4))
        is_anomaly = bool(anomaly_score > 0.35 or z_anomaly or rate_flag or stuck)

        return {
            "is_anomaly": bool(is_anomaly),
            "anomaly_score": float(anomaly_score),
            "reasons": list(reasons),
            "z_score": float(round(z, 4)),
            "isolation_score": float(if_score),
            "stuck_sensor": bool(stuck),
        }

    def get_info(self) -> Dict:
        return {
            "history_size": len(self._history),
            "isolation_forest_trained": self._if_trained,
            "z_score_window": self.z_score_window,
            "z_score_threshold": self.z_score_threshold,
        }
