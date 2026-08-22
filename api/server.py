"""
FastAPI Server for AI Aquaculture Guardian.

Integrates the full AI pipeline:
Sensor Data → Validation → Features → Forecasting → Anomaly →
Risk → Early Warning → Explainability → Recommendations → Dashboard
"""

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
import threading
import time
import sys
import os
import json
import platform
import traceback

# ── Robust beep helper ──
def play_beep(duration_seconds: float = 2.0):
    try:
        if platform.system() == "Windows":
            try:
                import winsound
                winsound.Beep(1000, int(duration_seconds * 1000))
            except Exception:
                for _ in range(int(duration_seconds * 2)):
                    print("\a", end="", flush=True)
                    time.sleep(0.5)
        else:
            for _ in range(int(duration_seconds * 2)):
                print("\a", end="", flush=True)
                time.sleep(0.5)
    except Exception:
        pass

# ── Ensure Root Directory in sys.path for Vercel / Serverless Runtimes ──
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in [ROOT_DIR, os.getcwd(), "/var/task"]:
    if p and os.path.exists(p) and p not in sys.path:
        sys.path.insert(0, p)

# ── AI Pipeline Imports ──
from simulator.ph_simulator import PHSimulator, Scenario
from alerts.ph_alert_engine import PHAlertEngine, AlertStatus
from ai.forecasting import ForecastingEngine
from ai.anomaly import AnomalyDetector
from ai.risk import AquacultureRiskEngine
from ai.explainability import ExplainabilityEngine
from ai.recommendations import RecommendationEngine
from ai.sensor_schema import (
    SensorReading, SensorQualityMonitor, validate_reading,
)
from storage.alert_history import alert_history
from edge.inference_engine import (
    create_inference_engine, BaseInferenceEngine,
    OPENVINO_AVAILABLE, SKL2ONNX_AVAILABLE,
)
from ai.features import FeatureEngineer
from data.real_data_loader import RealDataLoader
from alerts.notification_dispatcher import dispatcher
from devices.actuator_manager import actuator_manager
from reports.report_generator import generate_csv_data, generate_html_report
from digital_twin.twin_simulator import digital_twin_simulator
from ai.chatbot_advisor import chatbot_advisor
from vision.fish_behavior_detector import fish_detector
from ai.drift_detector import drift_detector

# ── Global State ──
monitoring_system = None
system_thread = None
is_running = False
use_simulator = True
current_data_source = "demo"  # "demo" | "real_validation" | "live_sensor"
recent_readings = []
MAX_RECENT_READINGS = 200
manual_ph_queue = []


class PHMonitoringSystem:
    """Central orchestrator for all AI pipeline components."""

    def __init__(
        self,
        low_threshold: float = 7.0,
        high_threshold: float = 8.5,
        consecutive_count: int = 1,
        reading_interval_seconds: float = 1.0,
        scenario: Optional[str] = None,
        seed: Optional[int] = None,
    ):
        self.reading_interval_seconds = reading_interval_seconds

        self.simulator = PHSimulator(
            base_ph=7.5, noise_level=0.25, enable_events=True,
            scenario=scenario, seed=seed,
        )
        self.alert_engine = PHAlertEngine(
            low_threshold=low_threshold,
            high_threshold=high_threshold,
            consecutive_count=consecutive_count,
        )
        self.forecaster = ForecastingEngine(
            window_size=20, min_train_samples=30, retrain_interval=50,
        )
        self.anomaly_detector = AnomalyDetector(
            z_score_window=30, z_score_threshold=2.5,
            isolation_forest_samples=60,
        )
        self.risk_engine = AquacultureRiskEngine(
            low_threshold=low_threshold,
            high_threshold=high_threshold,
        )
        self.explainer = ExplainabilityEngine(
            low_threshold=low_threshold,
            high_threshold=high_threshold,
        )
        self.recommender = RecommendationEngine()
        self.sensor_monitor = SensorQualityMonitor()
        self.inference_engine: BaseInferenceEngine = create_inference_engine(
            prefer_openvino=True
        )

        self.reading_count = 0
        self.scenario = scenario
        self.seed = seed

        # Latest pipeline outputs
        self.latest_forecast: Optional[dict] = None
        self.latest_anomaly: Optional[dict] = None
        self.latest_risk: Optional[dict] = None
        self.latest_explanation: Optional[dict] = None
        self.latest_recommendations: Optional[dict] = None
        self.latest_alert_status: Optional[str] = None
        self.latest_alert_message: Optional[str] = None
        self.latest_sensor_quality: Optional[dict] = None


