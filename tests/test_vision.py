"""
Tests for Computer Vision Fish Behavior Detector.
"""

import pytest
from vision.fish_behavior_detector import FishBehaviorDetector

def test_vision_detector_init():
    det = FishBehaviorDetector()
    assert det.is_active is True
    assert det.camera_id == "CAM-POND-01-HD"

def test_vision_normal_frame():
    det = FishBehaviorDetector()
    res = det.process_frame({
        "ph_value": 7.5,
        "do_value": 7.5,
        "risk_score": 10.0,
        "status": "NORMAL"
    })
    assert res["status"] == "ONLINE"
    assert res["stress_index"] < 30.0
    assert len(res["detections"]) > 0
    categories = [d["category"] for d in res["detections"]]
    assert "NORMAL_SWIMMING" in categories

def test_vision_hypoxia_piping():
    det = FishBehaviorDetector()
    res = det.process_frame({
        "ph_value": 6.4,
        "do_value": 3.8,
        "risk_score": 85.0,
        "status": "CRITICAL"
    })
    assert res["stress_index"] > 50.0
    categories = [d["category"] for d in res["detections"]]
    assert "SURFACE_PIPING" in categories
