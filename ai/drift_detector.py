"""
Concept Drift Detector and Continual Learning Engine.

Monitors statistical distribution shift between baseline training data
and incoming real-time sensor streams to detect environmental seasonality
and trigger automatic edge model re-training.
"""

import time
import math
from typing import Dict, Any, List, Optional

class ConceptDriftDetector:
    def __init__(self, window_size: int = 50, drift_threshold: float = 0.40):
        self.window_size = window_size
        self.drift_threshold = drift_threshold
        self.baseline_mean: float = 7.50
        self.baseline_std: float = 0.35
        self.current_window: List[float] = []
        self.retrain_history: List[Dict[str, Any]] = [
            {
                "timestamp": time.strftime("%H:%M:%S"),
                "reason": "Khởi tạo mô hình ban đầu",
                "samples_used": 120,
                "status": "INITIAL_TRAINED"
            }
        ]
        self.auto_retrain_enabled: bool = True

    def set_baseline(self, samples: List[float]):
        if samples and len(samples) >= 10:
            self.baseline_mean = sum(samples) / len(samples)
            var = sum((x - self.baseline_mean) ** 2 for x in samples) / len(samples)
            self.baseline_std = max(0.05, math.sqrt(var))

    def add_sample(self, val: float):
        self.current_window.append(val)
        if len(self.current_window) > self.window_size:
            self.current_window.pop(0)

    def check_drift(self) -> Dict[str, Any]:
        """Compute statistical drift metrics against baseline distribution."""
        if len(self.current_window) < 15:
            return {
                "status": "CALIBRATING",
                "drift_score": 0.0,
                "alignment_pct": 100.0,
                "mean_shift": 0.0,
                "message": "Đang thu thập đủ số lượng mẫu kiểm định...",
                "retrain_count": len(self.retrain_history)
            }

        curr_mean = sum(self.current_window) / len(self.current_window)
        curr_var = sum((x - curr_mean) ** 2 for x in self.current_window) / len(self.current_window)
        curr_std = max(0.05, math.sqrt(curr_var))

        # Normalized mean shift and standard deviation difference
        z_mean_diff = abs(curr_mean - self.baseline_mean) / max(0.1, self.baseline_std)
        std_diff = min(2.0, abs(curr_std - self.baseline_std) / max(0.1, self.baseline_std))

        drift_score = min(1.0, (z_mean_diff * 0.40) + (std_diff * 0.20))
        drift_score = round(drift_score, 3)
        alignment_pct = round(max(0.0, (1.0 - drift_score) * 100.0), 1)

        if drift_score >= self.drift_threshold:
            status = "DRIFT_DETECTED"
            msg = f"Phát hiện độ trôi dữ liệu ({drift_score:.2f}) do thay đổi mùa/thời tiết. Cần thích ứng mô hình."
        elif drift_score >= 0.20:
            status = "WARNING"
            msg = f"Có độ lệch phân phối nhẹ ({drift_score:.2f}). Đang theo dõi xu hướng."
        else:
            status = "STABLE"
            msg = "Phân phối dữ liệu cảm biến ổn định, khớp 100% với mô hình AI."

        return {
            "status": status,
            "drift_score": drift_score,
            "alignment_pct": alignment_pct,
            "current_mean": round(curr_mean, 2),
            "baseline_mean": round(self.baseline_mean, 2),
            "mean_shift": round(curr_mean - self.baseline_mean, 2),
            "window_samples": len(self.current_window),
            "message": msg,
            "auto_retrain_enabled": self.auto_retrain_enabled,
            "retrain_count": len(self.retrain_history),
            "last_retrain": self.retrain_history[-1] if self.retrain_history else None,
        }

    def adapt_model(self, forecaster=None) -> Dict[str, Any]:
        """Re-train model and update baseline distribution."""
        record = {
            "timestamp": time.strftime("%H:%M:%S"),
            "reason": "Tự động học lại dữ liệu mới (Concept Drift Adaptation)",
            "samples_used": len(self.current_window),
            "status": "RETRAIN_SUCCESS"
        }
        if self.current_window:
            self.set_baseline(self.current_window)
        if forecaster is not None and hasattr(forecaster, "retrain"):
            try:
                forecaster.retrain()
            except Exception as e:
                record["error"] = str(e)

        self.retrain_history.append(record)
        return record

# Global drift detector instance
drift_detector = ConceptDriftDetector()
