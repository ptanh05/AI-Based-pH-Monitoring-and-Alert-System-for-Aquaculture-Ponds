"""
Temporal Resampling and Regularization Pipeline for AI Aquaculture Guardian.

Transforms irregular or multi-reading raw time-series into regularized
fixed-interval grids (e.g. 5-minute, 15-minute, 1-hour intervals).

Transparently tracks and reports:
- Original sample count
- Resampled grid count
- Number and percentage of interpolated/filled points
- Resampling metadata
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional


class TimeSeriesResampler:
    """
    Resamples time-series water quality data with full provenance tracking.
    """

    def __init__(
        self,
        target_freq: str = "5min",
        interpolation_method: str = "time",
        max_fill_gap_intervals: int = 6,
    ):
        """
        Args:
            target_freq: Target pandas frequency string (e.g. '5min', '15min', '1h').
            interpolation_method: Interpolation method ('time', 'linear', 'nearest').
            max_fill_gap_intervals: Maximum consecutive missing intervals to interpolate.
        """
        self.target_freq = target_freq
        self.interpolation_method = interpolation_method
        self.max_fill_gap_intervals = max_fill_gap_intervals

    def resample(
        self,
        df: pd.DataFrame,
        timestamp_col: str = "timestamp",
        value_cols: Optional[list] = None,
    ) -> Tuple[pd.DataFrame, Dict]:
        """
        Resample input DataFrame onto a uniform time grid.

        Args:
            df: Input DataFrame containing datetime timestamp column.
            timestamp_col: Name of the timestamp column.
            value_cols: List of numeric columns to resample. If None,
                        auto-detects numeric columns.

        Returns:
            (resampled_df, metadata_dict)
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

        # Set index for time resampling
        df_work = df_work.set_index(timestamp_col)

        # Step 1: Resample with mean aggregation for duplicate/dense readings in same bucket
        resampled = df_work[value_cols].resample(self.target_freq).mean()

        # Step 2: Track which slots were natively observed vs missing
        was_observed = ~resampled[value_cols[0]].isna() if value_cols else pd.Series(True, index=resampled.index)
        native_samples = int(was_observed.sum())

        # Step 3: Interpolate small gaps
        resampled_filled = resampled.interpolate(
            method=self.interpolation_method,
            limit=self.max_fill_gap_intervals,
            limit_direction="both",
        )

        resampled_df = resampled_filled.reset_index()
        resampled_count = len(resampled_df)
        interpolated_count = resampled_count - native_samples
        interpolated_pct = float(round(interpolated_count / max(1, resampled_count) * 100, 2))

        # Add explicit boolean flag column
        resampled_df["is_interpolated"] = ~was_observed.values

        metadata = {
            "original_samples": original_count,
            "resampled_samples": resampled_count,
            "native_observed_samples": native_samples,
            "interpolated_samples": interpolated_count,
            "interpolated_pct": interpolated_pct,
            "target_frequency": self.target_freq,
            "interpolation_method": self.interpolation_method,
            "max_gap_limit": self.max_fill_gap_intervals,
            "time_range_start": resampled_df[timestamp_col].min().isoformat() if not resampled_df.empty else None,
            "time_range_end": resampled_df[timestamp_col].max().isoformat() if not resampled_df.empty else None,
        }

        return resampled_df, metadata