# ── Pydantic Models ──
class ReadingResponse(BaseModel):
    timestamp: str
    ph_value: float
    status: str
    predicted_ph: Optional[float] = None
    predicted_timestamp: Optional[str] = None
    has_early_warning: bool = False
    warning_message: Optional[str] = None
    risk_score: Optional[float] = None
    risk_level: Optional[str] = None

class StatusResponse(BaseModel):
    is_running: bool
    total_readings: int
    current_status: str
    model_info: dict
    thresholds: dict

class ManualPHInput(BaseModel):
    ph_value: float
    timestamp: Optional[str] = None


IS_SERVERLESS = bool(
    os.environ.get("VERCEL")
    or os.environ.get("VERCEL_ENV")
    or os.environ.get("AWS_LAMBDA_FUNCTION_NAME")
)


def step_serverless_simulation():
    """Step simulation on-demand for serverless environments (Vercel) without background threads."""
    global monitoring_system
    if not monitoring_system or not use_simulator:
        return
    try:
        ts, ph = monitoring_system.simulator.generate_reading()
        process_ph_reading(ts, ph)
    except Exception as e:
        print(f"Serverless simulation step error: {e}")


def ensure_system_initialized():
    global monitoring_system, recent_readings
    if monitoring_system is None:
        monitoring_system = PHMonitoringSystem()
    if not recent_readings:
        base_time = datetime.now() - timedelta(minutes=20)
        for i in range(20):
            ts = base_time + timedelta(minutes=i)
            try:
                _, ph = monitoring_system.simulator.generate_reading()
                process_ph_reading(ts, ph)
            except Exception:
                process_ph_reading(ts, 7.5)
    elif IS_SERVERLESS:
        step_serverless_simulation()


@asynccontextmanager
async def lifespan(app: FastAPI):
    global system_thread
    ensure_system_initialized()
    if not IS_SERVERLESS:
        system_thread = threading.Thread(target=run_monitoring_system, daemon=True)
        system_thread.start()
        print("[AI Aquaculture Guardian] Background monitoring thread started")
    else:
        print("[AI Aquaculture Guardian] Serverless mode active (on-demand simulation)")
    yield
    global is_running
    is_running = False
    print("[AI Aquaculture Guardian] Monitoring stopped")


# ── FastAPI App ──
app = FastAPI(
    title="AI Aquaculture Guardian API",
    description="AI-powered Early Warning System for Sustainable Aquaculture",
    version="2.0.0",
    lifespan=None if IS_SERVERLESS else lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def ensure_initialized_middleware(request: Request, call_next):
    """Ensure AI pipeline is initialized and step simulation on serverless invocations."""
    if request.url.path.startswith("/api") or request.url.path == "/":
        ensure_system_initialized()
    response = await call_next(request)
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "error_type": type(exc).__name__},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "error_type": "ValidationError"},
    )


