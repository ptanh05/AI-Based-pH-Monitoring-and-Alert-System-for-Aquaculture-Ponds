"""
Internationalization (i18n) Module for AI Aquaculture Guardian.
Supports Vietnamese (vi) and English (en).
"""

from typing import Dict, Any, List, Optional

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    # ── Status & Risk Levels ──
    "NORMAL": {"en": "NORMAL", "vi": "BÌNH THƯỜNG"},
    "WAITING": {"en": "WAITING", "vi": "ĐANG CHỜ"},
    "EARLY_WARNING": {"en": "EARLY WARNING", "vi": "CẢNH BÁO SỚM"},
    "HIGH_RISK": {"en": "HIGH RISK", "vi": "RỦI RO CAO"},
    "CRITICAL": {"en": "CRITICAL", "vi": "NGUY CẤP"},
    "ALERT_LOW_PH": {"en": "LOW pH ALERT", "vi": "CẢNH BÁO pH THẤP"},
    "ALERT_HIGH_PH": {"en": "HIGH pH ALERT", "vi": "CẢNH BÁO pH CAO"},
    "SENSOR_WARNING": {"en": "SENSOR WARNING", "vi": "CẢNH BÁO CẢM BIẾN"},
    
    "LOW": {"en": "LOW", "vi": "THẤP"},
    "MODERATE": {"en": "MODERATE", "vi": "TRUNG BÌNH"},
    "ELEVATED": {"en": "ELEVATED", "vi": "TĂNG CAO"},
    "HIGH": {"en": "HIGH", "vi": "CAO"},
    
    # ── Urgency ──
    "urgency_critical": {"en": "CRITICAL", "vi": "KHẨN CẤP"},
    "urgency_high": {"en": "HIGH", "vi": "CAO"},
    "urgency_medium": {"en": "MEDIUM", "vi": "TRUNG BÌNH"},
    "urgency_low": {"en": "LOW", "vi": "THẤP"},
    "urgency_info": {"en": "INFO", "vi": "THÔNG TIN"},

    # ── CLI & Headers ──
    "cli_title": {
        "en": "AI AQUACULTURE GUARDIAN — Competition Demo",
        "vi": "AI AQUACULTURE GUARDIAN — Trình diễn Mô phỏng AI Nuôi Trồng Thủy Sản"
    },
    "cli_subtitle": {
        "en": "AI-Powered Early Warning System for Sustainable Aquaculture",
        "vi": "Hệ thống Cảnh báo Sớm ứng dụng AI cho Nuôi trồng Thủy sản Bền vững"
    },
    "scenario": {"en": "Scenario", "vi": "Kịch bản"},
    "seed": {"en": "Seed", "vi": "Hạt giống ngẫu nhiên (Seed)"},
    "readings": {"en": "Readings", "vi": "Số mẫu đo"},
    "interval": {"en": "Interval", "vi": "Khoảng thời gian"},
    "data_simulated": {"en": "SIMULATED (not real sensor)", "vi": "MÔ PHỎNG (Dữ liệu giả lập)"},
    "data_real": {"en": "REAL-WORLD DATASET", "vi": "DỮ LIỆU THỰC TẾ (IoT)"},
    "demo_complete": {"en": "Demo Complete", "vi": "Hoàn tất Mô phỏng"},
    "why": {"en": "WHY", "vi": "TẠI SAO"},
    "action": {"en": "ACTION", "vi": "HÀNH ĐỘNG"},
}

