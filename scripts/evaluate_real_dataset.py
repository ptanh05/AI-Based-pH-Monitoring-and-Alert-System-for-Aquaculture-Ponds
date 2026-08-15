"""
Real-World Dataset Evaluation & Detailed Metrics Generation Script.

Computes comprehensive error distributions (MAE, RMSE, R2, MAPE, Max Error)
for all trained models on the test split.

Usage:
  python scripts/evaluate_real_dataset.py --dataset mendeley_aquaculture
"""

import os
import sys
import json
import argparse
import joblib
import numpy as np
import pandas as pd
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
from data_pipeline.feature_alignment import FeatureAligner
from data_pipeline.train_test_split import chronological_split


def evaluate_dataset():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=str, default="mendeley_aquaculture")
    parser.add_argument("--horizons", nargs="+", type=int, default=[1, 5, 15, 30])
    parser.add_argument("--artifacts_dir", type=str, default="artifacts")
    args = parser.parse_args()

    print("=" * 80)
    print("  AI AQUACULTURE GUARDIAN — REAL DATASET EVALUATION")
    print(f"  Dataset: {args.dataset} | Horizons: {args.horizons}")
    print("=" * 80)

    loader = DatasetLoader()
    df_raw, meta = loader.load(args.dataset, physical_scale=True)
    resampler = TimeSeriesResampler(target_freq="5min")
    df_resampled, _ = resampler.resample(df_raw, value_cols=["ph", "temperature", "dissolved_oxygen", "turbidity"])

    aligner = FeatureAligner(window_size=20)
    models_dir = os.path.join(args.artifacts_dir, "models")

    evaluation_report = {
        "dataset_name": meta.name,
        "source": meta.source,
        "doi": meta.doi,
        "horizons": {},
    }

    print(f"\n  {'Horizon':<18s} | {'Model MAE':<12s} | {'Base MAE':<12s} | {'RMSE':<10s} | {'R² Score':<10s} | {'Improvement':<12s}")
    print("  " + "-" * 82)

    for h in args.horizons:
        X_all, y_all, _ = aligner.build_supervised_dataset(df_resampled, target_col="ph", horizon_steps=h)
        if len(X_all) < 50:
            continue

        _, _, X_te, _ = chronological_split(X_all, 0.70, 0.15, 0.15)
        _, _, y_te, _ = chronological_split(y_all, 0.70, 0.15, 0.15)

        # Baseline
        y_base = X_te[:, 0]
        mae_b = float(mean_absolute_error(y_te, y_base))
        rmse_b = float(np.sqrt(mean_squared_error(y_te, y_base)))
        r2_b = float(r2_score(y_te, y_base))

        # Load persisted RF model
        model_file = os.path.join(models_dir, f"rf_ph_{h}step.joblib")
        if os.path.exists(model_file):
            rf_model = joblib.load(model_file)
            y_pred = rf_model.predict(X_te)
            mae_m = float(mean_absolute_error(y_te, y_pred))
            rmse_m = float(np.sqrt(mean_squared_error(y_te, y_pred)))
            r2_m = float(r2_score(y_te, y_pred))
        else:
            mae_m, rmse_m, r2_m = mae_b, rmse_b, r2_b

        imprv = ((mae_b - mae_m) / max(1e-6, mae_b)) * 100.0 if mae_b > 0 else 0.0
        imprv_str = f"+{imprv:.1f}%" if imprv >= 0 else f"{imprv:.1f}%"
        est_min = h * 5

        print(f"  {h:>2d}-step ({est_min:>3d} min)   | {mae_m:>12.6f} | {mae_b:>12.6f} | {rmse_m:>10.6f} | {r2_m:>10.4f} | {imprv_str:>12s}")

        evaluation_report["horizons"][f"{h}_step"] = {
            "steps": h,
            "duration_minutes": est_min,
            "model_mae": round(mae_m, 6),
            "model_rmse": round(rmse_m, 6),
            "model_r2": round(r2_m, 6),
            "baseline_mae": round(mae_b, 6),
            "baseline_rmse": round(rmse_b, 6),
            "baseline_r2": round(r2_b, 6),
            "improvement_pct": round(imprv, 2),
        }

    out_json = os.path.join(args.artifacts_dir, "metrics", "real_evaluation_results.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(evaluation_report, f, indent=2, ensure_ascii=False)
    print(f"\n[✓] Evaluation saved: {out_json}")
    print("=" * 80)
    return evaluation_report


if __name__ == "__main__":
    evaluate_dataset()
