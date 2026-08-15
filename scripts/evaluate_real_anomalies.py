"""
Real-World Data Anomaly Detection, Risk Scoring, and XAI Validation.

Runs the complete AI pipeline (AnomalyDetector, AquacultureRiskEngine, ExplainabilityEngine)
on real sensor observations from the Mendeley dataset (DOI: 10.17632/8s73jfvgr5.2).

Outputs:
- reports/real_anomaly_risk_xai.json
"""

import os
import sys
import json
import numpy as np
import pandas as pd
from datetime import datetime

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
from ai.anomaly import AnomalyDetector
from ai.risk import AquacultureRiskEngine
from ai.explainability import ExplainabilityEngine
from ai.features import FeatureEngineer


def run_real_anomaly_risk_evaluation() -> dict:
    """
    Evaluate anomaly detection, risk scoring, and XAI on real-world stream.
    """
    loader = RealDataLoader()
    df = loader.load_iot_stream(physical_scale=True, max_rows=5000)

    print("=" * 70)
    print("  EVALUATING ANOMALY, RISK & XAI ON REAL-WORLD STREAM")
    print("  Dataset: Mendeley Data (DOI: 10.17632/8s73jfvgr5.2)")
    print(f"  Sample Size: {len(df):,} observations")
    print("=" * 70)

    anomaly_detector = AnomalyDetector(z_score_window=30, isolation_forest_samples=100)
    risk_engine = AquacultureRiskEngine(low_threshold=7.0, high_threshold=8.5)
    explainer = ExplainabilityEngine(low_threshold=7.0, high_threshold=8.5)
    fe = FeatureEngineer(window_size=20)

    anomaly_records = []
    risk_scores = []
    risk_levels = {"LOW": 0, "MODERATE": 0, "ELEVATED": 0, "HIGH": 0, "CRITICAL": 0}
    xai_examples = []

    ph_history = []

    for idx, row in df.iterrows():
        ph = float(row["ph"])
        ts = row["timestamp"]
        ph_history.append(ph)

        # 1. Anomaly detection
        anomaly_detector.add_reading(ph)
        anom_res = anomaly_detector.detect(ph)

        # 2. Feature extraction
        if len(ph_history) >= 2:
            feats = fe.extract(ph_history, hour_of_day=row["hour"])
            roc = float(feats[6])
            trend = float(feats[5])
        else:
            roc = 0.0
            trend = 0.0

        # 3. Risk scoring
        risk_res = risk_engine.compute(
            current_ph=ph,
            predicted_ph=ph + roc,  # 1-step linear extrapolation for risk demonstration
            rate_of_change=roc,
            trend=trend,
            anomaly_score=anom_res["anomaly_score"],
        )

        score = risk_res["total"]
        level = risk_res["level"]
        risk_scores.append(score)
        risk_levels[level] = risk_levels.get(level, 0) + 1

        if anom_res["is_anomaly"]:
            anomaly_records.append({
                "timestamp": ts.isoformat(),
                "reading_id": int(row["reading_id"]),
                "ph": ph,
                "temperature": float(row["temperature"]),
                "dissolved_oxygen": float(row["dissolved_oxygen"]),
                "turbidity": float(row["turbidity"]),
                "anomaly_score": anom_res["anomaly_score"],
                "z_score": anom_res["z_score"],
                "reasons": anom_res["reasons"],
            })

        # Capture illustrative XAI examples across different risk levels
        if len(xai_examples) < 6 and level in ["ELEVATED", "HIGH", "CRITICAL"]:
            exp = explainer.explain(
                current_ph=ph,
                predicted_ph=ph + roc,
                risk_result=risk_res,
                anomaly_result=anom_res,
                rate_of_change=roc,
                trend=trend,
            )
            xai_examples.append({
                "timestamp": ts.isoformat(),
                "ph": ph,
                "risk_score": score,
                "risk_level": level,
                "components": risk_res["components"],
                "summary": exp["summary"],
                "reasons": exp["reasons"],
                "risk_drivers": exp["risk_drivers"],
            })

    total_readings = len(df)
    n_anomalies = len(anomaly_records)
    anomaly_pct = float(round(n_anomalies / total_readings * 100, 2))

    summary = {
        "evaluation_timestamp": datetime.now().isoformat(),
        "dataset_doi": "10.17632/8s73jfvgr5.2",
        "total_observations_analyzed": total_readings,
        "anomaly_statistics": {
            "total_anomalies_flagged": n_anomalies,
            "anomaly_percentage": anomaly_pct,
            "anomaly_score_mean": float(round(np.mean([a["anomaly_score"] for a in anomaly_records]) if anomaly_records else 0, 4)),
            "anomaly_score_max": float(round(np.max([a["anomaly_score"] for a in anomaly_records]) if anomaly_records else 0, 4)),
            "disclaimer": (
                "Detected anomalies are model-generated observations and do not represent "
                "confirmed physical events unless validated against ground truth."
            ),
        },
        "risk_score_distribution": {
            "mean_risk_score": float(round(np.mean(risk_scores), 2)),
            "median_risk_score": float(round(np.median(risk_scores), 2)),
            "max_risk_score": float(round(np.max(risk_scores), 2)),
            "level_counts": risk_levels,
            "level_percentages": {k: float(round(v / total_readings * 100, 2)) for k, v in risk_levels.items()},
        },
        "sample_anomalies": anomaly_records[:5],
        "sample_xai_explanations": xai_examples,
    }

    # Save report
    reports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports")
    os.makedirs(reports_dir, exist_ok=True)
    out_path = os.path.join(reports_dir, "real_anomaly_risk_xai.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"\n[✓] Detected Anomalies: {n_anomalies:,} / {total_readings:,} ({anomaly_pct}%)")
    print(f"[✓] Risk Distribution: {risk_levels}")
    print(f"[✓] Saved JSON report: {out_path}")
    print("=" * 70)
    return summary


if __name__ == "__main__":
    run_real_anomaly_risk_evaluation()