# ── Core Processing ──
def process_ph_reading(timestamp: datetime, ph_value: float):
    """Process a single pH reading through the full AI pipeline."""
    global monitoring_system, recent_readings

    if not monitoring_system:
        return

    ms = monitoring_system

    # 1. Sensor validation
    reading = SensorReading(
        timestamp=timestamp,
        sensor_id="POND-01-PH",
        pond_id="POND-01",
        parameter="pH",
        value=ph_value,
        unit="pH",
        source="simulator" if use_simulator else "manual_input",
    )
    quality_result = ms.sensor_monitor.process(reading)
    sensor_quality_str = quality_result.quality.value
    ms.latest_sensor_quality = ms.sensor_monitor.get_health_summary()

    # 2. Feature engineering + Forecasting
    ms.forecaster.add_reading(ph_value, timestamp)

    # Try to load model into inference engine if newly trained
    if ms.forecaster.is_trained and ms.forecaster.get_sklearn_model() is not None:
        n_features = len(FeatureEngineer.FEATURE_NAMES)
        engine_info = ms.inference_engine.get_info()
        if not engine_info.get("model_loaded", False):
            ms.inference_engine.load_model(
                ms.forecaster.get_sklearn_model(), n_features
            )

    hour = timestamp.hour + timestamp.minute / 60.0
    predicted_ph, is_trained = ms.forecaster.predict_single(hour)
    forecast_result = ms.forecaster.predict_multistep(n_steps=30, hour_of_day=hour)
    ms.latest_forecast = forecast_result

    # 3. Anomaly detection
    ms.anomaly_detector.add_reading(ph_value)
    anomaly_result = ms.anomaly_detector.detect(ph_value)
    ms.latest_anomaly = anomaly_result

    # 4. Extract features for risk
    values = ms.forecaster.history
    fe = ms.forecaster.feature_engineer
    if len(values) >= 2:
        features = fe.extract(values, hour)
        rate_of_change = float(features[6])  # rate_of_change
        trend = float(features[5])           # trend
    else:
        rate_of_change = 0.0
        trend = 0.0

    # 5. Risk scoring
    risk_result = ms.risk_engine.compute(
        current_ph=ph_value,
        predicted_ph=predicted_ph,
        rate_of_change=rate_of_change,
        trend=trend,
        anomaly_score=anomaly_result.get("anomaly_score", 0.0),
    )
    ms.latest_risk = risk_result

    # 6. Early warning (full pipeline)
    alert_status, alert_message = ms.alert_engine.process_full(
        timestamp=timestamp,
        ph_value=ph_value,
        predicted_ph=predicted_ph,
        risk_total=risk_result["total"],
        risk_level=risk_result["level"],
        anomaly_detected=anomaly_result.get("is_anomaly", False),
        sensor_quality=sensor_quality_str,
    )
    ms.latest_alert_status = alert_status.value
    ms.latest_alert_message = alert_message

    # 7. Explainability
    model_info = ms.forecaster.get_model_info()
    explanation = ms.explainer.explain(
        current_ph=ph_value,
        predicted_ph=predicted_ph,
        risk_result=risk_result,
        anomaly_result=anomaly_result,
        rate_of_change=rate_of_change,
        trend=trend,
        feature_importance=model_info.get("feature_importance"),
        feature_names=model_info.get("feature_names"),
    )
    ms.latest_explanation = explanation

    # 8. Recommendations
    recommendations = ms.recommender.generate(
        risk_level=risk_result["level"],
        risk_total=risk_result["total"],
        current_ph=ph_value,
        predicted_ph=predicted_ph,
        anomaly_result=anomaly_result,
        sensor_quality=sensor_quality_str,
    )
    ms.latest_recommendations = recommendations

    # 9. Play beep on significant alerts
    if alert_status in [
        AlertStatus.ALERT_LOW_PH, AlertStatus.ALERT_HIGH_PH,
        AlertStatus.CRITICAL, AlertStatus.HIGH_RISK,
    ]:
        alert_history.add_alert(
            timestamp=timestamp,
            ph_value=ph_value,
            alert_type=alert_status.value,
            predicted_ph=predicted_ph,
            threshold_low=ms.alert_engine.low_threshold,
            threshold_high=ms.alert_engine.high_threshold,
            message=alert_message,
        )
        threading.Thread(target=play_beep, args=(1.5,), daemon=True).start()

    # 9b. Dispatch notifications (Telegram / Email) & Evaluate IoT Actuators
    eval_dict = {
        "timestamp": timestamp.isoformat(),
        "ph_value": ph_value,
        "predicted_ph": predicted_ph,
        "risk_score": risk_result["total"],
        "status": alert_status.value,
        "alert_status": alert_status.value,
        "warning_message": alert_message,
        "do_value": 7.8,
        "turbidity": 4.2,
        "temperature": 27.5
    }
    try:
        dispatcher.dispatch_alert(eval_dict)
    except Exception as e:
        print(f"Notification error: {e}")
    try:
        actuator_manager.evaluate_conditions(eval_dict)
    except Exception as e:
        print(f"Actuator error: {e}")

    # 9c. Track Concept Drift & Check Auto-Adaptation
    try:
        drift_detector.add_sample(ph_value)
        drift_res = drift_detector.check_drift()
        if drift_res.get("status") == "DRIFT_DETECTED" and drift_detector.auto_retrain_enabled:
            drift_detector.adapt_model(ms.forecaster)
    except Exception as e:
        print(f"Drift check error: {e}")

    # 10. Store reading
    future_ts = timestamp + timedelta(seconds=10)
    has_warning = alert_status in [
        AlertStatus.EARLY_WARNING, AlertStatus.HIGH_RISK, AlertStatus.CRITICAL,
    ]

    reading_resp = ReadingResponse(
        timestamp=timestamp.isoformat(),
        ph_value=ph_value,
        status=alert_status.value,
        predicted_ph=predicted_ph,
        predicted_timestamp=future_ts.isoformat(),
        has_early_warning=has_warning,
        warning_message=alert_message if has_warning else None,
        risk_score=risk_result["total"],
        risk_level=risk_result["level"],
    )

    recent_readings.append(reading_resp)
    if len(recent_readings) > MAX_RECENT_READINGS:
        recent_readings.pop(0)

    ms.reading_count += 1


