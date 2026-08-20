"""
Tests for Digital Twin "What-If" Simulation Engine.
"""

import pytest
from digital_twin.twin_simulator import DigitalTwinSimulator

def test_digital_twin_init():
    sim = DigitalTwinSimulator(default_volume_m3=1000.0)
    assert sim.default_volume_m3 == 1000.0

def test_digital_twin_rain_stress():
    sim = DigitalTwinSimulator()
    res = sim.simulate(current_ph=7.5, rainfall_mm=50.0, lime_kg=0.0)
    assert len(res["baseline"]["ph_trajectory"]) == 24
    # Rain should cause pH drop in baseline
    assert res["baseline"]["final_ph"] < 7.5
    assert "risk_reduction_pct" in res

def test_digital_twin_lime_mitigation():
    sim = DigitalTwinSimulator()
    # With 30kg lime added during 50mm rain
    res = sim.simulate(current_ph=7.2, rainfall_mm=50.0, lime_kg=40.0, aerator_hours=4.0)
    # What-if trajectory should have higher pH and higher DO than baseline
    assert res["what_if"]["final_ph"] > res["baseline"]["final_ph"]
    assert res["what_if"]["risk_score"] <= res["baseline"]["risk_score"]
    assert res["risk_reduction_pct"] > 0
