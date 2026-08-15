# Domain Shift and Cross-Dataset Generalization Analysis

Evaluates in-domain vs. zero-shot cross-domain model transfer.

| Horizon | Real $\to$ Real MAE ($R^2$) | Synthetic $\to$ Synthetic MAE ($R^2$) | Synthetic $\to$ Real MAE ($R^2$) | Degradation |
|---|:---:|:---:|:---:|:---:|
| **1_step** | 0.0093 (0.96) | 0.0017 (1.00) | 0.0781 (0.66) | +739.3% error |
| **5_step** | 0.0213 (0.92) | 0.0013 (1.00) | 0.3099 (-3.33) | +1354.1% error |
| **15_step** | 0.0352 (0.87) | 0.0022 (1.00) | 0.2544 (-2.57) | +623.6% error |
| **30_step** | 0.0396 (0.84) | 0.0011 (1.00) | 0.2906 (-5.72) | +634.0% error |
