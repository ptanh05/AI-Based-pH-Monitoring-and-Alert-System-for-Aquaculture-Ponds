# SUBMISSION SUMMARY: AI AQUACULTURE GUARDIAN
**Intel® Vietnam AI Impact Festival 2026**  
*Theme: "Enriching Lives with AI Innovation"*

---

## 1. Project Header & Verified Metrics

- **Project Title**: AI Aquaculture Guardian (AI-Powered Early Warning System for Sustainable Aquaculture)
- **Repository**: `AI-Based-pH-Monitoring-and-Alert-System-for-Aquaculture-Ponds`
- **Core Architecture**: Edge-Native Multi-Horizon Lookahead Forecaster + 4-Layer Hybrid Anomaly Detector + Dynamic Risk Engine (0–100) + Explainable XAI Advisor
- **Real-World Dataset**: **37,284 IoT records** from Mendeley Data (DOI: `10.17632/8s73jfvgr5.2`)
- **150-Min Forecast Performance**: $\text{MAE} = 0.0415\text{ pH}$ vs $\text{Baseline} = 0.1559\text{ pH}$ (**73.4% MAE reduction**, $R^2 = 0.8192$)
- **Edge Inference Speed**: **1.42 ms median latency (P50)**, **699 inferences/second** on standard CPU
- **Test Suite Status**: **131 / 131 tests PASS** (100% Green, 0 warnings, 0 failures)
- **Deterministic Demo**: **120 / 120 steps reproducible** with `--seed 42`

---

## 2. Recommended 10-Slide Presentation Structure

| Slide | Title | Core Content & Key Visual |
|:---:|:---|:---|
| **Slide 1** | **Title & Vision** | AI Aquaculture Guardian: Transforming reactive pond monitoring into proactive early warning for Vietnam's $10B aquaculture sector. |
| **Slide 2** | **The Farmer's Crisis** | Water quality crashes (pH drops from acid rain / spikes from algal blooms) cause mass mortalities within 2–4 hours. Existing sensors alert too late. |
| **Slide 3** | **Our Innovation** | Multi-Horizon Lookahead Forecasting (up to 2.5 hours ahead) + 4-Layer Anomaly Detection + 0–100 Continuous Risk Index + Explainable SOPs. |
| **Slide 4** | **System Architecture** | End-to-end data pipeline: Ingestion $\to$ 5-min Resampling $\to$ Train-only Scaler $\to$ ML Regressor $\to$ Risk Engine $\to$ FastAPI $\to$ Edge UI. |
| **Slide 5** | **Real-World AI Results** | Evaluated on 37,284 real IoT readings: 73.4% error reduction over Persistence Baseline at 150 min ($R^2 = 0.8192$). |
| **Slide 6** | **Scientific Integrity & Domain Shift** | Transparent disclosure of simulation-to-reality gap (Synthetic $\to$ Real $R^2 = -5.7230$) and mitigation via automated in-situ calibration pipeline. |
| **Slide 7** | **Edge AI & Computational Efficiency** | Sub-2 ms CPU latency (1.42 ms P50, 699 FPS) on low-cost edge gateways without cloud dependency. OpenVINO runtime adapter support. |
| **Slide 8** | **Interactive Live Demo** | 6-scene deterministic storyline (`--seed 42`) demonstrating baseline $\to$ early warning $\to$ anomaly detection $\to$ XAI guidance $\to$ recovery. |
| **Slide 9** | **Responsible AI & Human-in-the-Loop** | Advisory decision-support system; zero autonomous chemical dosing; actionable SOPs (aeration, water exchange); transparent XAI. |
| **Slide 10** | **Social & Economic Impact** | Saving 50–150M VND/ha per crop across Mekong Delta communities; reducing antibiotic usage and protecting freshwater ecosystems. |

---

## 3. Likely Judge Questions & Recommended Answers

### Q1: Why did you choose Random Forest over Deep Learning (LSTM / Transformers)?
**Recommended Answer**:  
*"In rural edge deployments (e.g. pond-side IoT gateways), power, computational budget, and inference latency are critical constraints. Our Multi-Output Random Forest regressor achieves exceptional accuracy (73.4% MAE reduction, $R^2 = 0.8192$) with an ultra-fast P50 latency of **1.42 ms** on commodity CPUs without requiring a GPU. Furthermore, tree ensembles provide direct feature attribution for explainability (XAI) and avoid catastrophic overfitting on non-stationary diurnal cycles."*

---

### Q2: Why did zero-shot transfer from synthetic data to real data result in a negative R² (-5.7230)?
**Recommended Answer**:  
*"This is a key scientific finding that we transparently disclose: synthetic harmonic simulators model idealized sinusoidal dynamics, whereas real aquaculture ponds experience complex biological respiration, microbial activity, and micro-turbulence. This proves that synthetic data alone cannot replace real-world calibration. To solve this, we engineered an automated in-situ data pipeline (`data_pipeline/`) that calibrates models directly to local pond conditions upon deployment."*

---

### Q3: Why does your system not automatically dose chemicals or lime when pH drops?
**Recommended Answer**:  
*"In line with Responsible AI principles, our system is strictly a **Decision-Support System** (Human-in-the-loop). A faulty or fouled sensor triggering automated chemical injection could catastrophically wipe out an entire pond stock. Instead, AI Aquaculture Guardian alerts the farmer, explains the underlying cause (XAI), and provides standard operating procedures (SOPs)—such as activating paddlewheel aerators or performing manual titration checks."*

---

### Q4: How do you prevent data leakage in your time-series pipeline?
**Recommended Answer**:  
*"We implemented strict chronological splitting (70% Train / 15% Validation / 15% Test) without shuffling. All normalization scalers are fitted exclusively on the Train partition. For feature engineering, our sliding lag window $W=20$ indexes observations strictly at or prior to $t$, completely isolating future target observations ($t+h$)."*

---

### Q5: How is this solution adapted for Vietnamese farmers in the Mekong Delta?
**Recommended Answer**:  
*"The entire software stack is lightweight and runs locally on sub-$50 edge hardware (Raspberry Pi / Intel NUC) with zero recurring cloud subscription costs. The interface is intuitive, providing clear color-coded risk states (0–100) and simple, actionable SOPs tailored to local farming practices (e.g. bật quạt nước, thay nước, kiểm tra vôi)."*
