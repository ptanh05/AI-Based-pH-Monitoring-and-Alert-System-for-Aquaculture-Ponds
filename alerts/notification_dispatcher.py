"""
Notification Dispatcher Module for AI Aquaculture Guardian.

Supports:
- Telegram Bot API notification dispatching
- Cooldown & anti-spam rate limiting
- Configurable chat_id and bot_token
- Test notification triggers
"""

import time
import json
import logging
import urllib.request
import urllib.parse
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class NotificationDispatcher:
    def __init__(self, cooldown_seconds: float = 60.0):
        self.cooldown_seconds = cooldown_seconds
        self.last_sent_time = 0.0
        self.last_sent_status: Optional[str] = None
        self.enabled: bool = False
        self.telegram_token: str = ""
        self.telegram_chat_id: str = ""
        self.email_address: str = ""
        self.history: list = []

    def configure(self, enabled: bool, telegram_token: str = "", telegram_chat_id: str = "", email: str = ""):
        self.enabled = enabled
        if telegram_token is not None:
            self.telegram_token = telegram_token.strip()
        if telegram_chat_id is not None:
            self.telegram_chat_id = telegram_chat_id.strip()
        if email is not None:
            self.email_address = email.strip()

    def get_config(self) -> Dict[str, Any]:
        return {
            "enabled": self.enabled,
            "has_token": bool(self.telegram_token),
            "chat_id": self.telegram_chat_id,
            "email": self.email_address,
            "last_sent_time": self.last_sent_time,
            "history_count": len(self.history),
        }

    def can_send(self, status: str) -> bool:
        if not self.enabled:
            return False
        now = time.time()
        # Allow sending immediately if status is worse, otherwise respect cooldown
        if status in ("CRITICAL", "ALERT_LOW_PH", "ALERT_HIGH_PH"):
            if now - self.last_sent_time >= min(self.cooldown_seconds, 30.0):
                return True
        elif now - self.last_sent_time >= self.cooldown_seconds:
            return True
        return False

    def send_telegram_message(self, message: str) -> Dict[str, Any]:
        """Send message via Telegram Bot API or mock if no token configured."""
        record = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "channel": "telegram",
            "message": message,
            "status": "success",
        }
        
        if not self.telegram_token or not self.telegram_chat_id:
            # Simulated send when no credentials provided
            record["mocked"] = True
            record["status"] = "simulated_success"
            self.history.append(record)
            self.last_sent_time = time.time()
            return {
                "success": True, 
                "mocked": True, 
                "message": "Đã gửi thông báo mô phỏng (Chưa cấu hình Telegram Bot Token thực tế)."
            }

        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            data = urllib.parse.urlencode({
                "chat_id": self.telegram_chat_id,
                "text": message,
                "parse_mode": "Markdown"
            }).encode("utf-8")
            
            req = urllib.request.Request(url, data=data, headers={"User-Agent": "AIAquacultureGuardian/1.0"})
            with urllib.request.urlopen(req, timeout=5) as response:
                res_body = response.read().decode("utf-8")
                res_json = json.loads(res_body)
                if res_json.get("ok"):
                    self.history.append(record)
                    self.last_sent_time = time.time()
                    return {"success": True, "mocked": False, "message": "Gửi Telegram thành công!"}
                else:
                    record["status"] = "error"
                    record["error"] = res_json.get("description", "Lỗi phản hồi từ Telegram")
                    self.history.append(record)
                    return {"success": False, "error": record["error"]}
        except Exception as e:
            logger.warning(f"Telegram dispatch failed: {e}")
            record["status"] = "error"
            record["error"] = str(e)
            self.history.append(record)
            return {"success": False, "error": str(e)}

    def dispatch_alert(self, current_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        status = current_data.get("alert_status") or current_data.get("status", "NORMAL")
        if status == "NORMAL" or not self.can_send(status):
            return None

        ph = current_data.get("ph_value", 0.0)
        pred = current_data.get("predicted_ph", 0.0)
        risk = current_data.get("risk_score", 0.0)
        warning_msg = current_data.get("warning_message", "")

        msg = (
            f"🚨 *CẢNH BÁO CHẤT LƯỢNG NƯỚC AO NUÔI*\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"• *Trạng thái:* `{status}`\n"
            f"• *pH Hiện tại:* `{ph:.2f}`\n"
            f"• *AI Dự báo pH:* `{pred:.2f}`\n"
            f"• *Điểm rủi ro:* `{risk:.1f}/100`\n"
            f"• *Chi tiết:* {warning_msg}\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"⏰ *Thời gian:* {time.strftime('%H:%M:%S %d/%m/%Y')}\n"
            f"💡 *Hành động:* Vui lòng kiểm tra ao nuôi và hệ thống sục khí ngay."
        )

        res = self.send_telegram_message(msg)
        self.last_sent_status = status
        return res

# Global dispatcher instance
dispatcher = NotificationDispatcher()
