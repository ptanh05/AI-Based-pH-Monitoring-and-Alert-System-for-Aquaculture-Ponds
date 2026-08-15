# MODEL CARD: AI AQUACULTURE GUARDIAN FORECASTER
**Intel® Vietnam AI Impact Festival 2026**

---

## 1. Model Details

- **Model Name**: Multi-Horizon Aquaculture pH Forecaster
- **Version**: 2.0-Competition-Final
- **Model Architecture**: Multi-Output Random Forest Regressor (`n_estimators=100`, `max_depth=12`, `random_state=42`)
- **Primary Input**: $W=20$ step historical multivariate lag matrix (pH, Temperature, DO, Turbidity, diurnal harmonics)
- **Output Vector**: Multi-step predictions $\hat{y}_{t+h}$ for $h \in \{1, 5, 15, 30\}$ steps (5m, 25m, 75m, 150m)
- **Framework**: Scikit-Learn with Edge Inference Abstraction & OpenVINO runtime adapter
- **License**: MIT

---

## 2. Intended Use & Target Users

- **Primary Application**: Early warning decision-support for aquaculture farm managers.
- **Intended Deployment**: On-premise IoT edge gateway (Raspberry Pi, Intel NUC, or x86/ARM embedded computers).
- **Out-of-Scope Uses**: Automated actuator control (e.g. automatic chemical dosing without human confirmation).

---

## 3. Training & Evaluation Provenance

- **Training Dataset**: Mendeley Data Aquaculture Stream (37,284 records, DOI: `10.17632/8s73jfvgr5.2`)
- **Temporal Split**: Strict chronological 70% Train ($N=26,098$), 15% Validation ($N=5,593$), 15% Holdout Test ($N=5,593$).
- **Data Leakage Safeguards**: Scalers fitted exclusively on Train split; feature lags strictly indexed prior to target timestamp.

---

## 4. Quantitative Evaluation Results

Evaluated on the unseen 15% holdout test partition:

| Horizon | Nominal Time | Model MAE | Persistence Baseline MAE | RMSE | $R^2$ Score | MAE Reduction |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **1-step** | **5 min** | **0.010036** | 0.011020 | 0.035079 | **0.9599** | **+8.9%** |
| **5-step** | **25 min** | **0.024763** | 0.048517 | 0.057238 | **0.8933** | **+49.0%** |
| **15-step** | **75 min** | **0.040681** | 0.111336 | 0.072191 | **0.8302** | **+63.5%** |
| **30-step** | **150 min (2.5h)** | **0.041505** | 0.155939 | **0.074502** | **0.8192** | **+73.4%** |

---

## 5. Edge Inference Performance

- **Median (P50) Latency**: `1.4197 ms`
- **95th Percentile (P95)**: `1.5515 ms`
- **Throughput**: `699 inferences/sec`
- **Execution Platform**: Standard CPU (tested on Win32 / x86_64)
- **Fallback Transparency**: When OpenVINO ONNX translator lacks native rules for `TreeEnsembleRegressor`, runtime transparently falls back to Scikit-Learn CPU execution.

---

## 6. Limitations & Scientific Disclosures

1. **Simulation-to-Reality Gap**: Zero-shot transfer from synthetic harmonic simulations to real pond telemetry yields $R^2 = -5.7230$, proving that models must be calibrated on real-world in-situ data.
2. **Biological Regionality**: The primary dataset was collected from Tilapia ponds in Colombia. Deployment to shrimp ponds in the Mekong Delta requires running the automated in-situ calibration pipeline (`data_pipeline/`).
3. **Sensor Maintenance**: Severe sensor fouling, dry probe exposure, or biological biofilm accumulation requires physical probe cleaning and recalibration.
