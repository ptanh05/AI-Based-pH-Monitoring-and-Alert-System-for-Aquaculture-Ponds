# DATASET CARD: MENDELEY AQUACULTURE WATER QUALITY TELEMETRY
**Intel® Vietnam AI Impact Festival 2026**

---

## 1. Dataset Overview

- **Dataset Identifier**: `mendeley_aquaculture`
- **Source**: Mendeley Data
- **DOI**: `10.17632/8s73jfvgr5.2`
- **License**: Creative Commons Attribution 4.0 International (CC BY 4.0)
- **Total Record Count**: **37,284 raw IoT measurements**
- **Location**: Aquaculture Research Station, Montería, Colombia
- **Species Monitored**: Tilapia (*Oreochromis niloticus*)

---

## 2. Sensor Schema & Physical Ranges

| Parameter | Unit | Physical Range | Raw Mean | Resampled Standard Dev |
|:---|:---:|:---:|:---:|:---:|
| **pH** | pH units | 0.0 – 14.0 | 7.64 | 0.28 |
| **Water Temperature** | °C | 0.0 – 50.0 | 27.12 | 1.84 |
| **Dissolved Oxygen** | mg/L | 0.0 – 25.0 | 8.15 | 1.12 |
| **Turbidity** | NTU | 0.0 – 1000.0 | 142.30 | 38.60 |

---

## 3. Data Ingestion & Leakage Prevention Pipeline

1. **Regularization & Resampling**: Raw irregular IoT timestamps are regularized into 5-minute bins using forward/backward interpolation bounds (`data_pipeline/resampling.py`).
2. **Chronological Splitting**: Partitioned without random shuffling into:
   - **Train Set** (70%): Earliest 26,098 time points.
   - **Validation Set** (15%): Subsequent 5,593 time points.
   - **Holdout Test Set** (15%): Latest 5,593 time points.
3. **Scaler Fitting**: Normalization scalers are strictly fitted on the Train partition only.

---

## 4. Ethical & Environmental Considerations

- **Data Privacy**: Telemetry records contain only physical water parameters; zero personal farmer data is present.
- **Ecological Impact**: Data collected to optimize water aeration efficiency and reduce unnecessary chemical buffer discharges into surrounding watersheds.