def run_monitoring_system():
    global monitoring_system, is_running, use_simulator, current_data_source, manual_ph_queue

    if monitoring_system is None:
        monitoring_system = PHMonitoringSystem()

    is_running = True

    while is_running:
        try:
            if current_data_source == "real_validation":
                loader = RealDataLoader()
                for timestamp, ph_value, ctx in loader.stream_real_readings():
                    if not is_running or current_data_source != "real_validation":
                        break
                    try:
                        process_ph_reading(timestamp, ph_value)
                    except Exception as pe:
                        print(f"Error processing reading: {pe}")
                    time.sleep(monitoring_system.reading_interval_seconds)
            elif use_simulator:
                for timestamp, ph_value in monitoring_system.simulator.stream_readings(
                    interval_seconds=monitoring_system.reading_interval_seconds,
                    max_readings=None,
                ):
                    if not is_running or current_data_source != "demo":
                        break
                    try:
                        process_ph_reading(timestamp, ph_value)
                    except Exception as pe:
                        print(f"Error processing reading: {pe}")
            else:
                while is_running and current_data_source == "live_sensor":
                    if manual_ph_queue:
                        ph_data = manual_ph_queue.pop(0)
                        ts = (
                            datetime.fromisoformat(ph_data["timestamp"])
                            if ph_data.get("timestamp")
                            else datetime.now()
                        )
                        try:
                            process_ph_reading(ts, ph_data["ph_value"])
                        except Exception as pe:
                            print(f"Error processing reading: {pe}")
                    time.sleep(0.5)
        except Exception as e:
            print(f"Error in monitoring loop: {e}")
            traceback.print_exc()
            time.sleep(1.0)
            if not is_running:
                break




# ══════════════════════════════════════════════════
# API ENDPOINTS
# ══════════════════════════════════════════════════

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

