"""
AI Aquaculture Agronomist & Decision Support Chatbot.

Provides real-time expert aquaculture guidance, chemical dosing calculations
(CaCO3/CaO), and context-aware explanations of sensor telemetry.
"""

import re
from typing import Dict, Any, List

class AquacultureChatbotAdvisor:
    def __init__(self):
        self.knowledge_base = {
            "lime": {
                "keywords": ["vôi", "lime", "caco3", "canxi", "bón vôi", "tăng ph"],
                "formula": "Lượng vôi cần bón: m = ΔpH × V_ao × 0.025 (kg)",
            },
            "oxygen": {
                "keywords": ["oxy", "do", "ngộp", "nổi đầu", "quạt nước", "sục khí", "thở"],
                "threshold": "DO an toàn > 5.0 mg/L. Nếu DO < 4.0 mg/L cần bật quạt nước ngay.",
            },
            "rain": {
                "keywords": ["mưa", "rain", "axit", "rửa trôi", "mưa lớn"],
                "guide": "Sau mưa lớn: Rải vôi xung quanh bờ ao (10-20kg/100m bờ), bật quạt nước để chống phân tầng nhiệt độ.",
            },
            "heat": {
                "keywords": ["nắng", "nóng", "nhiệt độ", "heat", "tảo"],
                "guide": "Trời nắng gắt: pH tăng cao vào 14h do tảo quang hợp mạnh. Giảm 20-30% lượng thức ăn để tránh dư thừa.",
            }
        }

    def get_quick_prompts(self, lang: str = "vi") -> List[str]:
        if lang == "en":
            return [
                "Calculate required lime dosage for current pond",
                "Why is the risk score high right now?",
                "Action plan for upcoming rain event",
                "How to balance dissolved oxygen at night?"
            ]
        return [
            "Tính lượng vôi cần bón cho ao hiện tại",
            "Giải thích mức độ rủi ro hiện tại của ao",
            "Kế hoạch xử lý khi trời mưa lớn",
            "Làm sao để cân bằng oxy hòa tan ban đêm?"
        ]

    def answer_query(self, user_query: str, current_telemetry: Dict[str, Any], lang: str = "vi") -> Dict[str, Any]:
        """Process user query and return intelligent, context-aware answer."""
        q = user_query.lower().strip()
        ph = current_telemetry.get("ph_value", 7.5)
        pred_ph = current_telemetry.get("predicted_ph", 7.5)
        risk = current_telemetry.get("risk_score", 0.0)
        do_val = current_telemetry.get("do_value", 7.5)
        temp = current_telemetry.get("temperature", 28.0)
        vol = current_telemetry.get("pond_volume_m3", 1000.0)

        # 1. Lime calculation query
        if any(k in q for k in ["vôi", "lime", "caco3", "bón"]):
            target_ph = 7.8
            if ph < target_ph:
                delta = target_ph - ph
                # Standard aquaculture rule: ~20-30kg CaCO3 per 1000m3 per 0.5 pH drop
                lime_kg = round(delta * (vol / 1000.0) * 50.0, 1)
                lime_cao = round(lime_kg * 0.6, 1)
                
                if lang == "en":
                    msg = (
                        f"🧮 **Lime Dosage Calculation for Pond ({vol:,.0f} m³):**\n\n"
                        f"• Current pH: **{ph:.2f}** | Target pH: **{target_ph:.1f}** (ΔpH = +{delta:.2f})\n"
                        f"• **Recommended Agricultural Lime (CaCO₃):** **{lime_kg} kg**\n"
                        f"• *Alternative (Quicklime CaO for severe drops):* **{lime_cao} kg**\n\n"
                        f"💡 **Application Method:** Dissolve lime in water and splash evenly around the pond perimeter at 8:00 AM - 10:00 AM while running paddlewheel aerators."
                    )
                else:
                    msg = (
                        f"🧮 **Công thức Tính Liều Lượng Vôi Cho Ao ({vol:,.0f} m³):**\n\n"
                        f"• pH hiện tại: **{ph:.2f}** | pH mục tiêu: **{target_ph:.1f}** (Cần nâng: +{delta:.2f})\n"
                        f"• **Lượng vôi nông nghiệp (CaCO₃) khuyến nghị:** **{lime_kg} kg**\n"
                        f"• *Hoặc vôi nung (CaO - dùng khi tụt pH gấp):* **{lime_cao} kg**\n\n"
                        f"💡 **Cách bón chuẩn kỹ thuật:** Hòa tan vôi với nước sạch rồi tạt đều quanh bờ ao vào lúc 8h - 10h sáng khi quạt nước đang hoạt động để hòa tan tối đa."
                    )
            else:
                msg = (
                    f"✅ Độ pH hiện tại là **{ph:.2f}** (nằm trong ngưỡng tối ưu 7.5 - 8.5). "
                    f"Hiện tại **chưa cần bón thêm vôi**. Hãy tiếp tục theo dõi biến thiên theo chu kỳ dự báo của AI."
                    if lang == "vi" else
                    f"✅ Current pH is **{ph:.2f}** (within optimal 7.5 - 8.5 range). No additional lime required right now."
                )

            return {"answer": msg, "category": "lime_dosing", "calculated_kg": lime_kg if ph < target_ph else 0}

        # 2. Risk & Telemetry explanation
        if any(k in q for k in ["rủi ro", "nguy cơ", "tại sao", "risk", "why"]):
            if lang == "en":
                msg = (
                    f"📊 **Current Pond AI Diagnostic Report:**\n\n"
                    f"• **Risk Score:** `{risk:.1f}/100` ({'🟢 Low' if risk < 30 else '🟡 Warning' if risk < 70 else '🔴 Critical'})\n"
                    f"• **Sensor pH:** `{ph:.2f}` → **AI Forecast pH:** `{pred_ph:.2f}`\n"
                    f"• **Dissolved Oxygen (DO):** `{do_val:.1f} mg/L` | **Water Temp:** `{temp:.1f} °C`\n\n"
                    f"🔍 **Key Factor:** " + (
                        "All parameters are optimal." if risk < 30 else
                        "pH or Oxygen volatility detected. Proactive aeration recommended."
                    )
                )
            else:
                msg = (
                    f"📊 **Báo cáo Chẩn đoán AI Thời gian thực:**\n\n"
                    f"• **Điểm rủi ro tổng hợp:** `{risk:.1f}/100` ({'🟢 An toàn' if risk < 30 else '🟡 Chú ý theo dõi' if risk < 70 else '🔴 Nguy cấp'})\n"
                    f"• **pH Cảm biến:** `{ph:.2f}` → **AI Dự báo tương lai:** `{pred_ph:.2f}`\n"
                    f"• **Oxy hòa tan (DO):** `{do_val:.1f} mg/L` | **Nhiệt độ nước:** `{temp:.1f} °C`\n\n"
                    f"🔍 **Đánh giá AI:** " + (
                        "Chất lượng nước ao ổn định, các chỉ số sinh hóa đều trong dải tối ưu." if risk < 30 else
                        f"Phát hiện rủi ro biến động pH ({ph:.2f}) hoặc DO ({do_val:.1f} mg/L). Đã kích hoạt cơ chế điều tiết tự động."
                    )
                )
            return {"answer": msg, "category": "risk_explanation"}

        # 3. Rain & Storm handling
        if any(k in q for k in ["mưa", "rain", "bão", "storm"]):
            msg = (
                "🌧️ **Quy trình chuẩn bị & Xử lý sự kiện mưa lớn:**\n\n"
                "1. **Trước khi mưa:** Rải vôi nông nghiệp (CaCO₃) 15-20 kg/100m quanh bờ ao để chống xói mòn và rửa trôi phèn.\n"
                "2. **Trong khi mưa:** Bật 100% quạt nước để tránh hiện tượng phân tầng nhiệt độ và phân tầng oxy.\n"
                "3. **Sau khi mưa:** Xả lớp nước mặt trên cùng, đo lại pH và bón vôi bù khoáng nếu pH giảm dưới 7.2."
                if lang == "vi" else
                "🌧️ **Heavy Rain Management Protocol:**\n\n"
                "1. Spread agricultural lime around pond dikes to prevent acid runoff.\n"
                "2. Run paddlewheel aerators to prevent thermal and oxygen stratification.\n"
                "3. Drain surface rainwater and measure pH immediately."
            )
            return {"answer": msg, "category": "rain_protocol"}

        # 4. General fallback with intelligent context
        msg = (
            f"🤖 **Trợ lý AI Thủy sản:** Tôi đang theo dõi ao nuôi với pH={ph:.2f}, DO={do_val:.1f} mg/L, Rủi ro={risk:.1f}/100. "
            f"Bạn có thể hỏi tôi về: *Tính lượng vôi bón*, *Hướng dẫn xử lý khi trời mưa*, *Cách quản lý oxy ban đêm*, hoặc *Giải thích các chỉ số AI*."
            if lang == "vi" else
            f"🤖 **AI Aquaculture Assistant:** Monitoring pond with pH={ph:.2f}, DO={do_val:.1f} mg/L, Risk={risk:.1f}/100. "
            f"You can ask me to calculate lime dosage, explain risk factors, or guide emergency actions."
        )
        return {"answer": msg, "category": "general"}

# Global chatbot advisor instance
chatbot_advisor = AquacultureChatbotAdvisor()
