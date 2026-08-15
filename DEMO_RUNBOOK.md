# DEMO RUNBOOK: AI AQUACULTURE GUARDIAN
### Interactive Judge Demonstration & Evaluation Guide
**Intel® Vietnam AI Impact Festival 2026**

---

## 1. Quick Demonstration Commands

### Option A: Deterministic Competition Scenario (Recommended for Judges)
```bash
python run_demo.py --scenario competition_demo --seed 42
```
*Executes a deterministic 120-step aquaculture scenario showing the complete lifecycle from baseline to anomaly, crisis, and recovery.*

### Option B: Real-World IoT Dataset Stream
```bash
python run_real_demo.py --dataset mendeley_aquaculture --max_readings 50 --speed 10
```
*Streams 50 real-world telemetry readings from the Mendeley dataset at 10x playback speed.*

### Option C: Web Dashboard & Live REST API
```bash
python run_server.py
```
*Opens FastAPI backend and interactive web dashboard at `http://localhost:8000`.*

---

## 2. Six-Scene Narrative Structure (`run_demo.py`)

| Scene | Timestep | Physical Situation | AI System Behavior |
|:---:|:---:|:---|:---|
| **Scene 1** | Steps 1–30 | **Normal Baseline ($pH \approx 7.5$)** | System registers nominal water quality; Risk Score $< 10$; `[ OK ]` status badge. |
| **Scene 2** | Steps 31–60 | **Gradual Upward pH Drift ($pH \to 7.9$)** | Multi-horizon model projects upper threshold approach; Risk Score climbs to 15–20; Status transitions to `[ WARN ]`. |
| **Scene 3** | Steps 61–75 | **Statistical Anomaly Detected** | Hybrid anomaly engine detects rapid rate-of-change spike; XAI outputs probe inspection advice; Status badge displays `[ ANOMALY ]`. |
| **Scene 4** | Steps 76–105 | **Critical High pH Breach ($pH \approx 8.9$)** | Acute algal bloom condition; Risk Score surges to 35–45; Early Warning triggers 150m ahead; `[!HI!]` alert fires. |
| **Scene 5** | Steps 106–110 | **Farmer Intervention & Explainability** | XAI breaks down root causes (solar irradiance + photosynthesis); Recommendation engine prescribes SOP: activate paddlewheel aerators. |
| **Scene 6** | Steps 111–120 | **Stabilization & Model Calibration** | pH normalizes back to safe $7.50$; Online calibration incorporates post-event dynamics into historical ring buffer. |

---

## 3. Recommended 3-Minute Live Pitch & Demo Script

- **Minute 0:00 – 0:45 (The Problem & Vision)**:  
  *"In Vietnam's $10B aquaculture sector, water quality crashes cause massive fish/shrimp mortality within hours. Traditional threshold sensors alert farmers too late. We present AI Aquaculture Guardian—an Edge-native early warning system that forecasts water quality up to 2.5 hours in advance."*

- **Minute 0:45 – 2:00 (The Live Demo)**:  
  *Run `python run_demo.py --scenario competition_demo --seed 42`. Highlight Scene 2 and 4:*  
  *"Notice at step 50: while pH is still nominally safe at 7.89, our AI forecaster projects pH will breach 8.5 within 2.5 hours. The Risk Score climbs to 35, triggering proactive aerator activation before any fish mortality occurs."*

- **Minute 2:00 – 3:00 (Edge Performance & Responsible AI)**:  
  *"Our model achieves 73.4% MAE reduction on 37,284 real IoT readings with sub-2 ms CPU latency (1.42 ms P50). It operates strictly as a human-in-the-loop decision-support tool, ensuring farmers remain in control."*
