"""
Data Pipeline Package for AI Aquaculture Guardian.

Provides robust, reproducible ingestion, validation, preprocessing,
resampling, multivariate feature engineering, and temporal partitioning
for real-world and synthetic aquaculture datasets.
"""

from data_pipeline.dataset_registry import (
    DatasetMetadata,
    DATASET_REGISTRY,
    get_dataset_metadata,
    list_registered_datasets,
)
from data_pipeline.dataset_loader import DatasetLoader
from data_pipeline.dataset_validator import DatasetValidator, ValidationReport
from data_pipeline.preprocessing import DataPreprocessor
from data_pipeline.resampling import TimeSeriesResampler
from data_pipeline.feature_alignment import FeatureAligner
from data_pipeline.feature_adapter import MultivariateFeatureExtractor
from data_pipeline.train_test_split import chronological_split
from data_pipeline.downloader import DatasetDownloader

__all__ = [
    "DatasetMetadata",
    "DATASET_REGISTRY",
    "get_dataset_metadata",
    "list_registered_datasets",
    "DatasetLoader",
    "DatasetValidator",
    "ValidationReport",
    "DataPreprocessor",
    "TimeSeriesResampler",
    "FeatureAligner",
    "MultivariateFeatureExtractor",
    "chronological_split",
    "DatasetDownloader",
]
