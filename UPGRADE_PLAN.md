# AI AQUACULTURE GUARDIAN: UPGRADE PLAN
**AI-Powered Early Warning and Decision-Support System for Sustainable Aquaculture**
*Intel® Vietnam AI Impact Festival 2026 — Theme: "Enriching Lives with AI Innovation"*

---

## 1. Executive Summary & Context

The current repository (`AI-Based-pH-Monitoring-and-Alert-System-for-Aquaculture-Ponds`) provides a foundational pH monitoring and basic linear/Random Forest prediction prototype. 

To become a **competition-ready prototype** for the **Intel® Vietnam AI Impact Festival 2026**, the system will be elevated from a simple "pH predictor" to an **intelligent early-warning and decision-support pipeline** with Edge AI acceleration (Intel® OpenVINO™), multi-faceted risk scoring, anomaly detection, explainable alerts, actionable farmer guidance, and reproducible competition demo scenarios.

---

## 2. Repository Audit Findings

### 2.1 Current Strengths
- **Clean Architecture & Separation of Concerns**: Modular components (`simulator`, `ai`, `alerts`, `api`, `storage`, `dashboard`).
- **Operational Backend**: FastAPI asynchronous web server with background daemon monitoring thread and CORS middleware.
- **State Machine Protection**: `PHAlertEngine` uses consecutive reading counts to prevent false triggers from single sensor spikes.
- **Functional Baseline**: 15 unit tests passing cleanly out-of-the-box.
- **Lightweight Dependencies**: Easily runnable in standard Python 3.10+ environments.

### 2.2 Current Weaknesses & Technical Debt
1. **Artificial Prediction Mutation**: `ph_predictor.py` contains hardcoded offsets (`abs(predicted - current) < 0.02 -> force ±0.05`) which breaks scientific validity.
2. **Horizon Inconsistency**: Mixed references to `10 seconds` vs `30 minutes` across simulator intervals and output messages.
3. **Absence of Anomaly Detection**: No statistical/machine-learning anomaly detection for rapid shifts, high variance, or flatlined sensors before thresholds are breached.
4. **No Multi-Factor Risk Scoring**: Alerting is binary (safe vs breached) without a continuous, weighted 0–100 Aquaculture Risk Index.
5. **No Explainability (XAI)**: Alerts state "pH is low/high" without detailing feature contributions, rates of change, or model reasoning.
6. **No Actionable Recommendations**: Lacks structured farmer guidance or standard operating procedures (SOP).
7. **No Intel® OpenVINO™ / Edge AI Layer**: Inference runs solely on standard Python/scikit-learn without Intel CPU/NPU optimization or benchmarking.
8. **Stochastic-Only Simulator**: No deterministic scenarios (`RAPID_PH_RISE`, `HEAVY_RAIN`, `SENSOR_ANOMALY`, `RECOVERY`) with reproducible seeds for video recording and jury evaluation.
9. **Encoding Fragility on Windows**: Vietnamese stdout logging causes `UnicodeEncodeError` in standard `cp1252` PowerShell unless UTF-8 streams are explicitly configured.

---

## 3. Competition Gaps & Target State

| Dimension | Current State | Competition Target State (AI Aquaculture Guardian) |
|---|---|---|
| **Value Proposition** | pH measurement & simple prediction | Comprehensive early warning, anomaly detection, risk quantification & farm decision support |
| **Forecasting** | Single-step scalar prediction (with forced noise) | Multi-step horizon forecasting (5m, 15m, 30m) with genuine regression & confidence bounds |
| **Anomaly Detection** | None | Hybrid statistical (Z-Score/IQR) & Isolation Forest anomaly detection with root cause tagging |
| **Risk Scoring** | Boolean alert states (Normal / Alert) | Weighted 0–100 Aquaculture Risk Index (Deviation + Trend + Anomaly + Forecast) |
| **Explainability** | Raw values only | Feature importance + natural-language explanation cards ("Why is risk elevated?") |
| **Decision Support** | None | Safe, practical farmer recommendations categorized by risk level & environmental drivers |
| **Edge AI / Intel** | Unoptimized scikit-learn | Intel® OpenVINO™ inference engine adapter, ONNX export, and reproducible benchmark script |
| **Demo Quality** | Random live stream | Deterministic scenario runner (`--scenario rapid_ph_rise`, `--seed 42`) + Web UI scenario switcher |
| **Multi-Sensor Design** | Hardcoded pH only | Extensible `SensorReading` schema supporting pH, Temperature, DO, Turbidity, ORP |
| **Documentation & Ethics** | Generic README | `ARCHITECTURE.md`, `MODEL_CARD.md`, `RESPONSIBLE_AI.md`, & complete `competition/` submission pack |

---

## 4. Proposed Architecture & Pipeline

```
[Simulated Sensors / Real Sensor Ingestion] (pH, Temp, DO)
                       │
                       ▼
            [Data Ingestion & Validation]
        (Sensor Quality, Range Check, Anti-Glitch)
                       │
                       ▼
          [Feature Engineering Pipeline]
    (Rolling Stats, Rate of Change, Accel, Day Cycle)
                       │
        ┌──────────────┴──────────────┐
        ▼                             ▼
 [AI Multi-Step Forecast]   [Anomaly Detection Engine]
  (Sklearn / OpenVINO)       (Z-Score / Isolation Forest)
        └──────────────┬──────────────┘
                       │
                       ▼
             [Aquaculture Risk Engine]
   (0-100 Score: Threshold + Trend + Anomaly + Forecast)
                       │
                       ▼
            [Early Warning State Machine]
      (NORMAL / WAITING / EARLY_WARNING / ALERT / CRITICAL)
                       │
        ┌──────────────┴──────────────┐
        ▼                             ▼
 [AI Explainability (XAI)]   [Decision-Support Engine]
 (Why? Feature Contributions) (Actionable SOP Guidance)
        └──────────────┬──────────────┘
                       │
                       ▼
          [REST API (FastAPI) & Web UI]
   (Real-time Dashboard, Benchmark, Scenario Demo)
```

