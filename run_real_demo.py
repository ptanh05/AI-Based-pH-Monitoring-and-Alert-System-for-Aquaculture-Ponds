"""
Real-World Aquaculture Dataset Streaming CLI Demo.

Streams continuous observations from real pond datasets (e.g. Mendeley Tilapia dataset)
through the full AI pipeline:
  Validation -> Features -> Forecast -> Anomaly -> Risk -> XAI -> Recommendations

Usage:
  python run_real_demo.py --dataset mendeley_aquaculture --max_readings 50 --speed 10
"""

import os
import sys
import time
import argparse
from datetime import datetime

# Fix Windows console UTF-8
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data.real_data_loader import RealDataLoader
from ai.sensor_schema import SensorReading, SensorParameter, SensorQuality, validate_reading
from ai.features import FeatureEngineer
from ai.forecasting import ForecastingEngine
from ai.anomaly import AnomalyDetector
from ai.risk import AquacultureRiskEngine
from ai.explainability import ExplainabilityEngine
from ai.recommendations import RecommendationEngine


def run_real_demo(dataset_name: str = "mendeley_aquaculture", max_readings: int = 50, speed: float = 10.0):
    print("=" * 80)
    print("  AI AQUACULTURE GUARDIAN — REAL-WORLD DATASET STREAMING DEMO")
    print(f"  Dataset: {dataset_name} | Max Readings: {max_readings} | Playback Speed: {speed}x")
    print("=" * 80)

    loader = RealDataLoader()
    feature_engineer = FeatureEngineer(window_size=20)
    forecaster = ForecastingEngine(window_size=20)
    anomaly_detector = AnomalyDetector(z_score_window=20)
    risk_engine = AquacultureRiskEngine(low_threshold=7.0, high_threshold=8.5)
    explainer = ExplainabilityEngine(low_threshold=7.0, high_threshold=8.5)
    rec_engine = RecommendationEngine()

    # Pre-train forecaster on first 100 historical readings
    print("[*] Pre-calibrating forecasting model on historical stream...")
    df_init = loader.load_iot_stream(physical_scale=True, max_rows=150)
    init_ph = df_init["ph"].dropna().tolist()
    for v in init_ph:
        forecaster.add_reading(v)
    print("    Model calibrated and ready for real-time inference.")

    sleep_interval = max(0.01, 1.0 / speed)
    ph_history = list(init_ph)

    print("\n" + "-" * 80)
    print(f"  {'#':<4s} | {'Timestamp':<19s} | {'pH':<6s} | {'Temp':<7s} | {'DO':<7s} | {'Pred pH':<8s} | {'Risk':<10s} | {'Status':<10s}")
    print("-" * 80)

    stream_gen = loader.stream_real_readings(start_idx=150)
    count = 0

    for ts, ph_val, ctx in stream_gen:
        count += 1
        if count > max_readings:
            break

        ph_history.append(ph_val)
        forecaster.add_reading(ph_val, ts)
        temp = ctx.get("temperature", 27.0)
        do = ctx.get("dissolved_oxygen", 8.0)

        # 1. Validation
        reading = SensorReading(
            timestamp=ts,
            sensor_id="MONTERIA-01-PH",
            pond_id="MONTERIA-POND-01",
            parameter="pH",
            value=ph_val,
            unit="pH",
            source="csv_import",
            quality=SensorQuality.GOOD,
            temperature=temp,
            dissolved_oxygen=do,
        )
        val_res = validate_reading(reading)

        # 2. Features & Forecasting
        feats = feature_engineer.extract(ph_history, hour_of_day=ts.hour)
        fc_res = forecaster.predict_multistep(n_steps=5, hour_of_day=ts.hour)
        pred_ph = fc_res["model_predictions"][0] if fc_res["model_predictions"] else ph_val

        # 3. Anomaly Detection
        anomaly_detector.add_reading(ph_val)
        anom_res = anomaly_detector.detect(ph_val)

        # 4. Risk Scoring
        roc = float(feats[6])
        trend = float(feats[5])
        risk_res = risk_engine.compute(
            current_ph=ph_val,
            predicted_ph=pred_ph,
            rate_of_change=roc,
            trend=trend,
            anomaly_score=anom_res["anomaly_score"],
        )

        risk_score = risk_res["total"]
        risk_level = risk_res["level"]

        # Status badge
        if risk_score > 60 or ph_val < 7.0 or ph_val > 8.5:
            status_tag = "[ !ALERT! ]"
        elif risk_score > 30:
            status_tag = "[  WARN   ]"
        elif anom_res["is_anomaly"]:
            status_tag = "[ ANOMALY ]"
        else:
            status_tag = "[   OK    ]"

        risk_bar_len = int(risk_score / 5)
        risk_bar = "#" * risk_bar_len + "." * (20 - risk_bar_len)

        print(
            f"  {count:>3d}  | {ts.strftime('%Y-%m-%d %H:%M:%S')} | {ph_val:>6.2f} | {temp:>5.1f}°C | {do:>5.1f}mg | {pred_ph:>8.2f} | {risk_score:>5.1f} [{risk_bar[:8]}] | {status_tag}"
        )

        # If elevated risk, warning, or anomaly, print explainability and actionable recommendations
        if status_tag != "[   OK    ]":
            exp = explainer.explain(
                current_ph=ph_val,
                predicted_ph=pred_ph,
                risk_result=risk_res,
                anomaly_result=anom_res,
                rate_of_change=roc,
                trend=trend,
            )
            recs = rec_engine.generate(
                risk_level=risk_level,
                risk_total=risk_score,
                current_ph=ph_val,
                predicted_ph=pred_ph,
                anomaly_result=anom_res,
            )
            print(f"        🔍 WHY: {exp['summary']}")
            if exp["reasons"] and exp["reasons"][0] != "No significant issues detected.":
                print(f"           - {exp['reasons'][0]}")
            if recs["actions"]:
                # Pick the most relevant action (anomaly action if low risk, or top priority action)
                action_text = recs["actions"][-1]["text"] if (anom_res["is_anomaly"] and risk_level == "LOW") else recs["actions"][0]["text"]
                print(f"        💡 ACTION: {action_text}")

        time.sleep(sleep_interval)

    print("-" * 80)
    print("  REAL DATASET DEMO STREAM COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=str, default="mendeley_aquaculture")
    parser.add_argument("--max_readings", type=int, default=30)
    parser.add_argument("--speed", type=float, default=20.0)
    args = parser.parse_args()
    run_real_demo(args.dataset, args.max_readings, args.speed)
