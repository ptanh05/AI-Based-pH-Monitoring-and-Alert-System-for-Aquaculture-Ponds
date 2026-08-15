# AI Aquaculture Guardian
## AI-Powered Early Warning System for Sustainable Aquaculture

> Submission for **Intel® Vietnam AI Impact Festival 2026**
> Theme: *"Enriching Lives with AI Innovation"*

---

## Overview

AI Aquaculture Guardian is an intelligent monitoring system that uses machine learning to predict water quality problems in aquaculture ponds **before they occur**, enabling farmers to protect their livestock and livelihoods through early intervention.

### The Problem

pH fluctuations in aquaculture ponds can cause mass fish die-offs within hours. Traditional monitoring only alerts farmers **after** dangerous conditions have already developed — often too late to prevent losses.

### Our Solution

A complete AI pipeline that:
1. **Forecasts** pH changes 5-30 steps ahead using Random Forest models
2. **Detects anomalies** using hybrid Z-Score + Isolation Forest analysis
3. **Scores risk** transparently on a 0-100 scale with component breakdown
4. **Explains** every alert in human-readable language
5. **Recommends** safe, conservative actions for farmers
6. **Runs efficiently** on edge hardware via Intel® OpenVINO™ optimization

---

## Architecture

```
Sensor Data → Validation → Feature Engineering → Forecasting
                                                      ↓
Risk Scoring ← Anomaly Detection ← Isolation Forest / Z-Score
      ↓
Early Warning Engine → Explainability → Recommendations
      ↓
Dashboard / API / Alerts
```

### AI Pipeline Modules

| Module | File | Purpose |
|--------|------|---------|
| Sensor Schema | `ai/sensor_schema.py` | Input validation, quality monitoring |
| Feature Engineering | `ai/features.py` | Rolling stats, trend, acceleration, time encoding |
| Forecasting | `ai/forecasting.py` | Multi-step pH prediction with Random Forest |
| Anomaly Detection | `ai/anomaly.py` | Hybrid Z-Score + Isolation Forest |
| Risk Scoring | `ai/risk.py` | Transparent 0-100 risk score |
| Explainability | `ai/explainability.py` | Human-readable alert reasoning |
| Recommendations | `ai/recommendations.py` | Safe, actionable guidance |
| Edge Inference | `edge/inference_engine.py` | OpenVINO integration with sklearn fallback |
| Alert Engine | `alerts/ph_alert_engine.py` | Multi-state early warning system |
| Simulator | `simulator/ph_simulator.py` | 8 deterministic scenarios |

---

### Three Data Source Modes

