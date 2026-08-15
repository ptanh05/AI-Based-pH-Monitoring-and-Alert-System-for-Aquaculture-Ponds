"""
Data Preprocessing and Scaler Pipeline for AI Aquaculture Guardian.

Handles sorting, deduplication, physical bound clamping,
missing value imputation, and strictly train-only scaling.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from sklearn.preprocessing import StandardScaler, MinMaxScaler


class DataPreprocessor:
    """Cleans time series and applies leak-free feature scaling."""

    PHYSICAL_BOUNDS = {
        "ph": (0.0, 14.0),
        "temperature": (0.0, 50.0),
        "dissolved_oxygen": (0.0, 25.0),
        "turbidity": (0.0, 1000.0),
        "salinity": (0.0, 50.0),
        "ammonia": (0.0, 100.0),
    }

    def __init__(self, scaler_type: str = "standard"):
        """
        Args:
            scaler_type: 'standard', 'minmax', or 'none'.
        """
        self.scaler_type = scaler_type
        self.scalers: Dict[str, Any] = {}
        self.is_fitted = False

    def clean_raw_data(
        self,
        df: pd.DataFrame,
        timestamp_col: str = "timestamp",
        drop_duplicates: bool = True,
        clamp_physical: bool = True,
    ) -> pd.DataFrame:
        """
        Sort chronologically, deduplicate, and clamp physically impossible values.
        """
        if df.empty:
            return df.copy()

        df_clean = df.copy()

        # 1. Parse & Sort by Timestamp
        if timestamp_col in df_clean.columns:
            df_clean[timestamp_col] = pd.to_datetime(df_clean[timestamp_col], errors="coerce")
            df_clean = df_clean.dropna(subset=[timestamp_col])
            df_clean = df_clean.sort_values(timestamp_col).reset_index(drop=True)

            # 2. Deduplicate timestamps
            if drop_duplicates:
                df_clean = df_clean.drop_duplicates(subset=[timestamp_col], keep="first").reset_index(drop=True)

        # 3. Clamp physical bounds
        if clamp_physical:
            for col, (low, high) in self.PHYSICAL_BOUNDS.items():
                if col in df_clean.columns and pd.api.types.is_numeric_dtype(df_clean[col]):
                    df_clean[col] = df_clean[col].clip(lower=low, upper=high)

        return df_clean

    def impute_missing(
        self,
        df: pd.DataFrame,
        numeric_cols: Optional[List[str]] = None,
        method: str = "time",
        max_gap: int = 12,
    ) -> pd.DataFrame:
        """
        Impute missing values using forward fill and interpolation.
        """
        if df.empty:
            return df.copy()

        df_imputed = df.copy()
        if numeric_cols is None:
            numeric_cols = [c for c in df_imputed.columns if c != "timestamp" and pd.api.types.is_numeric_dtype(df_imputed[c])]

        for col in numeric_cols:
            if col in df_imputed.columns:
                # First interpolate short gaps
                df_imputed[col] = df_imputed[col].interpolate(
                    method="linear", limit=max_gap, limit_direction="both"
                )
                # Forward fill / backward fill any residual boundary NaNs
                df_imputed[col] = df_imputed[col].ffill().bfill()

        return df_imputed

    def fit_scalers(self, train_df: pd.DataFrame, cols_to_scale: List[str]) -> None:
        """
        Fit normalization scalers STRICTLY on training split to prevent data leakage.
        """
        self.scalers = {}
        for col in cols_to_scale:
            if col in train_df.columns:
                vals = train_df[col].dropna().values.reshape(-1, 1)
                if len(vals) > 0:
                    if self.scaler_type == "standard":
                        scaler = StandardScaler()
                    elif self.scaler_type == "minmax":
                        scaler = MinMaxScaler()
                    else:
                        continue
                    scaler.fit(vals)
                    self.scalers[col] = scaler
        self.is_fitted = True

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Transform DataFrame using previously fitted scalers.
        """
        if not self.is_fitted or not self.scalers:
            return df.copy()

        df_out = df.copy()
        for col, scaler in self.scalers.items():
            if col in df_out.columns:
                vals = df_out[col].values.reshape(-1, 1)
                df_out[col] = scaler.transform(vals).flatten()
        return df_out

    def inverse_transform_column(self, col: str, values: np.ndarray) -> np.ndarray:
        """Inverse transform model predictions back to original physical scale."""
        if col in self.scalers:
            return self.scalers[col].inverse_transform(values.reshape(-1, 1)).flatten()
        return values
