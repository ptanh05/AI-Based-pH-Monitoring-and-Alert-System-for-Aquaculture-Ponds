# TECHNICAL REPORT: AI AQUACULTURE GUARDIAN
### AI-Powered Early Warning System for Sustainable Aquaculture
**Target Competition**: Intel® Vietnam AI Impact Festival 2026  
**Document Classification**: Comprehensive Technical Submission Document

---

## 1. Abstract

Water quality volatility in intensive aquaculture ponds poses severe existential risks to farmers across Vietnam and Southeast Asia. Sudden biochemical shocks—such as rapid nocturnal pH drops from respiratory acid accumulation or midday surges from uncontrolled phytoplankton blooms—often cause irreversible mortalities before traditional monitoring systems trigger alarms. 

This report presents **AI Aquaculture Guardian**, a production-tested, Edge-deployable early warning platform that transforms reactive water quality management into proactive risk mitigation. Evaluated on **37,284 real-world IoT pond telemetry records**, our multi-horizon Random Forest regressor achieves a **73.4% reduction in Mean Absolute Error (MAE)** at a 150-minute (2.5-hour) forecast horizon compared to the standard Persistence Baseline ($\text{MAE} = 0.0415\text{ pH}$ vs. $0.1559\text{ pH}$, $R^2 = 0.8192$). On commodity CPU hardware, the system executes inference in **1.42 ms (P50)** at **699 inferences per second**. Combined with a 4-layer hybrid anomaly detector, dynamic risk index (0–100), and explainable SOP recommendations, the system provides farmers with actionable advance warning while maintaining a strict human-in-the-loop operational boundary.

---

## 2. Mathematical Framework & AI Methodology

### 2.1 Multi-Step Time-Series Lookahead Formulation

Let $x_t \in \mathbb{R}^d$ represent the multi-sensor measurement vector observed at discrete timestep $t$ (sampled on a uniform $\Delta t = 5\text{-minute}$ grid), where the primary target $y_t \in \mathbb{R}$ denotes pond water pH. 

Given a historical lag window $W = 20$, the feature extraction operator $\Phi$ maps past observations strictly prior to or at time $t$:
$$\mathbf{f}_t = \Phi\Big(x_{t-W+1}, x_{t-W+2}, \dots, x_t\Big) \in \mathbb{R}^{K}$$

The multi-step forecasting model $\mathcal{M}_\theta$ simultaneously estimates future pH values across horizons $h \in \{1, 5, 15, 30\}$ steps (corresponding to nominal 5, 25, 75, and 150 minutes):
$$\hat{\mathbf{y}}_{t+1:t+H} = \mathcal{M}_\theta(\mathbf{f}_t) = \big[\hat{y}_{t+1}, \hat{y}_{t+5}, \hat{y}_{t+15}, \hat{y}_{t+30}\big]^T$$

### 2.2 Leakage-Free Temporal Splitting & Standardization

To eliminate future data leakage, all preprocessing parameters $\mu_{\text{train}}, \sigma_{\text{train}}$ are computed strictly on the training partition ($t \le T_{\text{train}}$):
$$z_t = \frac{x_t - \mu_{\text{train}}}{\sigma_{\text{train}} + \epsilon}, \quad \forall t$$
The dataset partition is strictly chronological without shuffling:
- **Train Set** (70%): $t \in [0, 0.70 N]$ (model training & scaler fitting)
- **Validation Set** (15%): $t \in (0.70 N, 0.85 N]$ (hyperparameter tuning)
- **Holdout Test Set** (15%): $t \in (0.85 N, N]$ (independent final evaluation)

### 2.3 Continuous Dynamic Risk Score Formulation

The composite Aquaculture Risk Score $\mathcal{R}_t \in [0, 100]$ combines four physical and statistical risk vectors:
$$\mathcal{R}_t = \text{clamp}\Big(w_c \cdot S_{\text{current}}(y_t) + w_f \cdot S_{\text{forecast}}(\hat{\mathbf{y}}_{t+1:t+H}) + w_t \cdot S_{\text{trend}}(\mathbf{f}_t) + w_a \cdot \mathbb{I}_{\text{anomaly}}, \, 0, \, 100\Big)$$
where:
- $S_{\text{current}}(y_t) = 100 \cdot \big(\frac{|y_t - 7.75|}{8.5 - 7.75}\big)^2$ measures non-linear distance from optimal pH ($7.75$).
- $S_{\text{forecast}}$ evaluates the maximum predicted deviation across the 150-minute forecast trajectory.
- $S_{\text{trend}}$ scales with the least-squares slope $\beta_1$ over window $W$.
- $\mathbb{I}_{\text{anomaly}} \in \{0, 1\}$ is triggered by the 4-layer anomaly engine.

---

## 3. Experimental Evaluation on Real IoT Dataset

### 3.1 Dataset Provenance & Preprocessing

