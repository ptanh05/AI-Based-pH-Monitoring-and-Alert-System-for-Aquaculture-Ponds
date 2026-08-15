"""
Chronological Train/Validation/Test Splitter for AI Aquaculture Guardian.

Guarantees 100% leak-free temporal splitting with zero shuffling.
"""

import numpy as np
import pandas as pd
from typing import Tuple, Dict, Any, Union


def chronological_split(
    data: Union[pd.DataFrame, np.ndarray],
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
) -> Tuple[Any, Any, Any, Dict[str, Any]]:
    """
    Split time series or feature matrix strictly in chronological order without shuffling.

    Args:
        data: DataFrame or NumPy array.
        train_ratio: Fraction of earliest data for training (e.g. 0.70).
        val_ratio: Fraction for validation (e.g. 0.15).
        test_ratio: Fraction for final holdout testing (e.g. 0.15).

    Returns:
        (train_data, val_data, test_data, metadata_dict)
    """
    total_len = len(data)
    if total_len == 0:
        raise ValueError("Cannot split empty dataset.")

    # Normalize ratios
    total_ratio = train_ratio + val_ratio + test_ratio
    train_ratio /= total_ratio
    val_ratio /= total_ratio
    test_ratio /= total_ratio

    train_end = int(total_len * train_ratio)
    val_end = int(total_len * (train_ratio + val_ratio))

    if isinstance(data, pd.DataFrame):
        train = data.iloc[:train_end].copy().reset_index(drop=True)
        val = data.iloc[train_end:val_end].copy().reset_index(drop=True)
        test = data.iloc[val_end:].copy().reset_index(drop=True)
    else:
        train = data[:train_end]
        val = data[train_end:val_end]
        test = data[val_end:]

    meta = {
        "total_samples": total_len,
        "train_samples": len(train),
        "val_samples": len(val),
        "test_samples": len(test),
        "train_ratio": round(train_ratio, 4),
        "val_ratio": round(val_ratio, 4),
        "test_ratio": round(test_ratio, 4),
        "split_strategy": "STRICT_CHRONOLOGICAL_NO_SHUFFLE",
    }

    return train, val, test, meta
