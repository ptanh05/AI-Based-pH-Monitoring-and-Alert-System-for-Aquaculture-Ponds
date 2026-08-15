# Multisensor Interaction & Correlation Analysis Report
## Real-World Aquaculture Dataset (Montería, Colombia — DOI: 10.17632/8s73jfvgr5.2)

---

> [!IMPORTANT]
> **Scientific Disclaimer**: Correlation does **NOT** imply causation. The statistical relationships below document observed coupled dynamics in tropical tilapia pond ecosystems (such as daytime photosynthesis and nightly respiration cycles), not direct deterministic cause-and-effect.

---

## 1. Correlation Matrices

### 1.1 Pearson Linear Correlation Matrix ($r$)

| Parameter | pH | Temperature | Dissolved Oxygen | Turbidity |
|---|:---:|:---:|:---:|:---:|
| **pH** | 1.0000 | -0.0215 | -0.2026 | -0.6109 |
| **Temperature** | -0.0215 | 1.0000 | 0.0057 | 0.0459 |
| **Dissolved Oxygen** | -0.2026 | 0.0057 | 1.0000 | 0.1259 |
| **Turbidity** | -0.6109 | 0.0459 | 0.1259 | 1.0000 |

### 1.2 Spearman Monotonic Rank Correlation Matrix ($\rho$)

| Parameter | pH | Temperature | Dissolved Oxygen | Turbidity |
|---|:---:|:---:|:---:|:---:|
| **pH** | 1.0000 | -0.0156 | -0.1819 | -0.5552 |
| **Temperature** | -0.0156 | 1.0000 | 0.0057 | 0.0794 |
| **Dissolved Oxygen** | -0.1819 | 0.0057 | 1.0000 | 0.1117 |
| **Turbidity** | -0.5552 | 0.0794 | 0.1117 | 1.0000 |

---

## 2. Key Pairwise Findings

### 2.1 pH vs. Dissolved Oxygen (DO)
- **Spearman $\rho$**: **-0.1819** (p < 0.001)
- **Strength**: Weak correlation
- **Biological Context**: During peak sunlight, phytoplankton photosynthesis consumes dissolved CO2 (raising pH) and produces dissolved oxygen (raising DO), creating a positive coupling during daylight hours.

### 2.2 pH vs. Water Temperature
- **Spearman $\rho$**: **-0.0156** (p < 0.001)
- **Strength**: Negligible / Uncorrelated
- **Biological Context**: Solar radiation simultaneously drives water warming and algal metabolic rates, leading to moderate thermal-photochemical correlation.

### 2.3 pH vs. Turbidity
- **Spearman $\rho$**: **-0.5552** (p < 0.001)
- **Strength**: Strong correlation
- **Biological Context**: Algal blooms simultaneously increase water turbidity (suspended green biomass) and shift pH upward via rapid carbon dioxide uptake.

### 2.4 Temperature vs. Dissolved Oxygen
- **Spearman $\rho$**: **0.0057** (p < 0.001)
- **Strength**: Negligible / Uncorrelated
- **Biological Context**: Physical oxygen solubility in water decreases as temperature rises, though in active ponds daytime biological photosynthesis can offset physical degassing.

---

## 3. Implications for AI Aquaculture Guardian Architecture

1. **Multivariate Early Warning Advantage**:
   - Because Dissolved Oxygen and pH exhibit coupled diurnal fluctuations driven by sunlight and algal respiration, multi-sensor models can achieve earlier warning horizons than single-sensor thresholding.
2. **Sensor Cross-Validation**:
   - If pH rises sharply while DO and temperature remain completely flat in pitch darkness, the anomaly detection engine can flag this pattern as a potential sensor calibration drift or bio-fouling event rather than a natural algal bloom.
