"""
Unit tests for pH Alert Engine
"""

import pytest
from datetime import datetime
from alerts.ph_alert_engine import PHAlertEngine, AlertStatus


def test_alert_engine_initialization():
    """Test alert engine initialization."""
    engine = PHAlertEngine(low_threshold=7.0, high_threshold=8.5, consecutive_count=3)
    
    assert engine.low_threshold == 7.0
    assert engine.high_threshold == 8.5
    assert engine.consecutive_count == 3
    assert engine.current_status == AlertStatus.NORMAL


def test_normal_ph():
    """Test normal pH values."""
    engine = PHAlertEngine(consecutive_count=3)
    timestamp = datetime.now()
    
    status, message = engine.process_reading(timestamp, 7.5)
    assert status == AlertStatus.NORMAL
    assert "Normal" in message or "normal" in message.lower()


def test_low_ph_alert():
    """Test low pH alert triggering."""
    engine = PHAlertEngine(low_threshold=7.0, consecutive_count=3)
    timestamp = datetime.now()
    
    # First low reading - should be WAITING
    status, _ = engine.process_reading(timestamp, 6.9)
    assert status == AlertStatus.WAITING
    
    # Second low reading - still WAITING
    status, _ = engine.process_reading(timestamp, 6.8)
    assert status == AlertStatus.WAITING
    
    # Third low reading - should trigger ALERT
    status, message = engine.process_reading(timestamp, 6.7)
    assert status == AlertStatus.ALERT_LOW_PH
    assert "LOW" in message or "low" in message.lower()


def test_high_ph_alert():
    """Test high pH alert triggering."""
    engine = PHAlertEngine(high_threshold=8.5, consecutive_count=3)
    timestamp = datetime.now()
    
    # Three high readings
    engine.process_reading(timestamp, 8.6)
    engine.process_reading(timestamp, 8.7)
    status, message = engine.process_reading(timestamp, 8.8)
    
    assert status == AlertStatus.ALERT_HIGH_PH
    assert "HIGH" in message or "high" in message.lower()


def test_alert_reset():
    """Test that alerts reset when pH returns to normal."""
    engine = PHAlertEngine(consecutive_count=2)
    timestamp = datetime.now()
    
    # Trigger low alert
    engine.process_reading(timestamp, 6.9)
    engine.process_reading(timestamp, 6.8)
    
    # Return to normal
    status, _ = engine.process_reading(timestamp, 7.5)
    assert status == AlertStatus.NORMAL


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

