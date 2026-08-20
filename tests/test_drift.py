"""
Tests for Concept Drift & Auto-Retraining Engine.
"""

import pytest
from ai.drift_detector import ConceptDriftDetector

def test_drift_detector_init():
    det = ConceptDriftDetector(window_size=30)
    assert det.baseline_mean == 7.50
    assert det.auto_retrain_enabled is True

def test_drift_stable():
    det = ConceptDriftDetector(window_size=20)
    for _ in range(25):
        det.add_sample(7.52)
    res = det.check_drift()
    assert res["status"] == "STABLE"
    assert res["drift_score"] < 0.20

def test_drift_detected_on_shift():
    det = ConceptDriftDetector(window_size=20, drift_threshold=0.35)
    det.set_baseline([7.5] * 20)
    # Feed shifted data (e.g. 8.6)
    for _ in range(25):
        det.add_sample(8.75)
    res = det.check_drift()
    assert res["status"] in ("DRIFT_DETECTED", "WARNING")
    assert res["drift_score"] > 0.30

def test_drift_adaptation():
    det = ConceptDriftDetector(window_size=20)
    for _ in range(20):
        det.add_sample(8.2)
    rec = det.adapt_model()
    assert rec["status"] == "RETRAIN_SUCCESS"
    assert len(det.retrain_history) >= 2
