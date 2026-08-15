"""
Unit tests for multisensor correlation and cross-parameter validation.
"""

import pytest
import pandas as pd
from scripts.analyze_multisensor import analyze_multisensor, interpret_strength, get_biological_context


def test_interpret_strength():
    assert interpret_strength(0.05) == "Negligible / Uncorrelated"
    assert interpret_strength(0.25) == "Weak correlation"
    assert interpret_strength(0.45) == "Moderate correlation"
    assert interpret_strength(0.65) == "Strong correlation"
    assert interpret_strength(0.85) == "Very strong correlation"


def test_biological_context():
    ctx = get_biological_context("ph", "dissolved_oxygen", 0.5)
    assert "photosynthesis" in ctx.lower()
    ctx_temp = get_biological_context("temperature", "dissolved_oxygen", -0.3)
    assert "solubility" in ctx_temp.lower() or "temperature" in ctx_temp.lower()


def test_analyze_multisensor_execution():
    res = analyze_multisensor()
    assert "pearson_correlation_matrix" in res
    assert "spearman_correlation_matrix" in res
    assert "pairwise_relationships" in res
    assert "scientific_disclaimer" in res
    assert "ph" in res["pearson_correlation_matrix"]
    assert res["pearson_correlation_matrix"]["ph"]["ph"] == 1.0