# Regex / Substring translation dictionary for Explainability reasons & recommendations
PHRASE_TRANSLATIONS_VI = [
    # Reasons
    ("Current pH", "Độ pH hiện tại"),
    ("is below the safe threshold", "thấp hơn ngưỡng an toàn"),
    ("is above the safe threshold", "vượt quá ngưỡng an toàn"),
    ("is approaching the upper safety threshold", "đang tiệm cận ngưỡng an toàn trên"),
    ("is approaching the lower safety threshold", "đang tiệm cận ngưỡng an toàn dưới"),
    ("AI forecasts pH rising to", "AI dự báo pH sẽ tăng lên mức"),
    ("AI forecasts pH dropping to", "AI dự báo pH sẽ giảm xuống mức"),
    ("AI forecasts pH approaching the upper threshold", "AI dự báo pH đang tiệm cận ngưỡng cảnh báo trên"),
    ("AI forecasts pH approaching the lower threshold", "AI dự báo pH đang tiệm cận ngưỡng cảnh báo dưới"),
    ("which exceeds the upper safe threshold", "vượt quá ngưỡng an toàn trên"),
    ("which is below the lower safe threshold", "thấp hơn ngưỡng an toàn dưới"),
    ("pH is rising rapidly", "Độ pH đang tăng rất nhanh"),
    ("pH is falling rapidly", "Độ pH đang giảm rất nhanh"),
    ("rate:", "tốc độ:"),
    ("per reading", "mỗi chu kỳ đo"),
    ("Sustained upward trend detected", "Phát hiện xu hướng tăng liên tục"),
    ("Sustained downward trend detected", "Phát hiện xu hướng giảm liên tục"),
    ("slope:", "độ dốc:"),
    ("Statistical anomaly detected", "Phát hiện bất thường thống kê"),
    ("z-score:", "điểm z-score:"),
    ("ML anomaly detected by Isolation Forest", "Phát hiện bất thường ML bởi Isolation Forest"),
    ("Elevated risk.", "Rủi ro tăng cao."),
    ("Risk:", "Điểm rủi ro:"),
    ("Anomaly detected.", "Phát hiện bất thường."),

    # Recommendations & Actions
    ("Maintain regular monitoring schedule.", "Duy trì lịch theo dõi và giám sát định kỳ."),
    ("Continue monitoring water quality closely.", "Tiếp tục theo dõi chặt chẽ chất lượng nước."),
    ("Verify sensor measurements immediately with a backup measurement device.", "Kiểm tra đối chứng ngay lập tức bằng thiết bị đo dự phòng."),
    ("Notify the responsible operator or farm manager.", "Thông báo ngay cho người quản lý ao hoặc kỹ thuật viên."),
    ("Follow your farm's established emergency procedures for high pH events.", "Thực hiện quy trình khẩn cấp theo tiêu chuẩn của trang trại khi pH tăng cao."),
    ("Follow your farm's established emergency procedures for low pH events.", "Thực hiện quy trình khẩn cấp theo tiêu chuẩn của trang trại khi pH giảm thấp."),
    ("Consider increasing mechanical aeration to promote gas exchange.", "Cân nhắc tăng cường quạt nước / sục khí cơ học để thúc đẩy trao đổi khí."),
    ("Prepare water exchange if supported by farm design.", "Chuẩn bị phương án cấp/thay nước nếu điều kiện ao cho phép."),
    ("Check for signs of phytoplankton bloom (color change, high midday DO).", "Kiểm tra dấu hiệu bùng phát tảo (đổi màu nước, DO tăng cao giữa trưa)."),
    ("Sensor quality is degraded — verify physical sensor before acting on readings.", "Chất lượng cảm biến suy giảm — hãy kiểm tra đầu dò trước khi thực hiện can thiệp."),
    ("Sensor appears stuck (constant readings). Clean or recalibrate the sensor probe.", "Cảm biến có dấu hiệu bị treo (giá trị không đổi). Hãy vệ sinh hoặc hiệu chuẩn lại đầu dò."),
]


def t(key: str, lang: str = "vi") -> str:
    """Translate a simple key."""
    if key in TRANSLATIONS:
        return TRANSLATIONS[key].get(lang, TRANSLATIONS[key].get("en", key))
    return key


def translate_text(text: str, lang: str = "vi") -> str:
    """Translate complex reason or recommendation text."""
    if lang == "en" or not text:
        return text
    
    result = text
    for en_phrase, vi_phrase in PHRASE_TRANSLATIONS_VI:
        result = result.replace(en_phrase, vi_phrase)
    return result