@app.get("/", response_class=HTMLResponse)
@app.get("/api/index", response_class=HTMLResponse)
async def root():
    dash_path = os.path.join(BASE_DIR, "dashboard", "index.html")
    try:
        with open(dash_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<html><body><h1>AI Aquaculture Guardian API</h1><p>Dashboard not found. Visit <a href='/docs'>/docs</a>.</p></body></html>"

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return HTMLResponse(content="", status_code=204)

@app.get("/i18n.js")
async def serve_i18n_js():
    """Serve the i18n translation module for the dashboard."""
    i18n_path = os.path.join(BASE_DIR, "dashboard", "i18n.js")
    if os.path.exists(i18n_path):
        return FileResponse(i18n_path, media_type="application/javascript")
    raise HTTPException(status_code=404, detail="i18n.js not found")

@app.get("/api/status")
async def get_status():
    ensure_system_initialized()
    return {
        "is_running": is_running,
        "total_readings": monitoring_system.reading_count,
        "current_status": monitoring_system.alert_engine.get_status().value,
        "model_info": monitoring_system.forecaster.get_model_info(),
        "thresholds": {
            "low": monitoring_system.alert_engine.low_threshold,
            "high": monitoring_system.alert_engine.high_threshold,
        },
        "scenario": monitoring_system.scenario,
        "data_source": "simulator" if use_simulator else "manual",
    }

@app.get("/api/current")
async def get_current_reading():
    ensure_system_initialized()
    if not recent_readings:
        raise HTTPException(status_code=404, detail="No readings available yet")
    return recent_readings[-1]

@app.get("/api/history")
async def get_history(limit: int = 50):
    readings = recent_readings[-limit:] if limit > 0 else recent_readings
    return {"readings": readings, "count": len(readings)}

@app.get("/api/forecast")
async def get_forecast(steps: int = 30):
    if not monitoring_system:
        raise HTTPException(status_code=503, detail="System not initialized")
    hour = datetime.now().hour + datetime.now().minute / 60.0
    result = monitoring_system.forecaster.predict_multistep(n_steps=steps, hour_of_day=hour)
    result["sampling_interval_seconds"] = monitoring_system.reading_interval_seconds
    return result

@app.get("/api/prediction")
async def get_prediction():
    """Backward-compatible prediction endpoint."""
    if not monitoring_system:
        raise HTTPException(status_code=503, detail="System not initialized")
    hour = datetime.now().hour + datetime.now().minute / 60.0
    predicted_ph, is_trained = monitoring_system.forecaster.predict_single(hour)
    return {
        "predicted_ph": predicted_ph,
        "is_reliable": is_trained,
        "model_type": monitoring_system.forecaster.get_model_info()["model_type"],
    }

@app.get("/api/risk")
async def get_risk():
    if not monitoring_system or not monitoring_system.latest_risk:
        return {"total": 0, "level": "LOW", "components": {}}
    return monitoring_system.latest_risk

@app.get("/api/anomalies")
async def get_anomalies():
    if not monitoring_system or not monitoring_system.latest_anomaly:
        return {"is_anomaly": False, "anomaly_score": 0.0, "reasons": []}
    return monitoring_system.latest_anomaly

@app.get("/api/explanation")
async def get_explanation():
    if not monitoring_system or not monitoring_system.latest_explanation:
        return {"summary": "Waiting for data...", "reasons": []}
    return monitoring_system.latest_explanation

@app.get("/api/recommendations")
async def get_recommendations():
    if not monitoring_system or not monitoring_system.latest_recommendations:
        return {"actions": [], "disclaimer": "System initializing..."}
    return monitoring_system.latest_recommendations

@app.get("/api/alerts")
async def get_alerts():
    if not monitoring_system:
        raise HTTPException(status_code=503, detail="System not initialized")
    status = monitoring_system.alert_engine.get_status()
    return {
        "status": status.value,
        "summary": monitoring_system.alert_engine.get_status_summary(),
        "message": monitoring_system.latest_alert_message,
        "is_alerting": status in [
            AlertStatus.ALERT_LOW_PH, AlertStatus.ALERT_HIGH_PH,
            AlertStatus.HIGH_RISK, AlertStatus.CRITICAL,
        ],
    }

@app.get("/api/alert-history")
async def get_alert_history(limit: int = 50, alert_type: Optional[str] = None):
    if alert_type:
        alerts = alert_history.get_alerts_by_type(alert_type, limit)
    else:
        alerts = alert_history.get_recent_alerts(limit)
    return {
        "alerts": alerts,
        "statistics": alert_history.get_statistics(),
        "count": len(alerts),
    }

@app.get("/api/alert-statistics")
async def get_alert_statistics():
    return alert_history.get_statistics()

@app.get("/api/model-metrics")
async def get_model_metrics():
    if not monitoring_system:
        raise HTTPException(status_code=503, detail="System not initialized")
    info = monitoring_system.forecaster.get_model_info()
    feature_labels = info.get("feature_names", [])
    importance = info.get("feature_importance")
    return {
        "model_type": info.get("model_type", "Unknown"),
        "is_trained": info.get("is_trained", False),
        "history_size": info.get("history_size", 0),
        "accuracy": info.get("train_metrics"),
        "feature_importance": {
            "values": importance,
            "labels": feature_labels[:len(importance)] if importance else [],
        } if importance else None,
        "total_retrains": info.get("total_retrains", 0),
    }

@app.get("/api/inference-engine")
async def get_inference_engine():
    if not monitoring_system:
        return {"backend": "not_initialized"}
    return monitoring_system.inference_engine.get_info()

@app.get("/api/system-health")
async def get_system_health():
    if not monitoring_system:
        raise HTTPException(status_code=503, detail="System not initialized")
    return {
        "sensor_health": monitoring_system.latest_sensor_quality or {},
        "anomaly_detector": monitoring_system.anomaly_detector.get_info(),
        "forecaster": {
            "is_trained": monitoring_system.forecaster.is_trained,
            "history_size": len(monitoring_system.forecaster.history),
        },
        "inference_engine": monitoring_system.inference_engine.get_info(),
        "total_readings": monitoring_system.reading_count,
        "is_running": is_running,
    }

@app.get("/api/benchmark")
async def get_benchmark():
    if not monitoring_system:
        raise HTTPException(status_code=503, detail="System not initialized")
    if not monitoring_system.forecaster.is_trained:
        return {"error": "Model not trained yet. Collect more data."}
    import numpy as np
    n_features = len(FeatureEngineer.FEATURE_NAMES)
    X_sample = np.random.rand(1, n_features)
    result = monitoring_system.inference_engine.benchmark(X_sample, n_iterations=200)
    result["engine"] = monitoring_system.inference_engine.get_info().get("backend", "unknown")
    return result

@app.post("/api/scenario")
async def set_scenario(scenario: str = "competition_demo", seed: int = 42):
    global monitoring_system, is_running, recent_readings, system_thread, current_data_source, use_simulator
    is_running = False
    time.sleep(0.3)
    recent_readings = []
    current_data_source = "demo"
    use_simulator = True
    monitoring_system = PHMonitoringSystem(
        scenario=scenario, seed=seed, reading_interval_seconds=0.8,
    )
    system_thread = threading.Thread(target=run_monitoring_system, daemon=True)
    system_thread.start()
    return {
        "success": True,
        "scenario": scenario,
        "seed": seed,
        "available_scenarios": PHSimulator.available_scenarios(),
    }

@app.post("/api/retrain-model")
async def retrain_model():
    if not monitoring_system:
        raise HTTPException(status_code=503, detail="System not initialized")
    success = monitoring_system.forecaster.train()
    return {
        "success": success,
        "model_info": monitoring_system.forecaster.get_model_info(),
    }

@app.post("/api/submit-ph")
async def submit_ph(input_data: ManualPHInput):
    global manual_ph_queue, use_simulator
    if use_simulator:
        return {
            "success": False,
            "message": "System is in auto mode. Switch to manual: POST /api/set-mode?mode=manual",
        }
    if not (0.0 <= input_data.ph_value <= 14.0):
        raise HTTPException(status_code=400, detail="pH must be 0-14")
    manual_ph_queue.append({
        "ph_value": input_data.ph_value,
        "timestamp": input_data.timestamp or datetime.now().isoformat(),
    })
    return {"success": True, "ph_value": input_data.ph_value}

@app.post("/api/set-mode")
async def set_mode(mode: str = "auto"):
    """Legacy endpoint for switching auto/manual mode."""
    global use_simulator, current_data_source
    if mode.lower() == "manual":
        use_simulator = False
        current_data_source = "live_sensor"
        return {"success": True, "mode": "manual"}
    elif mode.lower() == "auto":
        use_simulator = True
        current_data_source = "demo"
        return {"success": True, "mode": "auto"}
    raise HTTPException(status_code=400, detail="Mode must be 'auto' or 'manual'")


@app.get("/api/source-info")
async def get_source_info():
    """Legacy endpoint returning data source provenance."""
    return {
        "current_mode": "auto" if use_simulator else "manual",
        "data_source": "simulator (synthetic)" if current_data_source == "demo" else "real_world_validation" if current_data_source == "real_validation" else "manual_input",
        "active_source": current_data_source,
        "disclaimer": "Data provenance: " + ("Software simulator" if current_data_source == "demo" else "Mendeley Data DOI 10.17632/8s73jfvgr5.2" if current_data_source == "real_validation" else "Live manual/sensor input"),
    }


@app.get("/api/data-sources")
async def get_data_sources():
    """Return available data sources and active mode."""
    return {
        "active_source": current_data_source,
        "available_sources": [
            {
                "id": "demo",
                "name": "Competition Demo (Synthetic Simulator)",
                "description": "Deterministic competition scenarios with synthetic mathematical generation.",
                "provenance": "SIMULATED",
            },
            {
                "id": "real_validation",
                "name": "Real-World Validation (Mendeley Data)",
                "description": "37,284 high-resolution IoT observations from Tilapia ponds in Montería, Colombia (2024).",
                "provenance": "REAL-WORLD DATASET (DOI: 10.17632/8s73jfvgr5.2)",
            },
            {
                "id": "live_sensor",
                "name": "Live Sensor / Manual Input",
                "description": "Accepts live HTTP payload from hardware probe gateways or manual input.",
                "provenance": "LIVE SENSOR / MANUAL",
            },
        ],
    }


@app.post("/api/select-source")
async def select_source(source: str = "demo"):
    """Switch active data source mode (demo | real_validation | live_sensor)."""
    global current_data_source, use_simulator, is_running, recent_readings, system_thread
    source = source.lower()
    if source not in ["demo", "real_validation", "live_sensor"]:
        raise HTTPException(status_code=400, detail="Invalid source. Must be 'demo', 'real_validation', or 'live_sensor'")

    is_running = False
    time.sleep(1.0)
    current_data_source = source
    recent_readings = []

    if source == "demo":
        use_simulator = True
    elif source == "real_validation":
        use_simulator = True
    else:  # live_sensor
        use_simulator = False

    system_thread = threading.Thread(target=run_monitoring_system, daemon=True)
    system_thread.start()

    return {
        "success": True,
        "active_source": current_data_source,
        "mode": "auto" if use_simulator else "manual",
    }


@app.get("/api/real-data/status")
async def get_real_data_status():
    """Get metadata about the real-world dataset."""
    reports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports")
    quality_path = os.path.join(reports_dir, "real_data_quality.json")
    if os.path.exists(quality_path):
        with open(quality_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "dataset_name": "Environmental Parameters in Aquaculture",
        "doi": "10.17632/8s73jfvgr5.2",
        "license": "CC BY 4.0",
        "status": "Loaded in data/real/",
    }


@app.get("/api/real-data/validation")
async def get_real_data_validation():
    """Get 3-way evaluation results comparing synthetic vs real data."""
    reports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports")
    res_path = os.path.join(reports_dir, "three_way_comparison.json")
    if os.path.exists(res_path):
        with open(res_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"message": "Run python scripts/evaluate_real_forecasting.py to generate."}


@app.get("/api/real-data/multisensor")
async def get_real_multisensor():
    """Get cross-parameter correlation analysis from real dataset."""
    reports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports")
    res_path = os.path.join(reports_dir, "multisensor_analysis.json")
    if os.path.exists(res_path):
        with open(res_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"message": "Run python scripts/analyze_multisensor.py to generate."}


# ── Notification Endpoints ──
class NotificationConfigRequest(BaseModel):
    enabled: bool
    telegram_token: Optional[str] = ""
    telegram_chat_id: Optional[str] = ""
    email: Optional[str] = ""

@app.get("/api/notifications/config")
async def get_notification_config():
    return dispatcher.get_config()

@app.post("/api/notifications/config")
async def set_notification_config(req: NotificationConfigRequest):
    dispatcher.configure(
        enabled=req.enabled,
        telegram_token=req.telegram_token,
        telegram_chat_id=req.telegram_chat_id,
        email=req.email
    )
    return {"success": True, "config": dispatcher.get_config()}

@app.post("/api/notifications/test")
async def test_notification():
    msg = (
        f"🧪 *AI AQUACULTURE GUARDIAN - TIN NHẮN THỬ NGHIỆM*\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"• *Hệ thống:* Hoạt động bình thường\n"
        f"• *Kênh thông báo:* Telegram Bot / Webhook\n"
        f"• *Thời gian:* {time.strftime('%H:%M:%S %d/%m/%Y')}\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"✅ Kết nối thành công! Bạn sẽ nhận được thông báo khi có cảnh báo khẩn cấp."
    )
    res = dispatcher.send_telegram_message(msg)
    return res


# ── IoT Actuators & Automation Endpoints ──
class ActuatorModeRequest(BaseModel):
    mode: str

class ActuatorToggleRequest(BaseModel):
    device_id: str
    state: Optional[bool] = None
    reason: Optional[str] = ""

@app.get("/api/actuators")
async def get_actuators_status():
    return actuator_manager.get_status()

@app.post("/api/actuators/mode")
async def set_actuator_mode(req: ActuatorModeRequest):
    new_mode = actuator_manager.set_mode(req.mode)
    return {"success": True, "mode": new_mode}

@app.post("/api/actuators/toggle")
async def toggle_actuator(req: ActuatorToggleRequest):
    new_state = actuator_manager.toggle_device(req.device_id, req.state, req.reason or "Thao tác từ Dashboard")
    return {"success": True, "device_id": req.device_id, "is_on": new_state}


# ── Export Endpoints (CSV & HTML/PDF Report) ──
@app.get("/api/export/csv")
async def export_csv():
    history_buf = {
        "labels": [r.timestamp for r in recent_readings],
        "actual": [r.ph_value for r in recent_readings],
        "forecast": [r.predicted_ph or r.ph_value for r in recent_readings],
        "upper": [8.5] * len(recent_readings),
        "lower": [7.0] * len(recent_readings),
        "risk": [r.risk_score or 0.0 for r in recent_readings],
    }
    csv_content = generate_csv_data(history_buf)
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=aquaculture_data_{int(time.time())}.csv"}
    )

