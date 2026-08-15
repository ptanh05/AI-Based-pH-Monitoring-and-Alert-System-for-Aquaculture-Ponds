"""
Time-Series Resampling and Regularization Pipeline.

Converts raw, irregular or high-frequency telemetry into regular time grids
(e.g., 5-minute, 15-minute, 1-hour) with complete provenance and interpolation tracking.
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Tuple, Optional, List, Any


class TimeSeriesResampler:
    """Resamples multi-sensor telemetry with provenance metadata."""

    def __init__(
        self,
        target_freq: str = "5min",
        interpolation_method: str = "time",
        max_fill_gap: int = 6,
    ):
        self.target_freq = target_freq
        self.interpolation_method = interpolation_method
        self.max_fill_gap = max_fill_gap

    def resample(
        self,
        df: pd.DataFrame,
        timestamp_col: str = "timestamp",
        value_cols: Optional[List[str]] = None,
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Resample input DataFrame onto a uniform time grid.
        """
        if df.empty:
            return pd.DataFrame(), {
                "original_samples": 0,
                "resampled_samples": 0,
                "interpolated_samples": 0,
                "interpolated_pct": 0.0,
                "freq": self.target_freq,
            }

        df_work = df.copy()
        if not pd.api.types.is_datetime64_any_dtype(df_work[timestamp_col]):
            df_work[timestamp_col] = pd.to_datetime(df_work[timestamp_col])

        df_work = df_work.sort_values(timestamp_col).reset_index(drop=True)
        original_count = len(df_work)

        if value_cols is None:
            value_cols = [c for c in df_work.columns if c != timestamp_col and pd.api.types.is_numeric_dtype(df_work[c])]

        df_work = df_work.set_index(timestamp_col)

        # Resample with mean aggregation
        resampled = df_work[value_cols].resample(self.target_freq).mean()

        was_observed = ~resampled[value_cols[0]].isna() if value_cols else pd.Series(True, index=resampled.index)
        native_samples = int(was_observed.sum())

        resampled_filled = resampled.interpolate(
            method=self.interpolation_method if self.interpolation_method != "time" or isinstance(resampled.index, pd.DatetimeIndex) else "linear",
            limit=self.max_fill_gap,
            limit_direction="both",
        )
        resampled_filled = resampled_filled.ffill().bfill()

        resampled_df = resampled_filled.reset_index()
        resampled_count = len(resampled_df)
        interpolated_count = resampled_count - native_samples
        interpolated_pct = float(round(interpolated_count / max(1, resampled_count) * 100, 2))

        resampled_df["is_interpolated"] = ~was_observed.values

        metadata = {
            "original_samples": original_count,
            "resampled_samples": resampled_count,
            "native_observed_samples": native_samples,
            "interpolated_samples": interpolated_count,
            "interpolated_pct": interpolated_pct,
            "target_frequency": self.target_freq,
            "interpolation_method": self.interpolation_method,
            "time_range_start": resampled_df[timestamp_col].min().isoformat() if not resampled_df.empty else None,
            "time_range_end": resampled_df[timestamp_col].max().isoformat() if not resampled_df.empty else None,
        }

        return resampled_df, metadata
