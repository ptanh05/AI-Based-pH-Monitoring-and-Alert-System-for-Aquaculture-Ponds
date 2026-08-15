"""
Early Warning Alert Engine for AI Aquaculture Guardian.

Upgraded state machine that distinguishes:
- Current threshold breaches (measured pH is out of range)
- Predictive early warnings (AI forecasts future breach)
- Anomaly warnings (unusual patterns detected)
- Sensor warnings (data quality issues)

States:
  NORMAL → EARLY_WARNING → HIGH_RISK → CRITICAL
  NORMAL → WAITING → ALERT_LOW_PH / ALERT_HIGH_PH
  NORMAL → SENSOR_WARNING
"""

from enum import Enum
from typing import Optional, Tuple, Dict
from datetime import datetime


class AlertStatus(Enum):
    """Alert status enumeration — expanded for AI Aquaculture Guardian."""
    NORMAL = "NORMAL"
    WAITING = "WAITING"
    EARLY_WARNING = "EARLY_WARNING"
    HIGH_RISK = "HIGH_RISK"
    CRITICAL = "CRITICAL"
    ALERT_LOW_PH = "ALERT_LOW_PH"
    ALERT_HIGH_PH = "ALERT_HIGH_PH"
    SENSOR_WARNING = "SENSOR_WARNING"


