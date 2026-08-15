"""
Real-World Dataset Training and Multi-Model Benchmarking Script.

Trains and evaluates:
1. Persistence Baseline
2. Linear Regression
3. Random Forest Regressor
4. HistGradientBoosting Regressor

Usage:
  python scripts/train_real_dataset.py --dataset mendeley_aquaculture --horizons 1 5 15 30 --seed 42
  python scripts/train_real_dataset.py --path data/samples/sample_aquaculture_data.csv --seed 42
"""

import os
import sys
import json
import argparse
import joblib
import numpy as np
import pandas as pd
from datetime import datetime
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor
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
from data_pipeline.dataset_validator import DatasetValidator
from data_pipeline.preprocessing import DataPreprocessor
from data_pipeline.resampling import TimeSeriesResampler
from data_pipeline.feature_alignment import FeatureAligner
from data_pipeline.train_test_split import chronological_split


def parse_args():
    parser = argparse.ArgumentParser(description="Train and evaluate models on real aquaculture datasets.")
    parser.add_argument("--dataset", type=str, default="mendeley_aquaculture", help="Registered dataset name")
    parser.add_argument("--path", type=str, default=None, help="Explicit dataset file path (CSV/Excel)")
    parser.add_argument("--target", type=str, default="ph", help="Target column to forecast (default: ph)")
    parser.add_argument("--horizons", nargs="+", type=int, default=[1, 5, 15, 30], help="Forecast horizons in steps")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    parser.add_argument("--output_dir", type=str, default="artifacts", help="Root directory to save artifacts")
    return parser.parse_args()


