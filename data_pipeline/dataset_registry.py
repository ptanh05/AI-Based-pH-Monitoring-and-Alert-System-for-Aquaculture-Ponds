"""
Dataset Registry for AI Aquaculture Guardian.

Maintains metadata, provenance, licensing, and schema definitions
for real-world, sample, and synthetic aquaculture datasets.
"""

import os
from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class DatasetMetadata:
    """Metadata describing an aquaculture water-quality dataset."""
    name: str
    source: str
    doi: Optional[str] = None
    url: Optional[str] = None
    license: str = "CC BY 4.0"
    target_column: str = "ph"
    timestamp_column: str = "timestamp"
    sensor_columns: List[str] = field(default_factory=lambda: ["ph", "temperature", "dissolved_oxygen", "turbidity"])
    optional_sensors: List[str] = field(default_factory=lambda: ["salinity", "ammonia"])
    sampling_interval_seconds: float = 300.0  # default 5 minutes
    location: Optional[str] = None
    collection_period: Optional[str] = None
    description: str = ""
    default_path: Optional[str] = None


# Official Dataset Registries
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATASET_REGISTRY: Dict[str, DatasetMetadata] = {
    "mendeley_aquaculture": DatasetMetadata(
        name="mendeley_aquaculture",
        source="Mendeley Data",
        doi="10.17632/8s73jfvgr5.2",
        url="https://data.mendeley.com/datasets/8s73jfvgr5/2",
        license="Creative Commons Attribution 4.0 International (CC BY 4.0)",
        target_column="ph",
        timestamp_column="timestamp",
        sensor_columns=["ph", "temperature", "dissolved_oxygen", "turbidity"],
        optional_sensors=["salinity", "ammonia"],
        sampling_interval_seconds=300.0,
        location="Montería, Córdoba, Colombia",
        collection_period="January 1, 2024 – June 30, 2024",
        description="37,284 high-resolution IoT observations of pH, Temperature, DO, and Turbidity from Tilapia aquaculture ponds.",
        default_path=os.path.join(_BASE_DIR, "data", "real", "Data IoTMLCQ.xlsx"),
    ),
    "sample_aquaculture": DatasetMetadata(
        name="sample_aquaculture",
        source="AI Aquaculture Guardian Sample (Subset of Mendeley Dataset)",
        doi="10.17632/8s73jfvgr5.2",
        url="https://data.mendeley.com/datasets/8s73jfvgr5/2",
        license="Creative Commons Attribution 4.0 International (CC BY 4.0)",
        target_column="ph",
        timestamp_column="timestamp",
        sensor_columns=["ph", "temperature", "dissolved_oxygen", "turbidity"],
        optional_sensors=["salinity", "ammonia"],
        sampling_interval_seconds=300.0,
        location="Montería, Córdoba, Colombia",
        collection_period="January 2024",
        description="500-sample test slice for quick pipeline validation, continuous integration, and lightweight benchmarking.",
        default_path=os.path.join(_BASE_DIR, "data", "samples", "sample_aquaculture_data.csv"),
    ),
}


def get_dataset_metadata(name: str) -> Optional[DatasetMetadata]:
    """Retrieve metadata for a registered dataset by name."""
    return DATASET_REGISTRY.get(name.lower().strip())


def list_registered_datasets() -> List[str]:
    """List all registered dataset identifiers."""
    return list(DATASET_REGISTRY.keys())


def register_custom_dataset(metadata: DatasetMetadata) -> None:
    """Register or override a custom dataset metadata entry."""
    DATASET_REGISTRY[metadata.name.lower().strip()] = metadata
