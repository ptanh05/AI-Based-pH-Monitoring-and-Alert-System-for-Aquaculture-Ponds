"""
AI Explainability Engine for AI Aquaculture Guardian.

Generates human-readable explanations for risk assessments and alerts.
Uses feature contributions and rule-based reasoning.

Architecture supports future upgrade to SHAP-based explanations.
"""

from typing import Dict, List, Optional


class ExplainabilityEngine:
    """
    Produces transparent, human-readable explanations for AI alerts.

    Current approach: rule-based reasoning from feature contributions
    and risk components.

    Future: SHAP value integration when computational budget allows.
    """

    def __init__(
        self,
        low_threshold: float = 7.0,
        high_threshold: float = 8.5,
    ):
        self.low_threshold = low_threshold
        self.high_threshold = high_threshold

    def explain(
        self,
        current_ph: float,
        predicted_ph: Optional[float],
        risk_result: Dict,
        anomaly_result: Dict,
        rate_of_change: float = 0.0,
        trend: float = 0.0,
        feature_importance: Optional[List[float]] = None,
        feature_names: Optional[List[str]] = None,
    ) -> Dict:
        """
        Generate explanation for the current system state.

        Returns:
            {
                "summary": str,
                "reasons": [str, ...],
                "risk_drivers": [{"factor": ..., "contribution": ...}, ...],
                "confidence_note": str,
                "feature_contributions": [...] if available,
            }
        """
        reasons = []
        risk_drivers = []
        risk_total = risk_result.get("total", 0)
        risk_level = risk_result.get("level", "LOW")
        components = risk_result.get("components", {})

        # ── Current value analysis ──
        if current_ph < self.low_threshold:
            reasons.append(
                f"Current pH ({current_ph:.2f}) is below the safe threshold "
                f"({self.low_threshold})"
            )
        elif current_ph > self.high_threshold:
            reasons.append(
                f"Current pH ({current_ph:.2f}) is above the safe threshold "
                f"({self.high_threshold})"
            )
        elif current_ph > self.high_threshold - 0.3:
            reasons.append(
                f"Current pH ({current_ph:.2f}) is approaching the upper "
                f"safety threshold ({self.high_threshold})"
            )
        elif current_ph < self.low_threshold + 0.3:
            reasons.append(
                f"Current pH ({current_ph:.2f}) is approaching the lower "
                f"safety threshold ({self.low_threshold})"
            )

        # ── Forecast analysis ──
        if predicted_ph is not None:
            if predicted_ph > self.high_threshold:
                reasons.append(
                    f"AI forecasts pH rising to {predicted_ph:.2f}, which "
                    f"exceeds the upper safe threshold ({self.high_threshold})"
                )
            elif predicted_ph < self.low_threshold:
                reasons.append(
                    f"AI forecasts pH dropping to {predicted_ph:.2f}, which "
                    f"is below the lower safe threshold ({self.low_threshold})"
                )
            elif predicted_ph > self.high_threshold - 0.2:
                reasons.append(
                    f"AI forecasts pH approaching the upper threshold "
                    f"({predicted_ph:.2f})"
                )

        # ── Trend analysis ──
        if abs(rate_of_change) > 0.05:
            direction = "rising" if rate_of_change > 0 else "falling"
            reasons.append(
                f"pH is {direction} rapidly "
                f"(rate: {rate_of_change:+.3f} per reading)"
            )

        if abs(trend) > 0.02:
            direction = "upward" if trend > 0 else "downward"
            reasons.append(f"Sustained {direction} trend detected (slope: {trend:+.4f})")

        # ── Anomaly analysis ──
        if anomaly_result.get("is_anomaly", False):
            for r in anomaly_result.get("reasons", []):
                reasons.append(r)

        # ── Risk drivers (sorted by contribution) ──
        for factor, score in sorted(
            components.items(), key=lambda x: x[1], reverse=True
        ):
            if score > 5:
                risk_drivers.append({
                    "factor": factor,
                    "contribution": score,
                    "description": self._describe_factor(factor, score),
                })

        # ── Summary ──
        if risk_total <= 20:
            summary = "Water quality conditions appear normal."
        elif risk_total <= 40:
            summary = "Minor water quality changes detected. Continue monitoring."
        elif risk_total <= 60:
            summary = (
                "Elevated water quality risk detected. "
                "Increased attention recommended."
            )
        elif risk_total <= 80:
            summary = (
                "High water quality risk. "
                "AI predicts elevated probability of exceeding the safe pH range."
            )
        else:
            summary = (
                "Critical water quality risk. "
                "Immediate attention and sensor verification recommended."
            )

        # ── Confidence note ──
        confidence_note = (
            "These explanations are based on AI analysis of simulated sensor data. "
            "Always verify with physical measurements before taking action."
        )

        # ── Feature contributions ──
        feat_contrib = None
        if feature_importance and feature_names:
            n = min(len(feature_importance), len(feature_names))
            pairs = list(zip(feature_names[:n], feature_importance[:n]))
            pairs.sort(key=lambda x: abs(x[1]), reverse=True)
            feat_contrib = [
                {"feature": name, "importance": round(imp, 4)}
                for name, imp in pairs[:8]
            ]

        return {
            "summary": summary,
            "reasons": reasons if reasons else ["No significant issues detected."],
            "risk_drivers": risk_drivers,
            "confidence_note": confidence_note,
            "feature_contributions": feat_contrib,
        }

    def _describe_factor(self, factor: str, score: float) -> str:
        descriptions = {
            "current_value": f"Current pH deviation contributes {score:.0f} points",
            "forecast": f"AI forecast contributes {score:.0f} points to risk",
            "trend": f"pH trend contributes {score:.0f} points to risk",
            "anomaly": f"Anomaly detection contributes {score:.0f} points to risk",
        }
        return descriptions.get(
            factor, f"{factor} contributes {score:.0f} points to risk"
        )
