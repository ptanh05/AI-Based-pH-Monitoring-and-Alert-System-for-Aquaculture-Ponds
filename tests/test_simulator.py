"""
Unit tests for pH Simulator
"""

import pytest
from datetime import datetime
from simulator.ph_simulator import PHSimulator


def test_simulator_initialization():
    """Test simulator initialization."""
    simulator = PHSimulator(base_ph=7.5)
    assert simulator.base_ph == 7.5
    assert simulator.current_ph == 7.5


def test_generate_reading():
    """Test reading generation."""
    simulator = PHSimulator(base_ph=7.5)
    timestamp, ph_value = simulator.generate_reading()
    
    assert isinstance(timestamp, datetime)
    assert isinstance(ph_value, float)
    assert 4.0 <= ph_value <= 10.0  # Realistic pH range


def test_ph_range():
    """Test that pH values stay in realistic range."""
    simulator = PHSimulator(base_ph=7.5)
    
    for _ in range(100):
        _, ph_value = simulator.generate_reading()
        assert 4.0 <= ph_value <= 10.0


def test_stream_readings():
    """Test streaming readings."""
    simulator = PHSimulator(base_ph=7.5)
    readings = list(simulator.stream_readings(interval_seconds=0.1, max_readings=5))
    
    assert len(readings) == 5
    for timestamp, ph_value in readings:
        assert isinstance(timestamp, datetime)
        assert isinstance(ph_value, float)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

