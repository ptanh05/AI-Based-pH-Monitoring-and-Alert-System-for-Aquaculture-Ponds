# Competition Demo Runbook & Judge Presentation Guide
## AI Aquaculture Guardian — Intel® Vietnam AI Impact Festival 2026

---

## 1. Quick Start: Demo Execution Commands

### A. Deterministic Competition Scenario (Recommended for Judges)
```bash
python run_demo.py --scenario competition_demo --seed 42
```

### B. Real-World IoT Dataset Continuous Streaming (CLI)
```bash
python run_real_demo.py --dataset mendeley_aquaculture --max_readings 50 --speed 10
```

### C. Interactive Web Dashboard & Real-Time Visualization
```bash
python run_demo.py --web
# Dashboard opens automatically at: http://localhost:8000
```

---

## 2. Six-Scene Narrative Structure (`competition_demo`)

| Scene | Timeline (Steps) | System Physical State | AI Guardian Autonomous Actions | Judge Talking Points |
|---|:---:|---|---|---|
| **Scene 1: Normal Pond** | Steps 1 – 35 | pH stable at $7.50 \pm 0.05$. Temperature 27°C, DO 8.0 mg/L. | Sensor Quality: `GOOD`. Risk: `LOW` (< 15/100). Status: `[ OK ]`. | "System continuously validates sensor kinetics and calculates real-time rolling statistics." |
| **Scene 2: Sub-threshold Trend** | Steps 36 – 60 | pH starts rising ($7.60 \to 8.05$). Rate: $+0.09\text{ pH/step}$. | Trend slope turns positive (+0.020). Risk elevates to `MODERATE` (18–35). | "Standard threshold alarms are silent (pH < 8.5), but AI feature extractor detects biological acceleration." |
| **Scene 3: Early Warning** | Steps 61 – 79 | pH reaches $8.10 \to 8.45$ (still strictly inside nominal safe zone). | **AI Forecast predicts pH breach to 8.65 within 25 min**. Risk elevates to `ELEVATED / HIGH`. | "AI gives farmer 25–75 minutes advance notice before boundary breach occurs." |
| **Scene 4: Boundary Breach** | Steps 80 – 95 | pH crosses upper threshold ($8.80 \to 8.93$). | Alert Engine triggers `HIGH pH ALERT`. Anomaly detector flags kinetic spike. | "Immediate escalation if preventative action was delayed." |
| **Scene 5: XAI & Decision Support** | Steps 96 – 105 | Elevated risk sustained ($R = 43/100$). | XAI attributes risk driver: *"pH is rising rapidly (+0.090 per reading), forecast approaching 8.46"*. Recommendation: *"Inspect pond conditions and check aeration"*. | "AI explains *why* the risk is high and suggests conservative farm SOP actions." |
| **Scene 6: Recovery** | Steps 106 – 120 | Corrective water management stabilizes pH back to $7.50$. | Risk score falls back to `LOW` ($R = 12.4$). Status returns to `[ OK ]`. | "System verifies environmental recovery and resumes standard routine monitoring." |

---

## 3. Verification Checklist for Presenters

1. **Deterministic Seed**: Always specify `--seed 42` for live presentation consistency.
2. **Terminal Encoding**: Run in standard Windows Terminal / PowerShell (UTF-8 console is automatically configured).
3. **Data Provenance Badge**: Verify the dashboard clearly displays `[ REAL DATA ]` when streaming Mendeley dataset and `[ DEMO / SIMULATION ]` during the competition scenario.
