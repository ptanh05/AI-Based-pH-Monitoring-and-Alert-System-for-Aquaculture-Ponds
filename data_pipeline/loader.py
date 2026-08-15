"""
Loader module for data_pipeline package.
"""

from data_pipeline.dataset_loader import DatasetLoader
from data_pipeline.dataset_registry import (
    DatasetMetadata,
    DATASET_REGISTRY,
    get_dataset_metadata,
    list_registered_datasets,
)

__all__ = [
    "DatasetLoader",
    "DatasetMetadata",
    "DATASET_REGISTRY",
    "get_dataset_metadata",
    "list_registered_datasets",
]
