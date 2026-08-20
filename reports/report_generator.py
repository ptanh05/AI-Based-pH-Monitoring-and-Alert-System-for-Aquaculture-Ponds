"""
Report & Data Export Generator for AI Aquaculture Guardian.

Generates:
1. CSV/Excel data streams for sensor and AI history
2. Professional VietGAP/GlobalGAP Printable HTML/PDF Audit Reports
"""

import io
import csv
import time
from typing import Dict, Any, List

def generate_csv_data(history_buffer: Dict[str, List]) -> str:
    """Generate CSV string from history buffer."""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Headers
    writer.writerow([
        "Timestamp",
        "Actual_pH",
        "Predicted_pH",
        "Safe_Upper_Limit",
        "Safe_Lower_Limit",
        "Risk_Score_0_to_100",
        "Status"
    ])
    
    labels = history_buffer.get("labels", [])
    actual = history_buffer.get("actual", [])
    forecast = history_buffer.get("forecast", [])
    upper = history_buffer.get("upper", [])
    lower = history_buffer.get("lower", [])
    risk = history_buffer.get("risk", [])
    
    for i in range(len(labels)):
        writer.writerow([
            labels[i] if i < len(labels) else "",
            f"{actual[i]:.2f}" if i < len(actual) else "",
            f"{forecast[i]:.2f}" if i < len(forecast) else "",
            f"{upper[i]:.2f}" if i < len(upper) else "8.50",
            f"{lower[i]:.2f}" if i < len(lower) else "7.00",
            f"{risk[i]:.1f}" if i < len(risk) else "0.0",
            "NORMAL" if (i < len(risk) and risk[i] < 30) else "ELEVATED_RISK"
        ])
        
    return output.getvalue()


