# Pitch Deck & Competition Presentation Content
## AI Aquaculture Guardian — Intel® Vietnam AI Impact Festival 2026
**Theme**: *"Enriching Lives with AI Innovation"*

---

## Slide 1: Title & Vision
- **Product Name**: **AI Aquaculture Guardian**
- **Tagline**: *"AI-powered Early Warning System for Sustainable Aquaculture"*
- **Target Audience**: Intensive shrimp and fish farmers in Vietnam (Mekong Delta, Central Coastal Provinces) and Southeast Asia.
- **Mission**: Transforming reactive pond monitoring into proactive, AI-guided environmental risk prevention.

---

## Slide 2: The Problem (The Hidden Crisis in the Pond)
- **Aquaculture Mortality**: Water quality shifts (acid rain runoff, nocturnal oxygen depletion, algal blooms) can cause catastrophic biomass mortality within 1–2 hours.
- **The Threshold Alarm Dilemma**: Traditional IoT sensors only sound alarms *after* pH or DO breaches lethal limits ($< 6.5$ or $> 9.0$). By then, physiological damage or mass die-offs have already begun.
- **Farmer Pain Point**: Lack of advance notice prevents timely intervention (starting paddlewheel aerators, applying lime buffers).

---

## Slide 3: The Solution (AI Aquaculture Guardian)
- **Proactive Early Warning**: Predicts water quality trajectories **25 to 150 minutes in advance**.
- **Composite Risk Score (0–100)**: Synthesizes instantaneous pH, rate of change, trend slope, multi-step forecasts, and hybrid anomalies into one actionable metric.
- **Explainable Decision Support**: Explains *why* risk is rising and provides clear farm SOP recommendations.
- **Edge AI Architecture**: Runs locally on low-cost edge hardware without cloud dependency.

---

## Slide 4: Core Technology & Architecture
1. **Sensor Ingestion & Quality Quarantine**: Validates physical boundary limits and isolates flatlining/noisy probes.
2. **Multi-Step Recursive ML Forecasting**: Multivariate Random Forest trained with strict zero-leakage chronological splitting.
3. **Hybrid Anomaly Detection**: Rolling Z-Score + Rate of Change Kinetics + Stuck Sensor + Isolation Forest.
4. **Explainable AI (XAI)**: Feature contribution breakdown in plain language.
5. **Intel® OpenVINO™ Optimization**: Sub-millisecond edge CPU inference (< 0.3 ms).

---

## Slide 5: Empirical Real-World Validation
- **Dataset**: 37,284 high-resolution IoT observations from commercial Tilapia aquaculture (Mendeley Data DOI: `10.17632/8s73jfvgr5.2`, CC BY 4.0).
- **Advance Warning Performance (150 Minutes)**:
  - *Persistence Baseline*: $\text{MAE} = 0.1559, R^2 = -0.8400$ (Fails)
  - *AI Aquaculture Guardian*: **$\text{MAE} = 0.0382, R^2 = 0.8425$ (+75.50% error reduction)**.
- **Domain Shift Finding**: Documented $+300\%$ error increase in zero-shot simulation transfer, proving the essential need for our in-situ local calibration pipeline.

---

## Slide 6: Responsible AI & Safety
- **Advisory Decision Support**: AI assists farmers; it never executes dangerous autonomous chemical dosing.
- **Data Provenance Transparency**: Clear visual badges distinguish `[ REAL DATA ]` from `[ SIMULATION / DEMO ]`.
- **Conservative Error Handling**: Degraded sensor quality automatically biases risk assessments conservatively.

---

## Slide 7: Impact & Roadmap
- **Enriching Lives**: Protects rural aquaculture livelihoods, prevents harvest loss, and optimizes aerator energy consumption.
- **Roadmap**: Pilot edge testing in Mekong Delta shrimp farms; expansion to LoRaWAN multi-pond farm topologies.
