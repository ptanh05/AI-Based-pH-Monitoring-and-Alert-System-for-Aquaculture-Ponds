"""
Edge AI Inference Abstraction for AI Aquaculture Guardian.

Defines the BaseInferenceEngine interface and provides:
- SklearnInferenceEngine: Default backend using scikit-learn.
- OpenVINOInferenceEngine: Intel® OpenVINO™ accelerated backend.

The application selects the backend at runtime based on availability.
If OpenVINO is not installed or model conversion fails, the system
falls back gracefully to sklearn.
"""

import numpy as np
import time
import os
import tempfile
from abc import ABC, abstractmethod
from typing import Optional, Dict, List

try:
    from sklearn.ensemble import RandomForestRegressor
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import openvino as ov
    OPENVINO_AVAILABLE = True
except ImportError:
    OPENVINO_AVAILABLE = False

try:
    from skl2onnx import convert_sklearn
    from skl2onnx.common.data_types import FloatTensorType
    SKL2ONNX_AVAILABLE = True
except ImportError:
    SKL2ONNX_AVAILABLE = False


class BaseInferenceEngine(ABC):
    """Abstract base class for inference backends."""

    @abstractmethod
    def load_model(self, model, n_features: int) -> bool:
        """Load or convert a model for inference."""
        ...

    @abstractmethod
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Run inference on input array X."""
        ...

    @abstractmethod
    def get_info(self) -> Dict:
        """Return engine metadata."""
        ...

    def benchmark(self, X: np.ndarray, n_iterations: int = 100, num_runs: Optional[int] = None) -> Dict:
        """
        Benchmark inference latency.

        Returns latency stats (P50, P95, P99, mean) in milliseconds.
        """
        runs = num_runs if num_runs is not None else n_iterations
        latencies = []
        if X.ndim == 1:
            X_in = X.reshape(1, -1)
        else:
            X_in = X

        for _ in range(runs):
            start = time.perf_counter()
            self.predict(X_in)
            end = time.perf_counter()
            latencies.append((end - start) * 1000)  # ms

        latencies.sort()
        mean_v = round(float(np.mean(latencies)), 4)
        p50_v = round(float(np.percentile(latencies, 50)), 4)
        p95_v = round(float(np.percentile(latencies, 95)), 4)
        p99_v = round(float(np.percentile(latencies, 99)), 4)
        min_v = round(float(min(latencies)), 4)
        max_v = round(float(max(latencies)), 4)
        fps_v = round(runs / (sum(latencies) / 1000) if sum(latencies) > 0 else 0.0, 2)

        return {
            "n_iterations": runs,
            "mean_ms": mean_v,
            "p50_ms": p50_v,
            "p95_ms": p95_v,
            "p99_ms": p99_v,
            "min_ms": min_v,
            "max_ms": max_v,
            "throughput_per_sec": fps_v,
            # Backward-compatible aliases:
            "mean_latency_ms": mean_v,
            "p50_latency_ms": p50_v,
            "p95_latency_ms": p95_v,
            "p99_latency_ms": p99_v,
            "throughput_fps": fps_v,
        }


class SklearnInferenceEngine(BaseInferenceEngine):
    """Default inference backend using scikit-learn."""

    def __init__(self, model=None, n_features: int = 0):
        self._model = None
        self._n_features = 0
        if model is not None:
            nf = n_features or getattr(model, "n_features_in_", 0)
            self.load_model(model, nf)

    @property
    def engine_type(self) -> str:
        return "sklearn"

    def load_model(self, model, n_features: int) -> bool:
        if model is None:
            return False
        self._model = model
        self._n_features = n_features
        return True

    def predict(self, X: np.ndarray) -> np.ndarray:
        if self._model is None:
            raise RuntimeError("No model loaded in SklearnInferenceEngine")
        return self._model.predict(X)

    def get_info(self) -> Dict:
        return {
            "backend": "sklearn",
            "model_loaded": self._model is not None,
            "n_features": self._n_features,
        }


class OpenVINOInferenceEngine(BaseInferenceEngine):
    """
    Intel® OpenVINO™ inference backend.

    Converts sklearn RandomForest → ONNX → OpenVINO IR,
    then runs inference on Intel CPU via OpenVINO runtime.

    Requires: openvino, skl2onnx (optional — for conversion).
    If conversion fails, falls back to sklearn silently.
    """

    def __init__(self, device: str = "CPU"):
        self._device = device
        self._compiled_model = None
        self._infer_request = None
        self._input_name = None
        self._output_name = None
        self._n_features = 0
        self._conversion_success = False
        self._model_path: Optional[str] = None
        self._fallback_sklearn = SklearnInferenceEngine()

    def load_model(self, model, n_features: int) -> bool:
        """
        Convert sklearn model to OpenVINO IR and compile.

        Falls back to sklearn if conversion is unsupported.
        """
        self._n_features = n_features

        if not OPENVINO_AVAILABLE:
            self._fallback_sklearn.load_model(model, n_features)
            return False

        if not SKL2ONNX_AVAILABLE:
            self._fallback_sklearn.load_model(model, n_features)
            return False

        if model is None:
            return False

        try:
            # Step 1: sklearn → ONNX
            initial_type = [("X", FloatTensorType([None, n_features]))]
            onnx_model = convert_sklearn(model, initial_types=initial_type)

            # Step 2: Save ONNX temporarily
            model_dir = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "..", "data", "models"
            )
            os.makedirs(model_dir, exist_ok=True)
            onnx_path = os.path.join(model_dir, "ph_forecast_rf.onnx")

            with open(onnx_path, "wb") as f:
                f.write(onnx_model.SerializeToString())

            self._model_path = onnx_path

            # Step 3: ONNX → OpenVINO compiled model
            core = ov.Core()
            ov_model = core.read_model(onnx_path)
            self._compiled_model = core.compile_model(ov_model, self._device)
            self._infer_request = self._compiled_model.create_infer_request()

            # Get input/output names
            self._input_name = self._compiled_model.input(0)
            self._output_name = self._compiled_model.output(0)

            self._conversion_success = True
            return True

        except Exception as e:
            print(f"[OpenVINO] Conversion failed: {e}. Falling back to sklearn.")
            self._fallback_sklearn.load_model(model, n_features)
            self._conversion_success = False
            return False

    def predict(self, X: np.ndarray) -> np.ndarray:
        if self._conversion_success and self._infer_request is not None:
            X_float = X.astype(np.float32)
            result = self._infer_request.infer({self._input_name: X_float})
            output = result[self._output_name]
            return output.flatten()
        else:
            return self._fallback_sklearn.predict(X)

    @property
    def engine_type(self) -> str:
        return "openvino" if self._conversion_success else "sklearn_fallback"

    def get_info(self) -> Dict:
        info = {
            "backend": "openvino" if self._conversion_success else "sklearn_fallback",
            "openvino_available": OPENVINO_AVAILABLE,
            "skl2onnx_available": SKL2ONNX_AVAILABLE,
            "conversion_success": self._conversion_success,
            "device": self._device,
            "model_path": self._model_path,
            "n_features": self._n_features,
        }
        if OPENVINO_AVAILABLE:
            try:
                core = ov.Core()
                info["available_devices"] = core.available_devices
                info["openvino_version"] = ov.__version__
            except Exception:
                pass
        return info


def create_inference_engine(
    model=None, prefer_openvino: bool = True, n_features: int = 0
) -> BaseInferenceEngine:
    """
    Factory function: create the best available inference engine.

    Args:
        model: Optional model to load immediately.
        prefer_openvino: If True and OpenVINO is available, use it.
        n_features: Feature dimension for model compilation.

    Returns:
        An inference engine instance.
    """
    if isinstance(model, bool):
        prefer_openvino = model
        model = None

    if prefer_openvino and OPENVINO_AVAILABLE and SKL2ONNX_AVAILABLE:
        engine = OpenVINOInferenceEngine()
    else:
        engine = SklearnInferenceEngine()

    if model is not None:
        nf = n_features or getattr(model, "n_features_in_", 0)
        engine.load_model(model, nf)

    return engine
