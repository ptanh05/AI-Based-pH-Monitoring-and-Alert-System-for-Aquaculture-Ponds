"""
pH Alert Engine for Aquaculture Monitoring System

This module implements threshold-based alerting logic that triggers
alerts when pH values exceed safe ranges for multiple consecutive readings.
"""

from enum import Enum
from typing import Optional, Tuple
from datetime import datetime


class AlertStatus(Enum):
    """Alert status enumeration."""
    NORMAL = "NORMAL"
    WAITING = "WAITING"
    ALERT_LOW_PH = "ALERT_LOW_PH"
    ALERT_HIGH_PH = "ALERT_HIGH_PH"


class PHAlertEngine:
    """
    Alert engine that monitors pH values and triggers alerts when
    pH exceeds safe thresholds for consecutive readings.
    
    Safe range: 7.0 ≤ pH ≤ 8.5
    Low pH alert: pH < 7.0
    High pH alert: pH > 8.5
    """
    
    def __init__(
        self,
        low_threshold: float = 7.0,
        high_threshold: float = 8.5,
        consecutive_count: int = 3
    ):
        """
        Initialize the alert engine.
        
        Args:
            low_threshold: Lower bound of safe pH range (default: 7.0)
            high_threshold: Upper bound of safe pH range (default: 8.5)
            consecutive_count: Number of consecutive out-of-range readings
                              required to trigger alert (default: 3)
        """
        self.low_threshold = low_threshold
        self.high_threshold = high_threshold
        self.consecutive_count = consecutive_count
        
        self.current_status = AlertStatus.NORMAL
        self.consecutive_low_count = 0
        self.consecutive_high_count = 0
        self.last_alert_time: Optional[datetime] = None
        
    def _is_low(self, ph_value: float) -> bool:
        """Check if pH is below safe range."""
        return ph_value < self.low_threshold
    
    def _is_high(self, ph_value: float) -> bool:
        """Check if pH is above safe range."""
        return ph_value > self.high_threshold
    
    def _is_safe(self, ph_value: float) -> bool:
        """Check if pH is within safe range."""
        return self.low_threshold <= ph_value <= self.high_threshold
    
    def process_reading(self, timestamp: datetime, ph_value: float) -> Tuple[AlertStatus, str]:
        """
        Process a new pH reading and determine alert status.
        
        Args:
            timestamp: Timestamp of the reading
            ph_value: pH value to check
            
        Returns:
            Tuple of (alert_status, message)
        """
        previous_status = self.current_status
        
        if self._is_low(ph_value):
            self.consecutive_low_count += 1
            self.consecutive_high_count = 0
            
            if self.consecutive_low_count >= self.consecutive_count:
                self.current_status = AlertStatus.ALERT_LOW_PH
                self.last_alert_time = timestamp
                message = (
                    f"⚠️ LOW pH ALERT: pH = {ph_value:.2f} "
                    f"(below safe threshold {self.low_threshold})"
                )
            else:
                self.current_status = AlertStatus.WAITING
                message = (
                    f"⏳ Waiting: pH = {ph_value:.2f} is low "
                    f"({self.consecutive_low_count}/{self.consecutive_count} consecutive readings)"
                )
                
        elif self._is_high(ph_value):
            self.consecutive_high_count += 1
            self.consecutive_low_count = 0
            
            if self.consecutive_high_count >= self.consecutive_count:
                self.current_status = AlertStatus.ALERT_HIGH_PH
                self.last_alert_time = timestamp
                message = (
                    f"⚠️ HIGH pH ALERT: pH = {ph_value:.2f} "
                    f"(above safe threshold {self.high_threshold})"
                )
            else:
                self.current_status = AlertStatus.WAITING
                message = (
                    f"⏳ Waiting: pH = {ph_value:.2f} is high "
                    f"({self.consecutive_high_count}/{self.consecutive_count} consecutive readings)"
                )
                
        else:  # pH is safe
            self.consecutive_low_count = 0
            self.consecutive_high_count = 0
            
            # Only change to NORMAL if we were in an alert state
            if previous_status in [AlertStatus.ALERT_LOW_PH, AlertStatus.ALERT_HIGH_PH]:
                self.current_status = AlertStatus.NORMAL
                message = f"✓ pH returned to safe range: {ph_value:.2f}"
            else:
                self.current_status = AlertStatus.NORMAL
                message = f"✓ Normal: pH = {ph_value:.2f}"
        
        return self.current_status, message
    
    def get_status(self) -> AlertStatus:
        """Get current alert status."""
        return self.current_status
    
    def get_status_summary(self) -> dict:
        """
        Get a summary of current alert engine state.
        
        Returns:
            Dictionary with status information
        """
        return {
            "status": self.current_status.value,
            "consecutive_low_count": self.consecutive_low_count,
            "consecutive_high_count": self.consecutive_high_count,
            "last_alert_time": self.last_alert_time.isoformat() if self.last_alert_time else None,
            "thresholds": {
                "low": self.low_threshold,
                "high": self.high_threshold
            }
        }


if __name__ == "__main__":
    # Demo: Test alert engine
    print("pH Alert Engine Demo")
    print("=" * 50)
    
    engine = PHAlertEngine(consecutive_count=3)
    
    # Simulate a sequence of readings
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
    
    from datetime import datetime
    
    for ph_value, description in test_readings:
        timestamp = datetime.now()
        status, message = engine.process_reading(timestamp, ph_value)
        print(f"pH: {ph_value:.2f} | {description}")
        print(f"  → {message}")
        print()

