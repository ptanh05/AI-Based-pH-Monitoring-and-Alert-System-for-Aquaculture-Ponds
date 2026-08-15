"""
Config-Driven Real Model Training Script.

Trains multi-step forecasting models according to configs/real_data.yaml
and persists versioned model artifacts to models/real/.

Usage:
  python scripts/train_real_model.py --config configs/real_data.yaml
"""

import os
import sys
import yaml
import json
import joblib
import argparse
import numpy as np
import pandas as pd
from datetime import datetime
from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Fix Windows console UTF-8
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_pipeline.dataset_loader import DatasetLoader
from data_pipeline.resampling import TimeSeriesResampler
from data_pipeline.feature_adapter import MultivariateFeatureExtractor
from data_pipeline.train_test_split import chronological_split


def train_models_from_config(config_path: str = "configs/real_data.yaml"):
    print("=" * 80)
    print("  AI AQUACULTURE GUARDIAN — REAL MODEL TRAINING PIPELINE")
    print(f"  Configuration: {config_path}")
    print("=" * 80)

    # 1. Load Config
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    dataset_name = cfg["dataset"]["name"]
    target_col = cfg["dataset"]["target_column"]
    horizons = cfg["horizons"]
    version = cfg["output"].get("version", "v2.0")
    model_dir = cfg["output"]["model_dir"]
    os.makedirs(model_dir, exist_ok=True)

    # 2. Ingest & Resample
    loader = DatasetLoader()
    df_raw, meta = loader.load(dataset_name, physical_scale=True)
    resampler = TimeSeriesResampler(target_freq=cfg["dataset"]["sampling_frequency"])
    sensor_cols = [c for c in ["ph", "temperature", "dissolved_oxygen", "turbidity"] if c in df_raw.columns]
    df_grid, _ = resampler.resample(df_raw, value_cols=sensor_cols)

    extractor = MultivariateFeatureExtractor(window_size=cfg["features"]["window_size"])
    include_multi = cfg["features"].get("include_multisensor", True)

    training_metadata = {
        "model_version": version,
        "trained_at": datetime.now().isoformat(),
        "config_path": config_path,
        "dataset_name": dataset_name,
        "dataset_doi": meta.doi,
        "dataset_license": meta.license,
        "features": {
            "window_size": cfg["features"]["window_size"],
            "multisensor": include_multi,
        },
        "horizons": {},
    }

    print(f"\n[1/3] Training Models across {len(horizons)} Horizons ({horizons})...")
    print(f"  {'Horizon':<18s} | {'Model':<20s} | {'MAE':<10s} | {'RMSE':<10s} | {'R²':<10s}")
    print("  " + "-" * 75)

    for h in horizons:
        est_min = h * 5
        horizon_key = f"{h}_step"
        X_all, y_all, feat_names = extractor.build_supervised_dataset(
            df_grid, target_col=target_col, horizon_steps=h, include_multisensor=include_multi
        )

        tr_r = cfg["split"]["train_ratio"]
        val_r = cfg["split"]["val_ratio"]
        te_r = cfg["split"]["test_ratio"]

        X_tr, X_val, X_te, split_info = chronological_split(X_all, tr_r, val_r, te_r)
        y_tr, y_val, y_te, _ = chronological_split(y_all, tr_r, val_r, te_r)

        # Baseline
        y_base = X_te[:, 0]
        mae_b = float(mean_absolute_error(y_te, y_base))
        rmse_b = float(np.sqrt(mean_squared_error(y_te, y_base)))
        r2_b = float(r2_score(y_te, y_base))

        # Random Forest
        rf_params = cfg["models"]["random_forest"]
        rf = RandomForestRegressor(**rf_params)
        rf.fit(X_tr, y_tr)
        y_pred_rf = rf.predict(X_te)

        mae_rf = float(mean_absolute_error(y_te, y_pred_rf))
        rmse_rf = float(np.sqrt(mean_squared_error(y_te, y_pred_rf)))
        r2_rf = float(r2_score(y_te, y_pred_rf))

        # Save model artifact
        model_filename = f"rf_{target_col}_h{h}_{version}.joblib"
        model_path = os.path.join(model_dir, model_filename)
        joblib.dump(rf, model_path)

        print(f"  {h:>2d}-step ({est_min:>3d} min)   | {'Persistence Base':<20s} | {mae_b:>10.6f} | {rmse_b:>10.6f} | {r2_b:>10.4f}")
        print(f"  {h:>2d}-step ({est_min:>3d} min)   | {'Random Forest':<20s} | {mae_rf:>10.6f} | {rmse_rf:>10.6f} | {r2_rf:>10.4f}")
        print("  " + "-" * 75)

        training_metadata["horizons"][horizon_key] = {
            "steps": h,
            "advance_minutes": est_min,
            "model_file": model_filename,
            "baseline": {"mae": round(mae_b, 6), "rmse": round(rmse_b, 6), "r2": round(r2_b, 6)},
            "random_forest": {"mae": round(mae_rf, 6), "rmse": round(rmse_rf, 6), "r2": round(r2_rf, 6)},
            "feature_names": feat_names,
            "feature_importances": [round(float(x), 5) for x in rf.feature_importances_],
        }

    # 3. Save Metadata
    meta_path = os.path.join(model_dir, f"model_metadata_{version}.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(training_metadata, f, indent=2, ensure_ascii=False)

    print(f"\n[2/3] [✓] Saved model artifacts to: {model_dir}")
    print(f"[3/3] [✓] Saved model metadata:   {meta_path}")
    print("=" * 80)
    return training_metadata


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="configs/real_data.yaml")
    args = parser.parse_args()
    train_models_from_config(args.config)
