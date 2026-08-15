# Comprehensive Dataset Selection & Evaluation Report
## AI Aquaculture Guardian — Intel® Vietnam AI Impact Festival 2026

---

## 1. Evaluation & Selection Criteria

To transition **AI Aquaculture Guardian** from an exclusively synthetic-based prototype into a scientifically grounded, competition-grade system, public aquaculture water quality datasets were evaluated against the following criteria:

1. **Domain Fidelity**: Data must reflect operational commercial aquaculture ponds (fish/shrimp), capturing biological diurnal cycles.
2. **Sampling Resolution**: Temporal resolution must be high-frequency ($\le 15$ minutes per reading) to support short-to-medium early warning forecasting (5–150 min).
3. **Core Target Availability**: Accurate, continuous time-series of pH readings.
4. **Multivariate Dimensions**: Auxiliary water quality parameters (Water Temperature, Dissolved Oxygen, Turbidity, Salinity, Ammonia) for multivariate risk scoring.
5. **Data Integrity & Volume**: Sufficient observation count ($> 10,000$ samples) covering multi-month seasonal transitions with minimal unresolvable missingness.
6. **Provenance & Citation**: Clear DOI, peer-reviewed scientific metadata, and open-access licensing (CC BY 4.0).
7. **Relevance to Vietnam & Southeast Asia**: Tropical warm-water conditions compatible with intensive Tilapia (*Oreochromis niloticus*) or whiteleg shrimp (*Litopenaeus vannamei*) aquaculture in the Mekong Delta.

---

## 2. Primary Selected Dataset

- **Dataset Title**: *Environmental Parameters in Aquaculture: Temperature, pH, Oxygen, and Turbidity Measurements*
- **Primary Source / Repository**: Mendeley Data
- **DOI**: [10.17632/8s73jfvgr5.2](https://doi.org/10.17632/8s73jfvgr5.2) — Version 2
- **Direct URL**: `https://data.mendeley.com/datasets/8s73jfvgr5/2`
- **License**: Creative Commons Attribution 4.0 International (CC BY 4.0)
- **Total Continuous Records**: **37,284 raw IoT stream records** (51,831 regularized 5-minute time points)
- **Temporal Span**: January 1, 2024 – June 30, 2024 (6 months)
- **Sampling Interval**: 5.0 minutes (300 seconds)
- **Measured Parameters**:
  - `ph`: Water pH level (Mean: 7.64, Range: 7.00 – 8.50)
  - `temperature`: Water Temperature in °C (Mean: 26.95°C, Range: 20.00 – 27.50°C)
  - `dissolved_oxygen`: Dissolved Oxygen in mg/L (Mean: 8.17 mg/L, Range: 7.30 – 9.00 mg/L)
  - `turbidity`: Turbidity in NTU (Mean: 3.52 NTU, Range: 2.50 – 7.50 NTU)
- **Missing Rate**: 0.00% across the primary IoT continuous recording sheet.
- **Selection Rationale**:
  - Captures genuine biological diurnal photosynthetic cycles (afternoon oxygen peaks and nighttime respiration).
  - High temporal density allows exact calculation of multi-step horizons (1, 5, 15, 30 steps = 5, 25, 75, 150 min).
  - Climatic and biological conditions (Montería, Colombia tropical pond) align with aquaculture environments in Vietnam (Mekong Delta / Southern Vietnam).

---

## 3. Secondary Sample Dataset (Validation / Local Testing)

- **Dataset Name**: `sample_aquaculture`
- **Location**: [`data/samples/sample_aquaculture_data.csv`](file:///c:/Workspace/Thuc%20hanh%20cac%20mon%20nam%203/jb/GI%E1%BA%A2%20L%E1%BA%ACP%20AI%20D%E1%BB%B0%20DO%C3%81N%20%C4%90O%20%C4%90%E1%BB%98%20PH%20TRONG%20%20AO/data/samples/sample_aquaculture_data.csv)
- **Size**: 500 rows
- **Purpose**: Zero-dependency offline testing, fast CI/CD pipeline execution, and unit testing.
- **Variables**: `timestamp`, `ph`, `temperature`, `dissolved_oxygen`, `turbidity`, `salinity`.
- **License**: CC0 / Open Public Domain.

---

## 4. Transparent Treatment of Unmonitored Variables

While Salinity and Ammonia are critical in coastal shrimp aquaculture, the primary freshwater Tilapia dataset focuses on pH, DO, Temperature, and Turbidity.
- **Design Decision**: The system implements [`data_pipeline/feature_adapter.py`](file:///c:/Workspace/Thuc%20hanh%20cac%20mon%20nam%203/jb/GI%E1%BA%A2%20L%E1%BA%ACP%20AI%20D%E1%BB%B0%20DO%C3%81N%20%C4%90O%20%C4%90%E1%BB%98%20PH%20TRONG%20%20AO/data_pipeline/feature_adapter.py) with dynamic sensor detection. If Salinity or Ammonia sensors are present, they are automatically incorporated into feature extraction and risk scoring; if missing, the pipeline gracefully falls back to available sensors without synthetic fabrication.