def train_and_evaluate():
    args = parse_args()
    np.random.seed(args.seed)

    print("=" * 80)
    print("  AI AQUACULTURE GUARDIAN — REAL DATASET TRAINING PIPELINE")
    print(f"  Target: {args.target.upper()} | Seed: {args.seed} | Horizons: {args.horizons}")
    print("=" * 80)

    # 1. Ingest Data
    loader = DatasetLoader()
    source_target = args.path if args.path else args.dataset
    print(f"\n[1/6] Ingesting dataset: {source_target}...")
    df_raw, meta = loader.load(source_target, physical_scale=True)
    print(f"      Loaded {len(df_raw):,} raw records. Source: {meta.source} (License: {meta.license})")

    # 2. Validate Data Quality
    validator = DatasetValidator()
    print("[2/6] Running data quality audit & boundary verification...")
    val_report = validator.validate(df_raw, dataset_name=meta.name, target_col=args.target)
    print(f"      Valid for training: {val_report.is_valid_for_training}")
    print(f"      Sensors detected: {val_report.detected_sensors}")
    print(f"      Estimated sampling interval: {val_report.estimated_sampling_interval_seconds:.0f}s ({val_report.estimated_sampling_interval_seconds/60:.1f} min)")

    # 3. Clean & Resample
    preprocessor = DataPreprocessor(scaler_type="none")  # Keep original physical units for direct interpretation
    df_clean = preprocessor.clean_raw_data(df_raw)
    df_imputed = preprocessor.impute_missing(df_clean)

    resampler = TimeSeriesResampler(target_freq="5min")
    sensor_cols = [c for c in val_report.detected_sensors if c in df_imputed.columns]
    df_resampled, resample_meta = resampler.resample(df_imputed, value_cols=sensor_cols)
    print(f"      Resampled grid: {len(df_resampled):,} observations (Interpolated: {resample_meta['interpolated_pct']}%)")

    # 4. Create Artifact Directories
    models_dir = os.path.join(args.output_dir, "models")
    metrics_dir = os.path.join(args.output_dir, "metrics")
    reports_dir = os.path.join(args.output_dir, "reports")
    for d in [models_dir, metrics_dir, reports_dir]:
        os.makedirs(d, exist_ok=True)

    aligner = FeatureAligner(window_size=20)
    interval_min = val_report.estimated_sampling_interval_seconds / 60.0

    all_results = {
        "dataset_name": meta.name,
        "dataset_source": meta.source,
        "doi": meta.doi,
        "license": meta.license,
        "training_timestamp": datetime.now().isoformat(),
        "random_seed": args.seed,
        "sampling_interval_seconds": val_report.estimated_sampling_interval_seconds,
        "sampling_interval_minutes": interval_min,
        "validation_report": val_report.to_dict(),
        "resampling_metadata": resample_meta,
        "horizons_evaluated": {},
    }

    # 5. Train & Evaluate for each Horizon
    print("\n[3/6] Training & Benchmarking Models across Horizons...")
    print(f"  {'Horizon':<18s} | {'Model':<22s} | {'MAE':<10s} | {'RMSE':<10s} | {'R² Score':<10s} | {'Improvement vs Base':<20s}")
    print("  " + "-" * 98)

    for h in args.horizons:
        est_duration = int(h * interval_min)
        horizon_label = f"{h}-step ({est_duration} min)"

        # Construct Supervised Lag Matrix
        X_all, y_all, feat_names = aligner.build_supervised_dataset(
            df_resampled, target_col=args.target, horizon_steps=h
        )

        if len(X_all) < 50:
            print(f"      [!] Insufficient samples for horizon {h} (got {len(X_all)})")
            continue

        # Strict Chronological Split
        X_tr, X_val, X_te, split_meta = chronological_split(X_all, 0.70, 0.15, 0.15)
        y_tr, y_val, y_te, _ = chronological_split(y_all, 0.70, 0.15, 0.15)

        # Baseline: Persistence
        y_base = X_te[:, 0]
        mae_base = float(mean_absolute_error(y_te, y_base))
        rmse_base = float(np.sqrt(mean_squared_error(y_te, y_base)))
        r2_base = float(r2_score(y_te, y_base))

        # Models to train
        models = {
            "Persistence Baseline": None,
            "Linear Regression": LinearRegression(),
            "HistGradientBoosting": HistGradientBoostingRegressor(random_state=args.seed),
            "Random Forest": RandomForestRegressor(n_estimators=100, max_depth=12, random_state=args.seed, n_jobs=-1),
        }

        h_results = {
            "steps": h,
            "estimated_duration_minutes": est_duration,
            "split_info": split_meta,
            "baseline": {"mae": round(mae_base, 6), "rmse": round(rmse_base, 6), "r2": round(r2_base, 6)},
            "models": {},
        }

        best_model_name = "Persistence Baseline"
        best_mae = mae_base

        for m_name, model in models.items():
            if model is None:
                # Baseline
                mae_m, rmse_m, r2_m = mae_base, rmse_base, r2_base
            else:
                model.fit(X_tr, y_tr)
                y_pred = model.predict(X_te)
                mae_m = float(mean_absolute_error(y_te, y_pred))
                rmse_m = float(np.sqrt(mean_squared_error(y_te, y_pred)))
                r2_m = float(r2_score(y_te, y_pred))

                # Save best model to disk
                if mae_m < best_mae:
                    best_mae = mae_m
                    best_model_name = m_name

                # Persist RF model
                if m_name == "Random Forest":
                    model_file = os.path.join(models_dir, f"rf_{args.target}_{h}step.joblib")
                    joblib.dump(model, model_file)

            imprv = ((mae_base - mae_m) / max(1e-6, mae_base)) * 100.0 if mae_base > 0 else 0.0
            imprv_str = f"+{imprv:.2f}%" if imprv >= 0 else f"{imprv:.2f}%"

            h_results["models"][m_name] = {
                "mae": round(mae_m, 6),
                "rmse": round(rmse_m, 6),
                "r2": round(r2_m, 6),
                "improvement_vs_baseline_pct": round(imprv, 2),
            }

            print(f"  {horizon_label:<18s} | {m_name:<22s} | {mae_m:>10.6f} | {rmse_m:>10.6f} | {r2_m:>10.4f} | {imprv_str:>20s}")

        h_results["best_model"] = best_model_name
        all_results["horizons_evaluated"][f"{h}_step"] = h_results

    # 6. Save Run Metadata & Metrics
    print("\n[4/6] Saving trained models and validation metrics...")
    metrics_path = os.path.join(metrics_dir, "training_metrics.json")
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    print(f"      [✓] Saved: {metrics_path}")

    meta_run = {
        "run_id": f"RUN-AQUA-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "dataset_name": meta.name,
        "dataset_source": meta.source,
        "doi": meta.doi,
        "license": meta.license,
        "seed": args.seed,
        "target": args.target,
        "feature_window": 20,
        "feature_names": feat_names,
        "train_val_test_split": [0.70, 0.15, 0.15],
        "software": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "sklearn": "1.9.0",
        },
    }
    run_meta_path = os.path.join(args.output_dir, "run_metadata.json")
    with open(run_meta_path, "w", encoding="utf-8") as f:
        json.dump(meta_run, f, indent=2, ensure_ascii=False)
    print(f"      [✓] Saved: {run_meta_path}")

    # Generate Markdown Summary
    md_summary_path = os.path.join(reports_dir, "real_training_summary.md")
    _write_training_markdown(all_results, md_summary_path)
    print(f"      [✓] Saved: {md_summary_path}")

    print("=" * 80)
    print("  TRAINING & BENCHMARK COMPLETE — ALL MODELS PERSISTED")
    print("=" * 80)
    return all_results


def _write_training_markdown(results: dict, path: str):
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# Real Dataset Training & Benchmark Report\n\n")
        f.write(f"**Dataset**: {results['dataset_name']} ({results.get('doi', 'N/A')})\n")
        f.write(f"**License**: {results.get('license', 'N/A')}\n")
        f.write(f"**Timestamp**: {results['training_timestamp']}\n\n")
        f.write("| Horizon | Best Model | Model MAE | Base MAE | Improvement | Model $R^2$ |\n")
        f.write("|---|---|:---:|:---:|:---:|:---:|\n")
        for h_key, h_data in results["horizons_evaluated"].items():
            best_m = h_data["best_model"]
            m_stats = h_data["models"][best_m]
            b_stats = h_data["baseline"]
            imprv = m_stats["improvement_vs_baseline_pct"]
            imprv_str = f"+{imprv:.1f}%" if imprv >= 0 else f"{imprv:.1f}%"
            f.write(f"| **{h_data['steps']}-step ({h_data['estimated_duration_minutes']} min)** | {best_m} | {m_stats['mae']:.4f} | {b_stats['mae']:.4f} | **{imprv_str}** | {m_stats['r2']:.4f} |\n")


if __name__ == "__main__":
    train_and_evaluate()
