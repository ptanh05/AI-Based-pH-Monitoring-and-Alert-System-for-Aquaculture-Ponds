# RESPONSIBLE AI & ETHICAL FRAMEWORK
## AI AQUACULTURE GUARDIAN
**Intel® Vietnam AI Impact Festival 2026**

---

## 1. Ethical Mission & Core Principles

The AI Aquaculture Guardian project adheres to strict ethical standards for AI deployment in vulnerable agricultural communities:

1. **Human-in-the-Loop Mandate**: AI provides actionable decision support; human farm operators retain 100% operational authority over pond interventions.
2. **Exclusion of Autonomous Chemical Dosing**: The system intentionally does **not** integrate autonomous chemical dispensing valves or acid pumps to prevent catastrophic chemical overdosing from sensor failure.
3. **Transparent Explainability (XAI)**: Every alert and risk score is accompanied by natural-language root-cause explanations and verified Standard Operating Procedures (SOPs).
4. **Data Integrity & Open Science**: Built upon peer-reviewed, open-access real-world telemetry (DOI: `10.17632/8s73jfvgr5.2`) under CC BY 4.0 license.

---

## 2. Risk Mitigation & Operational Safeguards

| Potential Failure Mode | Technical Risk | Implemented Safeguard |
|:---|:---|:---|
| **Sensor Biofouling / Stuck Probe** | False reading reported as true water quality | 4-layer anomaly engine detects zero-variance stuck probe condition and flags `[ ANOMALY ]` with probe cleaning instructions. |
| **Abrupt Weather Shock (Acid Rain)** | Forecast lag due to rapid non-stationary event | Online dynamic risk scoring incorporates real-time rate of change and triggers immediate warning regardless of forecast horizon. |
| **Edge Hardware Failure** | Power outage / microcontroller crash | Fail-safe local persistence; system resumes seamlessly from latest verified telemetry state. |
| **OpenVINO Translation Mismatch** | Engine crash on unsupported ONNX operators | Transparent fallback to Scikit-Learn CPU engine with logged warning. |

---

## 3. Socio-Economic Impact for Vietnamese Aquaculture

- **Target Beneficiaries**: Smallholder and commercial shrimp/fish farmers across the Mekong Delta (Đồng bằng Sông Cửu Long) and coastal provinces (Bến Tre, Sóc Trăng, Cà Mau).
- **Economic Value**: Mitigating 1 major pH mortality event per cycle preserves an estimated **50–150 million VND per hectare**.
- **Environmental Sustainability**: Preventing severe pH spikes reduces unnecessary antibiotic usage and chemical buffer runoff into surrounding river ecosystems.
