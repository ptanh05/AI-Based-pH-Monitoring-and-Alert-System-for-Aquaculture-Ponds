"""
Unit tests for data/real_data_loader.py.
"""

import os
import pytest
import pandas as pd
from datetime import datetime

from data.real_data_loader import RealDataLoader
from ai.sensor_schema import SensorReading


@pytest.fixture
def loader():
    return RealDataLoader()


def test_loader_iot_stream(loader):
    df = loader.load_iot_stream(physical_scale=True, max_rows=100)
    assert not df.empty
    assert len(df) == 100
    assert "timestamp" in df.columns
    assert "ph" in df.columns
    assert "temperature" in df.columns
    assert "dissolved_oxygen" in df.columns
    assert "turbidity" in df.columns

    # Verify physical ranges
    assert (df["ph"] >= 6.5).all() and (df["ph"] <= 9.0).all()
    assert (df["temperature"] >= 15.0).all() and (df["temperature"] <= 35.0).all()
    assert (df["dissolved_oxygen"] >= 5.0).all() and (df["dissolved_oxygen"] <= 12.0).all()


def test_loader_raw_scale(loader):
    df_raw = loader.load_iot_stream(physical_scale=False, max_rows=50)
    assert not df_raw.empty
    assert (df_raw["ph"] >= -0.1).all() and (df_raw["ph"] <= 1.5).all()


def test_loader_historical_baseline(loader):
    df_base = loader.load_historical_baseline()
    assert not df_base.empty
    assert "alkalinity" in df_base.columns
    assert "nitrates" in df_base.columns
    assert len(df_base) == 12  # 12 months


def test_loader_fish_health(loader):
    df_health = loader.load_fish_health_data()
    assert not df_health.empty
    assert "avg_fish_weight_g" in df_health.columns
    assert "survival_rate_pct" in df_health.columns


def test_to_sensor_readings(loader):
    from ai.sensor_schema import validate_reading
    readings = loader.to_sensor_readings(parameter="pH", pond_id="TEST-POND", max_readings=25)
    assert len(readings) == 25
    assert all(isinstance(r, SensorReading) for r in readings)
    assert all(r.pond_id == "TEST-POND" for r in readings)
    assert all(r.parameter == "pH" for r in readings)
    assert all(validate_reading(r).is_valid for r in readings)


def test_stream_real_readings(loader):
    gen = loader.stream_real_readings(parameter="pH", start_idx=0)
    count = 0
    for ts, val, ctx in gen:
        assert isinstance(ts, datetime)
        assert isinstance(val, float)
        assert "temperature" in ctx
        assert "dissolved_oxygen" in ctx
        assert "turbidity" in ctx
        count += 1
        if count >= 10:
            break
    assert count == 10