1. **🎯 DEMO MODE (Deterministic Simulator)**: 8 reproducible scenarios (`--scenario competition_demo --seed 42`).
2. **🌊 REAL DATA VALIDATION MODE**: 37,284 high-resolution IoT observations from tropical Tilapia ponds (Mendeley Data DOI: [10.17632/8s73jfvgr5.2](https://doi.org/10.17632/8s73jfvgr5.2)).
3. **📡 LIVE SENSOR / GATEWAY MODE**: Live telemetry ingestion from edge hardware probes or manual API input.

---

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the CLI competition demo (deterministic, reproducible)
python run_demo.py --scenario competition_demo --seed 42

# Start the web dashboard (with Demo, Real-Data, and Live-Sensor switcher)
python run_demo.py --web

# Run all 108 automated unit and integration tests
python -m pytest tests/ -v

# Run Real-World Dataset Validation & 3-Way Benchmark
python scripts/evaluate_real_forecasting.py

# Run Real-World Dataset Quality Audit
python scripts/audit_real_dataset.py

# Run Multisensor Correlation & Ecological Analysis
python scripts/analyze_multisensor.py
```

### Web Dashboard
Open `http://localhost:8000` to interact with the real-time AI dashboard, risk score telemetry, and XAI reasoning.

Open `http://localhost:8000` after starting the web server. The dashboard features:
- Real-time pH monitoring with forecast overlay
- Risk score gauge with component breakdown
- AI explainability panel ("Why is this alert happening?")
- Actionable recommendations for farmers
- Scenario switcher for live demos
- Sensor health monitoring
- Model performance metrics

---

## Demo Scenarios

| Scenario | Description |
|----------|-------------|
| `normal` | Stable pH around 7.5 |
| `rapid_ph_rise` | pH climbs toward/above upper threshold |
| `rapid_ph_drop` | pH drops toward/below lower threshold |
| `heavy_rain` | Simulates acidic rain event |
| `heat_event` | Algal bloom pH increase |
| `sensor_anomaly` | Stuck sensor + glitch readings |
| `recovery` | pH returns to normal after stress |
| `competition_demo` | Full arc: normal → rise → critical → recovery |

All scenarios are **deterministic** with the same seed, ensuring reproducible demos.

---

## Model Performance

> **IMPORTANT**: All metrics below are evaluated on **synthetic simulator data**, not real-world sensor data. They demonstrate the model's ability to learn patterns from the simulator, not real-world aquaculture performance.

### Forecasting Accuracy (competition_demo scenario, seed=42)

| Horizon | Model MAE | Model RMSE | Model R² | Baseline MAE | Baseline R² |
|---------|-----------|------------|----------|--------------|-------------|
| 1-step  | 0.0038    | 0.0076     | 0.9998   | 0.0558       | 0.9581      |
| 5-step  | 0.0031    | 0.0047     | 0.9999   | 0.1503       | 0.7837      |
| 15-step | 0.0033    | 0.0058     | 0.9999   | 0.4291       | 0.0154      |
| 30-step | 0.0040    | 0.0068     | 0.9999   | 0.8453       | -1.5641     |

The Random Forest model significantly outperforms the persistence baseline at all horizons, particularly at longer prediction windows where the baseline fails.

---

## Intel® OpenVINO™ Integration

The system includes an honest OpenVINO integration:

- **Architecture**: `sklearn → ONNX (via skl2onnx) → OpenVINO IR → CPU Inference`
- **Current Status**: Tree ensemble models (RandomForest) are not yet natively supported by OpenVINO's ONNX frontend. The system **gracefully falls back to sklearn** when conversion fails.
- **Future Path**: When OpenVINO adds tree model support, or if we migrate to neural network models, the inference engine will automatically use OpenVINO acceleration.
- **Abstraction**: The `BaseInferenceEngine` interface allows swapping backends without changing application code.

We do **not** fake OpenVINO benchmarks or claim unsupported optimizations.

---

## Ethical Commitments

1. **No fabricated metrics**: All accuracy claims are backed by reproducible evaluation scripts
2. **Synthetic data transparency**: The system clearly labels all data as simulated
3. **Safe recommendations**: Never prescribes chemical dosages or claims veterinary authority
4. **Prediction vs. measurement**: The system never confuses "AI predicts" with "pH has exceeded"
5. **Sensor validation**: Distinguishes sensor problems from water quality issues
6. **Honest edge AI**: Reports actual OpenVINO conversion status, doesn't fake acceleration

---

## Project Structure

```
AI-Based-pH-Monitoring-and-Alert-System-for-Aquaculture-Ponds/
├── ai/                          # AI Pipeline
│   ├── sensor_schema.py         # Sensor validation & quality monitoring
│   ├── features.py              # Feature engineering pipeline
│   ├── forecasting.py           # Multi-step forecasting engine
│   ├── anomaly.py               # Anomaly detection (Z-Score + IF)
│   ├── risk.py                  # Risk scoring engine
│   ├── explainability.py        # Human-readable explanations
│   ├── recommendations.py       # Safe action recommendations
│   └── ph_predictor.py          # Original predictor (preserved)
├── edge/                        # Edge AI
│   └── inference_engine.py      # OpenVINO / sklearn inference
├── alerts/                      # Alert System
│   └── ph_alert_engine.py       # Multi-state early warning
├── simulator/                   # Data Generation
│   └── ph_simulator.py          # 8 deterministic scenarios
├── api/                         # Backend
│   └── server.py                # FastAPI with full pipeline
├── dashboard/                   # Frontend
│   └── index.html               # Competition-grade dark dashboard
├── storage/                     # Data Persistence
│   └── alert_history.py         # Alert history storage
├── scripts/                     # Evaluation & Benchmarking
│   ├── evaluate_forecasting.py  # Multi-horizon accuracy evaluation
│   └── benchmark_inference.py   # Inference speed comparison
├── tests/                       # Test Suite
│   ├── test_guardian.py          # 57 new comprehensive tests
│   ├── test_alert_engine.py     # 5 original tests (preserved)
│   ├── test_predictor.py        # 6 original tests (preserved)
│   └── test_simulator.py        # 4 original tests (preserved)
├── run_demo.py                  # Competition demo runner
├── main.py                      # Original entry point (preserved)
├── requirements.txt             # Dependencies
└── README.md                    # This file
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Dashboard |
| GET | `/api/status` | System status |
| GET | `/api/current` | Current reading |
| GET | `/api/history` | Reading history |
| GET | `/api/forecast` | Multi-step forecast |
| GET | `/api/prediction` | Single-step prediction |
| GET | `/api/risk` | Risk score & components |
| GET | `/api/anomalies` | Anomaly detection results |
| GET | `/api/explanation` | AI explainability |
| GET | `/api/recommendations` | Action recommendations |
| GET | `/api/alerts` | Alert status |
| GET | `/api/alert-history` | Alert history |
| GET | `/api/model-metrics` | Model performance |
| GET | `/api/inference-engine` | Edge AI backend info |
| GET | `/api/system-health` | Full system health |
| GET | `/api/benchmark` | Live inference benchmark |
| POST | `/api/scenario` | Switch demo scenario |
| POST | `/api/retrain-model` | Force model retrain |
| POST | `/api/submit-ph` | Submit manual pH reading |
| POST | `/api/set-mode` | Switch auto/manual mode |

---

## Testing

```bash
# Run all 72 tests
python -m pytest tests/ -v

# Run only new pipeline tests
python -m pytest tests/test_guardian.py -v

# Run with coverage
python -m pytest tests/ -v --cov=ai --cov=edge --cov=alerts --cov=simulator
```

---

## Technology Stack

- **AI/ML**: scikit-learn (RandomForest, IsolationForest)
- **Edge AI**: Intel® OpenVINO™ toolkit (with honest fallback)
- **Backend**: Python FastAPI
- **Frontend**: Vanilla HTML/CSS/JS + Chart.js
- **Testing**: pytest (72 tests)

---

## License

This project is submitted to the Intel® Vietnam AI Impact Festival 2026.

---

*Built with the goal of enriching lives through sustainable aquaculture.*