- **Dataset**: Mendeley Data Aquaculture Water Quality Stream (DOI: `10.17632/8s73jfvgr5.2`)
- **Total Records**: 37,284 raw IoT telemetry readings
- **Measured Parameters**: pH, Water Temperature (°C), Dissolved Oxygen (mg/L), Turbidity (NTU)
- **Resampling**: Regularized onto a 5-minute uniform time grid using forward/backward interpolation bounds.

### 3.2 Forecasting Accuracy Across Horizons

All models were evaluated on the unseen 15% holdout test partition against the standard **Persistence Baseline** ($y_{t+h} = x_t$).

| Metric | 1-step (5 min) | 5-step (25 min) | 15-step (75 min) | 30-step (150 min) |
|:---|:---:|:---:|:---:|:---:|
| **Model MAE (pH)** | **0.010036** | **0.024763** | **0.040681** | **0.041505** |
| **Baseline MAE (pH)** | 0.011020 | 0.048517 | 0.111336 | 0.155939 |
| **Model RMSE (pH)** | 0.035079 | 0.057238 | 0.072191 | 0.074502 |
| **Model $R^2$ Score** | **0.9599** | **0.8933** | **0.8302** | **0.8192** |
| **MAE Reduction vs Baseline** | **+8.9%** | **+49.0%** | **+63.5%** | **+73.4%** |

```
                       150-MINUTE FORECAST ERROR COMPARISON
      ┌──────────────────────────────────────────────────────────────┐
      │ Persistence Baseline MAE: 0.1559 pH                          │
      ├──────────────────────────────┬───────────────────────────────┤
      │ AI Guardian MAE: 0.0415 pH   │  73.4% Error Reduction       │
      └──────────────────────────────┴───────────────────────────────┘
```

---

## 4. Simulation-to-Reality Domain Shift Analysis

To rigorously evaluate model generalization, we conducted a three-way domain transfer experiment:

1. **In-Domain Real ($\text{Real} \to \text{Real}$)**: Model trained and evaluated on real IoT pond data ($\text{MAE} = 0.0396\text{ pH}, \, R^2 = 0.8384$).
2. **In-Domain Synthetic ($\text{Syn} \to \text{Syn}$)**: Model trained and evaluated on synthetic harmonic curves ($\text{MAE} = 0.0011\text{ pH}, \, R^2 = 1.0000$).
3. **Zero-Shot Transfer ($\text{Syn} \to \text{Real}$)**: Model trained on synthetic curves applied zero-shot to real pond data ($\text{MAE} = 0.2906\text{ pH}, \, R^2 = -5.7230$).

### Scientific Interpretation
The catastrophic degradation of zero-shot transfer ($R^2 < 0$) highlights the **fundamental simulation-to-reality gap**: real aquaculture ponds exhibit complex diurnal solar cycles, biological respiration fluctuations, and environmental micro-turbulence that cannot be captured by simplified harmonic equations alone. 

**Engineering Solution**: The system incorporates an automated in-situ calibration pipeline (`data_pipeline/`) that allows the model to calibrate directly to local pond conditions upon deployment.

---

## 5. Edge Inference & Computational Efficiency

Edge deployment tests were conducted using standard CPU hardware across 1,000 continuous inference iterations:

- **Median (P50) Latency**: `1.4197 ms`
- **95th Percentile (P95) Latency**: `1.5515 ms`
- **99th Percentile (P99) Latency**: `1.6757 ms`
- **Inference Throughput**: `699 inferences/second`
- **Memory Footprint**: `< 150 MB RSS`
- **OpenVINO Compatibility**: Implemented an edge runtime adapter that verifies OpenVINO operator availability and transparently falls back to Scikit-Learn CPU execution for unsupported ONNX tree ensemble structures.

---

## 6. Responsible AI & Operational Safety

1. **Human-in-the-Loop Mandate**: AI Aquaculture Guardian acts strictly as an advisory system. Automated chemical, buffer, or lime actuators are intentionally excluded from the architecture.
2. **Explainable AI (XAI)**: Every alert outputs feature-attribution scores and natural language explanations (e.g., *"pH falling rapidly at -0.18 pH/reading due to high respiratory load"*).
3. **Standard Operating Procedures (SOP)**: Prescribes graduated, non-hazardous interventions:
   - *Risk 0–30 (Low)*: Routine monitoring.
   - *Risk 31–60 (Moderate)*: Activate paddlewheel aerators; inspect inlet filters.
   - *Risk 61–100 (Critical)*: Immediate partial water exchange; manual chemical titration verification.

---

## 7. Conclusion

AI Aquaculture Guardian provides a mathematically sound, leak-free, and scientifically validated Edge AI platform for aquaculture pond monitoring. By delivering **73.4% error reduction 2.5 hours ahead of time** at **sub-2 ms CPU latency**, the system delivers tangible economic and food-security impact for sustainable aquaculture communities across Vietnam.
