"""
Feature Engineering Pipeline for AI Aquaculture Guardian.

Builds time-series features from sensor reading history for
forecasting, anomaly detection, and risk scoring.

All features use ONLY information available BEFORE the prediction
timestamp to avoid data leakage.
"""

import numpy as np
from typing import List, Optional, Dict
from collections import deque


class FeatureEngineer:
    """
    Builds feature vectors from pH time-series history.

    Features computed:
    - current_value: latest pH
    - rolling_mean: mean over window
    - rolling_std: standard deviation over window
    - rolling_min: minimum over window
    - rolling_max: maximum over window
    - trend: linear slope over window (least-squares)
    - rate_of_change: delta between latest and previous value
    - recent_delta: change over last N readings
    - acceleration: change of rate_of_change (second derivative)
    - hour_sin / hour_cos: cyclical time-of-day encoding
    """

    # Ordered list of feature names produced by extract()
    FEATURE_NAMES = [
        "current_value",
        "rolling_mean",
        "rolling_std",
        "rolling_min",
        "rolling_max",
        "trend",
        "rate_of_change",
        "recent_delta",
        "acceleration",
        "hour_sin",
        "hour_cos",
    ]

    def __init__(self, window_size: int = 20):
        """
        Args:
            window_size: Number of recent readings for rolling statistics.
        """
        self.window_size = window_size

    def extract(
        self,
        values: List[float],
        hour_of_day: Optional[float] = None,
    ) -> np.ndarray:
        """
        Extract a single feature vector from a value history.

        Args:
            values: Chronological list of pH values (oldest → newest).
                    Must have at least 2 entries.
            hour_of_day: Fractional hour (0-24). If None, time features
                         are set to 0.

        Returns:
            1-D numpy array of length len(FEATURE_NAMES).
        """
        if len(values) < 2:
            # Not enough data — return zeros with current value if available
            vec = np.zeros(len(self.FEATURE_NAMES))
            if values:
                vec[0] = values[-1]
            return vec

        window = values[-self.window_size:] if len(values) >= self.window_size else values
        arr = np.array(window, dtype=np.float64)

        current_value = arr[-1]
        rolling_mean = float(np.mean(arr))
        rolling_std = float(np.std(arr, ddof=0))
        rolling_min = float(np.min(arr))
        rolling_max = float(np.max(arr))

        # Trend: slope of simple least-squares line
        x = np.arange(len(arr), dtype=np.float64)
        if len(arr) >= 2 and np.std(x) > 0:
            trend = float(np.polyfit(x, arr, 1)[0])
        else:
            trend = 0.0

        # Rate of change: difference between last two values
        rate_of_change = float(arr[-1] - arr[-2])

        # Recent delta: change over the whole window
        recent_delta = float(arr[-1] - arr[0])

        # Acceleration: change of rate_of_change
        if len(arr) >= 3:
            prev_roc = float(arr[-2] - arr[-3])
            acceleration = rate_of_change - prev_roc
        else:
            acceleration = 0.0

        # Cyclical time encoding
        if hour_of_day is not None:
            hour_sin = float(np.sin(2 * np.pi * hour_of_day / 24.0))
            hour_cos = float(np.cos(2 * np.pi * hour_of_day / 24.0))
        else:
            hour_sin = 0.0
            hour_cos = 0.0

        return np.array([
            current_value,
            rolling_mean,
            rolling_std,
            rolling_min,
            rolling_max,
            trend,
            rate_of_change,
            recent_delta,
            acceleration,
            hour_sin,
            hour_cos,
        ], dtype=np.float64)

    def extract_batch(
        self,
        all_values: List[float],
        target_offset: int = 1,
    ) -> tuple:
        """
        Build training matrices X, y from a full value history.

        For each position i (where i >= window_size), we extract
        features from values[:i+1] and the target is
        values[i + target_offset].

        Args:
            all_values: Full chronological list of pH values.
            target_offset: How many steps ahead the target is.

        Returns:
            (X, y) where X is (n_samples, n_features) and y is (n_samples,).
            Returns (empty, empty) if not enough data.
        """
        min_length = self.window_size + target_offset + 1
        if len(all_values) < min_length:
            return np.empty((0, len(self.FEATURE_NAMES))), np.empty(0)

        X_list = []
        y_list = []

        for i in range(self.window_size, len(all_values) - target_offset):
            features = self.extract(all_values[: i + 1])
            target = all_values[i + target_offset]
            X_list.append(features)
            y_list.append(target)

        if not X_list:
            return np.empty((0, len(self.FEATURE_NAMES))), np.empty(0)

        return np.array(X_list), np.array(y_list)
