"""
Unit tests for data_pipeline/preprocessing.py.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime
from data_pipeline.preprocessing import DataPreprocessor


def test_preprocessor_clamping():
    pre = DataPreprocessor()
    df = pd.DataFrame({
        "timestamp": [datetime(2024, 1, 1, 0, i) for i in range(5)],
        "ph": [-2.0, 5.0, 7.5, 9.0, 18.0],
    })
    df_clean = pre.clean_raw_data(df, clamp_physical=True)
    assert df_clean["ph"].min() >= 0.0
    assert df_clean["ph"].max() <= 14.0


def test_preprocessor_train_only_scaling():
    pre = DataPreprocessor(scaler_type="standard")
    df_tr = pd.DataFrame({"ph": [7.0, 7.5, 8.0]})
    df_te = pd.DataFrame({"ph": [8.5, 9.0]})

    pre.fit_scalers(df_tr, ["ph"])
    assert pre.is_fitted

    df_tr_scaled = pre.transform(df_tr)
    df_te_scaled = pre.transform(df_te)

    # Train mean should be 0
    assert np.isclose(df_tr_scaled["ph"].mean(), 0.0, atol=1e-6)

    # Inverse transform
    inv = pre.inverse_transform_column("ph", df_tr_scaled["ph"].values)
    assert np.allclose(inv, df_tr["ph"].values)
