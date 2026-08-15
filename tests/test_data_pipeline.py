"""
Unit tests for data_pipeline package and multivariate feature extractor.
"""

import os
import yaml
import pytest
import numpy as np
import pandas as pd

from data_pipeline.downloader import DatasetDownloader
from data_pipeline.feature_adapter import MultivariateFeatureExtractor
from data_pipeline.dataset_registry import list_registered_datasets


def test_dataset_downloader_registered():
    downloader = DatasetDownloader()
    res = downloader.verify_local_dataset("sample_aquaculture")
    assert res["status"] == "present"
    assert "sha256" in res
    assert res["size_bytes"] > 0


def test_multivariate_feature_extractor_shapes():
    dates = pd.date_range("2024-01-01", periods=100, freq="5min")
    df = pd.DataFrame({
        "timestamp": dates,
        "ph": np.linspace(7.2, 7.8, 100),
        "temperature": np.linspace(26.0, 28.0, 100),
        "dissolved_oxygen": np.linspace(7.5, 8.5, 100),
        "turbidity": np.linspace(3.0, 4.0, 100),
    })

    extractor = MultivariateFeatureExtractor(window_size=20)
    X, y, feat_names = extractor.build_supervised_dataset(df, target_col="ph", horizon_steps=1, include_multisensor=True)

    # 100 rows - 20 window - 1 horizon + 1 = 80 samples
    assert len(X) == 80
    assert len(y) == 80
    assert "ph_current" in feat_names
    assert "temperature_current" in feat_names
    assert "dissolved_oxygen_current" in feat_names


def test_config_files_validity():
    with open("configs/real_data.yaml", "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    assert cfg["dataset"]["name"] == "mendeley_aquaculture"
    assert cfg["split"]["strategy"] == "chronological"
    assert cfg["split"]["train_ratio"] == 0.70

    with open("configs/synthetic_demo.yaml", "r", encoding="utf-8") as f:
        cfg_syn = yaml.safe_load(f)
    assert cfg_syn["simulator"]["scenario"] == "competition_demo"
