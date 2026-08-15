"""
Dataset Validator for AI Aquaculture Guardian.

Performs schema verification, physical boundary validation,
duplicate detection, missingness analysis, and statistical outlier auditing.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class ValidationReport:
    """Detailed audit report for a time-series dataset."""
    dataset_name: str
    total_raw_rows: int
    clean_rows: int
    duplicate_timestamps: int
    missing_values_by_col: Dict[str, int]
    missing_pct_by_col: Dict[str, float]
    physical_violations_by_col: Dict[str, int]
    outliers_iqr_by_col: Dict[str, int]
    detected_sensors: List[str]
    time_start: Optional[str]
    time_end: Optional[str]
    estimated_sampling_interval_seconds: float
    is_valid_for_training: bool
    issues: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class DatasetValidator:
    """Validates raw and processed aquaculture datasets."""

    PHYSICAL_BOUNDS = {
        "ph": (0.0, 14.0),
        "temperature": (0.0, 50.0),
        "dissolved_oxygen": (0.0, 25.0),
        "turbidity": (0.0, 1000.0),
        "salinity": (0.0, 50.0),
        "ammonia": (0.0, 100.0),
    }

    def validate(
        self,
        df: pd.DataFrame,
        dataset_name: str = "aquaculture_data",
        timestamp_col: str = "timestamp",
        target_col: str = "ph",
    ) -> ValidationReport:
        """
        Run complete data quality validation suite on DataFrame.
        """
        issues: List[str] = []
        raw_count = len(df)

        if df.empty:
            return ValidationReport(
                dataset_name=dataset_name,
                total_raw_rows=0,
                clean_rows=0,
                duplicate_timestamps=0,
                missing_values_by_col={},
                missing_pct_by_col={},
                physical_violations_by_col={},
                outliers_iqr_by_col={},
                detected_sensors=[],
                time_start=None,
                time_end=None,
                estimated_sampling_interval_seconds=0.0,
                is_valid_for_training=False,
                issues=["Dataset is empty"],
            )

        # 1. Detect Available Sensors
        detected_sensors = [c for c in self.PHYSICAL_BOUNDS.keys() if c in df.columns]
        if target_col not in df.columns:
            issues.append(f"Target column '{target_col}' not found in dataset columns: {list(df.columns)}")

        # 2. Timestamp Checks
        dup_count = 0
        time_start, time_end = None, None
        sampling_interval = 300.0

        if timestamp_col in df.columns:
            ts_series = pd.to_datetime(df[timestamp_col], errors="coerce")
            dup_count = int(ts_series.duplicated().sum())
            if dup_count > 0:
                issues.append(f"Found {dup_count} duplicate timestamps.")

            valid_ts = ts_series.dropna().sort_values()
            if not valid_ts.empty:
                time_start = valid_ts.iloc[0].isoformat()
                time_end = valid_ts.iloc[-1].isoformat()
                if len(valid_ts) > 1:
                    diffs = valid_ts.diff().dropna().dt.total_seconds()
                    median_diff = float(diffs.median())
                    if median_diff > 0:
                        sampling_interval = median_diff

        # 3. Missing Value Analysis
        missing_counts = {}
        missing_pcts = {}
        for col in df.columns.unique():
            col_series = df[col]
            if isinstance(col_series, pd.DataFrame):
                col_series = col_series.iloc[:, 0]
            m_count = int(col_series.isna().sum())
            missing_counts[str(col)] = m_count
            missing_pcts[str(col)] = round(float(m_count / raw_count * 100), 2)
            if missing_pcts[str(col)] > 30.0 and str(col) in detected_sensors:
                issues.append(f"Sensor '{col}' has {missing_pcts[str(col)]}% missing values (> 30%).")

        # 4. Physical Boundaries & Outliers
        violations = {}
        outliers_iqr = {}

        for sensor in detected_sensors:
            s_data = pd.to_numeric(df[sensor], errors="coerce").dropna()
            low, high = self.PHYSICAL_BOUNDS[sensor]

            # Range violations
            v_count = int(((s_data < low) | (s_data > high)).sum())
            violations[sensor] = v_count
            if v_count > 0:
                issues.append(f"Sensor '{sensor}' has {v_count} readings violating physical range [{low}, {high}].")

            # Statistical IQR Outliers
            if len(s_data) >= 10:
                q25, q75 = np.percentile(s_data, [25, 75])
                iqr = q75 - q25
                iqr_low = q25 - 3.0 * iqr
                iqr_high = q75 + 3.0 * iqr
                out_count = int(((s_data < iqr_low) | (s_data > iqr_high)).sum())
                outliers_iqr[sensor] = out_count
            else:
                outliers_iqr[sensor] = 0

        # Overall validity
        is_valid = (
            raw_count >= 50
            and target_col in df.columns
            and missing_pcts.get(target_col, 100.0) < 20.0
            and violations.get(target_col, 0) == 0
        )

        return ValidationReport(
            dataset_name=dataset_name,
            total_raw_rows=raw_count,
            clean_rows=raw_count - dup_count,
            duplicate_timestamps=dup_count,
            missing_values_by_col=missing_counts,
            missing_pct_by_col=missing_pcts,
            physical_violations_by_col=violations,
            outliers_iqr_by_col=outliers_iqr,
            detected_sensors=detected_sensors,
            time_start=time_start,
            time_end=time_end,
            estimated_sampling_interval_seconds=sampling_interval,
            is_valid_for_training=is_valid,
            issues=issues,
        )
