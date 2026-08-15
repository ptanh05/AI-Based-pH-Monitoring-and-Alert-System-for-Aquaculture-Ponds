"""
Unit tests for data/resampling.py.
"""

import pytest
import pandas as pd
from datetime import datetime, timedelta

from data.resampling import TimeSeriesResampler


def test_resampler_regular_grid():
    # Create sample DataFrame with 1-minute steps and some missing gaps
    times = [datetime(2024, 1, 1, 0, i) for i in range(30) if i not in [5, 6, 12]]
    values = [7.5 + 0.01 * i for i in range(len(times))]
    df = pd.DataFrame({"timestamp": times, "ph": values, "temp": 27.0})

    resampler = TimeSeriesResampler(target_freq="5min")
    resampled_df, meta = resampler.resample(df, value_cols=["ph", "temp"])

    assert not resampled_df.empty
    assert "timestamp" in resampled_df.columns
    assert "ph" in resampled_df.columns
    assert "is_interpolated" in resampled_df.columns
    assert meta["target_frequency"] == "5min"
    assert meta["original_samples"] == len(times)
    assert meta["resampled_samples"] == len(resampled_df)
    assert meta["interpolated_pct"] >= 0.0


def test_resampler_empty_dataframe():
    resampler = TimeSeriesResampler(target_freq="15min")
    resampled_df, meta = resampler.resample(pd.DataFrame(), value_cols=["ph"])
    assert resampled_df.empty
    assert meta["original_samples"] == 0
    assert meta["interpolated_samples"] == 0
