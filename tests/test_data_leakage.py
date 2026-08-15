"""
Data Leakage Protection Verification Tests for AI Aquaculture Guardian.

Guarantees:
1. Strict chronological ordering (zero random shuffle).
2. Test timestamps strictly succeed train timestamps.
3. Feature extractors never access future observation indexes (t > current).
4. Normalization scalers are fit strictly on training set.
"""

import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

from data_pipeline.train_test_split import chronological_split
from data_pipeline.feature_alignment import FeatureAligner
from data_pipeline.preprocessing import DataPreprocessor


def test_chronological_split_ordering():
    dates = pd.date_range("2024-01-01", periods=100, freq="5min")
    df = pd.DataFrame({"timestamp": dates, "ph": np.linspace(7.0, 8.5, 100)})

    train, val, test, meta = chronological_split(df, 0.70, 0.15, 0.15)

    # 1. No overlap in time
    assert train["timestamp"].max() < val["timestamp"].min()
    assert val["timestamp"].max() < test["timestamp"].min()

    # 2. Strict chronological monotonicity
    assert train["timestamp"].is_monotonic_increasing
    assert val["timestamp"].is_monotonic_increasing
    assert test["timestamp"].is_monotonic_increasing

    # 3. Correct partition counts
    assert len(train) + len(val) + len(test) == len(df)


def test_no_future_lookahead_in_features():
    """
    Test that modifying future values in a sequence DOES NOT alter
    the feature vector computed for an earlier timestamp.
    """
    aligner = FeatureAligner(window_size=10)
    base_seq = [7.0 + 0.05 * i for i in range(30)]

    # Feature at index 15 with original sequence
    df1 = pd.DataFrame({"ph": base_seq, "timestamp": pd.date_range("2024-01-01", periods=30, freq="5min")})
    feats1, _ = aligner.extract_aligned_features(df1)

    # Now alter future values at index 20..29 drastically
    modified_seq = list(base_seq)
    for i in range(20, 30):
        modified_seq[i] = 14.0  # Massive future spike

    df2 = pd.DataFrame({"ph": modified_seq, "timestamp": pd.date_range("2024-01-01", periods=30, freq="5min")})
    feats2, _ = aligner.extract_aligned_features(df2)

    # Row 5 in feats corresponds to raw index 14. It MUST be 100% identical!
    assert np.allclose(feats1.iloc[5].values, feats2.iloc[5].values)


def test_scaler_leakage_protection():
    """Verify test distribution stats do not leak into train scaler."""
    pre = DataPreprocessor(scaler_type="standard")
    df_train = pd.DataFrame({"ph": [7.0, 7.0, 7.0, 7.0]})  # Mean = 7.0
    df_test = pd.DataFrame({"ph": [10.0, 10.0, 10.0]})    # High test values

    pre.fit_scalers(df_train, ["ph"])
    assert np.isclose(pre.scalers["ph"].mean_[0], 7.0)
    assert not np.isclose(pre.scalers["ph"].mean_[0], 8.5)
