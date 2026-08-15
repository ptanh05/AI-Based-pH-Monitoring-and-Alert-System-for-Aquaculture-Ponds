"""
Comprehensive Mathematical & Boundary Audit for AquacultureRiskEngine.

Verifies:
1. Boundedness in [0, 100]
2. Monotonicity near safe thresholds (7.75 optimal center -> 8.5 edge -> 9.0+ breach)
3. Rate of change and trend contributions
4. Hybrid anomaly contribution
5. Extreme value resilience (< 0, > 14)
6. Missing/None forecast fallback handling
"""

import pytest
from ai.risk import AquacultureRiskEngine, RiskLevel, classify_risk


@pytest.fixture
def risk_engine():
    return AquacultureRiskEngine(low_threshold=7.0, high_threshold=8.5)


def test_risk_boundedness(risk_engine):
    """Verify that under all extreme combinations, risk is bounded strictly in [0.0, 100.0]."""
    test_cases = [
        (7.75, 7.75, 0.0, 0.0, 0.0),   # Optimal center
        (0.0, 0.0, 5.0, -1.0, 1.0),    # Extreme low acid
        (14.0, 14.0, 5.0, 1.0, 1.0),   # Extreme high alkaline
        (-5.0, -5.0, 10.0, -2.0, 1.0), # Sub-zero physical impossibility
        (20.0, 20.0, 10.0, 2.0, 1.0),  # Beyond scale
    ]
    for cur, pred, roc, trend, anom in test_cases:
        res = risk_engine.compute(
            current_ph=cur,
            predicted_ph=pred,
            rate_of_change=roc,
            trend=trend,
            anomaly_score=anom,
        )
        assert 0.0 <= res["total"] <= 100.0
        assert res["level"] in ["LOW", "MODERATE", "ELEVATED", "HIGH", "CRITICAL"]


def test_risk_monotonicity_near_boundaries(risk_engine):
    """Verify risk increases monotonically as pH diverges from optimal center (7.75) towards and beyond 8.5."""
    r_775 = risk_engine.compute(7.75, 7.75, 0.0, 0.0, 0.0)["total"]
    r_80 = risk_engine.compute(8.0, 8.0, 0.0, 0.0, 0.0)["total"]
    r_84 = risk_engine.compute(8.4, 8.4, 0.0, 0.0, 0.0)["total"]
    r_86 = risk_engine.compute(8.6, 8.6, 0.0, 0.0, 0.0)["total"]
    r_90 = risk_engine.compute(9.0, 9.0, 0.0, 0.0, 0.0)["total"]

    assert r_775 <= r_80 <= r_84 <= r_86 <= r_90


def test_risk_forecast_advance_warning(risk_engine):
    """Verify that an impending breach in forecast raises risk even if current pH is nominal."""
    # Current pH is normal (7.75), but forecasted to spike to 8.8
    r_nominal = risk_engine.compute(current_ph=7.75, predicted_ph=7.75, rate_of_change=0.0, trend=0.0, anomaly_score=0.0)["total"]
    r_forecast_danger = risk_engine.compute(current_ph=7.75, predicted_ph=8.8, rate_of_change=0.05, trend=0.02, anomaly_score=0.0)["total"]

    assert r_forecast_danger > r_nominal
    assert r_forecast_danger >= 20.0  # Forecast penalty must elevate score


def test_risk_trend_and_anomaly_weights(risk_engine):
    """Verify trend slope and anomaly detector elevate risk proportionally."""
    r_clean = risk_engine.compute(7.75, 7.75, 0.0, 0.0, 0.0)["total"]
    r_trend = risk_engine.compute(7.75, 7.75, 0.1, 0.05, 0.0)["total"]
    r_anomaly = risk_engine.compute(7.75, 7.75, 0.0, 0.0, 0.8)["total"]
    r_both = risk_engine.compute(7.75, 7.75, 0.1, 0.05, 0.8)["total"]

    assert r_clean < r_trend
    assert r_clean < r_anomaly
    assert r_both > r_trend
    assert r_both > r_anomaly


def test_risk_none_forecast_resilience(risk_engine):
    """Verify graceful handling when forecast is None (cold start / initial buffer)."""
    res = risk_engine.compute(current_ph=7.75, predicted_ph=None, rate_of_change=0.0, trend=0.0, anomaly_score=0.0)
    assert 0.0 <= res["total"] <= 100.0
    assert res["level"] == "LOW"
