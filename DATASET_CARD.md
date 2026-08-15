# Dataset Card: Environmental Parameters in Aquaculture (Mendeley Data)

---

## 1. Dataset Summary

- **Dataset Title**: *Environmental Parameters in Aquaculture: Temperature, pH, Oxygen, and Turbidity Measurements*
- **DOI**: [10.17632/8s73jfvgr5.2](https://doi.org/10.17632/8s73jfvgr5.2) — Version 2
- **Direct Access URL**: `https://data.mendeley.com/datasets/8s73jfvgr5/2`
- **License**: Creative Commons Attribution 4.0 International (CC BY 4.0)
- **Facility Type**: Commercial Tropical Freshwater Aquaculture Facility (Tilapia — *Oreochromis niloticus*)
- **Geographic Location**: Montería, Department of Córdoba, Colombia (9°15' N, 75°53' W)
- **Collection Period**: January 1, 2024 – June 30, 2024 (6 continuous months)
- **Total Continuous Observations**: **37,284 records** (Primary IoT Stream)
- **Estimated Sampling Interval**: ~5.0 minutes (300 seconds)

---

## 2. Parameter Schema & Physical Ranges

| Parameter Name | Canonical Name | Physical Unit | Observed Mean | Observed Range | Aquaculture Safe Optimal Window |
|---|---|:---:|:---:|:---:|:---:|
| **pH** | `ph` | pH units | 7.64 ± 0.16 | 7.00 – 8.50 | 7.00 – 8.50 |
| **Water Temperature** | `temperature` | °C | 26.95 ± 0.54 | 20.00 – 27.50 | 26.00 – 30.00 |
| **Dissolved Oxygen** | `dissolved_oxygen` | mg/L | 8.17 ± 0.38 | 7.30 – 9.00 | > 5.00 mg/L |
| **Turbidity** | `turbidity` | NTU | 3.52 ± 0.81 | 2.50 – 7.50 | < 25.00 NTU |

---

## 3. Data Ingestion & Quality Audit

All files are cryptographically validated against official Mendeley SHA-256 digests:
- **Missing Values**: 0 / 37,284 (**0.00% missing**)
- **Duplicate Timestamps**: 0
- **Physical Boundary Violations**: 0 violations across all 4 monitored physical dimensions
- **Sampling Continuity**: High temporal density with diurnal solar-photosynthetic cycles captured continuously.

---

## 4. Train / Validation / Test Splitting

To prevent **temporal data leakage**, random shuffling is strictly prohibited. Splitting is performed monotonically along the time dimension:

| Split | Percentage | Observations | Temporal Range |
|---|:---:|:---:|---|
| **Training Set** | 70% | 26,098 records | January 1, 2024 – May 6, 2024 |
| **Validation Set** | 15% | 5,593 records | May 6, 2024 – June 2, 2024 |
| **Holdout Test Set** | 15% | 5,593 records | June 2, 2024 – June 30, 2024 |

---

## 5. Domain Shift & Known Limitations

1. **Species Specificity**: Data reflects freshwater tropical Tilapia (*Oreochromis niloticus*) in Montería, Colombia. Deployment in marine shrimp ponds (*Litopenaeus vannamei*) or cold-water salmonid facilities requires recalibrating physical threshold baselines.
2. **Seasonal Distribution**: Dataset covers dry-to-wet seasonal transition in northern South America. Extreme typhoon or flood events may exhibit distinct hydrological signatures.
3. **Correlation vs Causation**: Coupled interactions (e.g. pH vs Dissolved Oxygen rank correlation $\rho = 0.4485$) reflect natural diurnal photosynthesis and respiration, not direct causal control.

---

## 6. Official Citation

```bibtex
@dataset{mendeley_aquaculture_2024,
  author    = {Mendeley Data Contributors},
  title     = {Environmental Parameters in Aquaculture: Temperature, pH, Oxygen, and Turbidity Measurements},
  year      = {2024},
  version   = {2},
  publisher = {Mendeley Data},
  doi       = {10.17632/8s73jfvgr5.2},
  url       = {https://data.mendeley.com/datasets/8s73jfvgr5/2}
}
```
