/**
 * i18n (Internationalization) Module for AI Aquaculture Guardian Dashboard
 * Supports: English (en), Vietnamese (vi), Chinese (zh), Japanese (ja)
 */

const I18N = {
    currentLang: localStorage.getItem('aqua-lang') || 'en',

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
            'risk.high': 'HIGH',
            'risk.critical': 'CRITICAL',

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

            // Chart labels
            'chart.actual_ph': 'Actual pH',
            'chart.forecast_ph': 'Forecast pH',
            'chart.upper_threshold': 'Upper Threshold (8.5)',
            'chart.lower_threshold': 'Lower Threshold (7.0)',
            'chart.risk_score': 'Risk Score (0-100)',
            'chart.axis.ph': 'pH',
            'chart.axis.risk': 'Risk',

            // Language selector
            'lang.label': 'Language',
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
            'risk.high': 'CAO',
            'risk.critical': 'NGUY HIỂM',

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

            'lang.label': 'Ngôn ngữ',
        },

        // ═══════════════════════════════════════
        // CHINESE (Simplified)
        // ═══════════════════════════════════════
        zh: {
            'app.title': 'AI 水产养殖卫士',
            'app.subtitle': 'AI驱动的可持续水产养殖预警系统',
            'header.monitoring': '监控中',

            'badge.simulated': '数据来源：模拟数据（合成）',
            'badge.real': '数据来源：真实数据（Mendeley DOI: 10.17632/8s73jfvgr5.2）',
            'badge.live': '数据来源：实时传感器 / 手动输入',

            'source.demo': '🎯 演示模式（模拟器）',
            'source.real': '🌊 真实数据验证（Mendeley）',
            'source.live': '📡 实时传感器',
            'source.provenance.demo': '来源：PHSimulator（确定性竞赛场景）',
            'source.provenance.real': '罗非鱼塘物联网数据流（蒙特里亚，哥伦比亚 — 2024）',
            'source.provenance.live': '等待硬件遥测数据或手动API提交',

            'scenario.normal': '正常',
            'scenario.rapid_rise': '快速上升',
            'scenario.rapid_drop': '快速下降',
            'scenario.heavy_rain': '暴雨',
            'scenario.heat_event': '高温事件',
            'scenario.sensor_anomaly': '传感器异常',
            'scenario.competition_demo': '竞赛演示',

            'stat.pond': '鱼塘',
            'stat.current_ph': '当前 pH',
            'stat.forecast_ph': '预测 pH',
            'stat.risk_score': '风险评分',
            'stat.water_temp': '水温',
            'stat.dissolved_o2': '溶解氧',
            'stat.turbidity': '浊度',
            'stat.sensor_active': 'pH传感器运行中',
            'stat.optimal': '最优范围（7.0 - 8.5）',
            'stat.ai_projection': 'AI多步预测',
            'stat.tropical_range': '热带罗非鱼适宜范围',
            'stat.optical_probe': '光学DO探头',
            'stat.clarity_index': '清澈度指数',

            'risk.low': '低',
            'risk.medium': '中等',
            'risk.high': '高',
            'risk.critical': '危急',

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

            'lang.label': '语言',
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
            'risk.high': '高',
            'risk.critical': '危険',

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

            'lang.label': '言語',
        },
    },

    /**
     * Get translated text for a key.
     * Falls back to English, then to the key itself.
     */
    t(key) {
        return this.translations[this.currentLang]?.[key]
            || this.translations['en']?.[key]
            || key;
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
            updateChartLabels();
        }
    },

    /**
     * Get available languages with display info.
     */
    getLanguages() {
        return [
            { code: 'en', name: 'English', flag: '🇬🇧' },
            { code: 'vi', name: 'Tiếng Việt', flag: '🇻🇳' },
            { code: 'zh', name: '中文', flag: '🇨🇳' },
            { code: 'ja', name: '日本語', flag: '🇯🇵' },
        ];
    },

    /**
     * Initialize: apply translations on DOMContentLoaded.
     */
    init() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.applyAll());
        } else {
            this.applyAll();
        }
    }
};
