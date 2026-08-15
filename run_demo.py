"""
AI Aquaculture Guardian — Competition Demo Runner.

Runs a deterministic end-to-end scenario showing the full AI pipeline:
  NORMAL → pH rise → Anomaly → Risk increase →
  Early Warning → Critical → Recovery

Usage:
    python run_demo.py
    python run_demo.py --scenario competition_demo --seed 42
    python run_demo.py --web   (starts web dashboard in demo mode)
"""

import sys
import os
import argparse
import time
import numpy as np
from datetime import datetime

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Fix Windows UTF-8
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def run_cli_demo(scenario: str, seed: int, max_readings: int, interval: float):
    """Run the demo in CLI mode with full pipeline output."""
    from simulator.ph_simulator import PHSimulator
    from ai.forecasting import ForecastingEngine
    from ai.anomaly import AnomalyDetector
    from ai.risk import AquacultureRiskEngine
    from ai.explainability import ExplainabilityEngine
    from ai.recommendations import RecommendationEngine
    from alerts.ph_alert_engine import PHAlertEngine

    print()
    print("=" * 70)
    print("  AI AQUACULTURE GUARDIAN — Competition Demo")
    print("  AI-Powered Early Warning System for Sustainable Aquaculture")
    print("=" * 70)
    print(f"  Scenario:  {scenario}")
    print(f"  Seed:      {seed}")
    print(f"  Readings:  {max_readings}")
    print(f"  Interval:  {interval}s")
    print(f"  Time:      {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Data:      SIMULATED (not real sensor)")
    print("=" * 70)
    print()

    sim = PHSimulator(scenario=scenario, seed=seed)
    forecaster = ForecastingEngine(window_size=20, min_train_samples=25)
    anomaly = AnomalyDetector(z_score_window=20, isolation_forest_samples=40)
    risk_engine = AquacultureRiskEngine()
    explainer = ExplainabilityEngine()
    recommender = RecommendationEngine()
    alert_engine = PHAlertEngine(consecutive_count=1)

    online_actuals = []
    online_predictions = []
    last_predicted = None

    for i, (ts, ph) in enumerate(
        sim.stream_readings(interval_seconds=interval, max_readings=max_readings)
    ):
        # Track 1-step forecast accuracy if previous prediction was made while trained
        if last_predicted is not None and forecaster.is_trained:
            online_actuals.append(ph)
            online_predictions.append(last_predicted)

        # Pipeline
        forecaster.add_reading(ph, ts)
        anomaly.add_reading(ph)

        hour = ts.hour + ts.minute / 60.0
        predicted, trained = forecaster.predict_single(hour)
        last_predicted = predicted
        anomaly_result = anomaly.detect(ph)

        values = forecaster.history
        fe = forecaster.feature_engineer
        if len(values) >= 2:
            feats = fe.extract(values, hour)
            roc = float(feats[6])
            trend = float(feats[5])
        else:
            roc = 0.0
            trend = 0.0

        risk_result = risk_engine.compute(ph, predicted, roc, trend, anomaly_result["anomaly_score"])
        alert_status, alert_msg = alert_engine.process_full(
            ts, ph, predicted, risk_result["total"], risk_result["level"],
            anomaly_result["is_anomaly"],
        )
        explanation = explainer.explain(ph, predicted, risk_result, anomaly_result, roc, trend)
        recs = recommender.generate(
            risk_result["level"], risk_result["total"], ph, predicted, anomaly_result,
        )

        # Display
        status_icons = {
            "NORMAL": "  OK ",
            "EARLY_WARNING": " WARN",
            "HIGH_RISK": " HIGH",
            "CRITICAL": " CRIT",
            "ALERT_LOW_PH": "!LOW!",
            "ALERT_HIGH_PH": "!HI! ",
            "WAITING": " WAIT",
            "SENSOR_WARNING": " SENS",
        }
        icon = status_icons.get(alert_status.value, " ??? ")

        risk_bar_len = int(risk_result["total"] / 5)
        risk_bar = "#" * risk_bar_len + "." * (20 - risk_bar_len)

        print(f"[{i+1:4d}] {ts.strftime('%H:%M:%S')} | "
              f"pH: {ph:5.2f} | "
              f"Pred: {predicted:5.2f} | "
              f"Risk: {risk_result['total']:5.1f} [{risk_bar}] {risk_result['level']:>8s} | "
              f"[{icon}]")

        if alert_status.value not in ("NORMAL", "WAITING"):
            print(f"       >> {alert_msg}")
            if explanation["reasons"]:
                for reason in explanation["reasons"][:2]:
                    print(f"       WHY: {reason}")
            if recs["actions"]:
                print(f"       ACTION: {recs['actions'][0]['text']}")
            print()

    print()
    print("=" * 70)
    print("  Demo Complete")
    print(f"  Model trained: {forecaster.is_trained} ({forecaster.total_retrains} calibrations)")
    if online_actuals:
        online_mae = float(np.mean(np.abs(np.array(online_actuals) - np.array(online_predictions))))
        online_rmse = float(np.sqrt(np.mean((np.array(online_actuals) - np.array(online_predictions)) ** 2)))
        print(f"  Online 1-Step Forecast (t -> t+1):  MAE: {online_mae:.4f}  RMSE: {online_rmse:.4f}")
    if forecaster.get_model_info().get("train_metrics"):
        m = forecaster.get_model_info()["train_metrics"]
        print(f"  Latest Model Checkpoint (Holdout):  MAE: {m['mae']:.4f}  RMSE: {m['rmse']:.4f}  R2: {m['r2']:.4f}")
    print("=" * 70)


def run_web_demo(scenario: str, seed: int):
    """Start the web dashboard in demo mode."""
    import uvicorn
    # Set environment for the server to pick up
    os.environ["GUARDIAN_SCENARIO"] = scenario
    os.environ["GUARDIAN_SEED"] = str(seed)
    print(f"\n[AI Aquaculture Guardian] Starting web demo: {scenario} (seed={seed})")
    print(f"Open browser: http://localhost:8000\n")
    uvicorn.run("api.server:app", host="0.0.0.0", port=8000, reload=False)


def main():
    parser = argparse.ArgumentParser(
        description="AI Aquaculture Guardian — Competition Demo"
    )
    parser.add_argument(
        "--scenario", type=str, default="competition_demo",
        help="Scenario name (default: competition_demo)",
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument(
        "--max-readings", type=int, default=120, help="Number of readings"
    )
    parser.add_argument(
        "--interval", type=float, default=0.3, help="Seconds between readings"
    )
    parser.add_argument(
        "--web", action="store_true", help="Start web dashboard instead of CLI"
    )
    args = parser.parse_args()

    if args.web:
        run_web_demo(args.scenario, args.seed)
    else:
        run_cli_demo(args.scenario, args.seed, args.max_readings, args.interval)


if __name__ == "__main__":
    main()
