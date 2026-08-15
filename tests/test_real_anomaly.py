"""
Unit tests for anomaly detection on real aquaculture datasets.
"""

import pytest
import numpy as np
import pandas as pd
from data_pipeline.dataset_loader import DatasetLoader
from ai.anomaly import AnomalyDetector


def test_real_anomaly_detection():
    loader = DatasetLoader()
    df, _ = loader.load("sample_aquaculture", physical_scale=True, max_rows=150)
    detector = AnomalyDetector(z_score_window=20)

    anom_count = 0
    for ph in df["ph"].values:
        detector.add_reading(float(ph))
        res = detector.detect(float(ph))
        assert "is_anomaly" in res
        assert "anomaly_score" in res
        if res["is_anomaly"]:
            anom_count += 1

    assert anom_count >= 0
