"""
Inference Benchmark Script for AI Aquaculture Guardian.

Compares sklearn vs OpenVINO inference latency and throughput.

Usage:
    python scripts/benchmark_inference.py
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
from datetime import datetime
from ai.forecasting import ForecastingEngine
from ai.features import FeatureEngineer
from edge.inference_engine import (
    SklearnInferenceEngine,
    OpenVINOInferenceEngine,
    OPENVINO_AVAILABLE,
    SKL2ONNX_AVAILABLE,
    create_inference_engine,
)
from simulator.ph_simulator import PHSimulator


def main():
    print()
    print("=" * 70)
    print("  AI Aquaculture Guardian — Inference Benchmark")
    print("=" * 70)
    print(f"  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  OpenVINO available: {OPENVINO_AVAILABLE}")
    print(f"  skl2onnx available: {SKL2ONNX_AVAILABLE}")
    print("=" * 70)
    print()

    # Generate training data
    sim = PHSimulator(scenario="normal", seed=42)
    engine = ForecastingEngine(window_size=20, min_train_samples=30)
    for _ in range(200):
        _, ph = sim.generate_reading()
        engine.add_reading(ph)

    if not engine.is_trained:
        print("[!] Model did not train. Cannot benchmark.")
        return

    sklearn_model = engine.get_sklearn_model()
    n_features = len(FeatureEngineer.FEATURE_NAMES)
    X_sample = np.random.rand(1, n_features)

    n_iter = 500

    # Sklearn benchmark
    print(f"  Benchmarking sklearn ({n_iter} iterations)...")
    sklearn_engine = SklearnInferenceEngine()
    sklearn_engine.load_model(sklearn_model, n_features)
    sklearn_results = sklearn_engine.benchmark(X_sample, n_iterations=n_iter)

    print(f"    P50:  {sklearn_results['p50_ms']:.4f} ms")
    print(f"    P95:  {sklearn_results['p95_ms']:.4f} ms")
    print(f"    P99:  {sklearn_results['p99_ms']:.4f} ms")
    print(f"    Mean: {sklearn_results['mean_ms']:.4f} ms")
    print(f"    Throughput: {sklearn_results['throughput_per_sec']:.0f} inferences/sec")

    # OpenVINO benchmark
    if OPENVINO_AVAILABLE and SKL2ONNX_AVAILABLE:
        print(f"\n  Benchmarking OpenVINO CPU ({n_iter} iterations)...")
        ov_engine = OpenVINOInferenceEngine(device="CPU")
        success = ov_engine.load_model(sklearn_model, n_features)

        if success:
            # Validate numerical correctness first
            sklearn_pred = sklearn_engine.predict(X_sample)
            ov_pred = ov_engine.predict(X_sample)
            diff = abs(float(sklearn_pred[0]) - float(ov_pred[0]))
            print(f"    Numerical diff vs sklearn: {diff:.6f}")

            ov_results = ov_engine.benchmark(X_sample, n_iterations=n_iter)
            print(f"    P50:  {ov_results['p50_ms']:.4f} ms")
            print(f"    P95:  {ov_results['p95_ms']:.4f} ms")
            print(f"    P99:  {ov_results['p99_ms']:.4f} ms")
            print(f"    Mean: {ov_results['mean_ms']:.4f} ms")
            print(f"    Throughput: {ov_results['throughput_per_sec']:.0f} inferences/sec")

            # Speedup
            if sklearn_results['mean_ms'] > 0:
                speedup = sklearn_results['mean_ms'] / ov_results['mean_ms']
                print(f"\n  OpenVINO vs sklearn speedup: {speedup:.2f}x")

            ov_info = ov_engine.get_info()
            print(f"  Device: {ov_info.get('device', 'N/A')}")
            print(f"  OpenVINO version: {ov_info.get('openvino_version', 'N/A')}")
            print(f"  Model path: {ov_info.get('model_path', 'N/A')}")
        else:
            print("    [!] OpenVINO model conversion failed.")
            print("    Falling back to sklearn.")
    else:
        missing = []
        if not OPENVINO_AVAILABLE:
            missing.append("openvino")
        if not SKL2ONNX_AVAILABLE:
            missing.append("skl2onnx")
        print(f"\n  [!] OpenVINO benchmark skipped. Missing: {', '.join(missing)}")
        print(f"  Install with: pip install {' '.join(missing)}")

    print()
    print("=" * 70)
    print("  NOTE: Benchmarked on this machine's CPU.")
    print("  Results may differ on Intel® Core™/Xeon® or Intel® NPU hardware.")
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()
