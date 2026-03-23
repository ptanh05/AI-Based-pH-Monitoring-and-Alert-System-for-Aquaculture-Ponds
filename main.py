"""
Main Entry Point for pH Monitoring and Alert System

This script orchestrates the entire monitoring system:
- pH data simulator
- Alert engine
- AI prediction module
- Logging and output
"""

# PEAS description for AI pH Monitoring Agent
PEAS = {
    "Performance": [
        "Dự đoán pH tương lai với sai số thấp (MAE/RMSE nhỏ)",
        "Phát hiện kịp thời các trường hợp pH vượt ngưỡng an toàn",
        "Giảm số lần cảnh báo giả (false alarm)",
        "Cung cấp cảnh báo sớm khi pH có xu hướng vượt ngưỡng"
    ],
    "Environment": [
        "Môi trường: ao nuôi thủy sản thực tế",
        "pH biến động theo thời gian (ngày/đêm, mưa, nắng, hoạt động sinh học)",
        "Trong demo: môi trường được mô phỏng bởi PHSimulator (noise + event mưa/nắng)"
    ],
    "Actuators": [
        "Cảnh báo âm thanh (beep) khi pH vượt ngưỡng",
        "Cảnh báo trực quan qua console log / dashboard web",
        "Trong tương lai có thể mở rộng sang điều khiển bơm/thiết bị xử lý nước"
    ],
    "Sensors": [
        "Nguồn dữ liệu pH từ cảm biến thực (tích hợp sau) hoặc simulator",
        "Trong code hiện tại: PHSimulator (tự sinh pH) và API /api/submit-ph (nhập tay)",
        "Hệ thống coi mỗi giá trị pH theo thời gian là một observation từ sensor"
    ],
}

import time
import sys
import platform
import threading
from datetime import datetime
from typing import Optional

from simulator.ph_simulator import PHSimulator
from alerts.ph_alert_engine import PHAlertEngine, AlertStatus
from ai.ph_predictor import PHPredictor

# Import beep function based on OS
try:
    if platform.system() == 'Windows':
        import winsound
        def play_beep(duration_seconds=3):
            """Play beep sound on Windows."""
            winsound.Beep(1000, int(duration_seconds * 1000))
    else:
        def play_beep(duration_seconds=3):
            """Play beep sound on Linux/Mac."""
            import os
            for _ in range(int(duration_seconds * 2)):
                print('\a', end='', flush=True)
                time.sleep(0.5)
except ImportError:
    def play_beep(duration_seconds=3):
        """Fallback beep."""
        for _ in range(int(duration_seconds * 2)):
            print('\a', end='', flush=True)
            time.sleep(0.5)


