"""
Tests for Report & Data Export Generator.
"""

import pytest
from reports.report_generator import generate_csv_data, generate_html_report

def test_generate_csv():
    history = {
        "labels": ["12:00:00", "12:00:01"],
        "actual": [7.5, 7.6],
        "forecast": [7.52, 7.58],
        "upper": [8.5, 8.5],
        "lower": [7.0, 7.0],
        "risk": [12.0, 15.5]
    }
    csv_str = generate_csv_data(history)
    assert "Timestamp,Actual_pH,Predicted_pH" in csv_str
    assert "7.50" in csv_str
    assert "12.0" in csv_str

def test_generate_html_report():
    current = {
        "ph_value": 7.45,
        "predicted_ph": 7.50,
        "risk_score": 18.0,
        "status": "NORMAL",
        "temperature": 28.0,
        "do_value": 7.5,
        "turbidity": 3.8
    }
    history = {
        "actual": [7.4, 7.5, 7.45]
    }
    html = generate_html_report(current, history)
    assert "NHẬT KÝ GIÁM SÁT CHẤT LƯỢNG NƯỚC AO NUÔI" in html
    assert "7.45" in html
    assert "NORMAL" in html
