"""
Tests for AI Aquaculture Agronomist Chatbot.
"""

import pytest
from ai.chatbot_advisor import AquacultureChatbotAdvisor

def test_chatbot_prompts():
    bot = AquacultureChatbotAdvisor()
    prompts_vi = bot.get_quick_prompts("vi")
    prompts_en = bot.get_quick_prompts("en")
    assert len(prompts_vi) >= 4
    assert len(prompts_en) >= 4

def test_chatbot_lime_calculation():
    bot = AquacultureChatbotAdvisor()
    telemetry = {
        "ph_value": 6.8,
        "predicted_ph": 6.6,
        "risk_score": 65.0,
        "pond_volume_m3": 1000.0
    }
    ans = bot.answer_query("Cần bón bao nhiêu kg vôi cho ao này?", telemetry, lang="vi")
    assert ans["category"] == "lime_dosing"
    assert ans["calculated_kg"] > 0
    assert "CaCO₃" in ans["answer"]

def test_chatbot_risk_explanation():
    bot = AquacultureChatbotAdvisor()
    telemetry = {
        "ph_value": 8.9,
        "predicted_ph": 9.1,
        "risk_score": 80.0,
        "do_value": 4.5,
        "temperature": 31.0
    }
    ans = bot.answer_query("Tại sao rủi ro lại cao vậy?", telemetry, lang="vi")
    assert ans["category"] == "risk_explanation"
    assert "80.0" in ans["answer"]