@app.get("/api/export/report")
async def export_report():
    current_data = recent_readings[-1].__dict__ if recent_readings else {}
    history_buf = {
        "labels": [r.timestamp for r in recent_readings],
        "actual": [r.ph_value for r in recent_readings],
        "forecast": [r.predicted_ph or r.ph_value for r in recent_readings],
        "upper": [8.5] * len(recent_readings),
        "lower": [7.0] * len(recent_readings),
        "risk": [r.risk_score or 0.0 for r in recent_readings],
    }
    html_content = generate_html_report(current_data, history_buf, actuator_manager.get_status())
    return HTMLResponse(content=html_content)


# ── Digital Twin "What-If" Simulation Endpoints ──
class DigitalTwinSimRequest(BaseModel):
    rainfall_mm: Optional[float] = 0.0
    heat_multiplier: Optional[float] = 1.0
    lime_kg: Optional[float] = 0.0
    aerator_hours: Optional[float] = 0.0
    water_exchange_pct: Optional[float] = 0.0
    pond_volume_m3: Optional[float] = 1000.0
    n_steps: Optional[int] = 24

@app.post("/api/digital-twin/simulate")
async def run_digital_twin_simulation(req: DigitalTwinSimRequest):
    last_reading = recent_readings[-1] if recent_readings else None
    current_ph = last_reading.ph_value if last_reading else 7.5
    res = digital_twin_simulator.simulate(
        current_ph=current_ph,
        current_do=7.5,
        current_temp=28.0,
        pond_volume_m3=req.pond_volume_m3 or 1000.0,
        rainfall_mm=req.rainfall_mm or 0.0,
        heat_multiplier=req.heat_multiplier or 1.0,
        lime_kg=req.lime_kg or 0.0,
        aerator_hours=req.aerator_hours or 0.0,
        water_exchange_pct=req.water_exchange_pct or 0.0,
        n_steps=req.n_steps or 24,
    )
    return res


