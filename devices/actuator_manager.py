"""
IoT Actuators & Automation Engine for Aquaculture Ponds.

Manages automated and manual control of:
1. Paddlewheel Aerators (Quạt nước oxy)
2. Water Exchange Pump (Máy bơm nước cấp)
3. Lime Dispenser (Máy xả vôi trung hòa pH)
"""

import time
from typing import Dict, Any, List

class ActuatorManager:
    def __init__(self):
        self.mode: str = "AUTO"  # "AUTO" or "MANUAL"
        self.devices = {
            "aerator": {
                "id": "aerator",
                "name": "Quạt nước Oxy (Aerator)",
                "power_kw": 1.5,
                "is_on": True,
                "last_toggle": time.time(),
                "reason": "Duy trì nồng độ oxy hòa tan định kỳ",
            },
            "pump": {
                "id": "pump",
                "name": "Bơm nước tuần hoàn (Water Pump)",
                "power_kw": 2.2,
                "is_on": False,
                "last_toggle": time.time(),
                "reason": "Chờ lệnh điều tiết",
            },
            "lime": {
                "id": "lime",
                "name": "Máy xả vôi trung hòa (Lime Dispenser)",
                "power_kw": 0.75,
                "is_on": False,
                "last_toggle": time.time(),
                "reason": "Độ pH ở mức bình thường",
            }
        }
        self.logs: List[Dict[str, Any]] = [
            {
                "timestamp": time.strftime("%H:%M:%S"),
                "device": "aerator",
                "action": "ON",
                "trigger": "Khởi tạo hệ thống tự động",
                "mode": "AUTO"
            }
        ]

    def set_mode(self, mode: str) -> str:
        if mode.upper() in ("AUTO", "MANUAL"):
            self.mode = mode.upper()
            self._add_log("system", f"Chuyển sang chế độ {self.mode}", "Người dùng thao tác")
        return self.mode

    def toggle_device(self, device_id: str, state: bool = None, reason: str = "") -> bool:
        if device_id in self.devices:
            dev = self.devices[device_id]
            new_state = (not dev["is_on"]) if state is None else state
            if dev["is_on"] != new_state:
                dev["is_on"] = new_state
                dev["last_toggle"] = time.time()
                dev["reason"] = reason or ("Bật thủ công" if new_state else "Tắt thủ công")
                self._add_log(device_id, "ON" if new_state else "OFF", dev["reason"])
            return dev["is_on"]
        return False

    def evaluate_conditions(self, current_data: Dict[str, Any]):
        """Evaluate AI conditions in AUTO mode and trigger actuators accordingly."""
        if self.mode != "AUTO":
            return

        ph = current_data.get("ph_value", 7.5)
        pred_ph = current_data.get("predicted_ph", 7.5)
        risk = current_data.get("risk_score", 0.0)
        status = current_data.get("alert_status") or current_data.get("status", "NORMAL")
        do_val = current_data.get("do_value", 7.5)
        turbidity = current_data.get("turbidity", 5.0)

        # 1. Aerator evaluation
        if do_val < 6.0 or risk > 30.0 or status in ("HIGH_RISK", "CRITICAL", "ALERT_LOW_PH", "ALERT_HIGH_PH"):
            if not self.devices["aerator"]["is_on"]:
                self.toggle_device("aerator", True, "Tự động: Oxy giảm hoặc Rủi ro tăng")
        elif do_val >= 7.8 and risk < 15.0 and status == "NORMAL":
            # Keep aerator in eco mode but allow periodic runs
            pass

        # 2. Water Pump evaluation
        if status in ("CRITICAL", "HIGH_RISK") or turbidity > 15.0:
            if not self.devices["pump"]["is_on"]:
                self.toggle_device("pump", True, "Tự động: Điều hòa nước & giảm độ đục")
        elif status == "NORMAL" and turbidity <= 8.0:
            if self.devices["pump"]["is_on"]:
                self.toggle_device("pump", False, "Tự động: Chất lượng nước đã ổn định")

        # 3. Lime Dispenser evaluation
        if ph < 7.1 or pred_ph < 7.0 or status == "ALERT_LOW_PH":
            if not self.devices["lime"]["is_on"]:
                self.toggle_device("lime", True, "Tự động: Cấp vôi trung hòa pH thấp")
        elif ph >= 7.4:
            if self.devices["lime"]["is_on"]:
                self.toggle_device("lime", False, "Tự động: pH đã cân bằng")

    def get_status(self) -> Dict[str, Any]:
        total_kw = sum(d["power_kw"] for d in self.devices.values() if d["is_on"])
        active_count = sum(1 for d in self.devices.values() if d["is_on"])
        return {
            "mode": self.mode,
            "total_power_kw": round(total_kw, 2),
            "active_devices_count": active_count,
            "devices": self.devices,
            "recent_logs": self.logs[-10:],
        }

    def _add_log(self, device: str, action: str, trigger: str):
        self.logs.append({
            "timestamp": time.strftime("%H:%M:%S"),
            "device": device,
            "action": action,
            "trigger": trigger,
            "mode": self.mode
        })
        if len(self.logs) > 50:
            self.logs = self.logs[-50:]

# Global actuator manager instance
actuator_manager = ActuatorManager()
