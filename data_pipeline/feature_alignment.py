"""
Multi-Sensor Feature Alignment Pipeline for AI Aquaculture Guardian.

Aligns multi-parameter sensor feeds with graceful fallback when optional
sensors (salinity, ammonia, turbidity) are missing, preventing pipeline crashes.
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional, Any


class FeatureAligner:
    """Aligns multi-sensor time-series features with leak-free lag structures."""

    def __init__(self, window_size: int = 20):
        self.window_size = window_size
        self.feature_names: List[str] = []

    def extract_aligned_features(
        self,
        df: pd.DataFrame,
        target_col: str = "ph",
        timestamp_col: str = "timestamp",
        optional_sensors: Optional[List[str]] = None,
    ) -> Tuple[pd.DataFrame, List[str]]:
        """
        Extract tabular features from time-series DataFrame with graceful fallback.

        Args:
            df: Cleaned and resampled time-series DataFrame.
            target_col: Primary parameter to forecast (default 'ph').
            timestamp_col: Name of datetime timestamp column.
            optional_sensors: List of optional sensors to include if present.

        Returns:
            (Feature DataFrame, List of feature names)
        """
        if df.empty:
            return pd.DataFrame(), []

        df_work = df.copy()
        if timestamp_col in df_work.columns:
            ts = pd.to_datetime(df_work[timestamp_col])
            hour = ts.dt.hour.values
            day_of_week = ts.dt.dayofweek.values
        else:
            hour = np.zeros(len(df_work))
            day_of_week = np.zeros(len(df_work))

        target_vals = df_work[target_col].values
        n = len(target_vals)
        W = self.window_size

        if n < W + 1:
            return pd.DataFrame(), []

        feature_rows = []
        feature_names = [
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
            "day_sin",
            "day_cos",
        ]

        # Check which optional sensors actually exist in the DataFrame
        if optional_sensors is None:
            optional_sensors = ["temperature", "dissolved_oxygen", "turbidity", "salinity", "ammonia"]

        active_optional = [s for s in optional_sensors if s in df_work.columns and s != target_col]

        for s in active_optional:
            feature_names.extend([f"{s}_current", f"{s}_rolling_mean", f"{s}_trend"])

        self.feature_names = feature_names

        # Pre-extract optional sensor vectors
        opt_data = {s: df_work[s].values for s in active_optional}

        x_coords = np.arange(W)
        x_mean = (W - 1) / 2.0
        x_denom = np.sum((x_coords - x_mean) ** 2)

        for i in range(W - 1, n):
            window = target_vals[i - W + 1 : i + 1]

            # Primary Target Features (11 canonical)
            cur = float(window[-1])
            r_mean = float(np.mean(window))
            r_std = float(np.std(window))
            r_min = float(np.min(window))
            r_max = float(np.max(window))

            # Least-squares slope over past window
            y_mean = r_mean
            trend = float(np.sum((x_coords - x_mean) * (window - y_mean)) / x_denom) if x_denom > 0 else 0.0

            roc = float(window[-1] - window[-2])
            delta = float(window[-1] - window[0])
            acc = float((window[-1] - window[-2]) - (window[-2] - window[-3]))

            # Time Encodings
            h = hour[i]
            d = day_of_week[i]
            h_sin = float(np.sin(2.0 * np.pi * h / 24.0))
            h_cos = float(np.cos(2.0 * np.pi * h / 24.0))
            d_sin = float(np.sin(2.0 * np.pi * d / 7.0))
            d_cos = float(np.cos(2.0 * np.pi * d / 7.0))

            row_feats = [
                cur, r_mean, r_std, r_min, r_max, trend,
                roc, delta, acc, h_sin, h_cos, d_sin, d_cos,
            ]

            # Optional Sensor Features
            for s in active_optional:
                s_win = opt_data[s][i - W + 1 : i + 1]
                s_cur = float(s_win[-1])
                s_mean = float(np.mean(s_win))
                s_trend = float(np.sum((x_coords - x_mean) * (s_win - s_mean)) / x_denom) if x_denom > 0 else 0.0
                row_feats.extend([s_cur, s_mean, s_trend])

            feature_rows.append(row_feats)

        feature_df = pd.DataFrame(feature_rows, columns=feature_names)
        return feature_df, feature_names

    def build_supervised_dataset(
        self,
        df: pd.DataFrame,
        target_col: str = "ph",
        timestamp_col: str = "timestamp",
        horizon_steps: int = 1,
    ) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """
        Construct feature matrix X and target vector y for horizon_steps ahead.

        Ensures NO DATA LEAKAGE: y[t] = target[t + horizon_steps],
        while X[t] strictly contains observations up to t.
        """
        feats_df, feat_names = self.extract_aligned_features(df, target_col, timestamp_col)
        if feats_df.empty:
            return np.empty((0, 0)), np.empty(0), []

        # feats_df rows correspond to indices i in [W - 1, len(df) - 1]
        W = self.window_size
        n_raw = len(df)
        target_raw = df[target_col].values

        # For row k (which corresponds to raw index i = W - 1 + k):
        # Target y is target_raw[i + horizon_steps] = target_raw[W - 1 + k + horizon_steps]
        valid_rows = n_raw - (W - 1) - horizon_steps
        if valid_rows <= 0:
            return np.empty((0, 0)), np.empty(0), []

        X = feats_df.iloc[:valid_rows].values
        y = target_raw[W - 1 + horizon_steps : W - 1 + horizon_steps + valid_rows]

        return X, y, feat_names