---

## 5. File Modification & Creation Plan

### 5.1 New Files to Create
- **AI Core Modules**:
  - `ai/sensor_schema.py`: Universal `SensorReading`, data quality validation, and multi-sensor models.
  - `ai/features.py`: Dedicated feature engineering pipeline (rolling mean/std/min/max, velocity, acceleration, cyclic time).
  - `ai/forecasting.py`: Multi-step horizon forecaster with model training & persistence.
  - `ai/anomaly.py`: Statistical Z-Score/IQR & Isolation Forest anomaly detector.
  - `ai/risk.py`: 0–100 Aquaculture Risk Index calculator with configurable weights.
  - `ai/explainability.py`: Rule-based & feature contribution explainability generator.
  - `ai/recommendations.py`: Decision-support guidance generator tailored for aquaculture farmers.
- **Edge AI & Intel Integration**:
  - `edge/base_engine.py`: Abstract base class `BaseInferenceEngine`.
  - `edge/sklearn_engine.py`: Default Scikit-Learn inference backend.
  - `edge/openvino_engine.py`: Intel® OpenVINO™ inference backend with ONNX model export & fallback.
  - `edge/benchmark.py`: Inference latency (P50/P95/P99), throughput, and memory benchmark script.
- **Data & Dataset Management**:
  - `data/dataset_loader.py`: `SyntheticDataLoader` & `CSVDataLoader` for training/testing datasets.
  - `scripts/evaluate_model.py`: Rigorous model evaluation script reporting MAE, RMSE, R², and train/test split.
  - `scripts/run_demo.py`: Standalone CLI demo runner for competition presentations.
- **Documentation & Competition Material**:
  - `ARCHITECTURE.md`: Complete system architecture and Edge AI pipeline documentation.
  - `MODEL_CARD.md`: Transparent AI model documentation (inputs, outputs, synthetic data disclosure, limits).
  - `RESPONSIBLE_AI.md`: Ethics, human-in-the-loop safety, failure modes, and environmental disclaimer.
  - `competition/project_summary.md`
  - `competition/150_word_description.md`
  - `competition/video_script.md`
  - `competition/impact_statement.md`
  - `competition/technical_highlights.md`
  - `competition/demo_script.md`
  - `competition/submission_checklist.md`
- **Unit & Integration Tests**:
  - `tests/test_features.py`
  - `tests/test_anomaly.py`
  - `tests/test_risk.py`
  - `tests/test_edge_engine.py`
  - `tests/test_recommendations.py`
  - `tests/test_scenarios.py`

### 5.2 Existing Files to Refactor (Backward-Compatible)
- `simulator/ph_simulator.py`: Add deterministic scenario presets (`NORMAL`, `RAPID_PH_RISE`, `RAPID_PH_DROP`, `HEAVY_RAIN`, `HEAT_EVENT`, `SENSOR_ANOMALY`, `RECOVERY`) and seed support.
- `alerts/ph_alert_engine.py`: Upgrade state machine to support `EARLY_WARNING`, `HIGH_RISK`, and `CRITICAL` levels.
- `ai/ph_predictor.py`: Refactor to wrap the new modular pipeline while retaining backward-compatible signatures.
- `api/server.py`: Expose new endpoints (`/api/risk`, `/api/anomalies`, `/api/recommendations`, `/api/explanation`, `/api/forecast`, `/api/benchmark`, `/api/scenario`, `/api/inference-engine`).
- `dashboard/index.html`: Elevate UI into a competition-grade dashboard with modern design, risk gauge, anomaly telemetry, "Why?" explainability card, actionable guidance, and scenario switcher.
- `main.py`: Fix Windows stdout UTF-8 encoding, support `--scenario` and `--demo` flags.
- `README.md`: Rewrite into a professional, competition-ready project presentation.

---

## 6. Phased Implementation Roadmap

* **PHASE 0: Audit, Test Baseline, and Upgrade Plan** (Completed)
* **PHASE 1: AI Core & Multi-Step Forecasting Pipeline** (Features, Forecaster, Validation)
* **PHASE 2: Anomaly Detection & Aquaculture Risk Scoring Engine** (0–100 Index)
* **PHASE 3: AI Explainability (XAI) & Actionable Decision Support** (Recommendations)
* **PHASE 4: Intel® OpenVINO™ Edge AI Acceleration & Benchmark Suite**
* **PHASE 5: Scenario Simulator & Competition Demo Mode**
* **PHASE 6: REST API Expansion & Competition Web Dashboard**
* **PHASE 7: Comprehensive Unit & Integration Testing**
* **PHASE 8: Competition Submission Pack & Professional Documentation**

---

## 7. Risk Management & Mitigations

| Risk | Probability | Impact | Mitigation Strategy |
|---|---|---|---|
| Breaking existing test suite / API | Low | High | Maintain adapter layer in `ai/ph_predictor.py` and preserve existing API routes |
| OpenVINO environment mismatch | Low | Medium | Factory pattern with automatic fallback to `SklearnInferenceEngine` |
| Over-promising real-world claims | Medium | High | Explicit synthetic data notices and strict Responsible AI disclaimers |
| Windows terminal encoding glitches | High | Low | Explicit `sys.stdout.reconfigure(encoding='utf-8')` on CLI entry points |