class PHMonitoringSystem:
    """
    Main monitoring system that coordinates all components.
    """
    
    def __init__(
        self,
        reading_interval_seconds: float = 5.0,
        low_threshold: float = 7.0,
        high_threshold: float = 8.5,
        consecutive_count: int = 3,
        prediction_horizon_minutes: int = 30
    ):
        """
        Initialize the monitoring system.
        
        Args:
            reading_interval_seconds: Time between readings (default: 5.0)
            low_threshold: Lower pH threshold (default: 7.0)
            high_threshold: Upper pH threshold (default: 8.5)
            consecutive_count: Consecutive readings for alert (default: 3)
            prediction_horizon_minutes: Prediction horizon in minutes (default: 30)
        """
        self.reading_interval = reading_interval_seconds
        
        # Initialize components
        self.simulator = PHSimulator(base_ph=7.5, enable_events=True)
        self.alert_engine = PHAlertEngine(
            low_threshold=low_threshold,
            high_threshold=high_threshold,
            consecutive_count=consecutive_count
        )
        self.predictor = PHPredictor(
            prediction_horizon_minutes=prediction_horizon_minutes,
            min_samples_for_training=30
        )
        
        self.reading_count = 0
        self.start_time = datetime.now()
    
    def format_timestamp(self, timestamp: datetime) -> str:
        """Format timestamp for display."""
        return timestamp.strftime("%H:%M:%S")
    
    def print_header(self):
        """Print system startup header."""
        print("\n" + "=" * 70)
        print("  Hệ thống Giám sát và Cảnh báo pH dựa trên AI cho Ao Nuôi Thủy Sản")
        print("=" * 70)
        print(f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Reading Interval: {self.reading_interval} seconds")
        print(f"Safe pH Range: {self.alert_engine.low_threshold} - {self.alert_engine.high_threshold}")
        print(f"Alert Threshold: {self.alert_engine.consecutive_count} consecutive out-of-range readings")
        print(f"Prediction Horizon: {self.predictor.prediction_horizon_minutes} minutes")
        print("=" * 70 + "\n")
    
    def process_reading(self, timestamp: datetime, ph_value: float):
        """
        Process a single pH reading through all system components.
        
        Args:
            timestamp: Reading timestamp
            ph_value: pH value
        """
        self.reading_count += 1
        
        # Add to predictor history
        self.predictor.add_reading(timestamp, ph_value)
        
        # Check alert status
        alert_status, alert_message = self.alert_engine.process_reading(timestamp, ph_value)
        
        # Get AI prediction
        predicted_ph, is_reliable = self.predictor.predict(ph_value)
        
        # Check early warning
        has_early_warning, warning_message = self.predictor.check_early_warning(
            predicted_ph,
            self.alert_engine.low_threshold,
            self.alert_engine.high_threshold
        )
        
        # Format output
        status_icon = {
            AlertStatus.NORMAL: "✓",
            AlertStatus.WAITING: "⏳",
            AlertStatus.ALERT_LOW_PH: "⚠️",
            AlertStatus.ALERT_HIGH_PH: "⚠️"
        }.get(alert_status, "?")
        
        # Print reading information
        print(f"[{self.reading_count:4d}] {self.format_timestamp(timestamp)} | "
              f"pH: {ph_value:5.2f} | Status: {status_icon} {alert_status.value}")
        
        # Print alert message if not normal
        if alert_status != AlertStatus.NORMAL:
            print(f"         → {alert_message}")
            # Simple audible beep on alert (may depend on terminal support)
            print("\a", end="", flush=True)
        
        # Print prediction
        reliability_indicator = "✓" if is_reliable else "~"
        print(f"         → Prediction ({self.predictor.prediction_horizon_minutes}m): "
              f"{predicted_ph:.2f} {reliability_indicator}")
        
        # Print early warning if applicable
        if has_early_warning:
            print(f"         → {warning_message}")
        
        # Phát tiếng beep dài khi có cảnh báo
        if alert_status in [AlertStatus.ALERT_LOW_PH, AlertStatus.ALERT_HIGH_PH]:
            import random
            beep_duration = random.uniform(2.0, 4.0)
            # Chạy beep trong thread riêng để không block
            beep_thread = threading.Thread(
                target=play_beep,
                args=(beep_duration,),
                daemon=True
            )
            beep_thread.start()
        
        print()
    
    def run(self, max_readings: Optional[int] = None, duration_minutes: Optional[float] = None):
        """
        Run the monitoring system.
        
        Args:
            max_readings: Maximum number of readings (None = infinite)
            duration_minutes: Maximum duration in minutes (None = infinite)
        """
        self.print_header()
        
        end_time = None
        if duration_minutes:
            from datetime import timedelta
            end_time = self.start_time + timedelta(minutes=duration_minutes)
        
        try:
            for timestamp, ph_value in self.simulator.stream_readings(
                interval_seconds=self.reading_interval,
                max_readings=max_readings
            ):
                # Check duration limit
                if end_time and datetime.now() >= end_time:
                    print(f"\n⏱️  Duration limit reached ({duration_minutes} minutes)")
                    break
                
                self.process_reading(timestamp, ph_value)
                
        except KeyboardInterrupt:
            print("\n\n⚠️  Monitoring stopped by user")
        
        self.print_summary()
    
    def print_summary(self):
        """Print system summary statistics."""
        duration = datetime.now() - self.start_time
        
        print("\n" + "=" * 70)
        print("  System Summary")
        print("=" * 70)
        print(f"Total Readings: {self.reading_count}")
        print(f"Duration: {duration}")
        print(f"Final Status: {self.alert_engine.get_status().value}")
        print(f"Model Info: {self.predictor.get_model_info()}")
        print("=" * 70 + "\n")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Hệ thống Giám sát và Cảnh báo pH dựa trên AI cho Ao Nuôi Thủy Sản"
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=5.0,
        help="Reading interval in seconds (default: 5.0)"
    )
    parser.add_argument(
        "--low-threshold",
        type=float,
        default=7.0,
        help="Lower pH threshold (default: 7.0)"
    )
    parser.add_argument(
        "--high-threshold",
        type=float,
        default=8.5,
        help="Upper pH threshold (default: 8.5)"
    )
    parser.add_argument(
        "--consecutive",
        type=int,
        default=1,
        help="Consecutive readings for alert (default: 1 = cảnh báo ngay)"
    )
    parser.add_argument(
        "--max-readings",
        type=int,
        default=None,
        help="Maximum number of readings (default: infinite)"
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=None,
        help="Maximum duration in minutes (default: infinite)"
    )
    
    args = parser.parse_args()
    
    # Create and run system
    system = PHMonitoringSystem(
        reading_interval_seconds=args.interval,
        low_threshold=args.low_threshold,
        high_threshold=args.high_threshold,
        consecutive_count=args.consecutive,
        prediction_horizon_minutes=30
    )
    
    system.run(max_readings=args.max_readings, duration_minutes=args.duration)


if __name__ == "__main__":
    main()

