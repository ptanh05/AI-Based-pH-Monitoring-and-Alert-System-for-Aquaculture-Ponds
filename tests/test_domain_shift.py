"""
Unit tests for domain shift analysis.
"""

import pytest
import numpy as np
import pandas as pd
from scripts.evaluate_domain_shift import evaluate_domain_shift


def test_evaluate_domain_shift():
    report = evaluate_domain_shift()
    assert "experiments" in report
    assert "1_step" in report["experiments"]
    assert "real_to_real" in report["experiments"]["1_step"]
    assert "syn_to_real_transfer" in report["experiments"]["1_step"]
    assert "performance_degradation_pct" in report["experiments"]["1_step"]
