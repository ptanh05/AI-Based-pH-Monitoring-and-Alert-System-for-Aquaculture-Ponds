# Hệ thống Giám sát và Cảnh báo pH dựa trên AI cho Ao Nuôi Thủy Sản

Hệ thống phần mềm giám sát và cảnh báo độ pH trong ao nuôi thủy sản sử dụng AI. Tự động mô phỏng dữ liệu pH, dự đoán xu hướng và phát cảnh báo khi pH vượt ngưỡng an toàn.

---

## 📋 Đặc điểm chính

- ✅ **Mô phỏng dữ liệu pH thực tế** với các sự kiện tự nhiên
- ✅ **Cảnh báo thông minh** khi pH vượt ngưỡng liên tiếp
- ✅ **Dự đoán bằng AI** (Random Forest/LSTM) - dự đoán 10 giây trước
- ✅ **Web Dashboard** với biểu đồ real-time
- ✅ **REST API** đầy đủ
- ✅ **Lưu trữ lịch sử** cảnh báo tự động

### Phạm vi pH an toàn
- **An toàn**: 7.0 ≤ pH ≤ 8.5
- **Cảnh báo thấp**: pH < 7.0
- **Cảnh báo cao**: pH > 8.5

---

## 💻 Yêu cầu hệ thống

