# Responsible AI, Safety & Ethical Guidelines
## AI Aquaculture Guardian — Intel® Vietnam AI Impact Festival 2026

---

## 1. Primary Operating Principle

> [!IMPORTANT]
> **Core Responsible AI Mandate**: **AI Aquaculture Guardian is strictly an advisory decision-support system, NOT an autonomous chemical dosing or medical treatment system.**
>
> The system does not directly actuate high-risk chemical pumps, dispense algaecides, or prescribe veterinary treatments. All outputs are presented to human farm operators as early-warning indicators and suggested Standard Operating Procedures (SOP).

---

## 2. Safety & Risk Mitigation Framework

### 2.1 Human-in-the-Loop Architecture
1. **Operator Verification First**: Whenever a high-risk score or anomaly is flagged, the system advises verifying the reading with a secondary handheld probe before undertaking major interventions.
2. **Conservative Sensor Quarantine**: If a sensor exhibits erratic noise or flatlining, the system marks sensor quality as `SUSPECT` or `BAD`, applies a conservative multiplier ($1.15\times - 1.30\times$) to the risk score, and requests physical probe inspection.
3. **No Uncalibrated Automation**: Recommendations are framed as procedural guidelines (e.g. *"Inspect aeration equipment"*, *"Check for heavy rain runoff"*, *"Consult qualified aquaculture professional"*).

---

## 3. Data Integrity & Anti-Fabrication Principles

1. **Explicit Provenance Labeling**: The UI, API, and CLI clearly identify the active data source:
   - `[ REAL DATA ]`: Actual IoT measurements from Mendeley Data DOI: `10.17632/8s73jfvgr5.2`.
   - `[ SIMULATION / DEMO ]`: Deterministic synthetic scenario for live competition demonstration.
2. **No Fabricated Anomaly Labels**: Anomaly evaluation on real data is explicitly documented as **unsupervised proxy validation**, acknowledging the absence of manual ground-truth anomaly annotations.
3. **No Exaggerated Production Claims**: The system is documented as a competition-grade research prototype validated on historical IoT data, not a nationwide deployed production network.

---

## 4. Intel® OpenVINO™ Edge Transparency

- The system implements an honest fallback mechanism: if an operator (e.g., `ai.onnx.ml.TreeEnsembleRegressor`) cannot be natively converted by OpenVINO, the system explicitly logs `Falling back to standard scikit-learn engine` and records actual measured CPU latency (0.28 ms) rather than fabricating synthetic acceleration numbers.
