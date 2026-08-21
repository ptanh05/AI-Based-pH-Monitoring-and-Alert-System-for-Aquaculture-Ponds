# Real-World Aquaculture Dataset Repository
## Environmental Parameters in Aquaculture: Temperature, pH, Oxygen, and Turbidity Measurements

---

## 1. Dataset Provenance & Metadata

- **Official Dataset Name**: *Environmental Parameters in Aquaculture: Temperature, pH, Oxygen, and Turbidity Measurements*
- **Version**: 2
- **DOI**: [10.17632/8s73jfvgr5.2](https://doi.org/10.17632/8s73jfvgr5.2)
- **Official Repository URL**: [https://data.mendeley.com/datasets/8s73jfvgr5/2](https://data.mendeley.com/datasets/8s73jfvgr5/2)
- **Authors**: Rubén Baena-Navarro, Yulieth Carriazo-Regino, Francisco Torres-Hoyos
- **Institution**: Universidad de Córdoba, Montería, Colombia
- **License**: **Creative Commons Attribution 4.0 International (CC BY 4.0)**
- **Geographic Location**: Montería, Córdoba Department, Colombia ($8^\circ 45' N, 75^\circ 53' W$)
- **Aquaculture Species**: Nile Tilapia (*Oreochromis niloticus*)
- **Collection Period**: 2023 (Pre-IoT baseline) and 2024 (Continuous IoT monitoring, January – June 2024)

---

## 2. Directory Structure

```
data/
├── real/                                                  # Raw official files from Mendeley Data
│   ├── Data IoTMLCQ.xlsx                                 # Primary continuous IoT stream (37,284 records)
│   ├── Fish_Health_Intervention_Comparison_2024_Corrected.xlsx
│   ├── IoT_Intervention_Events.xlsx                      # Automated intervention event logs
│   ├── Monteria_Climate_Conditions_2023.xlsx             # Ambient weather & precipitation
│   ├── Non_IoT_Fish_Health_Data_2024.xlsx
│   ├── Pre_IoT_Historical_Water_Quality_2023.xlsx        # Monthly baseline with Alkalinity & Nitrates
│   ├── Pre_IoT_Validated_Fish_Health_Data_2023.xlsx
│   └── Validated_IoT_Fish_Health_Data 2024.xlsx
├── processed/                                            # Processed, regularized, and parquet/CSV caches
├── metadata/                                             # Download metadata and SHA-256 validation logs
│   └── mendeley_dataset_files_meta.json
└── README.md                                             # This document
```

---

## 3. Dataset Characteristics & Schema

### Primary High-Resolution Stream: `Data IoTMLCQ.xlsx`
- **Total Records**: 37,284 readings across 6 months (6,214 readings/month)
- **Sampling Frequency**: Multi-readings per hour (~every 1–3 minutes when IoT sensor node is active)
- **Columns**:
  - `id`: Sequential reading identifier
  - `month`: 1 to 6 (January – June 2024)
  - `day`: 1 to 31
  - `hour`: 0 to 23
  - `temperatura_scaled`: Water temperature in °C (Mean: 26.95 °C, Range: 20.00 – 27.50 °C)
  - `oxigeno_scaled`: Dissolved Oxygen in mg/L (Mean: 8.17 mg/L, Range: 7.30 – 9.00 mg/L)
  - `ph`: Water pH value (Normalized range 0.0 – 1.04; maps to physical aquaculture pH 7.00 – 8.50)
  - `turbidez`: Water turbidity (Normalized range 0.0 – 1.02; maps to 2.50 – 7.50 NTU)
  - `temperatura`, `oxigeno`: Standardized feature representations

---

## 4. Download & Verification Procedure

To download or re-verify all official Mendeley dataset files:
```bash
python scripts/download_real_dataset.py
```

The script connects to the official Mendeley Data API (`https://data.mendeley.com/api/datasets/8s73jfvgr5/files?version=2`), downloads all 8 files, and cryptographically verifies their SHA-256 hashes.

---

## 5. Scientific Citation

```bibtex
@misc{baena2024environmental,
  author = {Baena-Navarro, Rubén and Carriazo-Regino, Yulieth and Torres-Hoyos, Francisco},
  title = {Environmental Parameters in Aquaculture: Temperature, pH, Oxygen, and Turbidity Measurements},
  year = {2024},
  publisher = {Mendeley Data},
  version = {2},
  doi = {10.17632/8s73jfvgr5.2},
  url = {https://data.mendeley.com/datasets/8s73jfvgr5/2}
}
```
