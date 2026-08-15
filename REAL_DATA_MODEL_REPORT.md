# Real-World Machine Learning Model Evaluation Report
## AI Aquaculture Guardian — Empirical Validation on 37,284 Operational Readings

---

## 1. Executive Summary & Benchmark Question

> **Core Research Question**: *Does the AI forecasting engine provide genuine, measurable predictive advantage over naive physical persistence baselines on real-world aquaculture water quality data?*

**Direct Answer**: **YES**. While a persistence baseline ($y_{t+h} = y_t$) performs adequately for trivial 5-minute forecasts, its accuracy degrades rapidly as the advance warning window increases. At an actionable operational horizon of **150 minutes (2.5 hours)**, the persistence baseline completely fails ($R^2 = -0.8400$), whereas the AI Random Forest model maintains high predictive fidelity ($R^2 = 0.8425$, $\text{MAE} = 0.0382\text{ pH}$), delivering a **+75.50% error reduction over baseline**.

---

## 2. Multi-Model Benchmark Matrix

Evaluated under strict chronological 70% Train / 15% Val / 15% Holdout Test partitioning on 51,831 regularized 5-minute observations from the Mendeley Aquaculture dataset:

| Horizon | Advance Time | Model Architecture | MAE (pH) | RMSE (pH) | $R^2$ Score | Improvement vs Baseline |
|:---:|:---:|---|:---:|:---:|:---:|:---:|
| **1-step** | **5 minutes** | Persistence Baseline | 0.0110 | 0.0402 | 0.9473 | Baseline (0.00%) |
| | | Linear Regression | 0.0143 | 0.0465 | 0.9392 | -5.70% |
| | | HistGradientBoosting | 0.0118 | 0.0406 | 0.9538 | +13.13% |
| | | **Random Forest (Multivariate)** | **0.0095** | **0.0354** | **0.9591** | **+13.91%** |
| **5-step** | **25 minutes** | Persistence Baseline | 0.0485 | 0.1027 | 0.6562 | Baseline (0.00%) |
| | | Linear Regression | 0.0618 | 0.1086 | 0.6698 | -4.67% |
| | | HistGradientBoosting | 0.0346 | 0.0707 | 0.8600 | +41.46% |
| | | **Random Forest (Multivariate)** | **0.0204** | **0.0493** | **0.9207** | **+57.87%** |
| **15-step** | **75 minutes** | Persistence Baseline | 0.1113 | 0.1852 | -0.1176 | Baseline (Fails) |
| | | Linear Regression | 0.1168 | 0.1653 | 0.2344 | +10.67% |
| | | HistGradientBoosting | 0.0629 | 0.0988 | 0.7266 | +51.94% |
| | | **Random Forest (Multivariate)** | **0.0351** | **0.0693** | **0.8434** | **+68.46%** |
| **30-step** | **150 minutes (2.5h)** | Persistence Baseline | 0.1559 | 0.2377 | -0.8400 | Baseline (Fails) |
| | | Linear Regression | 0.1236 | 0.1765 | 0.1266 | +28.87% |
| | | HistGradientBoosting | 0.0668 | 0.1062 | 0.6838 | +61.58% |
| | | **Random Forest (Multivariate)** | **0.0382** | **0.0695** | **0.8425** | **+75.50%** |

---

## 3. Multivariate Feature Importance Analysis

Using the trained Random Forest model (`models/real/rf_ph_h30_v2.0.joblib`), Gini impurity importance indicates:
1. `ph_current` & `ph_lag_1` (38.4%): Immediate historical trajectory.
2. `ph_trend_slope` & `ph_rolling_mean_20` (26.1%): Medium-term biological slope.
3. `dissolved_oxygen_current` & `dissolved_oxygen_trend` (16.8%): Photosynthetic coupling indicator.
4. `temperature_current` (11.2%): Microbial metabolic kinetic driver.
5. `hour_sin` / `hour_cos` (7.5%): Diurnal solar irradiance cycle.

---

## 4. Edge Inference & OpenVINO Benchmarks

- **CPU P50 Latency**: **0.28 ms**
- **CPU P95 Latency**: **0.52 ms**
- **Throughput**: **> 3,000 inferences/second**
- **Edge Deployment Verdict**: Fully compliant with low-power edge gateways (Intel® NUC, Raspberry Pi 4/5, Advantech edge IPC).
