"""
Universal Dataset Loader for AI Aquaculture Guardian.

Loads aquaculture datasets from local paths or registered names,
normalizes column headers into standard names, and prepares time-series DataFrames.
"""

import os
import re
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, Any

from data_pipeline.dataset_registry import (
    get_dataset_metadata,
    DatasetMetadata,
    DATASET_REGISTRY,
)


class DatasetLoader:
    """Universal aquaculture dataset loader and parser."""

    CANONICAL_COLUMN_MAPPINGS = {
        "ph": ["ph", "ph_value", "water_ph", "ph_level", "ph (ph)"],
        "temperature": ["temperature", "temp", "temperatura", "temperatura_scaled", "water_temp", "temp_c", "temperature (°c)"],
        "dissolved_oxygen": ["dissolved_oxygen", "do", "oxigeno", "oxigeno_scaled", "oxygen", "do_mg_l", "dissolved oxygen (mg/l)"],
        "turbidity": ["turbidity", "turbidez", "turb", "ntu", "turbidity (ntu)"],
        "salinity": ["salinity", "sal", "salinidad", "ppt", "salinity (ppt)"],
        "ammonia": ["ammonia", "nh3", "nh4", "amonio", "ammonia (mg/l)"],
        "timestamp": ["timestamp", "time", "datetime", "date_time", "fecha_hora", "fecha"],
    }

    def __init__(self):
        pass

    def load(
        self,
        name_or_path: str,
        max_rows: Optional[int] = None,
        physical_scale: bool = True,
    ) -> Tuple[pd.DataFrame, DatasetMetadata]:
        """
        Load dataset by registered name or explicit file path.

        Args:
            name_or_path: Registered dataset name or path to CSV/Excel file.
            max_rows: Optional limit on number of rows to load.
            physical_scale: Whether to scale normalized dataset columns to physical units.

        Returns:
            (DataFrame with standardized column names, DatasetMetadata)
        """
        # Check if registered dataset name
        meta = get_dataset_metadata(name_or_path)
        if meta and meta.default_path and os.path.exists(meta.default_path):
            file_path = meta.default_path
        else:
            file_path = name_or_path
            if not os.path.isabs(file_path):
                # Try relative to workspace
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                cand = os.path.join(base_dir, file_path)
                if os.path.exists(cand):
                    file_path = cand

            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Dataset file not found: {name_or_path} (resolved: {file_path})")

            meta = DatasetMetadata(
                name=os.path.splitext(os.path.basename(file_path))[0],
                source="Custom File Ingestion",
                license="User Specified",
                default_path=file_path,
            )

        # Ingest file based on extension
        ext = os.path.splitext(file_path)[1].lower()
        if ext in [".xlsx", ".xls"]:
            df = pd.read_excel(file_path, nrows=max_rows)
        elif ext in [".csv", ".txt"]:
            df = pd.read_csv(file_path, nrows=max_rows)
        elif ext in [".parquet"]:
            df = pd.read_parquet(file_path)
            if max_rows:
                df = df.iloc[:max_rows]
        else:
            raise ValueError(f"Unsupported dataset format: {ext}")

        # Standardize column headers
        df_norm = self._standardize_columns(df)

        # Parse or reconstruct timestamp column
        df_norm = self._ensure_timestamp(df_norm)

        # Scale normalized parameters if required
        if physical_scale:
            df_norm = self._apply_physical_scaling(df_norm, file_path)

        return df_norm, meta

    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Map heterogeneous column names to canonical schema without duplicates."""
        df_work = df.copy()

        # If explicit scaled versions exist (e.g. Mendeley dataset), prefer them
        if "temperatura_scaled" in df_work.columns and "temperatura" in df_work.columns:
            df_work = df_work.drop(columns=["temperatura"]).rename(columns={"temperatura_scaled": "temperature"})
        if "oxigeno_scaled" in df_work.columns and "oxigeno" in df_work.columns:
            df_work = df_work.drop(columns=["oxigeno"]).rename(columns={"oxigeno_scaled": "dissolved_oxygen"})

        col_map = {}
        assigned = set(df_work.columns)

        for col in df_work.columns:
            clean_col = str(col).strip().lower()
            for canonical, aliases in self.CANONICAL_COLUMN_MAPPINGS.items():
                if clean_col == canonical or clean_col in aliases:
                    if canonical not in col_map.values():
                        col_map[col] = canonical
                    break

        df_renamed = df_work.rename(columns=col_map)
        # Remove any remaining duplicate column names if any
        df_renamed = df_renamed.loc[:, ~df_renamed.columns.duplicated()]
        return df_renamed

    def _ensure_timestamp(self, df: pd.DataFrame) -> pd.DataFrame:
        """Ensure a valid datetime timestamp column exists."""
        df_work = df.copy()

        if "timestamp" in df_work.columns:
            df_work["timestamp"] = pd.to_datetime(df_work["timestamp"], errors="coerce")
            # If any are NaT, fill sequentially
            if df_work["timestamp"].isna().any():
                base_time = datetime(2024, 1, 1, 0, 0, 0)
                df_work["timestamp"] = [base_time + timedelta(minutes=5 * i) for i in range(len(df_work))]
            return df_work

        # If columns month, day, hour exist (like Mendeley IoT sheet)
        if all(c in df_work.columns for c in ["month", "day", "hour"]):
            base_year = 2024
            timestamps = []
            cur_time = datetime(base_year, 1, 1, 0, 0, 0)
            last_m, last_d, last_h = None, None, None
            intra_hour_count = 0

            for _, row in df_work.iterrows():
                try:
                    m = int(row["month"])
                    d = int(row["day"])
                    h = int(row["hour"])
                except Exception:
                    m, d, h = 1, 1, 0

                if (m, d, h) == (last_m, last_d, last_h):
                    intra_hour_count += 1
                else:
                    intra_hour_count = 0
                    last_m, last_d, last_h = m, d, h

                minute = min(59, intra_hour_count * 5)
                second = (intra_hour_count * 5 * 60) % 60
                try:
                    ts = datetime(base_year, m, d, h, minute, second)
                except ValueError:
                    ts = cur_time + timedelta(minutes=5)
                timestamps.append(ts)
                cur_time = ts

            df_work["timestamp"] = timestamps
            return df_work

        # Default fallback synthetic timestamps
        base_time = datetime(2024, 1, 1, 0, 0, 0)
        df_work["timestamp"] = [base_time + timedelta(minutes=5 * i) for i in range(len(df_work))]
        return df_work

    def _apply_physical_scaling(self, df: pd.DataFrame, file_path: str) -> pd.DataFrame:
        """Scale normalized columns (0-1) to realistic aquaculture ranges if needed."""
        df_scaled = df.copy()

        # If ph is normalized in [0, 1.5], map to aquaculture window [7.0, 8.5]
        if "ph" in df_scaled.columns:
            ph_series = df_scaled["ph"].dropna()
            if not ph_series.empty and ph_series.max() <= 2.0:
                df_scaled["ph"] = 7.0 + 1.5 * df_scaled["ph"]

        # If turbidity is normalized in [0, 2.0], map to NTU window [2.5, 7.5]
        if "turbidity" in df_scaled.columns:
            turb_series = df_scaled["turbidity"].dropna()
            if not turb_series.empty and turb_series.max() <= 2.0:
                df_scaled["turbidity"] = 2.5 + 5.0 * df_scaled["turbidity"]

        # If temperature is unscaled, check if scaled alternative exists
        if "temperatura_scaled" in df.columns:
            df_scaled["temperature"] = df["temperatura_scaled"]
        if "oxigeno_scaled" in df.columns:
            df_scaled["dissolved_oxygen"] = df["oxigeno_scaled"]

        return df_scaled
