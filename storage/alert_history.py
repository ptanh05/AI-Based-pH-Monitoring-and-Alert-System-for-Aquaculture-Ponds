"""
Alert History Storage Module

Lưu trữ lịch sử các cảnh báo khi pH vượt quá giới hạn.
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path


class AlertHistory:
    """
    Quản lý lịch sử cảnh báo pH.
    Lưu trữ vào file JSON.
    """
    
    def __init__(self, storage_file: str = "data/alert_history.json"):
        """
        Initialize alert history storage.
        
        Args:
            storage_file: Path to JSON file for storing alerts
        """
        self.storage_file = storage_file
        self.storage_path = Path(storage_file)
        
        # Tạo thư mục nếu chưa có
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing alerts
        self.alerts = self._load_alerts()
    
    def _load_alerts(self) -> List[Dict]:
        """Load alerts from JSON file."""
        if not self.storage_path.exists():
            return []
        
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('alerts', [])
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load alert history: {e}")
            return []
    
    def _save_alerts(self):
        """Save alerts to JSON file."""
        try:
            data = {
                'last_updated': datetime.now().isoformat(),
                'total_alerts': len(self.alerts),
                'alerts': self.alerts
            }
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving alert history: {e}")
    
    def add_alert(
        self,
        timestamp: datetime,
        ph_value: float,
        alert_type: str,
        predicted_ph: Optional[float] = None,
        threshold_low: Optional[float] = None,
        threshold_high: Optional[float] = None,
        message: Optional[str] = None
    ):
        """
        Add a new alert to history.
        
        Args:
            timestamp: Timestamp of the alert
            ph_value: pH value that triggered the alert
            alert_type: Type of alert ('ALERT_LOW_PH' or 'ALERT_HIGH_PH')
            predicted_ph: Predicted pH value (optional)
            threshold_low: Lower threshold (optional)
            threshold_high: Upper threshold (optional)
            message: Alert message (optional)
        """
        alert_record = {
            'id': len(self.alerts) + 1,
            'timestamp': timestamp.isoformat(),
            'ph_value': round(ph_value, 2),
            'alert_type': alert_type,
            'predicted_ph': round(predicted_ph, 2) if predicted_ph else None,
            'threshold_low': threshold_low,
            'threshold_high': threshold_high,
            'message': message
        }
        
        self.alerts.append(alert_record)
        
        # Giữ tối đa 1000 alerts (xóa các alert cũ nhất nếu vượt quá)
        if len(self.alerts) > 1000:
            self.alerts = self.alerts[-1000:]
        
        self._save_alerts()
    
    def get_recent_alerts(self, limit: int = 50) -> List[Dict]:
        """
        Get recent alerts.
        
        Args:
            limit: Maximum number of alerts to return
            
        Returns:
            List of alert records (most recent first)
        """
        return list(reversed(self.alerts[-limit:]))
    
    def get_alerts_by_type(self, alert_type: str, limit: int = 50) -> List[Dict]:
        """
        Get alerts filtered by type.
        
        Args:
            alert_type: 'ALERT_LOW_PH' or 'ALERT_HIGH_PH'
            limit: Maximum number of alerts to return
            
        Returns:
            List of filtered alert records
        """
        filtered = [a for a in self.alerts if a['alert_type'] == alert_type]
        return list(reversed(filtered[-limit:]))
    
    def get_statistics(self) -> Dict:
        """
        Get statistics about alerts.
        
        Returns:
            Dictionary with statistics
        """
        total = len(self.alerts)
        low_alerts = len([a for a in self.alerts if a['alert_type'] == 'ALERT_LOW_PH'])
        high_alerts = len([a for a in self.alerts if a['alert_type'] == 'ALERT_HIGH_PH'])
        
        return {
            'total_alerts': total,
            'low_ph_alerts': low_alerts,
            'high_ph_alerts': high_alerts,
            'last_alert_time': self.alerts[-1]['timestamp'] if self.alerts else None
        }
    
    def clear_history(self):
        """Clear all alert history."""
        self.alerts = []
        self._save_alerts()


# Global instance
alert_history = AlertHistory()

