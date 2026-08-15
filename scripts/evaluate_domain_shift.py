"""
Domain Shift & Cross-Dataset Generalization Evaluation Script.

Evaluates:
1. In-Domain Real: Real Train -> Real Test
2. In-Domain Synthetic: Synthetic Train -> Synthetic Test
3. Cross-Domain Transfer: Synthetic Train -> Real Test (Zero-Shot Generalization)
4. Cross-Domain Transfer: Real Train -> Synthetic Test

Outputs:
- artifacts/metrics/domain_shift_metrics.json
- artifacts/reports/domain_shift_report.md
"""

import os
import sys
import json
import argparse
import numpy as np
import pandas as pd
from datetime import datetime
from sklearn.ensemble import RandomForestRegressor
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
from simulator.ph_simulator import PHSimulator


def evaluate_domain_shift(artifacts_dir: str = "artifacts", seed: int = 42):
    print("=" * 85)
    print("  AI AQUACULTURE GUARDIAN — DOMAIN SHIFT & GENERALIZATION ANALYSIS")
    print("=" * 85)

    # 1. Load Real Dataset
    loader = DatasetLoader()
    df_real_raw, _ = loader.load("mendeley_aquaculture", physical_scale=True)
    resampler = TimeSeriesResampler(target_freq="5min")
    df_real, _ = resampler.resample(df_real_raw, value_cols=["ph", "temperature", "dissolved_oxygen", "turbidity"])

    # 2. Generate Synthetic Dataset
    sim = PHSimulator(scenario="competition_demo", seed=seed)
    syn_ph = [sim.generate_reading()[1] for _ in range(5000)]
    df_syn = pd.DataFrame({
        "timestamp": pd.date_range("2024-01-01", periods=5000, freq="5min"),
        "ph": syn_ph,
    })

    aligner = FeatureAligner(window_size=20)
    horizons = [1, 5, 15, 30]

    domain_report = {
        "timestamp": datetime.now().isoformat(),
        "seed": seed,
        "experiments": {},
    }

    print(f"\n  {'Experiment' :<35s} | {'Horizon':<8s} | {'MAE':<10s} | {'RMSE':<10s} | {'R² Score':<10s}")
    print("  " + "-" * 81)

    for h in horizons:
        # Build Real X, y
        X_real_all, y_real_all, _ = aligner.build_supervised_dataset(df_real, target_col="ph", horizon_steps=h)
        X_r_tr, _, X_r_te, _ = chronological_split(X_real_all, 0.70, 0.15, 0.15)
        y_r_tr, _, y_r_te, _ = chronological_split(y_real_all, 0.70, 0.15, 0.15)

        # Build Synthetic X, y
        X_syn_all, y_syn_all, _ = aligner.build_supervised_dataset(df_syn, target_col="ph", horizon_steps=h)
        X_s_tr, _, X_s_te, _ = chronological_split(X_syn_all, 0.70, 0.15, 0.15)
        y_s_tr, _, y_s_te, _ = chronological_split(y_syn_all, 0.70, 0.15, 0.15)

        # Train Models (use 13 core features common to both)
        rf_real = RandomForestRegressor(n_estimators=50, max_depth=10, random_state=seed, n_jobs=-1)
        rf_real.fit(X_r_tr[:, :13], y_r_tr)

        rf_syn = RandomForestRegressor(n_estimators=50, max_depth=10, random_state=seed, n_jobs=-1)
        rf_syn.fit(X_s_tr[:, :13], y_s_tr)

        # 1. In-Domain Real (Real -> Real)
        y_pred_rr = rf_real.predict(X_r_te[:, :13])
        mae_rr, rmse_rr, r2_rr = float(mean_absolute_error(y_r_te, y_pred_rr)), float(np.sqrt(mean_squared_error(y_r_te, y_pred_rr))), float(r2_score(y_r_te, y_pred_rr))

        # 2. In-Domain Synthetic (Synthetic -> Synthetic)
        y_pred_ss = rf_syn.predict(X_s_te[:, :13])
        mae_ss, rmse_ss, r2_ss = float(mean_absolute_error(y_s_te, y_pred_ss)), float(np.sqrt(mean_squared_error(y_s_te, y_pred_ss))), float(r2_score(y_s_te, y_pred_ss))

        # 3. Cross-Domain (Synthetic -> Real)
        y_pred_sr = rf_syn.predict(X_r_te[:, :13])
        mae_sr, rmse_sr, r2_sr = float(mean_absolute_error(y_r_te, y_pred_sr)), float(np.sqrt(mean_squared_error(y_r_te, y_pred_sr))), float(r2_score(y_r_te, y_pred_sr))

        domain_report["experiments"][f"{h}_step"] = {
            "real_to_real": {"mae": round(mae_rr, 6), "rmse": round(rmse_rr, 6), "r2": round(r2_rr, 6)},
            "syn_to_syn": {"mae": round(mae_ss, 6), "rmse": round(rmse_ss, 6), "r2": round(r2_ss, 6)},
            "syn_to_real_transfer": {"mae": round(mae_sr, 6), "rmse": round(rmse_sr, 6), "r2": round(r2_sr, 6)},
            "performance_degradation_pct": round(((mae_sr - mae_rr) / max(1e-6, mae_rr)) * 100.0, 2),
        }

        print(f"  {'A. Real -> Real (In-Domain)' :<35s} | {h:>2d}-step   | {mae_rr:>10.6f} | {rmse_rr:>10.6f} | {r2_rr:>10.4f}")
        print(f"  {'B. Synthetic -> Synthetic (In-Domain)' :<35s} | {h:>2d}-step   | {mae_ss:>10.6f} | {rmse_ss:>10.6f} | {r2_ss:>10.4f}")
        print(f"  {'C. Synthetic -> Real (Transfer)' :<35s} | {h:>2d}-step   | {mae_sr:>10.6f} | {rmse_sr:>10.6f} | {r2_sr:>10.4f}")
        print("  " + "-" * 81)

    # Save JSON & Markdown
    metrics_dir = os.path.join(artifacts_dir, "metrics")
    reports_dir = os.path.join(artifacts_dir, "reports")
    os.makedirs(metrics_dir, exist_ok=True)
    os.makedirs(reports_dir, exist_ok=True)

    out_json = os.path.join(metrics_dir, "domain_shift_metrics.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(domain_report, f, indent=2, ensure_ascii=False)
    print(f"\n[✓] Saved domain shift metrics: {out_json}")

    out_md = os.path.join(reports_dir, "domain_shift_report.md")
    with open(out_md, "w", encoding="utf-8") as f:
        f.write("# Domain Shift and Cross-Dataset Generalization Analysis\n\n")
        f.write("Evaluates in-domain vs. zero-shot cross-domain model transfer.\n\n")
        f.write("| Horizon | Real $\\to$ Real MAE ($R^2$) | Synthetic $\\to$ Synthetic MAE ($R^2$) | Synthetic $\\to$ Real MAE ($R^2$) | Degradation |\n")
        f.write("|---|:---:|:---:|:---:|:---:|\n")
        for h_key, h_data in domain_report["experiments"].items():
            rr = h_data["real_to_real"]
            ss = h_data["syn_to_syn"]
            sr = h_data["syn_to_real_transfer"]
            deg = h_data["performance_degradation_pct"]
            f.write(f"| **{h_key}** | {rr['mae']:.4f} ({rr['r2']:.2f}) | {ss['mae']:.4f} ({ss['r2']:.2f}) | {sr['mae']:.4f} ({sr['r2']:.2f}) | +{deg:.1f}% error |\n")

    print(f"[✓] Saved domain shift report: {out_md}")
    print("=" * 85)
    return domain_report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifacts_dir", type=str, default="artifacts")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    evaluate_domain_shift(args.artifacts_dir, args.seed)
