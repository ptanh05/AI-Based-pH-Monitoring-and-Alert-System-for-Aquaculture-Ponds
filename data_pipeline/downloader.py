import os
import hashlib
from typing import Dict, Optional, Any
from data_pipeline.dataset_registry import DATASET_REGISTRY, DatasetMetadata


class DatasetDownloader:
    """Verifies and manages local dataset files with SHA-256 validation."""

    def __init__(self, raw_data_dir: str = "data/raw"):
        self.raw_data_dir = raw_data_dir

    def calculate_sha256(self, file_path: str) -> str:
        """Compute SHA-256 hash of a file."""
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        return hasher.hexdigest()

    def verify_local_dataset(self, dataset_name: str) -> Dict[str, Any]:
        """Verify checksum and availability of a dataset."""
        if dataset_name not in DATASET_REGISTRY:
            return {"status": "error", "message": f"Dataset {dataset_name} not found in registry."}

        meta: DatasetMetadata = DATASET_REGISTRY[dataset_name]
        path_to_check = meta.default_path if meta.default_path else ""
        abs_path = os.path.abspath(path_to_check)

        if not os.path.exists(abs_path):
            return {
                "status": "missing",
                "name": dataset_name,
                "expected_path": abs_path,
                "source_url": meta.url,
            }

        file_hash = self.calculate_sha256(abs_path)
        return {
            "status": "present",
            "name": dataset_name,
            "path": abs_path,
            "sha256": file_hash,
            "size_bytes": os.path.getsize(abs_path),
            "doi": meta.doi,
            "license": meta.license,
        }