- Python 3.10+ ([Tải Python](https://www.python.org/downloads/))
- RAM: Tối thiểu 2GB
- Ổ cứng: 500MB trống

---

## 📦 Cài đặt

### Bước 1: Cài đặt thư viện

```bash
pip install -r requirements.txt
```

### Bước 2: Xác nhận cài đặt

```bash
python -c "import fastapi, sklearn, numpy, pandas; print('✓ Cài đặt thành công!')"
```

---

## 🚀 Chạy hệ thống

### Web Dashboard (Khuyến nghị)

```bash
python run_server.py
```

Sau đó mở trình duyệt: **http://localhost:8000**

**Hoặc**:
```bash
uvicorn api.server:app --reload
```

### Command Line

```bash
python main.py
```

### Tùy chỉnh tham số

```bash
# Chạy với 50 lần đọc
python main.py --max-readings 50

# Tùy chỉnh ngưỡng
python main.py --low-threshold 6.8 --high-threshold 8.8

# Xem tất cả tùy chọn
python main.py --help
```

---

## 📁 Cấu trúc dự án

```
ph_monitoring_system/
├── ai/ph_predictor.py          # AI predictor (Random Forest/LSTM)
├── alerts/ph_alert_engine.py   # Engine cảnh báo
├── api/server.py                # REST API server
├── dashboard/index.html         # Web Dashboard
├── simulator/ph_simulator.py    # Simulator dữ liệu
├── storage/alert_history.py     # Lưu trữ lịch sử
├── main.py                      # CLI entry point
└── run_server.py                # Script chạy server
```

### Tổng quan các thư mục chính

| Thư mục     | Nội dung chính | Class/Hàm quan trọng | Ghi chú |
|-------------|----------------|-----------------------|--------|
| `ai`        | Thuật toán AI dự đoán pH | `PHPredictor` (Random Forest/LSTM), `add_reading()`, `predict()`, `train()`, `check_early_warning()` | Dự đoán pH trong tương lai (10 giây), tính accuracy, feature importance |
| `alerts`    | Logic cảnh báo pH vượt ngưỡng | `PHAlertEngine`, `AlertStatus`, `process_reading()` | Quản lý NORMAL/WAITING/ALERT, tránh cảnh báo sai nhờ consecutive readings |
| `api`       | FastAPI server, REST API, vòng lặp monitoring | `process_ph_reading()`, `run_monitoring_system()`, `play_beep()`, các endpoint `/api/*` | Kết nối simulator + AI + alert engine, cung cấp API và Dashboard |
| `dashboard` | Giao diện Web Dashboard | JS functions: `updateStatus()`, `updateCurrentReading()`, `updateChart()`, `updateAlerts()`, `updateModelMetrics()` | Biểu đồ Chart.js, hiển thị pH thực tế/dự đoán, cảnh báo, lịch sử, metrics AI |
| `simulator` | Mô phỏng dữ liệu pH | `PHSimulator`, `generate_reading()`, `stream_readings()` | Tạo dữ liệu pH giống thực tế, có sự kiện mưa/nắng để tạo kịch bản vượt ngưỡng |
| `storage`   | Lưu trữ lịch sử cảnh báo | `AlertHistory`, `add_alert()`, `get_recent_alerts()`, `get_statistics()` | Lưu vào `data/alert_history.json`, không mất khi restart, giới hạn 1000 bản ghi |
| `data`      | Dữ liệu lưu trữ | `alert_history.json` | File JSON chứa lịch sử cảnh báo đã xảy ra |
| `tests`     | Unit tests | `test_simulator.py`, `test_alert_engine.py`, `test_predictor.py` | Kiểm tra tự động từng module chính |

---

## 🔧 Các file chính

### `main.py` - CLI Entry Point
- Chạy hệ thống trong terminal
- Tùy chỉnh tham số: ngưỡng, số lần đọc, interval

### `api/server.py` - REST API Server
- Cung cấp REST API và Web Dashboard
- Xử lý readings, cảnh báo, phát beep

**API Endpoints**:
- `GET /` - Dashboard web
- `GET /api/status` - Trạng thái hệ thống
- `GET /api/current` - Lần đọc pH gần nhất
- `GET /api/history?limit=50` - Lịch sử pH
- `GET /api/prediction` - Dự đoán pH
- `GET /api/alerts` - Trạng thái cảnh báo
- `GET /api/alert-history` - Lịch sử cảnh báo
- `GET /api/model-metrics` - Metrics AI model
- `POST /api/retrain-model` - Retrain model
- `GET /docs` - Swagger API docs

### `simulator/ph_simulator.py` - Simulator
- Mô phỏng dữ liệu pH từ cảm biến
- Tạo các sự kiện: mưa, nắng nóng

### `alerts/ph_alert_engine.py` - Alert Engine
- Xử lý logic cảnh báo khi pH vượt ngưỡng
- Tránh cảnh báo sai bằng cách yêu cầu nhiều lần đọc liên tiếp

### `ai/ph_predictor.py` - AI Predictor
- Dự đoán pH trong tương lai (10 giây sau)
- Hỗ trợ Random Forest (mặc định) và LSTM (tùy chọn)
- Tự động train khi có đủ dữ liệu (15 mẫu)

### `storage/alert_history.py` - Lưu trữ lịch sử
- Lưu lịch sử cảnh báo vào `data/alert_history.json`
- Giữ tối đa 1000 cảnh báo
- Dữ liệu không bị mất khi restart

### `dashboard/index.html` - Web Dashboard
- Biểu đồ pH real-time (Chart.js)
- Hiển thị trạng thái, cảnh báo, metrics AI
- Tự động refresh mỗi 5 giây

---

## 🌐 Web Dashboard

### Tính năng

1. **Status Bar**: Trạng thái, pH hiện tại, pH dự đoán, tổng readings
2. **Biểu đồ pH**: Real-time với zoom/pan, xem lịch sử
3. **AI Metrics**: Loại model, accuracy (MAE, RMSE, R²)
4. **Feature Importance**: Độ quan trọng của features
5. **Cảnh báo**: Hiển thị cảnh báo hiện tại và early warning
6. **Lịch sử cảnh báo**: Danh sách và thống kê

### Cảnh báo âm thanh
Khi pH vượt ngưỡng: phát beep 2 giây, hiển thị cảnh báo, lưu vào lịch sử.

---

## 🔌 Tích hợp phần cứng thật

Thay thế simulator bằng cảm biến thật:

```python
# Trong api/server.py hoặc main.py
# Thay:
from simulator.ph_simulator import PHSimulator
simulator = PHSimulator()

# Bằng:
from hardware.ph_sensor import RealPHSensor
sensor = RealPHSensor(port="/dev/ttyUSB0")
ph_value = sensor.read()
```

---

## 🛠️ Xử lý sự cố

### 1. "ModuleNotFoundError"
**Giải pháp**: `pip install -r requirements.txt`

### 2. "Port 8000 is already in use"
**Giải pháp**: 
- Đóng ứng dụng khác dùng port 8000
- Hoặc: `uvicorn api.server:app --port 8001`

### 3. Dashboard không hiển thị dữ liệu
**Giải pháp**:
- Kiểm tra server: `http://localhost:8000/api/status`
- Mở F12 → Console để xem lỗi JavaScript

### 4. Beep không phát tiếng
**Giải pháp**: Kiểm tra loa/headphone đã bật chưa

---

## 📊 Ví dụ đầu ra

```
======================================================================
  Hệ thống Giám sát và Cảnh báo pH dựa trên AI cho Ao Nuôi Thủy Sản
======================================================================
Start Time: 2026-01-12 16:42:05
Reading Interval: 1.0 seconds
Safe pH Range: 7.0 - 8.5
Prediction Horizon: 10 seconds
======================================================================

[   1] 16:42:06 | pH:  7.52 | Status: ✓ NORMAL
         → Prediction (+10s): 7.50 ~

[   4] 16:42:09 | pH:  6.88 | Status: ⚠️ ALERT_LOW_PH
         → ⚠️ LOW pH ALERT: pH = 6.88 (below safe threshold 7.0)
         → 🔮 EARLY WARNING: Predicted pH may drop below safe range
         → 🔊 Beep alert played (2 seconds)
```

---

## 🧪 Testing

```bash
# Cài đặt pytest
pip install pytest

# Chạy tất cả tests
pytest tests/ -v
```

---

## 📝 Lưu ý

1. **Hệ thống mô phỏng**: Hiện đang mô phỏng dữ liệu. Để dùng cảm biến thật, cần tích hợp module đọc cảm biến.

2. **Lịch sử cảnh báo**: Lưu trong `data/alert_history.json`, không mất khi restart.

3. **AI Model**: Tự động train khi có 31 mẫu, retrain tự động khi có dữ liệu mới.

---

