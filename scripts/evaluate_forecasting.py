"""
Model Evaluation Script for AI Aquaculture Guardian.

Evaluates forecasting accuracy at multiple horizons using synthetic data.
Compares Random Forest against persistence baseline.
Uses chronological train/test split (no shuffling).

Usage:
    python scripts/evaluate_forecasting.py
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Fix Windows UTF-8
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import numpy as np
from datetime import datetime, timedelta
from ai.forecasting import ForecastingEngine
from simulator.ph_simulator import PHSimulator


def generate_evaluation_data(n_readings: int = 500, scenario: str = "normal", seed: int = 42):
    sim = PHSimulator(scenario=scenario, seed=seed)
    values = []
    for _ in range(n_readings):
        _, ph = sim.generate_reading()
        values.append(ph)
    return values


def main():
    print()
    print("=" * 70)
    print("  AI Aquaculture Guardian — Forecasting Evaluation")
    print("=" * 70)
    print(f"  Data source: SYNTHETIC (simulator)")
    print(f"  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print()

    scenarios = ["normal", "rapid_ph_rise", "heavy_rain", "competition_demo"]

    for scenario in scenarios:
        print(f"\n{'─' * 60}")
        print(f"  Scenario: {scenario}")
        print(f"{'─' * 60}")

        values = generate_evaluation_data(500, scenario=scenario, seed=42)

        engine = ForecastingEngine(
            window_size=20, min_train_samples=30, n_estimators=100,
        )
        for v in values:
            engine.add_reading(v)

        if not engine.is_trained:
            print("  [!] Model did not train — insufficient data.\n")
            continue

        horizons = [1, 5, 15, 30]
        results = engine.evaluate(horizons)

        print(f"\n  {'Horizon':>10s} | {'Model MAE':>10s} | {'Model RMSE':>11s} | "
              f"{'Model R²':>9s} | {'Base MAE':>9s} | {'Base R²':>8s} | "
              f"{'Train':>6s} | {'Test':>5s}")
        print(f"  {'-'*10}-+-{'-'*10}-+-{'-'*11}-+-"
              f"{'-'*9}-+-{'-'*9}-+-{'-'*8}-+-"
              f"{'-'*6}-+-{'-'*5}")

        for h in horizons:
            key = f"{h}_step"
            r = results.get(key, {})
            if "error" in r:
                print(f"  {h:>10d} | {r['error']}")
                continue

            m = r["model"]
            b = r["baseline_persistence"]
            print(
                f"  {h:>10d} | "
                f"{m['mae']:>10.6f} | {m['rmse']:>11.6f} | {m['r2']:>9.6f} | "
                f"{b['mae']:>9.6f} | {b['r2']:>8.6f} | "
                f"{r['train_samples']:>6d} | {r['test_samples']:>5d}"
            )

    print()
    print("=" * 70)
    print("  NOTE: All evaluations use SYNTHETIC data from the simulator.")
    print("  These metrics should NOT be cited as real-world performance.")
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()
