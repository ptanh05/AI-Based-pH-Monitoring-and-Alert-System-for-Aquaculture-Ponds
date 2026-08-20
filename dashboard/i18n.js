/**
 * i18n (Internationalization) Module for AI Aquaculture Guardian Dashboard
 * Supports: English (en), Vietnamese (vi), Chinese (zh), Japanese (ja)
 */

const I18N = {
    currentLang: localStorage.getItem('aqua-lang') || 'vi',

    translations: {
        // ═══════════════════════════════════════
        // ENGLISH
        // ═══════════════════════════════════════
        en: {
            // Header
            'app.title': 'AI Aquaculture Guardian',
            'app.subtitle': 'AI-Powered Early Warning for Sustainable Aquaculture',
            'header.monitoring': 'MONITORING',

            // Data source badges
            'badge.simulated': 'DATA SOURCE: SIMULATED (Synthetic)',
            'badge.real': 'DATA SOURCE: REAL-WORLD (Mendeley DOI: 10.17632/8s73jfvgr5.2)',
            'badge.live': 'DATA SOURCE: LIVE SENSOR / MANUAL',

            // Source selector
            'source.demo': '🎯 DEMO MODE (Simulator)',
            'source.real': '🌊 REAL DATA VALIDATION (Mendeley)',
            'source.live': '📡 LIVE SENSOR',
            'source.provenance.demo': 'Source: PHSimulator (Deterministic Competition Scenarios)',
            'source.provenance.real': 'Tilapia Pond IoT Stream (Montería, Colombia — 2024)',
            'source.provenance.live': 'Awaiting hardware telemetry or manual API submission',

            // Scenarios
            'scenario.normal': 'Normal',
            'scenario.rapid_rise': 'Rapid Rise',
            'scenario.rapid_drop': 'Rapid Drop',
            'scenario.heavy_rain': 'Heavy Rain',
            'scenario.heat_event': 'Heat Event',
            'scenario.sensor_anomaly': 'Sensor Anomaly',
            'scenario.competition_demo': 'Competition Demo',

            // Stat cards
            'stat.pond': 'Pond',
            'stat.current_ph': 'Current pH',
            'stat.forecast_ph': 'Forecast pH',
            'stat.risk_score': 'Risk Score',
            'stat.water_temp': 'Water Temp',
            'stat.dissolved_o2': 'Dissolved O₂',
            'stat.turbidity': 'Turbidity',
            'stat.sensor_active': 'pH Sensor Active',
            'stat.optimal': 'Optimal (7.0 - 8.5)',
            'stat.ai_projection': 'AI multi-step projection',
            'stat.tropical_range': 'Tropical Tilapia Range',
            'stat.optical_probe': 'Optical DO Probe',
            'stat.clarity_index': 'Clarity Index',

            // Risk levels
            'risk.low': 'LOW',
            'risk.medium': 'MEDIUM',
            'risk.moderate': 'MODERATE',
            'risk.elevated': 'ELEVATED',
            'risk.high': 'HIGH',
            'risk.critical': 'CRITICAL',

            // Alert status
            'status.NORMAL': 'NORMAL',
            'status.WAITING': 'WAITING CONFIRMATION',
            'status.EARLY_WARNING': 'PREDICTIVE EARLY WARNING',
            'status.HIGH_RISK': 'HIGH RISK ALERT',
            'status.CRITICAL': 'CRITICAL EMERGENCY',
            'status.ALERT_LOW_PH': 'CRITICAL LOW pH ALERT',
            'status.ALERT_HIGH_PH': 'CRITICAL HIGH pH ALERT',
            'status.SENSOR_WARNING': 'SENSOR ANOMALY WARNING',

            // Urgency tags
            'urgency.critical': 'CRITICAL',
            'urgency.high': 'HIGH',
            'urgency.medium': 'MEDIUM',
            'urgency.low': 'LOW',
            'urgency.info': 'INFO',

            // Section headings
            'chart.title': '📊 Water Quality Monitoring & Multi-Step AI Forecast',
            'risk.components.title': '🎯 Aquaculture Risk Score Components (0–100)',
            'explain.title': '🔍 Explainable AI ("Why?")',
            'recommend.title': '💡 Decision Support (Actionable Guidance)',
            'ai.status.title': '🤖 AI & Edge Inference Status',

            // Risk components
            'risk.current_ph': 'Current pH (30%)',
            'risk.ai_forecast': 'AI Forecast (30%)',
            'risk.trend': 'Trend / RoC (20%)',
            'risk.anomaly': 'Anomaly (20%)',

            // AI info
            'ai.model': 'Model',
            'ai.inference': 'Inference Engine',
            'ai.trained': 'Trained State',
            'ai.history': 'History Buffer',
            'ai.trained.yes': 'Yes',
            'ai.trained.no': 'No',

            // Chart labels & timeline controls
            'chart.actual_ph': 'Actual pH',
            'chart.forecast_ph': 'Forecast pH',
            'chart.upper_threshold': 'Upper Threshold (8.5)',
            'chart.lower_threshold': 'Lower Threshold (7.0)',
            'chart.risk_score': 'Risk Score (0-100)',
            'chart.axis.ph': 'pH',
            'chart.axis.risk': 'Risk',
            'chart.window': 'View Window:',
            'chart.win_15': '15 pts',
            'chart.win_30': '30 pts (Default)',
            'chart.win_50': '50 pts',
            'chart.win_100': '100 pts',
            'chart.slider_hint': '◀ Drag slider to browse timeline history | Drag rightmost for Live ▶',
            'chart.snap_live': '⚡ Live View',
            'timeline.live': '🔴 LIVE',
            'timeline.history': '⏸ VIEWING HISTORY',

            // Alert Card
            'alert.card_title': '🚨 System Alert & Status',
            'alert.normal_sub': 'System Safe',
            'alert.warning_sub': 'Attention Required',
            'alert.critical_sub': 'Immediate Action Needed',

            // IoT Actuators
            'actuators.title': '⚡ IoT Actuators & Pond Automation',
            'actuators.mode_auto': 'AI Auto',
            'actuators.mode_manual': 'Manual',
            'actuators.power_total': 'Total Load:',
            'actuators.aerator': 'Paddlewheel Aerator (1.5 kW)',
            'actuators.pump': 'Water Exchange Pump (2.2 kW)',
            'actuators.lime': 'Auto Lime Dispenser (0.75 kW)',
            'actuators.running': 'RUNNING',
            'actuators.idle': 'STANDBY',

            // Notifications & Telegram
            'notif.title': '📲 Alert Notification Channels (Telegram / Email)',
            'notif.btn': '📲 Alerts & Telegram',
            'notif.enable': 'Enable Telegram Alert Bot',
            'notif.token_placeholder': 'Telegram Bot Token (e.g. 123456:ABC-DEF...)',
            'notif.chatid_placeholder': 'Chat ID (e.g. 987654321)',
            'notif.save': 'Save Settings',
            'notif.test_btn': '🧪 Send Test Alert',
            'notif.status_ok': 'Telegram Dispatcher Active',

            // Export
            'export.pdf': '📄 Export PDF Report',
            'export.csv': '📊 Export CSV Data',

            // Language & Theme
            'lang.label': 'Language',
            'theme.light': 'Light Mode',
            'theme.dark': 'Dark Mode',
        },

        // ═══════════════════════════════════════
        // VIETNAMESE
        // ═══════════════════════════════════════
        vi: {
            'app.title': 'AI Giám Sát Thủy Sản',
            'app.subtitle': 'Hệ Thống Cảnh Báo Sớm Bằng AI Cho Nuôi Trồng Thủy Sản Bền Vững',
            'header.monitoring': 'ĐANG GIÁM SÁT',

            'badge.simulated': 'NGUỒN DỮ LIỆU: MÔ PHỎNG (Tổng hợp)',
            'badge.real': 'NGUỒN DỮ LIỆU: THỰC TẾ (Mendeley DOI: 10.17632/8s73jfvgr5.2)',
            'badge.live': 'NGUỒN DỮ LIỆU: CẢM BIẾN TRỰC TIẾP / THỦ CÔNG',

            'source.demo': '🎯 CHẾ ĐỘ DEMO (Mô phỏng)',
            'source.real': '🌊 XÁC THỰC DỮ LIỆU THỰC (Mendeley)',
            'source.live': '📡 CẢM BIẾN TRỰC TIẾP',
            'source.provenance.demo': 'Nguồn: PHSimulator (Kịch bản cuộc thi xác định)',
            'source.provenance.real': 'Luồng IoT ao cá rô phi (Montería, Colombia — 2024)',
            'source.provenance.live': 'Đang chờ dữ liệu từ cảm biến hoặc nhập thủ công qua API',

            'scenario.normal': 'Bình thường',
            'scenario.rapid_rise': 'Tăng nhanh',
            'scenario.rapid_drop': 'Giảm nhanh',
            'scenario.heavy_rain': 'Mưa lớn',
            'scenario.heat_event': 'Nắng nóng',
            'scenario.sensor_anomaly': 'Lỗi cảm biến',
            'scenario.competition_demo': 'Demo cuộc thi',

            'stat.pond': 'Ao',
            'stat.current_ph': 'pH Hiện tại',
            'stat.forecast_ph': 'pH Dự đoán',
            'stat.risk_score': 'Điểm Rủi Ro',
            'stat.water_temp': 'Nhiệt Độ Nước',
            'stat.dissolved_o2': 'Oxy Hòa Tan',
            'stat.turbidity': 'Độ Đục',
            'stat.sensor_active': 'Cảm biến pH đang hoạt động',
            'stat.optimal': 'Tối ưu (7.0 - 8.5)',
            'stat.ai_projection': 'Dự đoán đa bước bằng AI',
            'stat.tropical_range': 'Phạm vi cá rô phi nhiệt đới',
            'stat.optical_probe': 'Đầu dò DO quang học',
            'stat.clarity_index': 'Chỉ số độ trong',

            'risk.low': 'THẤP',
            'risk.medium': 'TRUNG BÌNH',
            'risk.moderate': 'VỪA PHẢI',
            'risk.elevated': 'GIA TĂNG',
            'risk.high': 'CAO',
            'risk.critical': 'NGUY HIỂM',

            'status.NORMAL': 'BÌNH THƯỜNG',
            'status.WAITING': 'ĐANG CHỜ XÁC NHẬN',
            'status.EARLY_WARNING': 'CẢNH BÁO SỚM TỪ DỰ ĐOÁN AI',
            'status.HIGH_RISK': 'CẢNH BÁO RỦI RO CAO',
            'status.CRITICAL': 'NGUY CẤP',
            'status.ALERT_LOW_PH': 'CẢNH BÁO pH QUÁ THẤP',
            'status.ALERT_HIGH_PH': 'CẢNH BÁO pH QUÁ CAO',
            'status.SENSOR_WARNING': 'CẢNH BÁO BẤT THƯỜNG CẢM BIẾN',

            'urgency.critical': 'NGUY CẤP',
            'urgency.high': 'CAO',
            'urgency.medium': 'TRUNG BÌNH',
            'urgency.low': 'THẤP',
            'urgency.info': 'THÔNG TIN',

            'chart.title': '📊 Giám Sát Chất Lượng Nước & Dự Đoán AI Đa Bước',
            'risk.components.title': '🎯 Thành Phần Điểm Rủi Ro Thủy Sản (0–100)',
            'explain.title': '🔍 AI Có Thể Giải Thích ("Tại sao?")',
            'recommend.title': '💡 Hỗ Trợ Quyết Định (Hướng Dẫn Hành Động)',
            'ai.status.title': '🤖 Trạng Thái AI & Suy Luận Biên',

            'risk.current_ph': 'pH Hiện tại (30%)',
            'risk.ai_forecast': 'Dự đoán AI (30%)',
            'risk.trend': 'Xu hướng / Tốc độ (20%)',
            'risk.anomaly': 'Bất thường (20%)',

            'ai.model': 'Mô hình',
            'ai.inference': 'Engine Suy luận',
            'ai.trained': 'Trạng thái huấn luyện',
            'ai.history': 'Bộ đệm lịch sử',
            'ai.trained.yes': 'Có',
            'ai.trained.no': 'Không',

            'chart.actual_ph': 'pH Thực tế',
            'chart.forecast_ph': 'pH Dự đoán',
            'chart.upper_threshold': 'Ngưỡng trên (8.5)',
            'chart.lower_threshold': 'Ngưỡng dưới (7.0)',
            'chart.risk_score': 'Điểm rủi ro (0-100)',
            'chart.axis.ph': 'pH',
            'chart.axis.risk': 'Rủi ro',
            'chart.window': 'Khung nhìn:',
            'chart.win_15': '15 điểm',
            'chart.win_30': '30 điểm (Mặc định)',
            'chart.win_50': '50 điểm',
            'chart.win_100': '100 điểm',
            'chart.slider_hint': '◀ Kéo thanh trượt để xem lại toàn bộ lịch sử đo | Kéo hết sang phải để xem trực tiếp ▶',
            'chart.snap_live': '⚡ Về trực tiếp',
            'timeline.live': '🔴 TRỰC TIẾP (LIVE)',
            'timeline.history': '⏸ ĐANG XEM LỊCH SỬ',

            // Alert Card
            'alert.card_title': '🚨 Trạng Thái Cảnh Báo Hệ Thống',
            'alert.normal_sub': 'Hệ thống an toàn',
            'alert.warning_sub': 'Cần chú ý theo dõi',
            'alert.critical_sub': 'Cần can thiệp khẩn cấp',

            // IoT Actuators
            'actuators.title': '⚡ Bảng Điều Khiển Thiết Bị Ao Nuôi',
            'actuators.mode_auto': 'Tự Động (AI)',
            'actuators.mode_manual': 'Thủ Công',
            'actuators.power_total': 'Tổng tải:',
            'actuators.aerator': 'Quạt nước tạo Oxy (1.5 kW)',
            'actuators.pump': 'Máy bơm nước sạch (2.2 kW)',
            'actuators.lime': 'Máy xả vôi trung hòa (0.75 kW)',
            'actuators.running': 'ĐANG CHẠY',
            'actuators.idle': 'ĐANG NGHỈ',

            // Notifications & Telegram
            'notif.title': '📲 Cấu Hình Kênh Báo Động (Telegram / Email)',
            'notif.btn': '📲 Cảnh báo Telegram',
            'notif.enable': 'Bật nhận cảnh báo qua Telegram Bot',
            'notif.token_placeholder': 'Nhập Telegram Bot Token (tùy chọn)',
            'notif.chatid_placeholder': 'Nhập Chat ID người nhận (tùy chọn)',
            'notif.save': 'Lưu Cấu Hình',
            'notif.test_btn': '🧪 Gửi Tin Thử Nghiệm',
            'notif.status_ok': 'Kênh thông báo Telegram đã sẵn sàng',

            // Export
            'export.pdf': '📄 Xuất Báo Cáo PDF',
            'export.csv': '📊 Xuất Dữ Liệu CSV',

            'lang.label': 'Ngôn ngữ',
            'theme.light': 'Giao diện Sáng',
            'theme.dark': 'Giao diện Tối',
        },

        // ═══════════════════════════════════════
        // CHINESE (Simplified)
        // ═══════════════════════════════════════
        zh: {
            'app.title': 'AI 水产养殖卫士',
            'app.subtitle': 'AI驱动的可持续水产养殖预警系统',
            'header.monitoring': '监控中',

            'badge.simulated': '数据源：模拟（合成）',
            'badge.real': '数据源：实测数据（Mendeley DOI: 10.17632/8s73jfvgr5.2）',
            'badge.live': '数据源：实时传感器/手动输入',

            'source.demo': '🎯 演示模式（模拟器）',
            'source.real': '🌊 真实数据验证（Mendeley）',
            'source.live': '📡 实时传感器',
            'source.provenance.demo': '来源：PHSimulator（竞赛确定性场景）',
            'source.provenance.real': '罗非鱼养殖池IoT数据流（哥伦比亚蒙特里亚 — 2024）',
            'source.provenance.live': '等待硬件遥测或手动API输入',

            'scenario.normal': '正常',
            'scenario.rapid_rise': '快速上升',
            'scenario.rapid_drop': '快速下降',
            'scenario.heavy_rain': '暴雨',
            'scenario.heat_event': '高温事件',
            'scenario.sensor_anomaly': '传感器异常',
            'scenario.competition_demo': '竞赛演示',

            'stat.pond': '养殖池',
            'stat.current_ph': '当前 pH',
            'stat.forecast_ph': '预测 pH',
            'stat.risk_score': '风险评分',
            'stat.water_temp': '水温',
            'stat.dissolved_o2': '溶解氧',
            'stat.turbidity': '浊度',
            'stat.sensor_active': 'pH 传感器运行中',
            'stat.optimal': '最佳范围（7.0 - 8.5）',
            'stat.ai_projection': 'AI 多步预测',
            'stat.tropical_range': '热带罗非鱼适宜范围',
            'stat.optical_probe': '光学溶氧探头',
            'stat.clarity_index': '水体透明度指数',

            'risk.low': '低',
            'risk.medium': '中',
            'risk.moderate': '适度',
            'risk.elevated': '上升',
            'risk.high': '高',
            'risk.critical': '危险',

            'status.NORMAL': '正常',
            'status.WAITING': '等待确认',
            'status.EARLY_WARNING': 'AI预测早期预警',
            'status.HIGH_RISK': '高风险警报',
            'status.CRITICAL': '紧急危险',
            'status.ALERT_LOW_PH': 'pH 过低警报',
            'status.ALERT_HIGH_PH': 'pH 过高警报',
            'status.SENSOR_WARNING': '传感器异常警报',

            'urgency.critical': '紧急',
            'urgency.high': '高',
            'urgency.medium': '中等',
            'urgency.low': '低',
            'urgency.info': '信息',

            'chart.title': '📊 水质监测与AI多步预测',
            'risk.components.title': '🎯 水产养殖风险评分组成（0–100）',
            'explain.title': '🔍 可解释AI（"为什么？"）',
            'recommend.title': '💡 决策支持（行动指南）',
            'ai.status.title': '🤖 AI与边缘推理状态',

            'risk.current_ph': '当前pH（30%）',
            'risk.ai_forecast': 'AI预测（30%）',
            'risk.trend': '趋势/变化率（20%）',
            'risk.anomaly': '异常（20%）',

            'ai.model': '模型',
            'ai.inference': '推理引擎',
            'ai.trained': '训练状态',
            'ai.history': '历史缓冲区',
            'ai.trained.yes': '是',
            'ai.trained.no': '否',

            'chart.actual_ph': '实际 pH',
            'chart.forecast_ph': '预测 pH',
            'chart.upper_threshold': '上限阈值（8.5）',
            'chart.lower_threshold': '下限阈值（7.0）',
            'chart.risk_score': '风险评分（0-100）',
            'chart.axis.ph': 'pH',
            'chart.axis.risk': '风险',
            'chart.window': '时间窗口:',
            'chart.win_15': '15点',
            'chart.win_30': '30点（默认）',
            'chart.win_50': '50点',
            'chart.win_100': '100点',
            'chart.slider_hint': '◀ 拖动滑块查看历史记录 | 拖至最右侧返回实时 ▶',
            'chart.snap_live': '⚡ 实时视图',
            'timeline.live': '🔴 实时 (LIVE)',
            'timeline.history': '⏸ 查看历史',

            // Alert Card
            'alert.card_title': '🚨 系统预警与状态',
            'alert.normal_sub': '系统安全正常',
            'alert.warning_sub': '需要密切注意',
            'alert.critical_sub': '需要立即处理',

            // IoT Actuators
            'actuators.title': '⚡ 物联网执行器与池塘自动化',
            'actuators.mode_auto': 'AI 自动',
            'actuators.mode_manual': '手动模式',
            'actuators.power_total': '总功耗:',
            'actuators.aerator': '水车式增氧机 (1.5 kW)',
            'actuators.pump': '循环换水泵 (2.2 kW)',
            'actuators.lime': '自动熟石灰机 (0.75 kW)',
            'actuators.running': '运行中',
            'actuators.idle': '待机中',

            // Notifications & Telegram
            'notif.title': '📲 警报通知渠道 (Telegram / Email)',
            'notif.btn': '📲 Telegram 警报',
            'notif.enable': '启用 Telegram 警报机器人',
            'notif.token_placeholder': '输入 Telegram Bot Token (可选)',
            'notif.chatid_placeholder': '输入 Chat ID (可选)',
            'notif.save': '保存设置',
            'notif.test_btn': '🧪 发送测试警报',
            'notif.status_ok': 'Telegram 通知已就绪',

            // Export
            'export.pdf': '📄 导出 PDF 报告',
            'export.csv': '📊 导出 CSV 数据',

            'lang.label': '语言',
            'theme.light': '浅色模式',
            'theme.dark': '深色模式',
        },

        // ═══════════════════════════════════════
        // JAPANESE
        // ═══════════════════════════════════════
        ja: {
            'app.title': 'AI 養殖ガーディアン',
            'app.subtitle': 'AI駆動の持続可能な養殖業向け早期警報システム',
            'header.monitoring': '監視中',

            'badge.simulated': 'データソース：シミュレーション（合成）',
            'badge.real': 'データソース：実世界（Mendeley DOI: 10.17632/8s73jfvgr5.2）',
            'badge.live': 'データソース：ライブセンサー / 手動入力',

            'source.demo': '🎯 デモモード（シミュレーター）',
            'source.real': '🌊 実データ検証（Mendeley）',
            'source.live': '📡 ライブセンサー',
            'source.provenance.demo': 'ソース：PHSimulator（決定論的コンペシナリオ）',
            'source.provenance.real': 'ティラピア養殖池IoTストリーム（モンテリア、コロンビア — 2024）',
            'source.provenance.live': 'ハードウェアテレメトリまたは手動API送信を待機中',

            'scenario.normal': '通常',
            'scenario.rapid_rise': '急上昇',
            'scenario.rapid_drop': '急低下',
            'scenario.heavy_rain': '豪雨',
            'scenario.heat_event': '高温イベント',
            'scenario.sensor_anomaly': 'センサー異常',
            'scenario.competition_demo': 'コンペデモ',

            'stat.pond': '養殖池',
            'stat.current_ph': '現在の pH',
            'stat.forecast_ph': '予測 pH',
            'stat.risk_score': 'リスクスコア',
            'stat.water_temp': '水温',
            'stat.dissolved_o2': '溶存酸素',
            'stat.turbidity': '濁度',
            'stat.sensor_active': 'pHセンサー稼働中',
            'stat.optimal': '最適範囲（7.0 - 8.5）',
            'stat.ai_projection': 'AIマルチステップ予測',
            'stat.tropical_range': '熱帯ティラピア適正範囲',
            'stat.optical_probe': '光学DOプローブ',
            'stat.clarity_index': '透明度指数',

            'risk.low': '低',
            'risk.medium': '中',
            'risk.moderate': '適度',
            'risk.elevated': '上昇',
            'risk.high': '高',
            'risk.critical': '危険',

            'status.NORMAL': '正常',
            'status.WAITING': '確認待機中',
            'status.EARLY_WARNING': 'AI予測早期警報',
            'status.HIGH_RISK': '高リスク警報',
            'status.CRITICAL': '緊急危険',
            'status.ALERT_LOW_PH': 'pH低下警報',
            'status.ALERT_HIGH_PH': 'pH上昇警報',
            'status.SENSOR_WARNING': 'センサー異常警報',

            'urgency.critical': '緊急',
            'urgency.high': '高',
            'urgency.medium': '中',
            'urgency.low': '低',
            'urgency.info': '情報',

            'chart.title': '📊 水質モニタリング＆AIマルチステップ予測',
            'risk.components.title': '🎯 養殖リスクスコア構成（0–100）',
            'explain.title': '🔍 説明可能なAI（「なぜ？」）',
            'recommend.title': '💡 意思決定支援（アクションガイダンス）',
            'ai.status.title': '🤖 AI＆エッジ推論ステータス',

            'risk.current_ph': '現在のpH（30%）',
            'risk.ai_forecast': 'AI予測（30%）',
            'risk.trend': 'トレンド/変化率（20%）',
            'risk.anomaly': '異常（20%）',

            'ai.model': 'モデル',
            'ai.inference': '推論エンジン',
            'ai.trained': '学習状態',
            'ai.history': '履歴バッファ',
            'ai.trained.yes': 'はい',
            'ai.trained.no': 'いいえ',

            'chart.actual_ph': '実際の pH',
            'chart.forecast_ph': '予測 pH',
            'chart.upper_threshold': '上限しきい値（8.5）',
            'chart.lower_threshold': '下限しきい値（7.0）',
            'chart.risk_score': 'リスクスコア（0-100）',
            'chart.axis.ph': 'pH',
            'chart.axis.risk': 'リスク',
            'chart.window': '表示範囲:',
            'chart.win_15': '15点',
            'chart.win_30': '30点（デフォルト）',
            'chart.win_50': '50点',
            'chart.win_100': '100点',
            'chart.slider_hint': '◀ スライダーを動かして履歴を確認 | 最右端でリアルタイム ▶',
            'chart.snap_live': '⚡ リアルタイムへ',
            'timeline.live': '🔴 リアルタイム (LIVE)',
            'timeline.history': '⏸ 履歴閲覧中',

            // Alert Card
            'alert.card_title': '🚨 システム警報＆ステータス',
            'alert.normal_sub': 'システム正常稼働中',
            'alert.warning_sub': '注意深い監視が必要',
            'alert.critical_sub': '緊急対応が必要',

            // IoT Actuators
            'actuators.title': '⚡ IoTアクチュエータ＆自動化',
            'actuators.mode_auto': 'AI 自動',
            'actuators.mode_manual': '手動モード',
            'actuators.power_total': '合計負荷:',
            'actuators.aerator': '水車式エアレーター (1.5 kW)',
            'actuators.pump': '循環給水ポンプ (2.2 kW)',
            'actuators.lime': '消石灰自動散布機 (0.75 kW)',
            'actuators.running': '稼働中',
            'actuators.idle': '待機中',

            // Notifications & Telegram
            'notif.title': '📲 警報通知チャンネル (Telegram / Email)',
            'notif.btn': '📲 Telegram 警報',
            'notif.enable': 'Telegram 警報ボットを有効化',
            'notif.token_placeholder': 'Telegram Bot Token を入力 (任意)',
            'notif.chatid_placeholder': 'Chat ID を入力 (任意)',
            'notif.save': '設定を保存',
            'notif.test_btn': '🧪 テスト警報送信',
            'notif.status_ok': 'Telegram 通知準備完了',

            // Export
            'export.pdf': '📄 PDF 監査レポート出力',
            'export.csv': '📊 CSV データ出力',

            'lang.label': '言語',
            'theme.light': 'ライトモード',
            'theme.dark': 'ダークモード',
        },
    },

    /**
     * Pattern-based translator for dynamic backend messages
     */
    dynamicPatterns: {
        vi: [
            // Explainability Summaries & Reasons
            { reg: /^Water quality conditions appear normal\./i, replace: 'Chất lượng nước có vẻ bình thường.' },
            { reg: /^No significant issues detected\./i, replace: 'Không phát hiện vấn đề bất thường.' },
            { reg: /^Minor sensor or statistical anomaly detected within nominal pH range\. Inspect sensor\./i, replace: 'Phát hiện bất thường nhỏ về thống kê hoặc cảm biến trong dải pH danh định. Cần kiểm tra cảm biến.' },
            { reg: /^Minor water quality changes detected\. Continue monitoring\./i, replace: 'Phát hiện thay đổi nhỏ về chất lượng nước. Tiếp tục theo dõi.' },
            { reg: /^Elevated water quality risk detected\. Increased attention recommended\./i, replace: 'Phát hiện rủi ro chất lượng nước gia tăng. Khuyến nghị chú ý theo dõi kỹ hơn.' },
            { reg: /^High water quality risk\. AI predicts elevated probability of exceeding the safe pH range\./i, replace: 'Rủi ro chất lượng nước cao. AI dự báo xác suất vượt ngưỡng pH an toàn tăng cao.' },
            // Warning Messages (Summary risk + values)
            { reg: /^Elevated risk\.\s*pH:\s*([\d.]+)\.\s*Risk:\s*([\d.]+)\/100\.\s*(.*)/i, replace: 'Rủi ro gia tăng. pH: $1. Rủi ro: $2/100. $3' },
            { reg: /^High risk\.\s*pH:\s*([\d.]+)\.\s*Risk:\s*([\d.]+)\/100\.\s*(.*)/i, replace: 'Rủi ro cao. pH: $1. Rủi ro: $2/100. $3' },
            { reg: /^Critical risk\.\s*pH:\s*([\d.]+)\.\s*Risk:\s*([\d.]+)\/100\.\s*(.*)/i, replace: 'Rủi ro nguy cấp. pH: $1. Rủi ro: $2/100. $3' },
            { reg: /^Low risk\.\s*pH:\s*([\d.]+)\.\s*Risk:\s*([\d.]+)\/100\.\s*(.*)/i, replace: 'Rủi ro thấp. pH: $1. Rủi ro: $2/100. $3' },
            { reg: /Anomaly detected\./i, replace: 'Phát hiện bất thường.' },
            { reg: /Predicted early warning\./i, replace: 'Cảnh báo sớm từ AI.' },
            { reg: /pH below safe threshold\./i, replace: 'pH thấp hơn ngưỡng an toàn.' },
            { reg: /pH above safe threshold\./i, replace: 'pH cao hơn ngưỡng an toàn.' },
            { reg: /Normal operations\./i, replace: 'Hoạt động bình thường.' },
            { reg: /^All parameters within safe limits\.?/i, replace: 'Tất cả thông số đều nằm trong giới hạn an toàn.' },
            { reg: /^Optimal conditions/i, replace: 'Điều kiện tối ưu' },
            { reg: /^Waiting for data\.\.\./i, replace: 'Đang chờ dữ liệu...' },
            { reg: /^System initializing\.\.\./i, replace: 'Hệ thống đang khởi tạo...' },

            // Thresholds and forecasts
            { reg: /^LOW pH ALERT: pH = ([\d.]+) \(below safe threshold ([\d.]+)\)/i, replace: 'CẢNH BÁO pH THẤP: pH = $1 (thấp hơn ngưỡng an toàn $2)' },
            { reg: /^HIGH pH ALERT: pH = ([\d.]+) \(above safe threshold ([\d.]+)\)/i, replace: 'CẢNH BÁO pH CAO: pH = $1 (cao hơn ngưỡng an toàn $2)' },
            { reg: /^Waiting: pH = ([\d.]+) is low \((\d+)\/(\d+) consecutive readings\)/i, replace: 'Đang chờ xác nhận: pH = $1 đang thấp ($2/$3 lần đo liên tiếp)' },
            { reg: /^Waiting: pH = ([\d.]+) is high \((\d+)\/(\d+) consecutive readings\)/i, replace: 'Đang chờ xác nhận: pH = $1 đang cao ($2/$3 lần đo liên tiếp)' },
            { reg: /^pH returned to safe range: ([\d.]+)/i, replace: 'pH đã trở lại phạm vi an toàn: $1' },
            { reg: /^Normal: pH = ([\d.]+)/i, replace: 'Bình thường: pH = $1' },
            { reg: /^Current pH \(([\d.]+)\) is below the safe threshold \(([\d.]+)\)/i, replace: 'pH hiện tại ($1) thấp hơn ngưỡng an toàn ($2)' },
            { reg: /^Current pH \(([\d.]+)\) is above the safe threshold \(([\d.]+)\)/i, replace: 'pH hiện tại ($1) cao hơn ngưỡng an toàn ($2)' },
            { reg: /^Current pH \(([\d.]+)\) is approaching the upper safety threshold \(([\d.]+)\)/i, replace: 'pH hiện tại ($1) đang tiến gần ngưỡng an toàn trên ($2)' },
            { reg: /^Current pH \(([\d.]+)\) is approaching the lower safety threshold \(([\d.]+)\)/i, replace: 'pH hiện tại ($1) đang tiến gần ngưỡng an toàn dưới ($2)' },
            { reg: /^AI forecasts pH rising to ([\d.]+), which exceeds the upper safe threshold \(([\d.]+)\)/i, replace: 'AI dự báo pH sẽ tăng lên $1, vượt quá ngưỡng trên an toàn ($2)' },
            { reg: /^AI forecasts pH dropping to ([\d.]+), which is below the lower safe threshold \(([\d.]+)\)/i, replace: 'AI dự báo pH sẽ giảm xuống $1, thấp hơn ngưỡng dưới an toàn ($2)' },
            { reg: /^AI forecasts pH approaching the upper threshold \(([\d.]+)\)/i, replace: 'AI dự báo pH đang tiến gần ngưỡng trên ($1)' },
            { reg: /^AI forecasts pH approaching the lower threshold \(([\d.]+)\)/i, replace: 'AI dự báo pH đang tiến gần ngưỡng dưới ($1)' },
            { reg: /^pH is rising rapidly \(rate: ([+-]?[\d.]+) per reading\)/i, replace: 'pH đang tăng nhanh (tốc độ: $1 mỗi chu kỳ đo)' },
            { reg: /^pH is falling rapidly \(rate: ([+-]?[\d.]+) per reading\)/i, replace: 'pH đang giảm nhanh (tốc độ: $1 mỗi chu kỳ đo)' },
            { reg: /^Sustained upward trend detected \(slope: ([+-]?[\d.]+)\)/i, replace: 'Phát hiện xu hướng tăng liên tục (hệ số dốc: $1)' },
            { reg: /^Sustained downward trend detected \(slope: ([+-]?[\d.]+)\)/i, replace: 'Phát hiện xu hướng giảm liên tục (hệ số dốc: $1)' },

            // Anomaly & Sensor
            { reg: /^Statistical anomaly detected \(z-score: ([+-]?[\d.]+)\)/i, replace: 'Phát hiện bất thường thống kê (điểm z-score: $1)' },
            { reg: /^ML anomaly detected by Isolation Forest/i, replace: 'Phát hiện bất thường ML bởi Isolation Forest' },
            { reg: /^Sensor anomaly detected: (.*)/i, replace: 'Phát hiện bất thường từ cảm biến: $1' },
            { reg: /^Anomaly detected: (.*)\. Investigate possible environmental cause\./i, replace: 'Phát hiện bất thường: $1. Cần kiểm tra nguyên nhân môi trường.' },
            { reg: /^Sensor quality is degraded — verify physical sensor before acting on readings\./i, replace: 'Chất lượng cảm biến suy giảm — hãy kiểm tra đầu dò vật lý trước khi xử lý.' },
            { reg: /^Sensor appears stuck \(constant readings\)\. Clean or recalibrate the sensor probe\./i, replace: 'Cảm biến có dấu hiệu bị kẹt (giá trị không đổi). Hãy vệ sinh hoặc hiệu chuẩn lại đầu dò.' },

            // Recommendations / Actions
            { reg: /^Water quality appears normal\. Continue routine monitoring\./i, replace: 'Chất lượng nước đang bình thường. Tiếp tục duy trì theo dõi định kỳ.' },
            { reg: /^Maintain regular monitoring schedule\./i, replace: 'Duy trì lịch theo dõi và giám sát định kỳ.' },
            { reg: /^Note any environmental changes that could affect water quality\./i, replace: 'Ghi nhận các thay đổi môi trường có thể ảnh hưởng đến chất lượng nước.' },
            { reg: /^Continue monitoring water quality closely\./i, replace: 'Tiếp tục theo dõi chặt chẽ chất lượng nước.' },
            { reg: /^Check recent weather conditions and environmental events\./i, replace: 'Kiểm tra diễn biến thời tiết và sự kiện môi trường gần đây.' },
            { reg: /^Verify sensor calibration if readings seem unusual\./i, replace: 'Hiệu chuẩn lại cảm biến nếu các số đo có dấu hiệu bất thường.' },
            { reg: /^Verify sensor readings with a secondary measurement\./i, replace: 'Kiểm tra đối chứng số đo cảm biến bằng thiết bị đo thứ hai.' },
            { reg: /^Inspect pond conditions and check for visible changes \(colour, odour, surface\)\./i, replace: 'Kiểm tra tình trạng ao và quan sát các thay đổi (màu nước, mùi, bọt mặt nước).' },
            { reg: /^Review aeration and water-management procedures\./i, replace: 'Rà soát lại quy trình quạt khí và điều tiết nguồn nước.' },
            { reg: /^AI predicts pH may rise above the safe range\. Prepare contingency measures per farm protocol\./i, replace: 'AI dự báo pH có thể vượt ngưỡng an toàn. Chuẩn bị biện pháp xử lý theo quy trình kỹ thuật trang trại.' },
            { reg: /^AI predicts pH may drop below the safe range\. Check for possible rain or runoff events\./i, replace: 'AI dự báo pH có thể giảm dưới ngưỡng an toàn. Kiểm tra nước mưa chảy tràn hoặc nguồn nước cấp.' },
            { reg: /^Verify sensor measurements immediately with a backup measurement device\./i, replace: 'Kiểm tra đối chứng ngay lập tức bằng thiết bị đo dự phòng.' },
            { reg: /^Notify the responsible operator or farm manager\./i, replace: 'Thông báo ngay cho người quản lý ao hoặc kỹ thuật viên phụ trách.' },
            { reg: /^Follow your farm's established emergency water-management procedure\./i, replace: 'Thực hiện quy trình khẩn cấp theo tiêu chuẩn kỹ thuật của trang trại.' },
            { reg: /^Increase monitoring frequency until conditions stabilise\./i, replace: 'Tăng tần suất đo kiểm tra cho đến khi chất lượng nước ổn định trở lại.' },

            // Disclaimers & Alert Prefixes
            { reg: /^These are suggested actions for decision support only\..*/i, replace: 'Các gợi ý này chỉ mang tính chất hỗ trợ ra quyết định. Không thay thế hướng dẫn chuyên môn thủy sản. Luôn tham khảo ý kiến kỹ thuật viên và tuân thủ quy trình trang trại.' },
            { reg: /^CRITICAL: (.*)/i, replace: 'NGUY CẤP: $1' },
            { reg: /^HIGH RISK: (.*)/i, replace: 'RỦI RO CAO: $1' },
            { reg: /^PREDICTIVE WARNING: (.*)/i, replace: 'CẢNH BÁO DỰ ĐOÁN: $1' },
            { reg: /^LOW pH ALERT: (.*)/i, replace: 'CẢNH BÁO pH THẤP: $1' },
            { reg: /^HIGH pH ALERT: (.*)/i, replace: 'CẢNH BÁO pH CAO: $1' },
            { reg: /^Waiting: (.*)/i, replace: 'Đang chờ: $1' },
        ],
        zh: [
            { reg: /^Water quality conditions appear normal\./i, replace: '水质状况正常。' },
            { reg: /^No significant issues detected\./i, replace: '未发现明显异常。' },
            { reg: /^Water quality appears normal\. Continue routine monitoring\./i, replace: '水质状况正常。继续常规监测。' },
            { reg: /^All parameters within safe limits/i, replace: '所有水质参数均在安全范围内' },
            { reg: /^Optimal conditions/i, replace: '水质状况优良' },
            { reg: /^Waiting for data/i, replace: '正在等待数据...' },
            { reg: /^System initializing/i, replace: '系统初始化中...' },
            { reg: /^Current pH \(([\d.]+)\) is below the safe threshold \(([\d.]+)\)/i, replace: '当前pH ($1) 低于安全阈值 ($2)' },
            { reg: /^Current pH \(([\d.]+)\) is above the safe threshold \(([\d.]+)\)/i, replace: '当前pH ($1) 高于安全阈值 ($2)' },
            { reg: /^AI forecasts pH rising to ([\d.]+), which exceeds the upper safe threshold \(([\d.]+)\)/i, replace: 'AI预测pH将上升至 $1，超过安全上限 ($2)' },
            { reg: /^AI forecasts pH dropping to ([\d.]+), which is below the lower safe threshold \(([\d.]+)\)/i, replace: 'AI预测pH将下降至 $1，低于安全下限 ($2)' },
            { reg: /^These are suggested actions for decision support only\..*/i, replace: '本建议仅供决策参考，不作为专业兽医或水产诊断依据。请遵循养殖场标准操作流程。' },
        ],
        ja: [
            { reg: /^Water quality conditions appear normal\./i, replace: '水質状態は正常です。' },
            { reg: /^No significant issues detected\./i, replace: '重大な問題は検出されていません。' },
            { reg: /^Water quality appears normal\. Continue routine monitoring\./i, replace: '水質は正常です。定期監視を継続してください。' },
            { reg: /^All parameters within safe limits/i, replace: 'すべてのパラメータが安全範囲内です' },
            { reg: /^Optimal conditions/i, replace: '水質状態は最適です' },
            { reg: /^Waiting for data/i, replace: 'データ待機中...' },
            { reg: /^System initializing/i, replace: 'システム初期化中...' },
            { reg: /^Current pH \(([\d.]+)\) is below the safe threshold \(([\d.]+)\)/i, replace: '現在のpH ($1) が安全下限 ($2) を下回っています' },
            { reg: /^Current pH \(([\d.]+)\) is above the safe threshold \(([\d.]+)\)/i, replace: '現在のpH ($1) が安全上限 ($2) を上回っています' },
            { reg: /^AI forecasts pH rising to ([\d.]+), which exceeds the upper safe threshold \(([\d.]+)\)/i, replace: 'AI予測：pHが $1 に上昇し、安全上限 ($2) を超える見込みです' },
            { reg: /^AI forecasts pH dropping to ([\d.]+), which is below the lower safe threshold \(([\d.]+)\)/i, replace: 'AI予測：pHが $1 に低下し、安全下限 ($2) を下回る見込みです' },
            { reg: /^These are suggested actions for decision support only\..*/i, replace: '本提案は意思決定支援のみを目的としています。農場の標準手順に従ってください。' },
        ]
    },

    /**
     * Translate dynamic text from backend if available
     */
    translateDynamic(text) {
        if (!text) return '';
        if (this.currentLang === 'en') return text;
        const patterns = this.dynamicPatterns[this.currentLang] || [];
        for (const p of patterns) {
            if (p.reg.test(text)) {
                return text.replace(p.reg, p.replace);
            }
        }
        return text;
    },

    /**
     * Get translated text for a key.
     * Robust lookup: direct match, uppercase, lowercase, with/without status. prefix.
     */
    t(key) {
        if (!key) return '';
        const lang = this.translations[this.currentLang] ? this.currentLang : 'en';
        const trans = this.translations[lang] || {};
        const enTrans = this.translations['en'] || {};

        if (trans[key] !== undefined) return trans[key];
        if (enTrans[key] !== undefined) return enTrans[key];

        const cleanKey = String(key).replace(/^status\./i, '');
        const withPrefix = 'status.' + cleanKey;

        if (trans[withPrefix] !== undefined) return trans[withPrefix];
        if (enTrans[withPrefix] !== undefined) return enTrans[withPrefix];

        const upperPrefix = 'status.' + cleanKey.toUpperCase();
        if (trans[upperPrefix] !== undefined) return trans[upperPrefix];
        if (enTrans[upperPrefix] !== undefined) return enTrans[upperPrefix];

        const lowerPrefix = 'status.' + cleanKey.toLowerCase();
        if (trans[lowerPrefix] !== undefined) return trans[lowerPrefix];
        if (enTrans[lowerPrefix] !== undefined) return enTrans[lowerPrefix];

        if (trans[cleanKey] !== undefined) return trans[cleanKey];
        if (enTrans[cleanKey] !== undefined) return enTrans[cleanKey];

        const dyn = this.translateDynamic(key);
        if (dyn !== key) return dyn;

        return key;
    },

    /**
     * Set the active language and re-render all i18n elements.
     */
    setLang(lang) {
        if (!this.translations[lang]) return;
        this.currentLang = lang;
        localStorage.setItem('aqua-lang', lang);
        this.applyAll();

        // Update HTML lang attribute
        document.documentElement.lang = lang === 'zh' ? 'zh-CN' : lang;

        // Update language switcher active state
        document.querySelectorAll('.lang-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.lang === lang);
        });

        // Update theme tooltip translation if theme button exists
        const themeTooltip = document.getElementById('theme-tooltip');
        const theme = localStorage.getItem('aqua-theme') || 'dark';
        if (themeTooltip) {
            const key = theme === 'light' ? 'theme.dark' : 'theme.light';
            themeTooltip.textContent = this.t(key);
        }

        // Trigger dashboard update if exists to re-render dynamic strings
        if (typeof update === 'function') {
            update();
        }

        // Dispatch event so other scripts can react
        window.dispatchEvent(new CustomEvent('langchange', { detail: { lang } }));
    },

    /**
     * Apply translations to all elements with data-i18n attribute.
     */
    applyAll() {
        document.querySelectorAll('[data-i18n]').forEach(el => {
            const key = el.dataset.i18n;
            const translated = this.t(key);
            if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
                el.placeholder = translated;
            } else {
                el.textContent = translated;
            }
        });

        // Update chart labels if chart exists
        if (typeof updateChartLabels === 'function') {
            try {
                updateChartLabels();
            } catch (e) {
                // Chart might not be initialized yet
            }
        }
    },

    /**
     * Get available languages with display info.
     */
    getLanguages() {
        return [
            { code: 'en', name: 'English', flag: 'EN' },
            { code: 'vi', name: 'Tiếng Việt', flag: 'VI' },
            { code: 'zh', name: '中文', flag: '中' },
            { code: 'ja', name: '日本語', flag: '日' },
        ];
    },

    /**
     * Initialize: apply translations on DOMContentLoaded.
     */
    init() {
        this.applyAll();
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.applyAll());
        }
    }
};

if (typeof window !== 'undefined') {
    window.I18N = I18N;
}
