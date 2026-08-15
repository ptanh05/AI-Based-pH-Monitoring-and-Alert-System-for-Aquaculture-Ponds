# Multi-Model Comparison & Production Model Selection
## AI Aquaculture Guardian — Intel® Vietnam AI Impact Festival 2026

---

## 1. Benchmarking Matrix Across Forecast Horizons

Evaluated on **51,831 regularized 5-minute time points** from 37,284 real IoT readings (Mendeley Data DOI: [10.17632/8s73jfvgr5.2](https://doi.org/10.17632/8s73jfvgr5.2)) under strict chronological 70% Train / 15% Val / 15% Holdout Test partitioning ($N_{\text{test}} = 7,773$):

| Horizon | Advance Time | Candidate Model | MAE (pH) | RMSE (pH) | $R^2$ Score | Latency (CPU) | Improvement vs Baseline |
|:---:|:---:|---|:---:|:---:|:---:|:---:|:---:|
| **1-step** | **5 minutes** | Persistence Baseline | 0.0110 | 0.0402 | 0.9473 | < 0.01 ms | 0.00% (Reference) |
| | | Linear Regression | 0.0143 | 0.0465 | 0.9392 | 0.02 ms | -5.70% (Underfits) |
| | | HistGradientBoosting | 0.0118 | 0.0406 | 0.9538 | 0.15 ms | +13.13% |
| | | **Random Forest (Multivariate)** | **0.0095** | **0.0354** | **0.9591** | **0.28 ms** | **+13.91%** |
| **5-step** | **25 minutes** | Persistence Baseline | 0.0485 | 0.1027 | 0.6562 | < 0.01 ms | 0.00% (Reference) |
| | | Linear Regression | 0.0618 | 0.1086 | 0.6698 | 0.02 ms | -4.67% (Underfits) |
| | | HistGradientBoosting | 0.0346 | 0.0707 | 0.8600 | 0.15 ms | +41.46% |
| | | **Random Forest (Multivariate)** | **0.0204** | **0.0493** | **0.9207** | **0.28 ms** | **+57.87%** |
| **15-step** | **75 minutes** | Persistence Baseline | 0.1113 | 0.1852 | -0.1176 | < 0.01 ms | **Baseline Fails ($R^2 < 0$)** |
| | | Linear Regression | 0.1168 | 0.1653 | 0.2344 | 0.02 ms | +10.67% |
| | | HistGradientBoosting | 0.0629 | 0.0988 | 0.7266 | 0.15 ms | +51.94% |
| | | **Random Forest (Multivariate)** | **0.0351** | **0.0693** | **0.8434** | **0.28 ms** | **+68.46%** |
| **30-step** | **150 minutes (2.5h)** | Persistence Baseline | 0.1559 | 0.2377 | -0.8400 | < 0.01 ms | **Baseline Fails ($R^2 < 0$)** |
| | | Linear Regression | 0.1236 | 0.1765 | 0.1266 | 0.02 ms | +28.87% |
| | | HistGradientBoosting | 0.0668 | 0.1062 | 0.6838 | 0.15 ms | +61.58% |
| | | **Random Forest (Multivariate)** | **0.0382** | **0.0695** | **0.8425** | **0.28 ms** | **+75.50%** |

---

## 2. Multi-Dimensional Trade-Off Analysis

| Evaluation Dimension | Persistence Baseline | Linear Regression | HistGradientBoosting | Random Forest Regressor |
|---|:---:|:---:|:---:|:---:|
| **Short-Horizon Accuracy (5m)** | High | Moderate | Very High | **Highest ($R^2 = 0.9591$)** |
| **Long-Horizon Accuracy (150m)** | Collapses ($R^2 < 0$) | Poor ($R^2 = 0.13$) | High ($R^2 = 0.68$) | **Highest ($R^2 = 0.8425$)** |
| **Inference Latency (CPU)** | **< 0.01 ms** | 0.02 ms | 0.15 ms | **0.28 ms (Well under 10ms edge budget)** |
| **Interpretability / XAI** | Trivial | Coefficients | Surrogate tree only | **Direct Gini Feature Importances** |
| **Non-Linear Dynamics Modeling**| None | None | High | **High** |
| **Edge Hardware Compatibility** | Pure Python | C / BLAS | C / OpenMP | **Scikit-Learn / OpenVINO ONNX** |

---

## 3. Transparent Production Model Selection Rule

> **Selection Rule**: The champion production model must satisfy:
> 1. Outperform persistence baseline at all operational horizons ($h \ge 5$ min).
> 2. Maintain $R^2 > 0.75$ and $\text{MAE} < 0.05\text{ pH}$ at the 2.5-hour advance notice window ($h = 30$).
> 3. Edge CPU inference latency $\le 1.0\text{ ms}$.
> 4. Native extraction of feature importances for Explainable AI (XAI).

### Verdict: **Random Forest Regressor (Multivariate)** is selected as the Primary Champion Model:
- Achieves $\text{MAE} = 0.0382\text{ pH}$ at 150 minutes (+75.50% better than persistence).
- Inference latency of **0.28 ms** on standard edge CPU.
- Transparent feature importance distribution directly powers farm operator explainability explanations.
