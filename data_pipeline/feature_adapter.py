"""
Multivariate Feature Adapter for AI Aquaculture Guardian.

Extracts feature matrices from single or multi-sensor time-series streams:
- Primary: pH (lags, rolling statistics, rate of change, trend, hour sin/cos)
- Optional Auxiliary: Temperature, Dissolved Oxygen (DO), Turbidity, Salinity, Ammonia

Gracefully falls back to pH-only mode when auxiliary sensors are absent.
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional, Any


class MultivariateFeatureExtractor:
    """Extracts aligned multi-sensor feature vectors with dynamic sensor availability."""

    def __init__(self, window_size: int = 20):
        self.window_size = window_size
        self.sensor_columns = ["ph", "temperature", "dissolved_oxygen", "turbidity", "salinity", "ammonia"]

    def extract_from_dataframe(
        self,
        df: pd.DataFrame,
        target_col: str = "ph",
        include_multisensor: bool = True,
    ) -> Tuple[np.ndarray, List[str]]:
        """
        Extract multivariate features for each row in a regularized DataFrame.

        Returns:
            X: 2D numpy array of features (N - window_size + 1, num_features)
            feature_names: List of column names
        """
        if len(df) < self.window_size:
            raise ValueError(f"DataFrame length ({len(df)}) must be at least window_size ({self.window_size})")

        available_sensors = [s for s in self.sensor_columns if s in df.columns]
        feature_list = []
        feature_names = []

        # 1. Base pH lag features (13 core features)
        ph_series = df["ph"].values
        feature_names.extend([
            "ph_current",
            "ph_lag_1", "ph_lag_2", "ph_lag_3", "ph_lag_5",
            "ph_rolling_mean_5", "ph_rolling_mean_10", "ph_rolling_mean_20",
            "ph_rolling_std_10",
            "ph_rate_of_change",
            "ph_trend_slope",
            "ph_min_window",
            "ph_max_window",
        ])

        # 2. Time features if timestamp exists
        has_time = "timestamp" in df.columns
        if has_time:
            feature_names.extend(["hour_sin", "hour_cos"])

        # 3. Auxiliary sensor features
        aux_sensors = [s for s in available_sensors if s != "ph"] if include_multisensor else []
        for s in aux_sensors:
            feature_names.extend([f"{s}_current", f"{s}_delta_5", f"{s}_trend"])

        # Construct rows
        for i in range(self.window_size - 1, len(df)):
            row_feats = []
            w_ph = ph_series[i - self.window_size + 1 : i + 1]

            # Core pH
            current = float(w_ph[-1])
            l1 = float(w_ph[-2]) if len(w_ph) >= 2 else current
            l2 = float(w_ph[-3]) if len(w_ph) >= 3 else current
            l3 = float(w_ph[-4]) if len(w_ph) >= 4 else current
            l5 = float(w_ph[-6]) if len(w_ph) >= 6 else current

            m5 = float(np.mean(w_ph[-5:]))
            m10 = float(np.mean(w_ph[-10:]))
            m20 = float(np.mean(w_ph))
            std10 = float(np.std(w_ph[-10:])) if len(w_ph) >= 10 else 0.0

            roc = float(w_ph[-1] - w_ph[-2]) if len(w_ph) >= 2 else 0.0
            # Linear trend
            x_axis = np.arange(len(w_ph))
            slope = float(np.polyfit(x_axis, w_ph, 1)[0]) if len(w_ph) >= 2 else 0.0

            min_w = float(np.min(w_ph))
            max_w = float(np.max(w_ph))

            row_feats.extend([current, l1, l2, l3, l5, m5, m10, m20, std10, roc, slope, min_w, max_w])

            # Time
            if has_time:
                ts = df["timestamp"].iloc[i]
                hour = ts.hour if hasattr(ts, "hour") else 12.0
                row_feats.append(float(np.sin(2 * np.pi * hour / 24.0)))
                row_feats.append(float(np.cos(2 * np.pi * hour / 24.0)))

            # Aux sensors
            for s in aux_sensors:
                w_s = df[s].iloc[i - self.window_size + 1 : i + 1].values
                s_cur = float(w_s[-1])
                s_d5 = float(w_s[-1] - w_s[-6]) if len(w_s) >= 6 else 0.0
                s_slope = float(np.polyfit(x_axis, w_s, 1)[0]) if len(w_s) >= 2 else 0.0
                row_feats.extend([s_cur, s_d5, s_slope])

            feature_list.append(row_feats)

        return np.array(feature_list, dtype=np.float64), feature_names

    def build_supervised_dataset(
        self,
        df: pd.DataFrame,
        target_col: str = "ph",
        horizon_steps: int = 1,
        include_multisensor: bool = True,
    ) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """Build (X, y) supervised matrices for multi-step forecasting."""
        X_all, feat_names = self.extract_from_dataframe(df, target_col=target_col, include_multisensor=include_multisensor)
        target_series = df[target_col].values[self.window_size - 1 :]

        if len(target_series) <= horizon_steps:
            raise ValueError("Insufficient rows for specified horizon_steps.")

        X = X_all[:-horizon_steps]
        y = target_series[horizon_steps:]
        return X, y, feat_names