def generate_html_report(current_data: Dict[str, Any], history_buffer: Dict[str, List], actuators_info: Dict[str, Any] = None) -> str:
    """Generate printable HTML report for audit & PDF printing."""
    now_str = time.strftime("%d/%m/%Y %H:%M:%S")
    ph = current_data.get("ph_value", 7.5)
    pred_ph = current_data.get("predicted_ph", 7.5)
    risk = current_data.get("risk_score", 0.0)
    status = current_data.get("alert_status") or current_data.get("status", "NORMAL")
    pond_name = current_data.get("pond_id", "POND-01 (Ao nuôi cá/tôm thử nghiệm)")
    temp = current_data.get("temperature", 27.5)
    do_val = current_data.get("do_value", 7.8)
    turb = current_data.get("turbidity", 4.2)
    warning = current_data.get("warning_message", "Tất cả các thông số đều nằm trong ngưỡng an toàn.")
    
    actual_list = history_buffer.get("actual", [])
    avg_ph = sum(actual_list) / len(actual_list) if actual_list else ph
    min_ph = min(actual_list) if actual_list else ph
    max_ph = max(actual_list) if actual_list else ph
    total_samples = len(actual_list)

    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Báo Cáo Nhật Ký Giám Sát Chất Lượng Nước - AI Aquaculture Guardian</title>
    <style>
        @page {{ size: A4; margin: 15mm; }}
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            color: #1e293b;
            background: #fff;
            margin: 0;
            padding: 24px;
            font-size: 13px;
            line-height: 1.5;
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid #0284c7;
            padding-bottom: 12px;
            margin-bottom: 20px;
        }}
        .logo-title h1 {{
            margin: 0 0 4px 0;
            font-size: 20px;
            color: #0369a1;
        }}
        .logo-title p {{
            margin: 0;
            font-size: 12px;
            color: #64748b;
        }}
        .badge {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 4px;
            font-weight: bold;
            font-size: 12px;
        }}
        .badge-safe {{ background: #dcfce7; color: #166534; }}
        .badge-warn {{ background: #fef3c7; color: #92400e; }}
        .badge-crit {{ background: #fee2e2; color: #991b1b; }}
        
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 12px;
            margin-bottom: 20px;
        }}
        .kpi-card {{
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 12px;
            background: #f8fafc;
            text-align: center;
        }}
        .kpi-val {{
            font-size: 18px;
            font-weight: 700;
            color: #0f172a;
            margin: 4px 0;
        }}
        .kpi-lbl {{
            font-size: 11px;
            color: #64748b;
            text-transform: uppercase;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 16px 0;
            font-size: 12px;
        }}
        th, td {{
            border: 1px solid #cbd5e1;
            padding: 8px 10px;
            text-align: left;
        }}
        th {{
            background: #f1f5f9;
            color: #334155;
            font-weight: 600;
        }}
        
        .section-title {{
            font-size: 14px;
            font-weight: 700;
            color: #0f172a;
            margin-top: 24px;
            margin-bottom: 8px;
            border-left: 4px solid #0284c7;
            padding-left: 8px;
        }}
        .print-btn-bar {{
            margin-bottom: 20px;
            padding: 10px;
            background: #e0f2fe;
            border-radius: 6px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .btn {{
            background: #0284c7;
            color: #fff;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            font-weight: 600;
        }}
        .btn:hover {{ background: #0369a1; }}
        @media print {{
            .print-btn-bar {{ display: none; }}
            body {{ padding: 0; }}
        }}
        .footer {{
            margin-top: 40px;
            display: flex;
            justify-content: space-between;
            padding-top: 20px;
            border-top: 1px dashed #cbd5e1;
        }}
        .signature-box {{
            text-align: center;
            width: 200px;
        }}
    </style>
</head>
<body>
    <div class="print-btn-bar">
        <span>📄 <strong>Báo cáo nhật ký giám sát chất lượng nước</strong> (Sẵn sàng in hoặc Lưu thành file PDF)</span>
        <button class="btn" onclick="window.print()">🖨️ In / Lưu PDF (Ctrl + P)</button>
    </div>

    <div class="header">
        <div class="logo-title">
            <h1>🐟 NHẬT KÝ GIÁM SÁT CHẤT LƯỢNG NƯỚC AO NUÔI</h1>
            <p>Hệ thống Giám sát & Cảnh báo Sớm AI Đa Bước (AI Aquaculture Guardian)</p>
        </div>
        <div style="text-align: right;">
            <div><strong>Mã ao:</strong> {pond_name}</div>
            <div style="color:#64748b; font-size:11px;">Thời gian xuất: {now_str}</div>
        </div>
    </div>

    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="kpi-lbl">pH Hiện tại</div>
            <div class="kpi-val" style="color:#0284c7">{ph:.2f}</div>
            <div style="font-size:10px;color:#64748b">Ngưỡng chuẩn: 7.0 - 8.5</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-lbl">AI Dự báo (Đa bước)</div>
            <div class="kpi-val" style="color:#0d9488">{pred_ph:.2f}</div>
            <div style="font-size:10px;color:#64748b">RandomForest / OpenVINO</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-lbl">Điểm rủi ro tổng hợp</div>
            <div class="kpi-val" style="color:{'#16a34a' if risk < 30 else '#ea580c' if risk < 70 else '#dc2626'}">{risk:.1f}/100</div>
            <div style="font-size:10px;color:#64748b">Trọng số 4 yếu tố</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-lbl">Trạng thái vận hành</div>
            <div class="kpi-val" style="font-size:14px; margin-top:8px;">
                <span class="badge {'badge-safe' if status == 'NORMAL' else 'badge-crit' if 'CRITICAL' in status or 'ALERT' in status else 'badge-warn'}">
                    {status}
                </span>
            </div>
        </div>
    </div>

    <div class="section-title">1. Thông số Cảm biến Đa chỉ tiêu Hiện tại</div>
    <table>
        <thead>
            <tr>
                <th>Chỉ số</th>
                <th>Giá trị đo</th>
                <th>Dải an toàn tiêu chuẩn</th>
                <th>Đánh giá chất lượng</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>Độ pH (Đầu dò công nghiệp)</strong></td>
                <td>{ph:.2f}</td>
                <td>7.0 - 8.5</td>
                <td>{'✅ Đạt chuẩn' if 7.0 <= ph <= 8.5 else '⚠️ Cần điều chỉnh'}</td>
            </tr>
            <tr>
                <td><strong>Nhiệt độ nước (°C)</strong></td>
                <td>{temp:.1f} °C</td>
                <td>26.0 - 32.0 °C</td>
                <td>{'✅ Đạt chuẩn nhiệt đới' if 26 <= temp <= 32 else '⚠️ Ngoài khoảng tối ưu'}</td>
            </tr>
            <tr>
                <td><strong>Oxy hòa tan (DO - mg/L)</strong></td>
                <td>{do_val:.1f} mg/L</td>
                <td>&gt; 5.0 mg/L</td>
                <td>{'✅ Đạt chuẩn hô hấp tốt' if do_val >= 5.0 else '🚨 Nguy cơ thiếu oxy'}</td>
            </tr>
            <tr>
                <td><strong>Độ đục quang học (NTU)</strong></td>
                <td>{turb:.1f} NTU</td>
                <td>&lt; 20.0 NTU</td>
                <td>{'✅ Nước trong sạch' if turb <= 20 else '⚠️ Phù sa / Tảo bùng phát'}</td>
            </tr>
        </tbody>
    </table>

    <div class="section-title">2. Thống kê & Phân tích Chuỗi Lịch sử (Tổng số mẫu: {total_samples})</div>
    <table>
        <thead>
            <tr>
                <th>pH Trung bình</th>
                <th>pH Thấp nhất</th>
                <th>pH Cao nhất</th>
                <th>Mức độ cảnh báo</th>
                <th>Tóm tắt chẩn đoán AI</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>{avg_ph:.2f}</strong></td>
                <td><span style="color:#b91c1c">{min_ph:.2f}</span></td>
                <td><span style="color:#1d4ed8">{max_ph:.2f}</span></td>
                <td><strong>{status}</strong></td>
                <td>{warning}</td>
            </tr>
        </tbody>
    </table>

    <div class="section-title">3. Khuyến nghị Hỗ trợ Quyết định (Decision Support)</div>
    <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px; padding:12px; margin-top:8px;">
        <ul style="margin:0; padding-left:20px;">
            <li>Duy trì giám sát liên tục theo chu kỳ dự báo đa bước của AI.</li>
            <li>Đảm bảo hệ thống quạt nước và sục khí hoạt động ổn định khi rủi ro tăng cao.</li>
            <li>Kiểm tra và hiệu chuẩn đầu dò định kỳ để duy trì độ tin cậy của thuật toán học máy.</li>
        </ul>
    </div>

    <div class="footer">
        <div class="signature-box">
            <p><strong>Người lập báo cáo</strong></p>
            <br><br>
            <p>Hệ thống AI Tự động</p>
        </div>
        <div class="signature-box">
            <p><strong>Kỹ sư Thủy sản phụ trách</strong></p>
            <br><br>
            <p><i>(Ký và ghi rõ họ tên)</i></p>
        </div>
    </div>
</body>
</html>"""
