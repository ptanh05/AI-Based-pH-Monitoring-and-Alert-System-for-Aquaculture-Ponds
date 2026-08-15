# Data Quality & Statistical Profile Report

**Dataset Name**: `mendeley_aquaculture`  
**Provenance / Source**: Mendeley Data (10.17632/8s73jfvgr5.2)  
**License**: Creative Commons Attribution 4.0 International (CC BY 4.0)  
**Audited Timestamp**: 2026-08-15T14:30:55.079525  

---

## 1. Executive Summary

- **Total Rows**: 37,284
- **Total Features**: 9
- **Time Coverage**: 2024-01-01T00:00:00 to 2024-06-28T23:10:00 (180.0 days)
- **Estimated Sampling Interval**: 300s (5.0 min)
- **Duplicate Timestamps**: 33922
- **Training Validity**: VALID ✓

## 2. Statistical Distribution by Monitored Variable

| Variable | Missing % | Mean ± Std | Min | Median | Max | Outliers (3×IQR) |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **`id`** | 0.0% | 5500.59 ± 1823.44 | 49.00 | 5514.50 | 8621.00 | 0 (0.0%) |
| **`ph`** | 0.0% | 7.64 ± 0.16 | 6.99 | 7.65 | 8.56 | 114 (0.31%) |
| **`turbidity`** | 0.0% | 3.79 ± 1.05 | 2.15 | 3.39 | 7.60 | 0 (0.0%) |
| **`temperature`** | 0.0% | 26.95 ± 0.20 | 20.00 | 26.96 | 27.50 | 18 (0.05%) |
| **`dissolved_oxygen`** | 0.0% | 8.17 ± 0.21 | 7.30 | 8.17 | 9.00 | 0 (0.0%) |

## 3. Physical Boundary Verification

| Parameter | Expected Physical Window | Violations Count | Status |
|---|:---:|:---:|:---:|
| `ph` | Standard Aquaculture Range | 0 | PASSED ✓ |
| `temperature` | Standard Aquaculture Range | 0 | PASSED ✓ |
| `dissolved_oxygen` | Standard Aquaculture Range | 0 | PASSED ✓ |
| `turbidity` | Standard Aquaculture Range | 0 | PASSED ✓ |

## 4. Anomaly Classification & Provenance Protocol

All sensor fluctuations are classified into:
1. **Legitimate Environmental Dynamics**: Diurnal solar-photosynthetic rise in DO and pH during afternoon peak hours.
2. **Hardware Faults**: Flatline readings (variance = 0 for > 15 readings) and rate-of-change jumps exceeding physical kinetics (> 0.5 pH / 5 min).
