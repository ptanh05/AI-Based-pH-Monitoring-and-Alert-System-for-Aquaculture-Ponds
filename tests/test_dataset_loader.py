"""
Unit tests for data_pipeline/dataset_loader.py.
"""

import os
import pytest
import pandas as pd
from data_pipeline.dataset_loader import DatasetLoader
from data_pipeline.dataset_registry import list_registered_datasets


def test_loader_registered_dataset():
    loader = DatasetLoader()
    df, meta = loader.load("sample_aquaculture", physical_scale=True)
    assert not df.empty
    assert "timestamp" in df.columns
    assert "ph" in df.columns
    assert "temperature" in df.columns
    assert "dissolved_oxygen" in df.columns
    assert meta.name == "sample_aquaculture"


def test_loader_custom_csv_path(tmp_path):
    # Create custom temporary CSV
    csv_file = tmp_path / "custom_pond_data.csv"
    df_temp = pd.DataFrame({
        "Date_Time": ["2024-01-01 00:00:00", "2024-01-01 00:05:00", "2024-01-01 00:10:00"],
        "Water_pH": [7.4, 7.5, 7.6],
        "Water_Temp": [27.0, 27.2, 27.1],
        "DO_mg_l": [8.1, 8.2, 8.0],
    })
    df_temp.to_csv(csv_file, index=False)

    loader = DatasetLoader()
    df_loaded, meta = loader.load(str(csv_file))
    assert not df_loaded.empty
    assert len(df_loaded) == 3
    assert "timestamp" in df_loaded.columns
    assert "ph" in df_loaded.columns
    assert "temperature" in df_loaded.columns
    assert "dissolved_oxygen" in df_loaded.columns


def test_loader_nonexistent_dataset():
    loader = DatasetLoader()
    with pytest.raises(FileNotFoundError):
        loader.load("non_existent_dataset_name_12345")
