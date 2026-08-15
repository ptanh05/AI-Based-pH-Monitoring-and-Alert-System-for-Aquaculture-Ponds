# FINAL REAL-WORLD DATA & ARCHITECTURAL AUDIT REPORT
## AI AQUACULTURE GUARDIAN
### Submission Candidate for Intel® Vietnam AI Impact Festival 2026

---

## 1. Executive Summary

This report documents the rigorous transition of **AI Aquaculture Guardian** into an empirically validated, edge-deployable AI system evaluated on **37,284 real-world tropical aquaculture IoT observations** (Mendeley Data DOI: [10.17632/8s73jfvgr5.2](https://doi.org/10.17632/8s73jfvgr5.2), CC BY 4.0).

### Key Transformation Metrics (BEFORE vs AFTER):
| Dimension | BEFORE (Initial Prototype) | AFTER (Competition-Grade System) |
|---|---|---|
| **Data Foundation** | Synthetic simulator only | **37,284 Real IoT observations + Synthetic simulator** |
| **Data Ingestion Layer** | None (Ad-hoc simulation loop) | **Standalone `data_pipeline/` package with universal loader & validator** |
| **Temporal Splitting** | Arbitrary slice | **Strict chronological 70/15/15 with zero temporal leakage** |
| **Multi-Step Horizon** | Uncalibrated steps | **Dynamic 5 / 25 / 75 / 150 minutes advance notice** |
| **AI vs Baseline (150 min)** | N/A (simulated only) | **+75.50% error reduction over baseline ($R^2 = 0.8425$ vs $-0.8400$)** |
| **Domain Shift Awareness** | Not measured | **Quantified $+300\%$ error degradation on zero-shot synthetic transfer** |
| **Automated Test Suite** | 91 passing tests | **123+ passing tests (100% GREEN)** |
| **Edge AI Compliance** | Preliminary | **P50 Latency: 0.28 ms, Throughput: > 3,000 FPS on CPU** |

---

## 2. Dataset Provenance, Schema & Integrity

- **Title**: *Environmental Parameters in Aquaculture: Temperature, pH, Oxygen, and Turbidity Measurements*
- **DOI**: [10.17632/8s73jfvgr5.2](https://doi.org/10.17632/8s73jfvgr5.2) — Version 2
- **License**: Creative Commons Attribution 4.0 International (CC BY 4.0)
- **Observations**: 37,284 raw records (51,831 regularized 5-minute time points)
- **Quality Audit**: 0 missing values, 0 timestamp duplicates, 0 physical boundary violations.

---

## 3. Real-World Multi-Step Forecasting Benchmark Matrix

Evaluated under strict chronological split on out-of-sample holdout test partition ($N = 7,773$):

| Horizon (Advance Notice) | Persistence Baseline MAE ($R^2$) | Linear Regression MAE ($R^2$) | HistGradientBoosting MAE ($R^2$) | Random Forest MAE ($R^2$) | AI Advantage over Baseline |
|---|:---:|:---:|:---:|:---:|:---:|
| **1-step (5 minutes)** | 0.0110 (0.9473) | 0.0143 (0.9392) | 0.0118 (0.9538) | **0.0095 (0.9591)** | **+13.91%** |
| **5-step (25 minutes)** | 0.0485 (0.6562) | 0.0618 (0.6698) | 0.0346 (0.8600) | **0.0204 (0.9207)** | **+57.87%** |
| **15-step (75 minutes)** | 0.1113 (-0.1176) | 0.1168 (0.2344) | 0.0629 (0.7266) | **0.0351 (0.8434)** | **+68.46%** |
| **30-step (150 minutes = 2.5h)** | 0.1559 (-0.8400) | 0.1236 (0.1266) | 0.0668 (0.6838) | **0.0382 (0.8425)** | **+75.50%** |

---

## 4. Domain Shift Analysis & Research Findings

| Domain Transfer Setup | 5-step MAE (25 min) | 15-step MAE (75 min) | 30-step MAE (150 min) | Research Verdict |
|---|:---:|:---:|:---:|---|
| **A. Real $\to$ Real (In-Domain)** | **0.0204** | **0.0351** | **0.0382** | Optimal Real Performance |
| **B. Synthetic $\to$ Synthetic** | 0.0003 | 0.0005 | 0.0002 | Idealized Mathematical Physics |
| **C. Synthetic $\to$ Real (Zero-Shot)** | 0.2365 | 0.3516 | 0.4457 | **Severe Domain Shift ($>300\%$ degradation)** |

> [!IMPORTANT]
> **Key Finding**: Synthetic simulation cannot replace real-world calibration. Real ponds exhibit complex unmodeled phytoplankton dynamics, feeding disturbances, and weather runoff. Our pipeline solves this by integrating local in-situ calibration (`data_pipeline/`).

---

## 5. Automated Test Suite Verification

```
pytest tests/ -v
================== 123 passed, 4 warnings in 75.74s (100% GREEN) ==================
```

All 123 test cases pass with zero failures:
- 15/15 original regression tests
- 57/57 AI Guardian pipeline & domain tests
- 22/22 REST API integration tests
- 29/29 real data pipeline, temporal split, leakage protection, domain shift, and anomaly validation tests.

---

## 6. Reproducibility Quick-Start Guide

```bash
# 1. Verify Dataset Integrity
python scripts/download_dataset.py --dataset mendeley_aquaculture

# 2. Profile Data Quality & Physical Validity
python scripts/profile_dataset.py --dataset mendeley_aquaculture

# 3. Regularize & Prepare 5-Minute Time Grid
python scripts/prepare_dataset.py --dataset mendeley_aquaculture

# 4. Train Config-Driven Model Version (v2.0)
python scripts/train_real_model.py --config configs/real_data.yaml

# 5. Evaluate Multi-Model Benchmarks
python scripts/evaluate_real_dataset.py --dataset mendeley_aquaculture

# 6. Evaluate Domain Shift
python scripts/evaluate_domain_shift.py

# 7. Run Edge Inference Benchmark
python scripts/benchmark_real_model.py

# 8. Run Streaming Playback Demo on Real Dataset (CLI)
python run_real_demo.py --dataset mendeley_aquaculture --max_readings 50 --speed 10

# 9. Run Deterministic Competition Demo (Live Presentation Mode)
python run_demo.py --scenario competition_demo --seed 42
```

---

## 7. Responsible AI & Limitations

1. **Advisory Decision Support**: AI outputs represent early-warning indicators, never automated chemical dosers.
2. **Environmental Threshold Tuning**: Farmers can tune threshold baselines (`configs/`) for specific species (e.g. Tilapia vs Whiteleg Shrimp).
3. **Data Provenance Transparency**: Dashboard and CLI explicitly flag data modes (`[ REAL DATA ]` vs `[ SYNTHETIC DEMO ]`).
