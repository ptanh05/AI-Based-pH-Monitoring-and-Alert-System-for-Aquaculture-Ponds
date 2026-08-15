"""
Recommendation Engine for AI Aquaculture Guardian.

Provides safe, conservative, actionable guidance for aquaculture
farmers based on current risk level and environmental context.

IMPORTANT:
- Recommendations are SUGGESTED ACTIONS, not guaranteed solutions.
- Never prescribe chemical dosages.
- Never claim veterinary authority.
- Never automate dangerous equipment control.
- Always advise verification of sensor readings.
"""

from typing import Dict, List, Optional


class RecommendationEngine:
    """
    Generates decision-support recommendations for aquaculture operators.

    Recommendations are categorised by risk level and tagged with
    urgency and category for dashboard display.
    """

    def generate(
        self,
        risk_level: str,
        risk_total: float,
        current_ph: float,
        predicted_ph: Optional[float],
        anomaly_result: Optional[Dict] = None,
        sensor_quality: str = "good",
        low_threshold: float = 7.0,
        high_threshold: float = 8.5,
    ) -> Dict:
        """
        Generate recommendations based on current system state.

        Returns:
            {
                "actions": [{"text": ..., "urgency": ..., "category": ...}, ...],
                "monitoring_advice": str,
                "disclaimer": str,
            }
        """
        actions = []

        # ── Sensor quality issues take priority ──
        if sensor_quality in ("suspect", "bad", "degraded"):
            actions.append({
                "text": "Sensor quality is degraded — verify physical sensor "
                        "before acting on readings.",
                "urgency": "high",
                "category": "sensor_verification",
            })

        if anomaly_result and anomaly_result.get("stuck_sensor", False):
            actions.append({
                "text": "Sensor appears stuck (constant readings). "
                        "Clean or recalibrate the sensor probe.",
                "urgency": "high",
                "category": "sensor_maintenance",
            })

        # ── Risk-level specific recommendations ──
        if risk_level == "CRITICAL":
            actions.extend(self._critical_actions(current_ph, predicted_ph, low_threshold, high_threshold))
        elif risk_level == "HIGH":
            actions.extend(self._high_actions(current_ph, predicted_ph, low_threshold, high_threshold))
        elif risk_level == "ELEVATED":
            actions.extend(self._elevated_actions(current_ph, predicted_ph, low_threshold, high_threshold))
        elif risk_level == "MODERATE":
            actions.extend(self._moderate_actions(current_ph))
        else:  # LOW
            actions.extend(self._low_actions())

        # ── Anomaly-specific ──
        if anomaly_result and anomaly_result.get("is_anomaly", False):
            for reason in anomaly_result.get("reasons", [])[:2]:
                actions.append({
                    "text": f"Anomaly detected: {reason}. "
                            "Investigate possible environmental cause.",
                    "urgency": "medium",
                    "category": "investigation",
                })

        # ── Monitoring advice ──
        monitoring = self._monitoring_advice(risk_level)

        return {
            "actions": actions,
            "monitoring_advice": monitoring,
            "disclaimer": (
                "These are suggested actions for decision support only. "
                "They do not constitute professional aquaculture or "
                "veterinary advice. Always consult qualified personnel "
                "and follow your farm's established procedures."
            ),
        }

    # ------------------------------------------------------------------
    # Per-level action generators
    # ------------------------------------------------------------------

    def _critical_actions(self, ph, predicted, low, high) -> List[Dict]:
        actions = [
            {
                "text": "Verify sensor measurements immediately with a "
                        "backup measurement device.",
                "urgency": "critical",
                "category": "verification",
            },
            {
                "text": "Notify the responsible operator or farm manager.",
                "urgency": "critical",
                "category": "notification",
            },
            {
                "text": "Follow your farm's established emergency "
                        "water-management procedure.",
                "urgency": "critical",
                "category": "emergency_response",
            },
            {
                "text": "Increase monitoring frequency until conditions stabilise.",
                "urgency": "critical",
                "category": "monitoring",
            },
        ]
        return actions

    def _high_actions(self, ph, predicted, low, high) -> List[Dict]:
        actions = [
            {
                "text": "Verify sensor readings with a secondary measurement.",
                "urgency": "high",
                "category": "verification",
            },
            {
                "text": "Inspect pond conditions and check for visible "
                        "changes (colour, odour, surface).",
                "urgency": "high",
                "category": "inspection",
            },
            {
                "text": "Review aeration and water-management procedures.",
                "urgency": "high",
                "category": "water_management",
            },
        ]
        if predicted is not None and predicted > high:
            actions.append({
                "text": "AI predicts pH may rise above the safe range. "
                        "Prepare contingency measures per farm protocol.",
                "urgency": "high",
                "category": "preparation",
            })
        if predicted is not None and predicted < low:
            actions.append({
                "text": "AI predicts pH may drop below the safe range. "
                        "Check for possible rain or runoff events.",
                "urgency": "high",
                "category": "preparation",
            })
        return actions

    def _elevated_actions(self, ph, predicted, low, high) -> List[Dict]:
        return [
            {
                "text": "Continue monitoring water quality closely.",
                "urgency": "medium",
                "category": "monitoring",
            },
            {
                "text": "Check recent weather conditions and "
                        "environmental events.",
                "urgency": "medium",
                "category": "investigation",
            },
            {
                "text": "Verify sensor calibration if readings seem unusual.",
                "urgency": "medium",
                "category": "sensor_verification",
            },
        ]

    def _moderate_actions(self, ph) -> List[Dict]:
        return [
            {
                "text": "Maintain regular monitoring schedule.",
                "urgency": "low",
                "category": "monitoring",
            },
            {
                "text": "Note any environmental changes that could "
                        "affect water quality.",
                "urgency": "low",
                "category": "observation",
            },
        ]

    def _low_actions(self) -> List[Dict]:
        return [
            {
                "text": "Water quality appears normal. Continue routine monitoring.",
                "urgency": "info",
                "category": "routine",
            },
        ]

    def _monitoring_advice(self, risk_level: str) -> str:
        advice = {
            "CRITICAL": "Continuous monitoring recommended. Check readings every minute.",
            "HIGH": "Increase monitoring frequency. Check every 5 minutes.",
            "ELEVATED": "Monitor closely. Check every 10-15 minutes.",
            "MODERATE": "Standard monitoring. Check every 30 minutes.",
            "LOW": "Routine monitoring. Regular schedule is sufficient.",
        }
        return advice.get(risk_level, advice["LOW"])
