# KỊCH BẢN QUAY VIDEO DEMO DỰ THI
## AI AQUACULTURE GUARDIAN
### Intel® Vietnam AI Impact Festival 2026 — Theme: "Enriching Lives with AI Innovation"

---

## 1. THÔNG TIN CHUNG
- **Thời lượng video khuyến nghị**: 3:00 – 4:30 phút
- **Độ phân giải**: Full HD (1080p, 60fps) hoặc 4K
- **Công cụ ghi hình**: OBS Studio / Loom (màn hình dashboard) + micro thu âm rõ ràng
- **Lệnh chạy chuẩn bị**:
  ```bash
  # Khởi động Web Dashboard với kịch bản Demo hoàn chỉnh
  python run_demo.py --web --scenario competition_demo --seed 42
  ```

---

## 2. TIMELINE CHI TIẾT THEO TỪNG PHÂN CẢNH

### Phân cảnh 1: Mở đầu & Đặt vấn đề (0:00 - 0:45)
- **Màn hình**: Slide tiêu đề + Logo dự án "AI Aquaculture Guardian" hoặc Camera người thuyết trình.
- **Lời thoại (Thuyết minh)**:
  > *"Xin chào Ban giám khảo Intel® Vietnam AI Impact Festival 2026. Tôi là đại diện dự án **AI Aquaculture Guardian** — Hệ thống Cảnh báo Sớm Thông minh vì một ngành Thủy sản Bền vững.*
  > 
  > *Tại Đồng bằng Sông Cửu Long và các vùng nuôi thủy sản Việt Nam, biến động đột ngột độ pH do mưa axit, tảo tàn hay nắng gắt là nguyên nhân hàng đầu gây sốc nước và chết hàng loạt tôm, cá chỉ trong vài giờ. Các hệ thống đo đạc truyền thống chỉ báo động **sau khi** thảm họa đã xảy ra — khi đó người nông dân đã thiệt hại hàng trăm triệu đồng.*
  > 
  > *Hôm nay, chúng tôi mang đến giải pháp ứng dụng AI và công nghệ biên Intel để **dự báo trước rủi ro**, chuyển từ ứng phó bị động sang chủ động phòng ngừa."*

---

### Phân cảnh 2: Giới thiệu Dashboard & Pipeline AI (0:45 - 1:45)
- **Màn hình**: Trình duyệt truy cập `http://localhost:8000`. Dashboard Dark Theme hiện đại hiển thị biểu đồ thời gian thực.
- **Thao tác**: Di chuột chỉ vào các khu vực: Biểu đồ giám sát & dự báo đa bước, Đồng hồ Risk Score (0-100), Bảng giải thích "Why?", và Kiến trúc Edge AI.
- **Lời thoại**:
  > *"Đây là giao diện điều hành của AI Aquaculture Guardian:*
  > 1. *Trung tâm là **Biểu đồ pH Thời gian Thực & Dự báo Đa bước (Multi-step Forecast)**: Đường nét đứt màu xanh ngọc hiển thị dự báo pH trong tương lai từ thuật toán Machine Learning.*
  > 2. *Thước đo **Aquaculture Risk Score (0-100)**: Tổng hợp 4 chỉ số: độ lệch hiện tại, độ lệch dự báo, vận tốc biến thiên và điểm số bất thường (Anomaly Score).*
  > 3. *Khối **AI Explainability ("Tại sao?")**: Cung cấp lý do bằng ngôn ngữ tự nhiên, minh bạch từng yếu tố đóng góp vào rủi ro.*
  > 4. *Khối **Khuyến nghị Hành động (Recommended Actions)**: Đưa ra hướng dẫn an toàn, phù hợp tình huống thực tế cho người nuôi mà không can thiệp liều lượng hóa chất một cách thiếu kiểm soát."*

---

