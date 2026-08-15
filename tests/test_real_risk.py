"""
Unit tests for AquacultureRiskEngine on real-world multi-sensor streams.
"""

import pytest
from data_pipeline.dataset_loader import DatasetLoader
from ai.risk import AquacultureRiskEngine


def test_real_risk_scoring():
    loader = DatasetLoader()
    df, _ = loader.load("sample_aquaculture", physical_scale=True, max_rows=50)
    risk_engine = AquacultureRiskEngine(low_threshold=7.0, high_threshold=8.5)

    for ph in df["ph"].values:
        res = risk_engine.compute(
            current_ph=float(ph),
            predicted_ph=float(ph),
            rate_of_change=0.0,
            trend=0.0,
            anomaly_score=0.0,
        )
        assert 0.0 <= res["total"] <= 100.0
        assert res["level"] in ["LOW", "MODERATE", "ELEVATED", "HIGH", "CRITICAL"]
        assert "current_value" in res["components"]
        assert "forecast" in res["components"]
