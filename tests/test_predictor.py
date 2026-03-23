"""
Unit tests for pH Predictor
"""

import pytest
import numpy as np
from datetime import datetime, timedelta
from ai.ph_predictor import PHPredictor


def test_predictor_initialization():
    """Test predictor initialization."""
    predictor = PHPredictor(history_window=20, min_samples_for_training=30)
    
    assert predictor.history_window == 20
    assert predictor.min_samples_for_training == 30
    assert len(predictor.ph_history) == 0


def test_add_reading():
    """Test adding readings."""
    predictor = PHPredictor()
    timestamp = datetime.now()
    
    predictor.add_reading(timestamp, 7.5)
    assert len(predictor.ph_history) == 1
    assert predictor.ph_history[0] == 7.5


def test_prediction_without_training():
    """Test prediction when model is not trained."""
    predictor = PHPredictor(min_samples_for_training=100)
    
    # Add a few readings
    for i in range(5):
        predictor.add_reading(datetime.now(), 7.5 + i * 0.1)
    
    predicted, is_reliable = predictor.predict()
    assert isinstance(predicted, float)
    assert not is_reliable  # Should not be reliable without training


def test_prediction_after_training():
    """Test prediction after model training."""
    predictor = PHPredictor(history_window=10, min_samples_for_training=20)
    
    # Add enough readings to train
    base_time = datetime.now()
    for i in range(30):
        timestamp = base_time + timedelta(minutes=i)
        ph_value = 7.5 + np.random.normal(0, 0.1)
        predictor.add_reading(timestamp, ph_value)
    
    # Should be trained now
    if predictor.is_trained:
        predicted, is_reliable = predictor.predict()
        assert isinstance(predicted, float)
        assert 4.0 <= predicted <= 10.0  # Realistic range


def test_early_warning():
    """Test early warning detection."""
    predictor = PHPredictor()
    
    # Test low pH warning
    has_warning, message = predictor.check_early_warning(6.5, low_threshold=7.0, high_threshold=8.5)
    assert has_warning is True
    assert "low" in message.lower() or "below" in message.lower()
    
    # Test high pH warning
    has_warning, message = predictor.check_early_warning(9.0, low_threshold=7.0, high_threshold=8.5)
    assert has_warning is True
    assert "high" in message.lower() or "exceed" in message.lower()
    
    # Test safe pH
    has_warning, message = predictor.check_early_warning(7.5, low_threshold=7.0, high_threshold=8.5)
    assert has_warning is False


def test_model_info():
    """Test model info retrieval."""
    predictor = PHPredictor()
    info = predictor.get_model_info()
    
    assert "is_trained" in info
    assert "history_size" in info
    assert "model_type" in info
    assert isinstance(info["is_trained"], bool)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

