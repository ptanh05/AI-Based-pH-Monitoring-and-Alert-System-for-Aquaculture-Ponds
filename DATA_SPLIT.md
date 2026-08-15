# Time-Series Splitting & Data Leakage Prevention Protocol
## AI Aquaculture Guardian

---

## 1. Fundamental Principle: Zero Temporal Data Leakage

In real-world aquaculture operations, an AI model deployed on an edge gateway at timestamp $t$ has access **only** to observations up to $t$. Evaluating a time-series model using standard random $K$-fold cross-validation or shuffled train/test splits introduces catastrophic data leakage (training on future samples to predict past samples), inflating accuracy metrics artificially.

**Strict Mandate**:
1. **Zero Random Shuffling**: The sequence ordering of measurements is strictly maintained.
2. **Chronological Splitting**: Partition boundaries are monotonic along the time axis.
3. **Train-Only Parameter Fitting**: Statistical scalers, imputers, and normalization parameters are computed strictly on the training partition and applied out-of-sample to validation and test sets.

---

## 2. Partitioning Breakdown

The continuous dataset is partitioned into three disjoint chronological segments:

```
[===================== TRAIN (70%) =====================][=== VAL (15%) ===][=== TEST (15%) ===]
t_0                                                    t_1               t_2                 t_end
```

| Partition | Fraction | Observation Count | Temporal Span (Mendeley Dataset) | Operational Purpose |
|---|:---:|:---:|---|---|
| **Training Set** | **70%** | 36,267 regularized records | Jan 1, 2024 00:00 – May 6, 2024 18:25 | Model feature fitting, decision tree optimization |
| **Validation Set** | **15%** | 7,771 regularized records | May 6, 2024 18:30 – Jun 2, 2024 05:40 | Hyperparameter tuning, early stopping, tree pruning |
| **Holdout Test Set** | **15%** | 7,773 regularized records | Jun 2, 2024 05:45 – Jun 30, 2024 23:55 | Unbiased out-of-sample generalization benchmark |

---

## 3. Supervised Lag Windowing Formulation

For any forecast horizon $h \in \{1, 5, 15, 30\}$ steps and historical window size $W = 20$:
$$\mathbf{x}_t = \left[ y_t, y_{t-1}, y_{t-2}, \dots, y_{t-W+1}, \mathbf{z}_t \right]$$
$$y_{\text{target}} = y_{t+h}$$

Where $\mathbf{z}_t$ represents auxiliary sensor readings (DO, Temp, Turbidity) at timestamp $\le t$.

- Target values $y_{t+h}$ belong exclusively to future timestamps.
- Features $\mathbf{x}_t$ never access any index $k > t$.

---

## 4. Verification Tests

Implemented in [`tests/test_data_leakage.py`](file:///c:/Workspace/Thuc%20hanh%20cac%20mon%20nam%203/jb/GI%E1%BA%A2%20L%E1%BA%ACP%20AI%20D%E1%BB%B0%20DO%C3%81N%20%C4%90O%20%C4%90%E1%BB%98%20PH%20TRONG%20%20AO/tests/test_data_leakage.py):
- `test_chronological_split_ordering`: Verifies $\max(t_{\text{train}}) < \min(t_{\text{val}}) < \min(t_{\text{test}})$.
- `test_no_future_lookahead_in_features`: Modifies future records and verifies that historical feature vectors remain bit-for-bit identical.
- `test_scaler_leakage_protection`: Verifies that test distribution statistics do not influence training scalers.