# ── AI Aquaculture Chatbot Endpoints ──
class ChatQueryRequest(BaseModel):
    query: str
    lang: Optional[str] = "vi"

@app.post("/api/ai/chat")
async def chat_with_advisor(req: ChatQueryRequest):
    last_reading = recent_readings[-1] if recent_readings else None
    telemetry = {
        "ph_value": last_reading.ph_value if last_reading else 7.5,
        "predicted_ph": last_reading.predicted_ph if last_reading else 7.5,
        "risk_score": last_reading.risk_score if last_reading else 0.0,
        "status": last_reading.status if last_reading else "NORMAL",
        "do_value": 7.8,
        "temperature": 27.5,
        "pond_volume_m3": 1000.0,
    }
    answer = chatbot_advisor.answer_query(req.query, telemetry, lang=req.lang or "vi")
    return answer

@app.get("/api/ai/chat/prompts")
async def get_chat_prompts(lang: str = "vi"):
    return {"prompts": chatbot_advisor.get_quick_prompts(lang)}


# ── Computer Vision Bio-Behavior Endpoints ──
@app.get("/api/vision/status")
async def get_vision_status():
    last_reading = recent_readings[-1] if recent_readings else None
    telemetry = {
        "ph_value": last_reading.ph_value if last_reading else 7.5,
        "do_value": 7.5,
        "risk_score": last_reading.risk_score if last_reading else 0.0,
        "status": last_reading.status if last_reading else "NORMAL",
    }
    return fish_detector.process_frame(telemetry)


# ── Concept Drift & Continual Learning Endpoints ──
@app.get("/api/drift/status")
async def get_drift_status():
    return drift_detector.check_drift()

@app.post("/api/drift/retrain")
async def trigger_drift_retrain():
    ms = monitoring_system
    forecaster = ms.forecaster if ms else None
    res = drift_detector.adapt_model(forecaster)
    return {"success": True, "details": res}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
