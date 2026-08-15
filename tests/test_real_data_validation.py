"""
Unit tests for real-world data validation pipeline and 3-way evaluation.
"""

import pytest
from scripts.evaluate_real_forecasting import run_three_way_evaluation
from scripts.evaluate_real_anomalies import run_real_anomaly_risk_evaluation
from data.real_data_loader import RealDataLoader


def test_real_data_loader_quality():
    loader = RealDataLoader()
    df = loader.load_iot_stream(max_rows=200)
    assert not df.empty
    assert len(df) == 200
    assert not df["ph"].isna().any()
    assert not df["temperature"].isna().any()


def test_real_anomaly_risk_pipeline():
    res = run_real_anomaly_risk_evaluation()
    assert "anomaly_statistics" in res
    assert "risk_score_distribution" in res
    assert res["total_observations_analyzed"] > 0
    assert res["anomaly_statistics"]["total_anomalies_flagged"] >= 0
    assert "LOW" in res["risk_score_distribution"]["level_counts"]


def test_three_way_evaluation_structure():
    matrix = run_three_way_evaluation()
    assert "experiments" in matrix
    assert "synthetic_to_synthetic" in matrix["experiments"]
    assert "real_to_real" in matrix["experiments"]
    assert "synthetic_to_real_generalization" in matrix["experiments"]
    assert "1_step" in matrix["experiments"]["real_to_real"]
    assert "model_rf" in matrix["experiments"]["real_to_real"]["1_step"]
    assert "persistence_baseline" in matrix["experiments"]["real_to_real"]["1_step"]
