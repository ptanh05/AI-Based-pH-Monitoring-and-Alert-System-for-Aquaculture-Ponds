"""
Tests for Telegram / Email Notification Dispatcher.
"""

import pytest
from alerts.notification_dispatcher import NotificationDispatcher

def test_dispatcher_init():
    d = NotificationDispatcher(cooldown_seconds=10.0)
    assert not d.enabled
    assert d.cooldown_seconds == 10.0
    assert len(d.history) == 0

def test_dispatcher_config():
    d = NotificationDispatcher()
    d.configure(enabled=True, telegram_token="123:ABC", telegram_chat_id="999")
    cfg = d.get_config()
    assert cfg["enabled"] is True
    assert cfg["has_token"] is True
    assert cfg["chat_id"] == "999"

def test_dispatcher_mock_send():
    d = NotificationDispatcher(cooldown_seconds=5.0)
    d.configure(enabled=True)
    res = d.send_telegram_message("Test message")
    assert res["success"] is True
    assert res["mocked"] is True
    assert len(d.history) == 1

def test_dispatcher_cooldown():
    d = NotificationDispatcher(cooldown_seconds=60.0)
    d.configure(enabled=True)
    # Should allow first critical dispatch
    assert d.can_send("CRITICAL") is True
    d.dispatch_alert({
        "status": "CRITICAL",
        "ph_value": 6.2,
        "predicted_ph": 6.0,
        "risk_score": 85.0,
        "warning_message": "pH drop critical"
    })
    # Immediate subsequent normal check should be blocked by cooldown
    assert d.can_send("WARNING") is False
