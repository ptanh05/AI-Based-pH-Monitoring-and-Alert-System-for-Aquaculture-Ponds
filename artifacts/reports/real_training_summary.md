# Real Dataset Training & Benchmark Report

**Dataset**: mendeley_aquaculture (10.17632/8s73jfvgr5.2)
**License**: Creative Commons Attribution 4.0 International (CC BY 4.0)
**Timestamp**: 2026-08-15T14:20:44.049675

| Horizon | Best Model | Model MAE | Base MAE | Improvement | Model $R^2$ |
|---|---|:---:|:---:|:---:|:---:|
| **1-step (5 min)** | HistGradientBoosting | 0.0118 | 0.0135 | **+13.1%** | 0.9538 |
| **5-step (25 min)** | Random Forest | 0.0328 | 0.0590 | **+44.5%** | 0.8605 |
| **15-step (75 min)** | Random Forest | 0.0605 | 0.1308 | **+53.8%** | 0.7270 |
| **30-step (150 min)** | HistGradientBoosting | 0.0668 | 0.1738 | **+61.6%** | 0.6838 |