class PHAlertEngine:
    """
    Early warning engine combining threshold alerts, predictive
    warnings, anomaly detection, and sensor quality monitoring.

    Backward-compatible: process_reading() still works as before.
    New: process_full() integrates all AI pipeline outputs.
    """

    def __init__(
        self,
        low_threshold: float = 7.0,
        high_threshold: float = 8.5,
        consecutive_count: int = 3,
    ):
        self.low_threshold = low_threshold
        self.high_threshold = high_threshold
        self.consecutive_count = consecutive_count

        self.current_status = AlertStatus.NORMAL
        self.consecutive_low_count = 0
        self.consecutive_high_count = 0
        self.last_alert_time: Optional[datetime] = None

    def _is_low(self, ph_value: float) -> bool:
        return ph_value < self.low_threshold

    def _is_high(self, ph_value: float) -> bool:
        return ph_value > self.high_threshold

    def _is_safe(self, ph_value: float) -> bool:
        return self.low_threshold <= ph_value <= self.high_threshold

    # ------------------------------------------------------------------
    # Original API (backward compatible)
    # ------------------------------------------------------------------

    def process_reading(
        self, timestamp: datetime, ph_value: float
    ) -> Tuple[AlertStatus, str]:
        """
        Process a pH reading for threshold-based alerting.

        Backward compatible with the original PHAlertEngine.
        """
        previous_status = self.current_status

        if self._is_low(ph_value):
            self.consecutive_low_count += 1
            self.consecutive_high_count = 0

            if self.consecutive_low_count >= self.consecutive_count:
                self.current_status = AlertStatus.ALERT_LOW_PH
                self.last_alert_time = timestamp
                message = (
                    f"LOW pH ALERT: pH = {ph_value:.2f} "
                    f"(below safe threshold {self.low_threshold})"
                )
            else:
                self.current_status = AlertStatus.WAITING
                message = (
                    f"Waiting: pH = {ph_value:.2f} is low "
                    f"({self.consecutive_low_count}/{self.consecutive_count} consecutive readings)"
                )

        elif self._is_high(ph_value):
            self.consecutive_high_count += 1
            self.consecutive_low_count = 0

            if self.consecutive_high_count >= self.consecutive_count:
                self.current_status = AlertStatus.ALERT_HIGH_PH
                self.last_alert_time = timestamp
                message = (
                    f"HIGH pH ALERT: pH = {ph_value:.2f} "
                    f"(above safe threshold {self.high_threshold})"
                )
            else:
                self.current_status = AlertStatus.WAITING
                message = (
                    f"Waiting: pH = {ph_value:.2f} is high "
                    f"({self.consecutive_high_count}/{self.consecutive_count} consecutive readings)"
                )

        else:
            self.consecutive_low_count = 0
            self.consecutive_high_count = 0

            if previous_status in [AlertStatus.ALERT_LOW_PH, AlertStatus.ALERT_HIGH_PH]:
                self.current_status = AlertStatus.NORMAL
                message = f"pH returned to safe range: {ph_value:.2f}"
            else:
                self.current_status = AlertStatus.NORMAL
                message = f"Normal: pH = {ph_value:.2f}"

        return self.current_status, message

    # ------------------------------------------------------------------
    # Extended API (integrates full AI pipeline)
    # ------------------------------------------------------------------

    def process_full(
        self,
        timestamp: datetime,
        ph_value: float,
        predicted_ph: Optional[float] = None,
        risk_total: float = 0.0,
        risk_level: str = "LOW",
        anomaly_detected: bool = False,
        sensor_quality: str = "good",
    ) -> Tuple[AlertStatus, str]:
        """
        Process a reading with full AI pipeline context.

        Determines the appropriate alert status by combining:
        1. Threshold breach (current pH)
        2. Predictive early warning (predicted pH)
        3. Risk score
        4. Anomaly detection
        5. Sensor quality

        IMPORTANT: Distinguishes between current breaches and
        predicted breaches — never claims pH has exceeded the range
        when it has only been predicted to do so.
        """
        # Start with threshold-based processing
        threshold_status, threshold_msg = self.process_reading(timestamp, ph_value)

        # Sensor quality overrides
        if sensor_quality in ("bad", "degraded"):
            self.current_status = AlertStatus.SENSOR_WARNING
            return self.current_status, (
                f"Sensor quality issue detected. Verify measurement. "
                f"pH reading: {ph_value:.2f}"
            )

        # Current threshold breach takes highest priority
        if threshold_status in [AlertStatus.ALERT_LOW_PH, AlertStatus.ALERT_HIGH_PH]:
            if risk_level == "CRITICAL":
                self.current_status = AlertStatus.CRITICAL
                return self.current_status, (
                    f"CRITICAL: pH = {ph_value:.2f} has breached the safe range. "
                    f"Risk score: {risk_total:.0f}/100."
                )
            return threshold_status, threshold_msg

        # Predictive early warning (pH is still safe, but AI predicts breach)
        if predicted_ph is not None and self._is_safe(ph_value):
            if predicted_ph > self.high_threshold or predicted_ph < self.low_threshold:
                if risk_level in ("CRITICAL", "HIGH"):
                    self.current_status = AlertStatus.HIGH_RISK
                    direction = "exceeding upper" if predicted_ph > self.high_threshold else "dropping below lower"
                    return self.current_status, (
                        f"HIGH RISK: AI predicts elevated probability of {direction} "
                        f"safe pH range. Current: {ph_value:.2f}, "
                        f"Predicted: {predicted_ph:.2f}. Risk: {risk_total:.0f}/100."
                    )
                else:
                    self.current_status = AlertStatus.EARLY_WARNING
                    direction = "rising above" if predicted_ph > self.high_threshold else "falling below"
                    return self.current_status, (
                        f"EARLY WARNING: AI forecasts pH may trend toward "
                        f"{direction} safe range. Current: {ph_value:.2f}, "
                        f"Predicted: {predicted_ph:.2f}."
                    )

        # Risk-score-based escalation
        if risk_level == "CRITICAL":
            self.current_status = AlertStatus.CRITICAL
            return self.current_status, (
                f"CRITICAL risk level. pH: {ph_value:.2f}. "
                f"Risk score: {risk_total:.0f}/100."
            )
        elif risk_level == "HIGH":
            self.current_status = AlertStatus.HIGH_RISK
            return self.current_status, (
                f"HIGH RISK detected. pH: {ph_value:.2f}. "
                f"Risk score: {risk_total:.0f}/100."
            )
        elif risk_level == "ELEVATED" or anomaly_detected:
            self.current_status = AlertStatus.EARLY_WARNING
            msg = f"Elevated risk. pH: {ph_value:.2f}. Risk: {risk_total:.0f}/100."
            if anomaly_detected:
                msg += " Anomaly detected."
            return self.current_status, msg

        # Default
        self.current_status = threshold_status
        return threshold_status, threshold_msg

    def get_status(self) -> AlertStatus:
        return self.current_status

    def get_status_summary(self) -> dict:
        return {
            "status": self.current_status.value,
            "consecutive_low_count": self.consecutive_low_count,
            "consecutive_high_count": self.consecutive_high_count,
            "last_alert_time": (
                self.last_alert_time.isoformat() if self.last_alert_time else None
            ),
            "thresholds": {
                "low": self.low_threshold,
                "high": self.high_threshold,
            },
        }


if __name__ == "__main__":
    print("pH Alert Engine Demo")
    print("=" * 50)

    engine = PHAlertEngine(consecutive_count=3)

    test_readings = [
        (7.2, "Normal"),
        (6.9, "First low reading"),
        (6.8, "Second low reading"),
        (6.7, "Third low reading - should trigger alert"),
        (7.1, "Back to normal"),
        (8.6, "First high reading"),
        (8.7, "Second high reading"),
        (8.8, "Third high reading - should trigger alert"),
    ]

    for ph_value, description in test_readings:
        timestamp = datetime.now()
        status, message = engine.process_reading(timestamp, ph_value)
        print(f"pH: {ph_value:.2f} | {description}")
        print(f"  -> {message}")
        print()
