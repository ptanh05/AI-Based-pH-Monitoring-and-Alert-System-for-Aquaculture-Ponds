"""
Aquaculture Risk Scoring Engine for AI Aquaculture Guardian.

Produces a 0–100 Aquaculture Risk Score by combining:
  - Current threshold deviation
  - Forecast deviation
  - Trend / rate of change
  - Anomaly score

All weights are configurable. Component contributions are transparent.
"""

from typing import Dict, Optional, List
from enum import Enum


class RiskLevel(str, Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    ELEVATED = "ELEVATED"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


def classify_risk(score: float) -> RiskLevel:
    """Map a 0-100 score to a risk level."""
    if score <= 20:
        return RiskLevel.LOW
    elif score <= 40:
        return RiskLevel.MODERATE
    elif score <= 60:
        return RiskLevel.ELEVATED
    elif score <= 80:
        return RiskLevel.HIGH
    else:
        return RiskLevel.CRITICAL


class AquacultureRiskEngine:
    """
    Computes a transparent 0-100 risk score for aquaculture ponds.

    Formula:
        total = w_current * current_risk
              + w_forecast * forecast_risk
              + w_trend * trend_risk
              + w_anomaly * anomaly_risk

    Each sub-score is in [0, 100].
    Weights are normalised so they sum to 1.
    """

    DEFAULT_WEIGHTS = {
        "current_value": 0.30,
        "forecast": 0.30,
        "trend": 0.20,
        "anomaly": 0.20,
    }

    def __init__(
        self,
        low_threshold: float = 7.0,
        high_threshold: float = 8.5,
        weights: Optional[Dict[str, float]] = None,
    ):
        self.low_threshold = low_threshold
        self.high_threshold = high_threshold
        self.weights = weights or dict(self.DEFAULT_WEIGHTS)

        # Normalise
        total_w = sum(self.weights.values())
        if total_w > 0:
            self.weights = {k: v / total_w for k, v in self.weights.items()}

    # ------------------------------------------------------------------
    # Sub-score helpers
    # ------------------------------------------------------------------

    def _deviation_score(self, value: float) -> float:
        """
        Score how far a value is from the safe range.

        Returns 0 if inside safe range, linearly increasing outside,
        capped at 100.
        """
        mid = (self.low_threshold + self.high_threshold) / 2
        half_range = (self.high_threshold - self.low_threshold) / 2

        if self.low_threshold <= value <= self.high_threshold:
            # Inside safe range: score based on proximity to boundary
            dist_to_edge = min(value - self.low_threshold, self.high_threshold - value)
            # Close to edge → higher risk, further → lower
            proximity = 1.0 - (dist_to_edge / half_range) if half_range > 0 else 0.0
            return max(0.0, proximity * 30.0)  # max 30 when at boundary
        else:
            # Outside safe range
            if value < self.low_threshold:
                overshoot = self.low_threshold - value
            else:
                overshoot = value - self.high_threshold
            # Scale: 0.5 pH overshoot → 100
            return min(100.0, 30.0 + overshoot * 140.0)

    def _trend_score(self, rate_of_change: float, trend: float) -> float:
        """
        Score based on rate of change and trend direction.

        Large absolute rate/trend → higher risk.
        """
        # Combine rate_of_change and trend
        combined = abs(rate_of_change) * 0.6 + abs(trend) * 0.4
        # Scale: 0.1 pH/reading combined → 50, 0.2 → 100
        return min(100.0, combined * 500.0)

    def _anomaly_risk(self, anomaly_score: float) -> float:
        """
        Convert anomaly score (0-1) to risk contribution (0-100).
        """
        return min(100.0, anomaly_score * 100.0)

    # ------------------------------------------------------------------
    # Main scoring API
    # ------------------------------------------------------------------

    def compute(
        self,
        current_ph: float,
        predicted_ph: Optional[float] = None,
        rate_of_change: float = 0.0,
        trend: float = 0.0,
        anomaly_score: float = 0.0,
    ) -> Dict:
        """
        Compute the Aquaculture Risk Score.

        Args:
            current_ph: Current pH reading.
            predicted_ph: AI-predicted future pH (if available).
            rate_of_change: Recent pH change rate.
            trend: Linear trend slope.
            anomaly_score: Anomaly detector score (0-1).

        Returns:
            {
                "total": 0-100,
                "level": "LOW" | "MODERATE" | ... | "CRITICAL",
                "components": {
                    "current_value": sub-score,
                    "forecast": sub-score,
                    "trend": sub-score,
                    "anomaly": sub-score,
                }
            }
        """
        # Sub-scores
        current_risk = self._deviation_score(current_ph)

        if predicted_ph is not None:
            forecast_risk = self._deviation_score(predicted_ph)
        else:
            forecast_risk = current_risk * 0.5  # Less confident without forecast

        trend_risk = self._trend_score(rate_of_change, trend)
        anomaly_risk_val = self._anomaly_risk(anomaly_score)

        # Weighted total
        total = (
            self.weights.get("current_value", 0.25) * current_risk
            + self.weights.get("forecast", 0.25) * forecast_risk
            + self.weights.get("trend", 0.25) * trend_risk
            + self.weights.get("anomaly", 0.25) * anomaly_risk_val
        )
        total = float(round(min(100.0, max(0.0, total)), 1))

        level = classify_risk(total)

        return {
            "total": float(total),
            "level": str(level.value),
            "components": {
                "current_value": float(round(current_risk, 1)),
                "forecast": float(round(forecast_risk, 1)),
                "trend": float(round(trend_risk, 1)),
                "anomaly": float(round(anomaly_risk_val, 1)),
            },
            "weights": {str(k): float(v) for k, v in self.weights.items()},
        }
