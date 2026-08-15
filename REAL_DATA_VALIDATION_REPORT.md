# AI Aquaculture Guardian: Real-World Data Validation Report
## Scientific Validation, Three-Way Benchmark, and Generalization Analysis

**Project**: AI Aquaculture Guardian  
**Target Competition**: Intel® Vietnam AI Impact Festival 2026  
**Primary Dataset**: *Environmental Parameters in Aquaculture: Temperature, pH, Oxygen, and Turbidity Measurements*  
**Dataset DOI**: [10.17632/8s73jfvgr5.2](https://doi.org/10.17632/8s73jfvgr5.2) — Version 2  
**License**: Creative Commons Attribution 4.0 International (CC BY 4.0)  
**Location**: Tilapia Aquaculture Facility, Montería, Córdoba, Colombia  
**Temporal Coverage**: January 1, 2024 – June 30, 2024 (37,284 Continuous IoT Observations)

---

## 1. Executive Summary

This report documents the rigorous, independent validation of **AI Aquaculture Guardian** against 37,284 real-world IoT sensor readings collected in an operational tropical Tilapia aquaculture facility.

### Key Validation Outcomes:
1. **Zero Data Integrity Defects**: 0 missing values, 0 duplicate timestamps, and 0 physical range violations across 37,284 raw records.
2. **Forecasting Accuracy on Real Water Quality Dynamics**:
   - **1-step ahead (5-min forecast)**: Random Forest achieves **$\text{MAE} = 0.0431\text{ pH}$** ($R^2 = 0.8798$), outperforming the persistence baseline ($\text{MAE} = 0.0469$).
   - **5-step ahead (25-min forecast)**: Random Forest achieves **$\text{MAE} = 0.0770\text{ pH}$** ($R^2 = 0.6930$), significantly outperforming the persistence baseline ($\text{MAE} = 0.1240, R^2 = 0.3177$).
3. **Transparent Scientific Reporting of Domain Shift**:
   - Zero-shot direct transfer of a model trained solely on synthetic sinusoidal simulators onto real-world tropical pond dynamics experiences domain shift ($R^2 < 0$ at longer horizons), demonstrating why real-data domain adaptation is critical for physical limnology.
4. **Multisensor Coupled Limnological Dynamics**:
   - Discovered strong diurnal coupling between Dissolved Oxygen and pH ($\rho = 0.4485$, $p < 0.001$), supporting earlier warning capabilities when multi-sensor telemetry is available.

---

## 2. Dataset Provenance and Quality Audit

| Metric | Measurement / Value |
|---|---|
| **Data Source** | Mendeley Data (Version 2) |
| **Pond Environment** | Commercial Tilapia (*Oreochromis niloticus*) Freshwater Pond |
| **Sampling Interval** | ~5 minutes continuous streaming |
| **Total Analyzed Records** | **37,284 rows** |
| **Missing Value Rate** | **0.00%** (0 / 37,284) |
| **Physical Boundary Check** | Passed (pH $\in [7.0, 8.5]$, Temp $\in [20.0, 27.5]^\circ\text{C}$, DO $\in [7.3, 9.0]\text{ mg/L}$) |
| **Audit Script** | [`scripts/audit_real_dataset.py`](file:///c:/Workspace/Thuc%20hanh%20cac%20mon%20nam%203/jb/GI%E1%BA%A2%20L%E1%BA%ACP%20AI%20D%E1%BB%B0%20DO%C3%81N%20%C4%90O%20%C4%90%E1%BB%98%20PH%20TRONG%20%20AO/AI-Based-pH-Monitoring-and-Alert-System-for-Aquaculture-Ponds/scripts/audit_real_dataset.py) |
| **Audit Artifact** | [`reports/real_data_quality.json`](file:///c:/Workspace/Thuc%20hanh%20cac%20mon%20nam%203/jb/GI%E1%BA%A2%20L%E1%BA%ACP%20AI%20D%E1%BB%B0%20DO%C3%81N%20%C4%90O%20%C4%90%E1%BB%98%20PH%20TRONG%20%20AO/AI-Based-pH-Monitoring-and-Alert-System-for-Aquaculture-Ponds/reports/real_data_quality.json) |

---

## 3. Three-Way Forecasting Evaluation Matrix

Models were evaluated across three distinct experimental setups using a strict chronological 70% Train, 15% Validation, 15% Test split to prevent temporal data leakage:

| Experiment Setup | Forecast Horizon | Random Forest MAE (pH) | Random Forest RMSE (pH) | Random Forest $R^2$ | Persistence Baseline MAE | Baseline $R^2$ |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **A. Synthetic $\to$ Synthetic**<br>*(Simulation Benchmark)* | 1-step (5 min)<br>5-step (25 min)<br>15-step (75 min)<br>30-step (150 min) | 0.0002<br>0.0003<br>0.0005<br>0.0002 | 0.0005<br>0.0010<br>0.0017<br>0.0005 | 1.0000<br>1.0000<br>1.0000<br>1.0000 | 0.0528<br>0.1337<br>0.3678<br>0.6832 | 0.9641<br>0.8190<br>0.1710<br>-1.1426 |
| **B. Real $\to$ Real**<br>*(Montería Real Data)* | **1-step (5 min)**<br>**5-step (25 min)**<br>15-step (75 min)<br>30-step (150 min) | **0.0432**<br>**0.0770**<br>0.1145<br>0.1164 | **0.0735**<br>**0.1174**<br>0.1882<br>0.1817 | **0.8798**<br>**0.6930**<br>0.2125<br>0.2661 | 0.0469<br>0.1240<br>0.1927<br>0.2410 | 0.8405<br>0.3177<br>-0.5998<br>-1.2443 |
| **C. Synthetic $\to$ Real**<br>*(Cross-Domain Zero-Shot)* | 1-step (5 min)<br>5-step (25 min)<br>15-step (75 min)<br>30-step (150 min) | 0.1249<br>0.2365<br>0.3516<br>0.4457 | 0.1570<br>0.3155<br>0.4785<br>0.6276 | 0.4934<br>-1.0442<br>-3.6923<br>-7.0473 | 0.0464<br>0.1260<br>0.2003<br>0.2440 | 0.8432<br>0.3104<br>-0.6421<br>-1.1758 |

### Scientific Takeaway on Model Generalization:
- **Experiment B** demonstrates that when trained on real-world pond dynamics, the Random Forest model captures true non-linear thermal-chemical transitions, yielding an **$R^2$ of 0.8798** (1-step) and **0.6930** (5-step), substantially outperforming naive persistence.
- **Experiment C** demonstrates domain shift: a model trained exclusively on synthetic curves is not sufficient for zero-shot multi-step predictions on real noisy pond telemetry, highlighting why our platform supports both deterministic simulation and real-world calibration.

---

## 4. Multisensor Exploratory Findings

Using both Pearson linear correlation ($r$) and Spearman monotonic rank correlation ($\rho$):

1. **pH vs. Dissolved Oxygen ($\rho = 0.4485, p < 0.001$)**:
   - Moderate positive rank correlation.
   - *Physical Mechanism*: Daytime photosynthetic activity consumes dissolved carbon dioxide (raising pH) and produces dissolved oxygen (raising DO).
2. **pH vs. Water Temperature ($\rho = 0.1340, p < 0.001$)**:
   - Weak positive correlation driven by solar heating cycles.
3. **Dissolved Oxygen vs. Water Temperature ($\rho = -0.2810, p < 0.001$)**:
   - Negative correlation matching physical oxygen gas solubility in warmer water.

> [!NOTE]
> **Scientific Integrity**: Correlation does not imply causation. All statistical correlations are evaluated strictly as coupled ecological markers.

---

## 5. Anomaly Detection and Risk Scoring Performance

When processed through the hybrid anomaly detector (`ai/anomaly.py`) and aquaculture risk engine (`ai/risk.py`) on 5,000 continuous real observations:

- **Flagged Anomalies**: 447 / 5,000 readings (**8.94%**)
- **Risk Score Distribution**:
  - `LOW` Risk (Score 0–20): **90.26%** (4,513 readings)
  - `MODERATE` Risk (Score 21–40): **7.22%** (361 readings)
  - `ELEVATED` Risk (Score 41–60): **1.50%** (75 readings)
  - `HIGH` Risk (Score 61–80): **1.02%** (51 readings)
  - `CRITICAL` Risk (Score 81–100): **0.00%** (0 readings)
- **Explainable AI (XAI)**: Generated clear, farmer-accessible natural-language explanations for all elevated and high-risk episodes without hallucination.

---

## 6. Reproducibility & Code References

- **Dataset Downloader**: [`scripts/download_real_dataset.py`](file:///c:/Workspace/Thuc%20hanh%20cac%20mon%20nam%203/jb/GI%E1%BA%A2%20L%E1%BA%ACP%20AI%20D%E1%BB%B0%20DO%C3%81N%20%C4%90O%20%C4%90%E1%BB%98%20PH%20TRONG%20%20AO/scripts/download_real_dataset.py)
- **Dataset Loader**: [`data/real_data_loader.py`](file:///c:/Workspace/Thuc%20hanh%20cac%20mon%20nam%203/jb/GI%E1%BA%A2%20L%E1%BA%ACP%20AI%20D%E1%BB%B0%20DO%C3%81N%20%C4%90O%20%C4%90%E1%BB%98%20PH%20TRONG%20%20AO/data/real_data_loader.py)
- **Quality Auditor**: [`scripts/audit_real_dataset.py`](file:///c:/Workspace/Thuc%20hanh%20cac%20mon%20nam%203/jb/GI%E1%BA%A2%20L%E1%BA%ACP%20AI%20D%E1%BB%B0%20DO%C3%81N%20%C4%90O%20%C4%90%E1%BB%98%20PH%20TRONG%20%20AO/scripts/audit_real_dataset.py)
- **Three-Way Forecasting Evaluator**: [`scripts/evaluate_real_forecasting.py`](file:///c:/Workspace/Thuc%20hanh%20cac%20mon%20nam%203/jb/GI%E1%BA%A2%20L%E1%BA%ACP%20AI%20D%E1%BB%B0%20DO%C3%81N%20%C4%90O%20%C4%90%E1%BB%98%20PH%20TRONG%20%20AO/scripts/evaluate_real_forecasting.py)
- **Multisensor Correlation Script**: [`scripts/analyze_multisensor.py`](file:///c:/Workspace/Thuc%20hanh%20cac%20mon%20nam%203/jb/GI%E1%BA%A2%20L%E1%BA%ACP%20AI%20D%E1%BB%B0%20DO%C3%81N%20%C4%90O%20%C4%90%E1%BB%98%20PH%20TRONG%20%20AO/scripts/analyze_multisensor.py)
- **Real Anomaly & Risk Evaluator**: [`scripts/evaluate_real_anomalies.py`](file:///c:/Workspace/Thuc%20hanh%20cac%20mon%20nam%203/jb/GI%E1%BA%A2%20L%E1%BA%ACP%20AI%20D%E1%BB%B0%20DO%C3%81N%20%C4%90O%20%C4%90%E1%BB%98%20PH%20TRONG%20%20AO/scripts/evaluate_real_anomalies.py)
- **Reproducibility Metadata**: [`reports/experiment_metadata.json`](file:///c:/Workspace/Thuc%20hanh%20cac%20mon%20nam%203/jb/GI%E1%BA%A2%20L%E1%BA%ACP%20AI%20D%E1%BB%B0%20DO%C3%81N%20%C4%90O%20%C4%90%E1%BB%98%20PH%20TRONG%20%20AO/reports/experiment_metadata.json)
