# Aquaculture Risk Scoring Methodology (0–100)
## AI Aquaculture Guardian

---

## 1. Mathematical Formulation

The composite risk score $R \in [0, 100]$ provides aquaculture farm operators with an interpretable, bounded metric reflecting holistic pond health. It synthesizes instantaneous sensor values, AI predictive trajectories, physical kinetics, and anomaly indicators.

$$R = \min\left(100.0, \, \sum_{i=1}^{5} w_i \cdot C_i \right) \times Q_{\text{sensor}}$$

### Component Breakdown & Weights:

| Component $C_i$ | Description | Weight $w_i$ | Normalization Function |
|---|---|:---:|---|
| **$C_{\text{current}}$** | Proximity of current pH $x_t$ to safe limits $[7.0, 8.5]$ | **35%** | $\frac{\max(0, 7.0 - x_t, x_t - 8.5)}{\Delta_{\text{crit}}} \times 100$ |
| **$C_{\text{forecast}}$** | Proximity of AI forecasted pH $\hat{x}_{t+h}$ to safe limits | **25%** | $\frac{\max(0, 7.0 - \hat{x}_{t+h}, \hat{x}_{t+h} - 8.5)}{\Delta_{\text{crit}}} \times 100$ |
| **$C_{\text{rate\_of\_change}}$** | Rate of pH change $\|x_t - x_{t-1}\|$ per 5 minutes | **15%** | $\min\left(100, \, \frac{\|x_t - x_{t-1}\|}{0.20} \times 100 \right)$ |
| **$C_{\text{trend}}$** | Directional linear slope over window $W=20$ | **10%** | $\min\left(100, \, \frac{\|\text{slope}\|}{0.05} \times 100 \right)$ |
| **$C_{\text{anomaly}}$** | Composite hybrid anomaly confidence score | **15%** | $S_{\text{anomaly}} \times 100$ |

### Sensor Quality Multiplier $Q_{\text{sensor}}$:
- **`GOOD` (1.0)**: Standard operating mode.
- **`SUSPECT` (1.15)**: Multiplied by $1.15$ to bias risk conservatively when sensor quality degrades.
- **`BAD / DEGRADED` (1.30)**: Triggers immediate sensor inspection notice.

---

## 2. Risk Level Tiering & Operational Action Matrix

| Risk Score ($R$) | Risk Tier | Color Indicator | Recommended Operational Action |
|:---:|:---:|:---:|---|
| **$0.0 - 20.0$** | **`LOW`** | Green | Routine operations. Standard monitoring interval. |
| **$20.1 - 40.0$** | **`MODERATE`** | Cyan | Normal observation. Maintain regular inspection logs. |
| **$40.1 - 60.0$** | **`ELEVATED`** | Yellow | Early warning. Increase monitoring to every 10 minutes. Check aerators. |
| **$60.1 - 80.0$** | **`HIGH`** | Orange | Imminent breach predicted. Verify sensor, prepare water exchange or buffering. |
| **$80.1 - 100.0$** | **`CRITICAL`** | Red | Active boundary breach or severe fault. Execute farm emergency protocol immediately. |
