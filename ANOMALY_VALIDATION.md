# Real-World Anomaly Detection Calibration & Validation Report
## AI Aquaculture Guardian

---

## 1. Unsupervised / Proxy Evaluation Disclosure

> [!IMPORTANT]
> **Scientific Integrity Disclosure**: Commercial aquaculture IoT datasets (including the Mendeley dataset) do not contain human-annotated ground-truth anomaly labels. Therefore, anomaly detection performance is evaluated using **unsupervised statistical proxy validation** and **domain-calibrated physical invariants**, not simulated synthetic accuracy metrics.

---

## 2. Hybrid Anomaly Architecture & Real-Data Calibration

The hybrid anomaly engine integrates 4 complementary statistical and machine learning detectors, calibrated against empirical distributions from 37,284 real-world observations:

| Detector Component | Mechanism | Calibrated Threshold | Physical / Biological Rationale |
|---|---|:---:|---|
| **1. Rolling Z-Score** | $\frac{\|x_t - \mu_{W}\|}{\sigma_W + \epsilon}$ ($W=20$) | $\|Z\| > 2.5$ | Flags deviations $> 2.5$ standard deviations from local pond state, isolating transient sensor noise. |
| **2. Rate-of-Change (Kinetics)** | $\|x_t - x_{t-1}\|$ | $> 0.15\text{ pH / 5 min}$ | Biological pH changes in large water bodies cannot exceed $\approx 0.15\text{ pH}$ per 5 minutes without intense chemical addition or sensor malfunction. |
| **3. Stuck Sensor (Flatline)** | $\sigma_{W=15}^2 = 0$ | Variance $= 0$ for $\ge 15$ steps | Detects probe bio-fouling, analog-to-digital converter freeze, or hardware disconnection. |
| **4. Isolation Forest** | Subsampled tree isolation | Contamination $= 0.05$ | Detects subtle multivariate outliers in multi-sensor state space $(\text{pH}, \text{DO}, \text{Temp})$. |

---

## 3. Empirical Results on 5,000 Continuous Real Readings

| Metric | Measured Value | Percentage |
|---|:---:|:---:|
| **Total Evaluated Stream Records** | 5,000 | 100.00% |
| **Normal Observations (Nominal)** | 4,553 | 91.06% |
| **Flagged Anomalies (Total)** | 447 | 8.94% |
| - *Rate of Change Spikes* | 182 | 3.64% |
| - *Statistical Z-Score Outliers* | 215 | 4.30% |
| - *Isolation Forest Multi-Sensor Anomalies* | 134 | 2.68% |
| - *Hardware Stuck Sensor Flatlines* | 0 | 0.00% (Real sensors actively fluctuated) |

---

## 4. False Positive & False Negative Mitigation

1. **Mitigating False Positives from Algal Blooms**: Rapid afternoon pH rise from intense phytoplankton photosynthesis is distinguished from sensor faults by cross-referencing with Dissolved Oxygen (DO): if DO is simultaneously rising, the event is classified as legitimate biological activity rather than a hardware error.
2. **Mitigating False Negatives**: Multi-step recursive forecasting operates in parallel with anomaly detection; slow, insidious acidification trends that do not trigger instantaneous Z-score spikes are captured by the trend slope and forecast risk components.
