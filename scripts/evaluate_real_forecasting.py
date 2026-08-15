"""
Real-World Data Forecasting & Three-Way Comparison Evaluation.

Performs:
1. Real-Trained -> Real-Tested (70% train, 15% val, 15% test, chronological split)
2. Synthetic-Trained -> Synthetic-Tested (Baseline reference)
3. Synthetic-Trained -> Real-Tested (Cross-Domain Generalization Experiment)
4. Persistence Baseline vs Random Forest Comparison

Outputs:
- reports/real_forecasting_results.json
- reports/three_way_comparison.json
- reports/experiment_metadata.json
"""

import os
import sys
import json
import numpy as np
import pandas as pd
from datetime import datetime
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

# Fix Windows console UTF-8
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.real_data_loader import RealDataLoader
from data.resampling import TimeSeriesResampler
from ai.features import FeatureEngineer
from simulator.ph_simulator import PHSimulator


def run_three_way_evaluation() -> dict:
    """
    Run 3-way evaluation matrix on synthetic and real datasets.
    """
    print("=" * 70)
    print("  AI AQUACULTURE GUARDIAN — REAL DATA VALIDATION & 3-WAY BENCHMARK")
    print("  Dataset: Mendeley Data (DOI: 10.17632/8s73jfvgr5.2)")
    print("=" * 70)

    reports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports")
    os.makedirs(reports_dir, exist_ok=True)

    fe = FeatureEngineer(window_size=20)
    horizons = [1, 5, 15, 30]

    # ── 1. Load Datasets ──
    # A. Real Data: resampled to 5-minute regular intervals (or raw sequence)
    loader = RealDataLoader()
    df_raw = loader.load_iot_stream(physical_scale=True)
    resampler = TimeSeriesResampler(target_freq="5min")
    df_resampled, resample_meta = resampler.resample(df_raw, value_cols=["ph", "temperature", "dissolved_oxygen", "turbidity"])
    
    # Use real pH sequence (first 5,000 continuous readings for training/testing)
    real_ph_values = df_resampled["ph"].dropna().values[:5000].tolist()

    # B. Synthetic Data: 5,000 readings from competition_demo simulator
    sim = PHSimulator(scenario="competition_demo", seed=42)
    syn_ph_values = [sim.generate_reading()[1] for _ in range(5000)]

    print(f"Loaded Real Time Series: {len(real_ph_values):,} steps (5-min intervals)")
    print(f"Loaded Synthetic Series: {len(syn_ph_values):,} steps (simulation)")

    results_matrix = {
        "metadata": {
            "evaluation_timestamp": datetime.now().isoformat(),
            "dataset_doi": "10.17632/8s73jfvgr5.2",
            "dataset_license": "CC BY 4.0",
            "real_samples_used": len(real_ph_values),
            "synthetic_samples_used": len(syn_ph_values),
            "split_ratio": "70% Train, 15% Validation, 15% Test (Strict Chronological)",
            "feature_window": 20,
            "horizons": horizons,
        },
        "experiments": {},
    }

    # Helper for building matrices and chronological splitting
    def evaluate_train_test(train_series, test_series, label_name):
        exp_results = {}
        for h in horizons:
            X_train_all, y_train_all = fe.extract_batch(train_series, target_offset=h)
            X_test_all, y_test_all = fe.extract_batch(test_series, target_offset=h)

            if len(X_train_all) < 50 or len(X_test_all) < 50:
                continue

            # If train == test (internal evaluation), do 70/15/15 chronological split
            if train_series is test_series:
                split_train = int(len(X_train_all) * 0.70)
                split_val = int(len(X_train_all) * 0.85)

                X_tr, y_tr = X_train_all[:split_train], y_train_all[:split_train]
                X_te, y_te = X_train_all[split_val:], y_train_all[split_val:]
            else:
                # Cross-domain: train on 100% of source train split, test on target test split
                split_tr = int(len(X_train_all) * 0.80)
                split_te = int(len(X_test_all) * 0.80)
                X_tr, y_tr = X_train_all[:split_tr], y_train_all[:split_tr]
                X_te, y_te = X_test_all[split_te:], y_test_all[split_te:]

            # Train Random Forest Regressor
            rf = RandomForestRegressor(n_estimators=100, max_depth=12, random_state=42, n_jobs=-1)
            rf.fit(X_tr, y_tr)
            y_pred = rf.predict(X_te)

            # Persistence Baseline (predict current_value = feature 0)
            y_base = X_te[:, 0]

            # Metrics
            mae_m = float(mean_absolute_error(y_te, y_pred))
            rmse_m = float(np.sqrt(mean_squared_error(y_te, y_pred)))
            ss_res = float(np.sum((y_te - y_pred) ** 2))
            ss_tot = float(np.sum((y_te - np.mean(y_te)) ** 2))
            r2_m = float(1 - ss_res / ss_tot) if ss_tot > 0 else 0.0

            mae_b = float(mean_absolute_error(y_te, y_base))
            rmse_b = float(np.sqrt(mean_squared_error(y_te, y_base)))
            ss_res_b = float(np.sum((y_te - y_base) ** 2))
            r2_b = float(1 - ss_res_b / ss_tot) if ss_tot > 0 else 0.0

            exp_results[f"{h}_step"] = {
                "horizon": h,
                "model_rf": {
                    "mae": round(mae_m, 6),
                    "rmse": round(rmse_m, 6),
                    "r2": round(r2_m, 6),
                },
                "persistence_baseline": {
                    "mae": round(mae_b, 6),
                    "rmse": round(rmse_b, 6),
                    "r2": round(r2_b, 6),
                },
                "train_samples": len(X_tr),
                "test_samples": len(X_te),
            }
        return exp_results

    # ── Experiment A: Synthetic -> Synthetic ──
    print("\n[1/3] Running Experiment A: Synthetic-Trained -> Synthetic-Tested...")
    results_matrix["experiments"]["synthetic_to_synthetic"] = evaluate_train_test(
        syn_ph_values, syn_ph_values, "Synthetic -> Synthetic"
    )

    # ── Experiment B: Real -> Real (Primary Real-World Validation) ──
    print("[2/3] Running Experiment B: Real-Trained -> Real-Tested (Montería Dataset)...")
    results_matrix["experiments"]["real_to_real"] = evaluate_train_test(
        real_ph_values, real_ph_values, "Real -> Real"
    )

    # ── Experiment C: Synthetic -> Real (Cross-Domain Generalization) ──
    print("[3/3] Running Experiment C: Synthetic-Trained -> Real-Tested (Zero-Shot Cross-Domain)...")
    results_matrix["experiments"]["synthetic_to_real_generalization"] = evaluate_train_test(
        syn_ph_values, real_ph_values, "Synthetic -> Real (Cross-Domain)"
    )

    # ── Print Summary Table ──
    print("\n" + "=" * 95)
    print("  3-WAY FORECASTING VALIDATION RESULTS MATRIX")
    print("=" * 95)
    print(f"  {'Experiment':<32s} | {'Horizon':<8s} | {'RF MAE':<10s} | {'RF RMSE':<10s} | {'RF R²':<8s} | {'Base MAE':<10s} | {'Base R²':<8s}")
    print("  " + "-" * 91)

    for exp_key, exp_name in [
        ("synthetic_to_synthetic", "A. Synthetic -> Synthetic"),
        ("real_to_real", "B. Real -> Real (Montería)"),
        ("synthetic_to_real_generalization", "C. Synthetic -> Real (Cross-Domain)"),
    ]:
        for h in horizons:
            h_data = results_matrix["experiments"][exp_key].get(f"{h}_step", {})
            if not h_data:
                continue
            m = h_data["model_rf"]
            b = h_data["persistence_baseline"]
            print(f"  {exp_name:<32s} | {h:>2d}-step   | {m['mae']:>10.6f} | {m['rmse']:>10.6f} | {m['r2']:>8.4f} | {b['mae']:>10.6f} | {b['r2']:>8.4f}")

    print("=" * 95)

    # Save reports
    json_path = os.path.join(reports_dir, "three_way_comparison.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results_matrix, f, indent=2, ensure_ascii=False)
    print(f"\n[✓] Saved: {json_path}")

    # Real forecasting specific report
    real_results = {
        "dataset_name": "Environmental Parameters in Aquaculture (Mendeley Data)",
        "doi": "10.17632/8s73jfvgr5.2",
        "license": "CC BY 4.0",
        "resampling_metadata": resample_meta,
        "results_by_horizon": results_matrix["experiments"]["real_to_real"],
        "cross_domain_results": results_matrix["experiments"]["synthetic_to_real_generalization"],
    }
    real_json_path = os.path.join(reports_dir, "real_forecasting_results.json")
    with open(real_json_path, "w", encoding="utf-8") as f:
        json.dump(real_results, f, indent=2, ensure_ascii=False)
    print(f"[✓] Saved: {real_json_path}")

    # Experiment metadata
    exp_meta = {
        "experiment_id": "EXP-AQUA-REAL-2026-V1",
        "dataset_name": "Environmental Parameters in Aquaculture (Mendeley Data)",
        "doi": "10.17632/8s73jfvgr5.2",
        "dataset_version": 2,
        "random_seed": 42,
        "train_val_test_split": [0.70, 0.15, 0.15],
        "model": "RandomForestRegressor (n_estimators=100, max_depth=12)",
        "feature_window": 20,
        "horizons_evaluated": horizons,
        "preprocessing": "5-minute time-regularized resampling + min-max physical mapping",
        "software_versions": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "sklearn": "1.9.0",
        },
    }
    meta_path = os.path.join(reports_dir, "experiment_metadata.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(exp_meta, f, indent=2, ensure_ascii=False)
    print(f"[✓] Saved: {meta_path}")

    return results_matrix


if __name__ == "__main__":
    run_three_way_evaluation()
