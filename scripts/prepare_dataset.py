"""
Dataset Preparation & Processing Script.

Cleans, regularizes to 5-minute sampling grids, extracts multivariate lag features,
and persists clean processed datasets into data/processed/.

Usage:
  python scripts/prepare_dataset.py --dataset mendeley_aquaculture
"""

import os
import sys
import argparse
import pandas as pd

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_pipeline.dataset_loader import DatasetLoader
from data_pipeline.dataset_validator import DatasetValidator
from data_pipeline.preprocessing import DataPreprocessor
from data_pipeline.resampling import TimeSeriesResampler
from data_pipeline.feature_adapter import MultivariateFeatureExtractor


def prepare_dataset(dataset_name: str = "mendeley_aquaculture", output_dir: str = "data/processed"):
    print("=" * 80)
    print("  AI AQUACULTURE GUARDIAN — DATASET PREPARATION PIPELINE")
    print(f"  Target: {dataset_name} -> {output_dir}")
    print("=" * 80)

    # 1. Load Raw
    loader = DatasetLoader()
    df_raw, meta = loader.load(dataset_name, physical_scale=True)
    print(f"[1/4] Loaded raw dataset: {len(df_raw):,} records.")

    # 2. Clean & Preprocess
    pre = DataPreprocessor()
    df_clean = pre.clean_raw_data(df_raw, clamp_physical=True)
    df_imputed = pre.impute_missing(df_clean)
    print(f"[2/4] Cleaned & imputed: {len(df_imputed):,} records.")

    # 3. Resample to Regular 5min Grid
    resampler = TimeSeriesResampler(target_freq="5min")
    sensor_cols = [c for c in ["ph", "temperature", "dissolved_oxygen", "turbidity", "salinity"] if c in df_imputed.columns]
    df_resampled, resample_meta = resampler.resample(df_imputed, value_cols=sensor_cols)
    print(f"[3/4] Regularized 5-minute grid: {len(df_resampled):,} observations.")

    # 4. Save Processed Artifacts
    os.makedirs(output_dir, exist_ok=True)
    clean_csv_path = os.path.join(output_dir, f"{dataset_name}_clean_5min.csv")
    df_resampled.to_csv(clean_csv_path, index=False)
    print(f"[4/4] Saved regularized dataset: {clean_csv_path}")

    # Build supervised feature matrix sample
    extractor = MultivariateFeatureExtractor(window_size=20)
    X, y, feat_names = extractor.build_supervised_dataset(df_resampled, target_col="ph", horizon_steps=1)
    print(f"      Supervised lag matrix: Shape {X.shape} ({len(feat_names)} features)")

    print("=" * 80)
    print("  PREPARATION COMPLETE")
    print("=" * 80)
    return clean_csv_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=str, default="mendeley_aquaculture")
    parser.add_argument("--output_dir", type=str, default="data/processed")
    args = parser.parse_args()
    prepare_dataset(args.dataset, args.output_dir)
