"""
Unit tests for real dataset forecasting training and multi-horizon prediction.
"""

import pytest
import numpy as np
import pandas as pd
from data_pipeline.dataset_loader import DatasetLoader
from data_pipeline.feature_alignment import FeatureAligner
from data_pipeline.train_test_split import chronological_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error


def test_real_forecasting_pipeline():
    loader = DatasetLoader()
    df, meta = loader.load("sample_aquaculture", physical_scale=True, max_rows=300)
    assert not df.empty

    aligner = FeatureAligner(window_size=15)
    X, y, feat_names = aligner.build_supervised_dataset(df, target_col="ph", horizon_steps=1)

    assert len(X) > 0
    assert len(X) == len(y)

    X_tr, _, X_te, _ = chronological_split(X, 0.70, 0.15, 0.15)
    y_tr, _, y_te, _ = chronological_split(y, 0.70, 0.15, 0.15)

    rf = RandomForestRegressor(n_estimators=20, max_depth=6, random_state=42)
    rf.fit(X_tr, y_tr)
    y_pred = rf.predict(X_te)

    mae = mean_absolute_error(y_te, y_pred)
    assert mae < 1.0  # MAE should be low on continuous water quality