### Phân cảnh 3: Live Demo Kịch bản Biến động & Cảnh báo Sớm (1:45 - 3:00)
- **Màn hình**: Chọn nút kịch bản `Competition Demo` (hoặc `Heavy Rain` / `Heat Event`).
- **Thao tác & Diễn biến**:
  - **Giai đoạn Bình thường (pH ~ 7.5)**: Dashboard hiển thị trạng thái `NORMAL`, màu xanh lá, Risk < 15.
  - **Giai đoạn Xu hướng Tăng/Giảm nhanh**:
    - AI phát hiện tốc độ biến thiên bất thường.
    - Dự báo tương lai vượt ngưỡng an toàn (ví dụ: pH dự báo chạm 8.8).
    - Hệ thống chuyển ngay sang trạng thái **`EARLY_WARNING`** và **`HIGH_RISK`** khi pH thực tế vẫn nằm trong ngưỡng an toàn (ví dụ 8.1)!
    - Âm thanh cảnh báo (Beep) kích hoạt.
    - Panel Explainability giải thích rõ: *"AI dự báo pH sẽ vượt ngưỡng 8.5 trong các bước tiếp theo do tốc độ tăng mạnh."*
  - **Giai đoạn Can thiệp & Hồi phục**: Nước ao ổn định trở lại, Risk Score hạ xuống, hệ thống tự động trả về `NORMAL`.
- **Lời thoại**:
  > *"Điểm đột phá chính là: Hệ thống kích hoạt **Cảnh báo Sớm (Early Warning)** ngay khi giá trị pH hiện tại vẫn ở mức 8.1 an toàn, nhờ mô hình Machine Learning phát hiện xu hướng tăng tốc độ biến thiên và dự báo sắp chạm 8.8. Người nông dân có thêm 15–30 phút vàng để bật quạt nước, che chắn ao hoặc chuẩn bị nước đệm."*

---

### Phân cảnh 4: Tích hợp Công nghệ Intel® & Đạo đức AI (3:00 - 3:45)
- **Màn hình**: Mở terminal chạy `python scripts/benchmark_inference.py` và hiển thị panel **Inference Engine**.
- **Lời thoại**:
  > *"Về mặt kiến trúc công nghệ:*
  > - *Hệ thống được thiết kế hướng tới **Edge AI**, tích hợp chuẩn Intel® OpenVINO™ Toolkit thông qua module `edge/inference_engine.py`.*
  > - *Với khả năng tối ưu hóa pipeline suy luận trên vi xử lý Intel® Core™ và Intel® NPU, hệ thống có thể chạy trực tiếp tại hộp điều khiển tại bờ ao (offline), không phụ thuộc vào kết nối Internet chập chờn tại vùng sâu.*
  > - *Chúng tôi tuân thủ nghiêm ngặt **Đạo đức AI**: Minh bạch nguồn dữ liệu giả lập, không ngụy tạo kết quả, bảo vệ an toàn vật nuôi bằng cách khuyến cáo kiểm tra chéo cảm biến vật lý trước khi can thiệp."*

---

### Phân cảnh 5: Tác động Xã hội & Kết luận (3:45 - 4:15)
- **Màn hình**: Slide tóm tắt tác động & định hướng phát triển (hỗ trợ đa cảm biến DO, nhiệt độ, độ mặn, ammonia).
- **Lời thoại**:
  > *"AI Aquaculture Guardian hiện thực hóa thông điệp 'Enriching Lives with AI Innovation' bằng cách bảo vệ nguồn sinh kế của hàng triệu hộ nông dân Việt Nam, thúc đẩy nuôi trồng thủy sản bền vững và giảm thiểu rủi ro môi trường.*
  > 
  > *Xin chân thành cảm ơn Ban Giám khảo đã lắng nghe!"*

---

## 3. CHECKLIST TRƯỚC KHI BẤM RECORD
- [ ] Chạy `python -m pytest tests/` để đảm bảo 72/72 tests pass.
- [ ] Bật server: `python run_demo.py --web --scenario competition_demo --seed 42`.
- [ ] Mở trình duyệt Chrome/Edge tại `http://localhost:8000`, zoom 100% hoặc 110% cho rõ chữ.
- [ ] Kiểm tra âm thanh micro không bị rè/vang.
- [ ] Kiểm tra loa có phát tiếng beep ngắn khi alert xuất hiện.
