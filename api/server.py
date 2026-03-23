"""
FastAPI Server for pH Monitoring System

Provides REST API endpoints for:
- Getting current pH status
- Getting historical data
- Getting predictions
- Getting alerts
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import threading
import time
import sys
import platform
import traceback

# Robust beep helper (prefers native sound, falls back to console bell)
def play_beep(duration_seconds: float = 2.0):
    """Play an audible beep for the given duration (seconds)."""
    try:
        if platform.system() == "Windows":
            try:
                import winsound
                # Use Beep; if blocked, fall back to MessageBeep
                winsound.Beep(1000, int(duration_seconds * 1000))
            except Exception:
                try:
                    import winsound
                    winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
                    time.sleep(duration_seconds)
                except Exception:
                    # Last-resort: console bell
                    for _ in range(int(duration_seconds * 2)):
                        print("\a", end="", flush=True)
                        time.sleep(0.5)
        else:
            # Linux/Mac: console bell loop (works in most terminals)
            for _ in range(int(duration_seconds * 2)):  # 2 beeps per second
                print("\a", end="", flush=True)
                time.sleep(0.5)
    except Exception:
        # Final fallback to avoid crashing alert flow
        for _ in range(int(duration_seconds * 2)):
            print("\a", end="", flush=True)
            time.sleep(0.5)

from simulator.ph_simulator import PHSimulator
from alerts.ph_alert_engine import PHAlertEngine, AlertStatus
from ai.ph_predictor import PHPredictor
from storage.alert_history import alert_history


# Global monitoring system
monitoring_system = None
system_thread = None
is_running = False
use_simulator = True  # True = tự động từ simulator, False = nhập thủ công

# Data storage for API
recent_readings = []
MAX_RECENT_READINGS = 100
manual_ph_queue = []  # Queue để lưu pH nhập thủ công


class PHMonitoringSystem:
    """Wrapper for monitoring system components."""
    
    def __init__(
        self,
        low_threshold: float = 7.0,
        high_threshold: float = 8.5,
        consecutive_count: int = 1,  # cảnh báo ngay khi vượt ngưỡng
        prediction_horizon_minutes: int = 30,
        reading_interval_seconds: float = 1.0,
        prediction_horizon_seconds: int = 10,
    ):
        # Store interval for simulator loop
        self.reading_interval_seconds = reading_interval_seconds

        # Components
        # Increase noise a bit to trigger alerts faster in demo
        self.simulator = PHSimulator(base_ph=7.5, noise_level=0.25, enable_events=True)
        self.alert_engine = PHAlertEngine(
            low_threshold=low_threshold,
            high_threshold=high_threshold,
            consecutive_count=consecutive_count,
        )
        self.predictor = PHPredictor(
            prediction_horizon_minutes=prediction_horizon_minutes,
            prediction_horizon_seconds=prediction_horizon_seconds,
            min_samples_for_training=15,  # Giảm xuống để train sớm hơn
        )
        self.reading_count = 0


class ReadingResponse(BaseModel):
    """Response model for pH reading."""
    timestamp: str
    ph_value: float
    status: str
    predicted_ph: Optional[float] = None
    predicted_timestamp: Optional[str] = None  # Timestamp của prediction (timestamp + 10s)
    has_early_warning: bool = False
    warning_message: Optional[str] = None


class StatusResponse(BaseModel):
    """Response model for system status."""
    is_running: bool
    total_readings: int
    current_status: str
    model_info: dict
    thresholds: dict


class HistoricalDataResponse(BaseModel):
    """Response model for historical data."""
    readings: List[ReadingResponse]
    count: int


class ManualPHInput(BaseModel):
    """Request model for manual pH input."""
    ph_value: float
    timestamp: Optional[str] = None  # Optional, sẽ dùng thời gian hiện tại nếu không có


# Initialize FastAPI app
app = FastAPI(
    title="pH Monitoring System API",
    description="REST API for AI-based pH monitoring and alerting",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions and return JSON."""
    print(f"❌ Unhandled exception: {exc}")
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={
            "detail": str(exc),
            "error_type": type(exc).__name__
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors."""
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "error_type": "ValidationError"
        }
    )


def process_ph_reading(timestamp: datetime, ph_value: float):
    """
    Process a single pH reading through the monitoring system.
    
    Args:
        timestamp: Timestamp of the reading
        ph_value: pH value to process
    """
    global monitoring_system, recent_readings
    
    if not monitoring_system:
        return
    
    # Process reading
    # Thêm pH hiện tại vào lịch sử để train AI
    monitoring_system.predictor.add_reading(timestamp, ph_value)
    
    # Dự đoán pH cho 10 giây sau (future prediction)
    from datetime import timedelta
    future_timestamp = timestamp + timedelta(seconds=10)
    predicted_ph, is_reliable = monitoring_system.predictor.predict(ph_value)
    
    # Update accuracy: so sánh prediction trước đó với pH hiện tại
    if len(monitoring_system.predictor.ph_history) > 1:
        # Lấy prediction từ 10 giây trước (nếu có) và so sánh với pH hiện tại
        if len(monitoring_system.predictor.accuracy_history) > 0:
            # Prediction từ 10 giây trước nên được so sánh với pH hiện tại
            monitoring_system.predictor.update_accuracy(predicted_ph, ph_value)
    
    # Check alert cho pH hiện tại
    alert_status, alert_message = monitoring_system.alert_engine.process_reading(
        timestamp, ph_value
    )
    
    # Check early warning cho pH dự đoán (10 giây sau)
    has_warning, warning_msg = monitoring_system.predictor.check_early_warning(
        predicted_ph, 
        monitoring_system.alert_engine.low_threshold,
        monitoring_system.alert_engine.high_threshold
    )
    
    # Phát tiếng beep khi có cảnh báo và lưu vào lịch sử
    if alert_status in [AlertStatus.ALERT_LOW_PH, AlertStatus.ALERT_HIGH_PH]:
        print(f"\n⚠️ ALERT: pH = {ph_value:.2f} | Status: {alert_status.value}")
        
        # Lưu cảnh báo vào lịch sử
        alert_history.add_alert(
            timestamp=timestamp,
            ph_value=ph_value,
            alert_type=alert_status.value,
            predicted_ph=predicted_ph,
            threshold_low=monitoring_system.alert_engine.low_threshold,
            threshold_high=monitoring_system.alert_engine.high_threshold,
            message=alert_message
        )
        
        # Phát beep trong 2 giây (ổn định, không ngẫu nhiên)
        beep_duration = 2.0
        # Chạy beep trong thread riêng để không block
        beep_thread = threading.Thread(
            target=play_beep,
            args=(beep_duration,),
            daemon=True
        )
        beep_thread.start()
    
    # Store reading - luôn trả về predicted_ph (có thể chưa reliable)
    # predicted_ph là dự đoán cho 10 giây sau (future_timestamp)
    reading = ReadingResponse(
        timestamp=timestamp.isoformat(),
        ph_value=ph_value,  # pH hiện tại tại timestamp này
        status=alert_status.value,
        predicted_ph=predicted_ph,  # Dự đoán cho 10 giây sau
        predicted_timestamp=future_timestamp.isoformat(),  # Timestamp của prediction
        has_early_warning=has_warning,
        warning_message=warning_msg if has_warning else None
    )
    
    recent_readings.append(reading)
    if len(recent_readings) > MAX_RECENT_READINGS:
        recent_readings.pop(0)
    
    monitoring_system.reading_count += 1


def run_monitoring_system():
    """Run monitoring system in background thread."""
    global monitoring_system, is_running, recent_readings, use_simulator, manual_ph_queue
    
    monitoring_system = PHMonitoringSystem(
        reading_interval_seconds=1.0,   # Tăng tần suất để demo và kích hoạt cảnh báo nhanh
        low_threshold=7.0,
        high_threshold=8.5,
        consecutive_count=1,            # Cảnh báo ngay khi vượt ngưỡng
        prediction_horizon_minutes=30,
    )
    
    is_running = True
    
    try:
        if use_simulator:
            # Chế độ tự động: dùng simulator
            print("📊 Chế độ: Tự động (Simulator)")
            for timestamp, ph_value in monitoring_system.simulator.stream_readings(
                interval_seconds=monitoring_system.reading_interval_seconds,
                max_readings=None
            ):
                if not is_running:
                    break
                
                process_ph_reading(timestamp, ph_value)
                time.sleep(monitoring_system.reading_interval_seconds)
        else:
            # Chế độ thủ công: chờ input từ API
            print("✋ Chế độ: Thủ công (Manual Input)")
            print("   Gửi pH qua POST /api/submit-ph")
            while is_running:
                if manual_ph_queue:
                    # Lấy pH từ queue
                    ph_data = manual_ph_queue.pop(0)
                    timestamp = datetime.fromisoformat(ph_data['timestamp']) if ph_data.get('timestamp') else datetime.now()
                    ph_value = ph_data['ph_value']
                    
                    process_ph_reading(timestamp, ph_value)
                
                time.sleep(1)  # Check queue mỗi giây
            
    except Exception as e:
        print(f"Error in monitoring system: {e}")
        import traceback
        traceback.print_exc()
        is_running = False


@app.on_event("startup")
async def startup_event():
    """Start monitoring system on server startup."""
    global system_thread
    system_thread = threading.Thread(target=run_monitoring_system, daemon=True)
    system_thread.start()
    print("✓ Monitoring system started")


@app.on_event("shutdown")
async def shutdown_event():
    """Stop monitoring system on server shutdown."""
    global is_running
    is_running = False
    print("✓ Monitoring system stopped")


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve dashboard HTML."""
    try:
        with open("dashboard/index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return """
        <html>
            <head><title>pH Monitoring System</title></head>
            <body>
                <h1>pH Monitoring System API</h1>
                <p>API is running. Dashboard not found.</p>
                <p>Visit <a href="/docs">/docs</a> for API documentation.</p>
            </body>
        </html>
        """


@app.get("/api/status", response_model=StatusResponse)
async def get_status():
    """Get current system status."""
    if not monitoring_system:
        raise HTTPException(status_code=503, detail="Monitoring system not initialized")
    
    return StatusResponse(
        is_running=is_running,
        total_readings=monitoring_system.reading_count,
        current_status=monitoring_system.alert_engine.get_status().value,
        model_info=monitoring_system.predictor.get_model_info(),
        thresholds={
            "low": monitoring_system.alert_engine.low_threshold,
            "high": monitoring_system.alert_engine.high_threshold
        }
    )


@app.get("/api/current", response_model=ReadingResponse)
async def get_current_reading():
    """Get most recent pH reading."""
    if not recent_readings:
        raise HTTPException(status_code=404, detail="No readings available yet")
    
    return recent_readings[-1]


@app.get("/api/history", response_model=HistoricalDataResponse)
async def get_history(limit: int = 50):
    """Get historical pH readings."""
    if not recent_readings:
        return HistoricalDataResponse(readings=[], count=0)
    
    readings = recent_readings[-limit:] if limit > 0 else recent_readings
    return HistoricalDataResponse(
        readings=readings,
        count=len(readings)
    )


@app.get("/api/prediction")
async def get_prediction():
    """Get current pH prediction."""
    if not monitoring_system:
        raise HTTPException(status_code=503, detail="Monitoring system not initialized")
    
    if not monitoring_system.predictor.is_trained:
        return {
            "predicted_ph": None,
            "is_reliable": False,
            "message": "Model not trained yet"
        }
    
    predicted_ph, is_reliable = monitoring_system.predictor.predict()
    has_warning, warning_msg = monitoring_system.predictor.check_early_warning(
        predicted_ph, 7.0, 8.5
    )
    
    return {
        "predicted_ph": predicted_ph,
        "is_reliable": is_reliable,
        "has_early_warning": has_warning,
        "warning_message": warning_msg,
        "prediction_horizon_minutes": monitoring_system.predictor.prediction_horizon_minutes
    }


@app.get("/api/alerts")
async def get_alerts():
    """Get current alert status."""
    if not monitoring_system:
        raise HTTPException(status_code=503, detail="Monitoring system not initialized")
    
    status = monitoring_system.alert_engine.get_status()
    summary = monitoring_system.alert_engine.get_status_summary()
    
    return {
        "status": status.value,
        "summary": summary,
        "is_alerting": status in [AlertStatus.ALERT_LOW_PH, AlertStatus.ALERT_HIGH_PH]
    }


@app.post("/api/submit-ph")
async def submit_ph(input_data: ManualPHInput):
    """
    Submit pH value manually (for manual input mode).
    
    **Nguồn pH hiện tại:**
    - Mặc định: Tự động từ PHSimulator (simulator/ph_simulator.py)
    - Thủ công: Gửi qua endpoint này
    
    **Cách sử dụng:**
    1. Chuyển sang chế độ thủ công: POST /api/set-mode?mode=manual
    2. Gửi pH: POST /api/submit-ph với {"ph_value": 7.5}
    """
    global manual_ph_queue, use_simulator
    
    if use_simulator:
        return {
            "success": False,
            "message": "Hệ thống đang ở chế độ tự động. Chuyển sang chế độ thủ công trước: POST /api/set-mode?mode=manual"
        }
    
    # Validate pH range
    if not (4.0 <= input_data.ph_value <= 10.0):
        raise HTTPException(
            status_code=400, 
            detail="pH value must be between 4.0 and 10.0"
        )
    
    # Add to queue
    manual_ph_queue.append({
        "ph_value": input_data.ph_value,
        "timestamp": input_data.timestamp or datetime.now().isoformat()
    })
    
    return {
        "success": True,
        "message": f"pH value {input_data.ph_value:.2f} đã được thêm vào queue",
        "ph_value": input_data.ph_value,
        "queue_size": len(manual_ph_queue)
    }


@app.post("/api/set-mode")
async def set_mode(mode: str = "auto"):
    """
    Chuyển đổi giữa chế độ tự động và thủ công.
    
    - mode="auto": Dùng PHSimulator tự động tạo pH
    - mode="manual": Chờ input pH thủ công qua POST /api/submit-ph
    """
    global use_simulator
    
    if mode.lower() == "manual":
        use_simulator = False
        return {
            "success": True,
            "mode": "manual",
            "message": "Đã chuyển sang chế độ thủ công. Gửi pH qua POST /api/submit-ph"
        }
    elif mode.lower() == "auto":
        use_simulator = True
        return {
            "success": True,
            "mode": "auto",
            "message": "Đã chuyển sang chế độ tự động (Simulator)"
        }
    else:
        raise HTTPException(
            status_code=400,
            detail="Mode must be 'auto' or 'manual'"
        )


@app.post("/api/retrain-model")
async def retrain_model():
    """
    Retrain the AI model manually.
    
    Returns:
        Success status and model info
    """
    if not monitoring_system:
        raise HTTPException(status_code=503, detail="Monitoring system not initialized")
    
    if len(monitoring_system.predictor.ph_history) < monitoring_system.predictor.min_samples_for_training:
        return {
            "success": False,
            "message": f"Cần ít nhất {monitoring_system.predictor.min_samples_for_training} readings để train. Hiện có: {len(monitoring_system.predictor.ph_history)}"
        }
    
    success = monitoring_system.predictor.retrain_model()
    
    if success:
        return {
            "success": True,
            "message": "Model đã được retrain thành công",
            "model_info": monitoring_system.predictor.get_model_info()
        }
    else:
        return {
            "success": False,
            "message": "Retrain thất bại"
        }


@app.get("/api/model-metrics")
async def get_model_metrics():
    """
    Get detailed AI model metrics including accuracy and feature importance.
    
    Returns:
        Model metrics and comparison
    """
    if not monitoring_system:
        raise HTTPException(status_code=503, detail="Monitoring system not initialized")
    
    model_info = monitoring_system.predictor.get_model_info()
    
    # Prepare feature importance labels
    feature_labels = []
    if model_info.get('feature_importance'):
        # Create labels for features (history_window values + 5 stats)
        history_window = monitoring_system.predictor.history_window
        feature_labels = [f"pH(t-{i})" for i in range(history_window, 0, -1)]
        feature_labels.extend(["Mean", "Std", "Min", "Max", "Trend"])
    
    return {
        "model_type": model_info.get("model_type", "Unknown"),
        "is_trained": model_info.get("is_trained", False),
        "history_size": model_info.get("history_size", 0),
        "accuracy": model_info.get("accuracy"),
        "feature_importance": {
            "values": model_info.get("feature_importance"),
            "labels": feature_labels[:len(model_info.get("feature_importance", []))]
        } if model_info.get("feature_importance") else None,
        "prediction_horizon": model_info.get("prediction_horizon_minutes", 30)
    }


@app.get("/api/source-info")
async def get_source_info():
    """
    Lấy thông tin về nguồn pH hiện tại.
    
    **Nguồn pH trong hệ thống:**
    1. **Simulator (Mặc định)**: 
       - File: simulator/ph_simulator.py
       - Tự động tạo pH với noise và events (mưa, nắng)
       - Có thể điều chỉnh: base_ph, noise_level, enable_events
       
    2. **Manual Input (Thủ công)**:
       - Gửi qua API: POST /api/submit-ph
       - Cần chuyển mode: POST /api/set-mode?mode=manual
    """
    return {
        "current_mode": "auto" if use_simulator else "manual",
        "ph_source": {
            "simulator": {
                "file": "simulator/ph_simulator.py",
                "description": "Tự động tạo pH với mô phỏng thực tế",
                "parameters": {
                    "base_ph": monitoring_system.simulator.base_ph if monitoring_system else 7.5,
                    "noise_level": monitoring_system.simulator.noise_level if monitoring_system else 0.25,
                    "enable_events": monitoring_system.simulator.enable_events if monitoring_system else True
                }
            },
            "manual": {
                "endpoint": "POST /api/submit-ph",
                "description": "Nhập pH thủ công qua API",
                "example": {
                    "ph_value": 7.5,
                    "timestamp": "2024-01-15T10:30:00"  # Optional
                }
            }
        },
        "how_to_change": {
            "switch_to_manual": "POST /api/set-mode?mode=manual",
            "switch_to_auto": "POST /api/set-mode?mode=auto",
            "submit_ph": "POST /api/submit-ph với body: {\"ph_value\": 7.5}"
        }
    }


@app.get("/api/alert-history")
async def get_alert_history(limit: int = 50, alert_type: Optional[str] = None):
    """
    Lấy lịch sử cảnh báo.
    
    Args:
        limit: Số lượng cảnh báo tối đa (default: 50)
        alert_type: Lọc theo loại ('ALERT_LOW_PH' hoặc 'ALERT_HIGH_PH')
    
    Returns:
        Danh sách cảnh báo và thống kê
    """
    if alert_type:
        alerts = alert_history.get_alerts_by_type(alert_type, limit)
    else:
        alerts = alert_history.get_recent_alerts(limit)
    
    stats = alert_history.get_statistics()
    
    return {
        "alerts": alerts,
        "statistics": stats,
        "count": len(alerts)
    }


@app.get("/api/alert-statistics")
async def get_alert_statistics():
    """
    Lấy thống kê về cảnh báo.
    
    Returns:
        Thống kê tổng hợp về cảnh báo
    """
    return alert_history.get_statistics()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

