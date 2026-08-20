"""
Tests for IoT Actuators & Automation Engine.
"""

import pytest
from devices.actuator_manager import ActuatorManager

def test_actuator_init():
    m = ActuatorManager()
    assert m.mode == "AUTO"
    status = m.get_status()
    assert "aerator" in status["devices"]
    assert "pump" in status["devices"]
    assert "lime" in status["devices"]
    assert status["total_power_kw"] >= 0

def test_actuator_mode_switch():
    m = ActuatorManager()
    assert m.set_mode("MANUAL") == "MANUAL"
    assert m.mode == "MANUAL"
    assert m.set_mode("AUTO") == "AUTO"

def test_actuator_toggle_manual():
    m = ActuatorManager()
    m.set_mode("MANUAL")
    new_state = m.toggle_device("pump", True, "Test manual on")
    assert new_state is True
    assert m.devices["pump"]["is_on"] is True
    m.toggle_device("pump", False, "Test manual off")
    assert m.devices["pump"]["is_on"] is False

def test_actuator_auto_evaluation_low_ph():
    m = ActuatorManager()
    m.set_mode("AUTO")
    m.evaluate_conditions({
        "ph_value": 6.5,
        "predicted_ph": 6.4,
        "risk_score": 75.0,
        "status": "ALERT_LOW_PH",
        "do_value": 7.0,
        "turbidity": 5.0
    })
    # Lime dispenser should be automatically triggered
    assert m.devices["lime"]["is_on"] is True
    # Aerator should be triggered due to high risk
    assert m.devices["aerator"]["is_on"] is True
