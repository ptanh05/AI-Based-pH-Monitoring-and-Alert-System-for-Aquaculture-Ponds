# AI AQUACULTURE GUARDIAN
### AI-Powered Early Warning System for Sustainable Aquaculture
**Intel® Vietnam AI Impact Festival 2026 Submission**  
*Theme: "Enriching Lives with AI Innovation"*

[![Tests](https://img.shields.io/badge/Tests-131%2F131%20Passing-brightgreen.svg)]()
[![Inference Latency](https://img.shields.io/badge/Edge%20Latency-1.42ms%20(P50)-blue.svg)]()
[![Dataset](https://img.shields.io/badge/Real%20IoT%20Data-37%2C284%20Readings-orange.svg)]()
[![Forecasting MAE](https://img.shields.io/badge/150m%20MAE%20Reduction-73.4%25-green.svg)]()
[![Responsible AI](https://img.shields.io/badge/Responsible%20AI-Human--in--the--Loop-purple.svg)]()

---

## 1. Executive Summary & Problem Statement

Aquaculture is a cornerstone of Vietnam's rural economy, with shrimp and fish farming contributing over **$10 billion USD annually** in export value. However, sudden water quality fluctuations—most notably pH crashes from acidic rain runoff or spikes from algal blooms—can wipe out entire pond stocks within 2 to 4 hours.

Traditional reactive testing kits or simple threshold alarms alert farmers **only after damage has already occurred**.

**AI Aquaculture Guardian** is an Edge-native, explainable Decision-Support System that forecasts water quality degradation **up to 150 minutes (2.5 hours) in advance**, computes a dynamic **Aquaculture Risk Score (0–100)**, detects sensor anomalies, and provides human-in-the-loop Standard Operating Procedures (SOPs).

---

## 2. Core Technical Innovations

```
                                  AI AQUACULTURE GUARDIAN PIPELINE
  ┌─────────────────┐     ┌──────────────────────┐     ┌────────────────────────────────┐
  │ Multi-Sensor    │ ──> │ Edge Ingestion &     │ ──> │ Multi-Step AI Forecasting      │
  │ Telemetry (IoT) │     │ 5-Min Resampling     │     │ (1, 5, 15, 30 steps ahead)     │
  └─────────────────┘     └──────────────────────┘     └────────────────────────────────┘
                                                                       │
  ┌─────────────────┐     ┌──────────────────────┐                     ▼
  │ Farmer Action   │ <── │ Explainable XAI &    │ <── ┌────────────────────────────────┐
  │ SOP Guidance    │     │ Dynamic Risk (0-100) │     │ 4-Layer Hybrid Anomaly Engine  │
  └─────────────────┘     └──────────────────────┘     └────────────────────────────────┘
```

1. **Multi-Horizon Lookahead Forecasting ($h \in \{1, 5, 15, 30\}$)**:
   Predicts water parameters up to 2.5 hours ahead on 5-minute resampled telemetry, providing actionable advance warning before thresholds are violated.
2. **4-Layer Hybrid Anomaly Detection**:
   Combines rolling Z-score statistical bounds, rate-of-change limits, sensor freeze detection, and Isolation Forest scoring to separate true biological shifts from sensor malfunctions.
3. **Continuous Risk Index (0–100)**:
   A non-linear composite risk metric integrating current pH deviations, forecasted threshold violations, trend momentum, and multi-sensor correlations.
4. **Explainable AI (XAI) & Standard Operating Procedures (SOP)**:
   Generates transparent natural-language diagnostic explanations (*"WHY"*) and step-by-step actionable recommendations (*"ACTION"*), keeping human operators firmly in the decision loop.
5. **Ultra-Low Latency Edge Architecture**:
   Optimized for rural IoT edge gateways, achieving **1.42 ms median inference latency** on commodity CPUs without requiring costly cloud infrastructure.

---

## 3. Verified Experimental Results

All reported metrics are measured directly from the evaluation pipeline on **37,284 real-world IoT aquaculture records** (DOI: [10.17632/8s73jfvgr5.2](https://doi.org/10.17632/8s73jfvgr5.2)) using a strict **70% Train / 15% Validation / 15% Test chronological split** with zero future lookahead.

### A. Multi-Step Forecasting Performance vs. Persistence Baseline

| Horizon | Nominal Duration | AI Model MAE (pH) | Persistence Baseline MAE | RMSE (pH) | $R^2$ Score | Error Reduction |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **1-step** | **5 minutes** | **0.0100** | 0.0110 | 0.0351 | **0.9599** | **+8.9%** |
| **5-step** | **25 minutes** | **0.0248** | 0.0485 | 0.0572 | **0.8933** | **+49.0%** |
| **15-step** | **75 minutes** | **0.0407** | 0.1113 | 0.0722 | **0.8302** | **+63.5%** |
| **30-step** | **150 minutes (2.5h)** | **0.0415** | 0.1559 | **0.0745** | **0.8192** | **+73.4%** |

### B. Domain Shift Characterization (Scientific Disclosure)

| Transfer Experiment | Target Dataset | 30-step MAE | 30-step $R^2$ | Scientific Finding |
|:---|:---:|:---:|:---:|:---|
| **Real $\to$ Real (In-Domain)** | Real IoT Test Split | **0.0396** | **0.8384** | Strong biological learning of diurnal curves. |
| **Synthetic $\to$ Synthetic** | Synthetic Test Split | 0.0011 | 1.0000 | Baseline validation on ideal harmonic waves. |
| **Synthetic $\to$ Real (Zero-Shot)** | Real IoT Test Split | **0.2906** | **-5.7230** | **Simulation-to-Reality Gap**: Synthetic models alone fail under real biological noise. |

> **Scientific Disclosure**: The synthetic-to-real domain shift is explicitly characterized as a limitation and research finding. The system mitigates this limitation through direct in-situ training and calibration on real aquaculture data (`data_pipeline/`).

### C. Edge Inference Latency & Throughput (1,000 Iterations)

- **Execution Engine**: Scikit-Learn Multi-Output Tree Ensemble
- **P50 (Median) Latency**: **1.42 ms**
- **P95 Latency**: **1.55 ms**
- **P99 Latency**: **1.68 ms**
- **Throughput**: **699 inferences/second**
- **OpenVINO Fallback**: The OpenVINO adapter transparently routes `TreeEnsembleRegressor` to Scikit-Learn CPU execution when native translation rules are unavailable on the CPU frontend.

---

## 4. Responsible AI & Human-in-the-Loop Mandate

- **Decision-Support Tool**: AI Aquaculture Guardian is designed exclusively as an operational decision-support tool.
- **No Autonomous Dosing**: The system **never** triggers automated chemical, lime, or acid injection into ponds. All interventions require human validation.
- **Transparent SOPs**: Every alert is accompanied by human-readable explanations (XAI) and non-hazardous remediation guidance (e.g., paddlewheel aeration, clean water exchange, dosage check).
- **Data Privacy & Open Science**: Built upon publicly accessible research data under CC BY 4.0 license.

---

## 5. Quickstart & Reproducibility Runbook

### Prerequisites
- Python 3.10+ (tested on Python 3.12)
- Virtual environment recommended

### Installation
```bash
git clone https://github.com/ptanh05/AI-Based-pH-Monitoring-and-Alert-System-for-Aquaculture-Ponds.git
cd AI-Based-pH-Monitoring-and-Alert-System-for-Aquaculture-Ponds
pip install -r requirements.txt
```

### Reproducing All Competition Results

```bash
# 1. Run Complete Automated Test Suite (131 tests)
python -m pytest tests/ -v -p no:httpbin -q

# 2. Benchmark Edge Inference Engine (1,000 runs)
python scripts/benchmark_real_model.py --iterations 1000

# 3. Evaluate Real Dataset Multi-Step Forecasting
python scripts/evaluate_real_dataset.py --dataset mendeley_aquaculture

# 4. Measure Simulation-to-Reality Domain Shift
python scripts/evaluate_domain_shift.py

# 5. Run Real-World Dataset Streaming Demo
python run_real_demo.py --dataset mendeley_aquaculture --max_readings 50 --speed 10

# 6. Run Deterministic Competition Demo (120 steps)
python run_demo.py --scenario competition_demo --seed 42
```

---

## 6. Repository Architecture

```
├── ai/                     # AI Subsystem (Forecasting, Anomaly, Risk, Explainability, Recommendations)
├── alerts/                 # State management & Threshold alert engine
├── api/                    # FastAPI REST API with modern lifespan lifecycle
├── artifacts/              # Generated benchmark metrics and JSON evaluation artifacts
├── data/                   # Real-world aquaculture datasets & metadata
├── data_pipeline/          # Leak-free cleaning, resampling, scaling, and splitting
├── edge/                   # Edge inference abstraction (Scikit-Learn & OpenVINO fallback)
├── scripts/                # Evaluation, benchmarking, and training scripts
├── simulator/              # Deterministic multi-scenario aquaculture simulator
├── tests/                  # 131 automated unit, integration, and mathematical audit tests
├── run_demo.py             # Deterministic CLI competition demo
├── run_real_demo.py        # Real-world telemetry streaming demo
├── MODEL_CARD.md           # Model architecture, training provenance, and evaluation limits
├── DATASET_CARD.md         # Real-world dataset card & provenance
├── TECHNICAL_REPORT.md     # In-depth technical and scientific report
└── RESPONSIBLE_AI.md       # Ethical guidelines and human-in-the-loop framework
```

---

## 7. Submission Metadata

- **Competition**: Intel® Vietnam AI Impact Festival 2026
- **Theme**: "Enriching Lives with AI Innovation"
- **Project Lead**: AI Aquaculture Guardian Engineering Team
- **License**: MIT
