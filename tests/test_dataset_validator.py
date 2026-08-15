"""
Unit tests for data_pipeline/dataset_validator.py.
"""

import pytest
import pandas as pd
from datetime import datetime, timedelta
from data_pipeline.dataset_validator import DatasetValidator


def test_validator_clean_data():
    validator = DatasetValidator()
    base_t = datetime(2024, 1, 1, 0, 0, 0)
    times = [base_t + timedelta(minutes=5 * i) for i in range(100)]
    df = pd.DataFrame({
        "timestamp": times,
        "ph": [7.5 + 0.01 * (i % 10) for i in range(100)],
        "temperature": [27.0] * 100,
        "dissolved_oxygen": [8.0] * 100,
        "turbidity": [3.0] * 100,
    })
    report = validator.validate(df, dataset_name="clean_test")
    assert report.is_valid_for_training
    assert report.total_raw_rows == 100
    assert report.duplicate_timestamps == 0
    assert report.missing_values_by_col["ph"] == 0
    assert report.physical_violations_by_col["ph"] == 0


def test_validator_physical_violations():
    validator = DatasetValidator()
    base_t = datetime(2024, 1, 1, 0, 0, 0)
    times = [base_t + timedelta(minutes=5 * i) for i in range(100)]
    df = pd.DataFrame({
        "timestamp": times,
        "ph": [-1.0] * 50 + [16.0] * 50,  # Violates [0, 14]
    })
    report = validator.validate(df, dataset_name="bad_ph")
    assert not report.is_valid_for_training
    assert report.physical_violations_by_col["ph"] == 100


def test_validator_empty_data():
    validator = DatasetValidator()
    report = validator.validate(pd.DataFrame())
    assert not report.is_valid_for_training
    assert report.total_raw_rows == 0
