"""
Comprehensive test suite for AI Aquaculture Guardian.

Tests all new AI pipeline modules: features, forecasting, anomaly,
risk, explainability, recommendations, sensor schema, scenarios,
and edge inference engine.
"""

import pytest
import numpy as np
import math
from datetime import datetime, timedelta

# ── Sensor Schema Tests ──
from ai.sensor_schema import (
    SensorReading, validate_reading, SensorQualityMonitor,
    SensorQuality, SensorParameter,
)


class TestSensorSchema:
    def test_valid_ph_reading(self):
        r = SensorReading(
            timestamp=datetime.now(), sensor_id="S1", pond_id="P1",
            parameter="pH", value=7.5, unit="pH",
        )
        result = validate_reading(r)
        assert result.is_valid
        assert result.quality == SensorQuality.GOOD

    def test_nan_value(self):
        r = SensorReading(
            timestamp=datetime.now(), sensor_id="S1", pond_id="P1",
            parameter="pH", value=float("nan"), unit="pH",
        )
        result = validate_reading(r)
        assert not result.is_valid
        assert result.quality == SensorQuality.BAD

    def test_infinity_value(self):
        r = SensorReading(
            timestamp=datetime.now(), sensor_id="S1", pond_id="P1",
            parameter="pH", value=float("inf"), unit="pH",
        )
        result = validate_reading(r)
        assert not result.is_valid

    def test_negative_ph(self):
        r = SensorReading(
            timestamp=datetime.now(), sensor_id="S1", pond_id="P1",
            parameter="pH", value=-1.0, unit="pH",
        )
        result = validate_reading(r)
        assert not result.is_valid
        assert "outside physical range" in result.issues[0]

    def test_ph_above_14(self):
        r = SensorReading(
            timestamp=datetime.now(), sensor_id="S1", pond_id="P1",
            parameter="pH", value=15.0, unit="pH",
        )
        result = validate_reading(r)
        assert not result.is_valid

    def test_ph_at_boundaries(self):
        for val in [0.0, 14.0, 7.0]:
            r = SensorReading(
                timestamp=datetime.now(), sensor_id="S1", pond_id="P1",
                parameter="pH", value=val, unit="pH",
            )
            result = validate_reading(r)
            assert result.is_valid

    def test_unrealistic_jump(self):
        r1 = SensorReading(
            timestamp=datetime.now(), sensor_id="S1", pond_id="P1",
            parameter="pH", value=7.0, unit="pH",
        )
        r2 = SensorReading(
            timestamp=datetime.now(), sensor_id="S1", pond_id="P1",
            parameter="pH", value=11.0, unit="pH",
        )
        result = validate_reading(r2, r1)
        assert result.quality == SensorQuality.SUSPECT
        assert any("jump" in i.lower() for i in result.issues)

    def test_sensor_quality_monitor_stuck(self):
        monitor = SensorQualityMonitor(stuck_threshold=5, stuck_tolerance=0.001)
        for _ in range(10):
            r = SensorReading(
                timestamp=datetime.now(), sensor_id="S1", pond_id="P1",
                parameter="pH", value=7.500, unit="pH",
            )
            result = monitor.process(r)
        assert any("stuck" in i.lower() for i in result.issues)

    def test_to_dict(self):
        r = SensorReading(
            timestamp=datetime(2026, 1, 1, 12, 0),
            sensor_id="S1", pond_id="P1",
            parameter="pH", value=7.5, unit="pH",
        )
        d = r.to_dict()
        assert d["value"] == 7.5
        assert d["parameter"] == "pH"


# ── Feature Engineering Tests ──
from ai.features import FeatureEngineer


class TestFeatureEngineering:
    def test_feature_count(self):
        fe = FeatureEngineer(window_size=10)
        values = [7.5 + 0.01 * i for i in range(20)]
        features = fe.extract(values)
        assert len(features) == len(FeatureEngineer.FEATURE_NAMES)

    def test_with_short_history(self):
        fe = FeatureEngineer(window_size=10)
        features = fe.extract([7.5, 7.6])
        assert len(features) == len(FeatureEngineer.FEATURE_NAMES)
        assert features[0] == pytest.approx(7.6, abs=0.01)

    def test_single_value(self):
        fe = FeatureEngineer()
        features = fe.extract([7.5])
        assert features[0] == pytest.approx(7.5, abs=0.01)

    def test_empty_values(self):
        fe = FeatureEngineer()
        features = fe.extract([])
        assert all(f == 0.0 for f in features)

    def test_constant_values(self):
        fe = FeatureEngineer(window_size=10)
        features = fe.extract([7.5] * 20)
        assert features[5] == pytest.approx(0.0, abs=0.001)  # trend = 0

    def test_time_of_day(self):
        fe = FeatureEngineer()
        features = fe.extract([7.5] * 5, hour_of_day=12.0)
        assert features[9] != 0.0  # hour_sin
        assert features[10] != 0.0  # hour_cos

    def test_batch_extraction(self):
        fe = FeatureEngineer(window_size=5)
        values = [7.5 + 0.01 * i for i in range(30)]
        X, y = fe.extract_batch(values, target_offset=1)
        assert len(X) == len(y)
        assert X.shape[1] == len(FeatureEngineer.FEATURE_NAMES)

    def test_batch_insufficient_data(self):
        fe = FeatureEngineer(window_size=20)
        X, y = fe.extract_batch([7.5, 7.6], target_offset=1)
        assert len(X) == 0


# ── Forecasting Tests ──
from ai.forecasting import ForecastingEngine, PersistenceBaseline


class TestForecasting:
    def test_persistence_baseline(self):
        b = PersistenceBaseline()
        preds = b.predict(7.5, n_steps=5)
        assert all(p == 7.5 for p in preds)
        assert len(preds) == 5

    def test_engine_no_data(self):
        engine = ForecastingEngine()
        pred, trained = engine.predict_single()
        assert pred == 7.5
        assert not trained

    def test_engine_training(self):
        engine = ForecastingEngine(window_size=10, min_train_samples=25)
        rng = np.random.RandomState(42)
        for i in range(50):
            engine.add_reading(7.5 + rng.normal(0, 0.1))
        assert engine.is_trained

    def test_multistep_forecast(self):
        engine = ForecastingEngine(window_size=10, min_train_samples=25)
        rng = np.random.RandomState(42)
        for i in range(60):
            engine.add_reading(7.5 + rng.normal(0, 0.1))
        result = engine.predict_multistep(n_steps=5)
        assert len(result["model_predictions"]) == 5
        assert len(result["baseline_predictions"]) == 5
        assert result["is_model_trained"]

    def test_multistep_30_steps(self):
        engine = ForecastingEngine(window_size=10, min_train_samples=25)
        rng = np.random.RandomState(42)
        for i in range(60):
            engine.add_reading(7.5 + rng.normal(0, 0.1))
        result = engine.predict_multistep(n_steps=30)
        assert len(result["model_predictions"]) == 30

    def test_evaluation(self):
        engine = ForecastingEngine(window_size=10, min_train_samples=25)
        rng = np.random.RandomState(42)
        for i in range(100):
            engine.add_reading(7.5 + rng.normal(0, 0.1))
        results = engine.evaluate([1, 5])
        assert "1_step" in results
        assert "model" in results["1_step"]
        assert "mae" in results["1_step"]["model"]

    def test_model_info(self):
        engine = ForecastingEngine()
        info = engine.get_model_info()
        assert "is_trained" in info
        assert "model_type" in info


# ── Anomaly Detection Tests ──
from ai.anomaly import AnomalyDetector


class TestAnomalyDetection:
    def test_no_anomaly_normal_data(self):
        det = AnomalyDetector(z_score_window=10)
        for v in [7.5 + 0.01 * i for i in range(20)]:
            det.add_reading(v)
        result = det.detect(7.55)
        assert isinstance(result["is_anomaly"], bool)
        assert 0.0 <= result["anomaly_score"] <= 1.0

    def test_spike_detection(self):
        det = AnomalyDetector(z_score_window=20, z_score_threshold=2.0)
        for _ in range(30):
            det.add_reading(7.5)
        result = det.detect(10.0)
        assert result["is_anomaly"]
        assert result["anomaly_score"] > 0.0
        assert abs(result["z_score"]) > 2.0

    def test_stuck_sensor(self):
        det = AnomalyDetector()
        for _ in range(40):
            det.add_reading(7.5)
        result = det.detect(7.5)
        assert result["stuck_sensor"]

    def test_empty_history(self):
        det = AnomalyDetector()
        result = det.detect()
        assert not result["is_anomaly"]


# ── Risk Scoring Tests ──
from ai.risk import AquacultureRiskEngine, RiskLevel, classify_risk


class TestRiskScoring:
    def test_safe_ph_low_risk(self):
        engine = AquacultureRiskEngine()
        result = engine.compute(current_ph=7.5)
        assert result["total"] < 30
        assert result["level"] in ("LOW", "MODERATE")

    def test_high_ph_high_risk(self):
        engine = AquacultureRiskEngine()
        result = engine.compute(current_ph=9.5, predicted_ph=10.0)
        assert result["total"] > 50

    def test_low_ph_high_risk(self):
        engine = AquacultureRiskEngine()
        result = engine.compute(current_ph=5.5)
        assert result["total"] > 40

    def test_components_present(self):
        engine = AquacultureRiskEngine()
        result = engine.compute(current_ph=7.5, predicted_ph=8.0, anomaly_score=0.5)
        assert "components" in result
        assert "current_value" in result["components"]
        assert "forecast" in result["components"]
        assert "trend" in result["components"]
        assert "anomaly" in result["components"]

    def test_risk_classification(self):
        assert classify_risk(10) == RiskLevel.LOW
        assert classify_risk(30) == RiskLevel.MODERATE
        assert classify_risk(50) == RiskLevel.ELEVATED
        assert classify_risk(70) == RiskLevel.HIGH
        assert classify_risk(90) == RiskLevel.CRITICAL

    def test_risk_clamped_0_100(self):
        engine = AquacultureRiskEngine()
        result = engine.compute(current_ph=7.5)
        assert 0 <= result["total"] <= 100
        result2 = engine.compute(current_ph=14.0, predicted_ph=14.0, anomaly_score=1.0, rate_of_change=1.0)
        assert 0 <= result2["total"] <= 100


# ── Explainability Tests ──
from ai.explainability import ExplainabilityEngine


class TestExplainability:
    def test_low_risk_explanation(self):
        engine = ExplainabilityEngine()
        risk = {"total": 10, "level": "LOW", "components": {"current_value": 5, "forecast": 3, "trend": 1, "anomaly": 1}}
        anomaly = {"is_anomaly": False, "reasons": []}
        result = engine.explain(7.5, 7.5, risk, anomaly)
        assert "summary" in result
        assert "reasons" in result
        assert "confidence_note" in result

    def test_high_risk_explanation(self):
        engine = ExplainabilityEngine()
        risk = {"total": 85, "level": "CRITICAL", "components": {"current_value": 30, "forecast": 30, "trend": 15, "anomaly": 10}}
        anomaly = {"is_anomaly": True, "reasons": ["Rapid change detected"]}
        result = engine.explain(8.8, 9.2, risk, anomaly)
        assert len(result["reasons"]) > 0
        assert "risk_drivers" in result


# ── Recommendation Tests ──
from ai.recommendations import RecommendationEngine


class TestRecommendations:
    def test_low_risk_recommendations(self):
        engine = RecommendationEngine()
        result = engine.generate("LOW", 10, 7.5, 7.5)
        assert len(result["actions"]) > 0
        assert "disclaimer" in result

    def test_critical_risk_recommendations(self):
        engine = RecommendationEngine()
        result = engine.generate("CRITICAL", 90, 9.5, 10.0)
        assert len(result["actions"]) >= 3
        assert any("verify" in a["text"].lower() for a in result["actions"])
        assert any("emergency" in a["text"].lower() or "notify" in a["text"].lower()
                    for a in result["actions"])

    def test_sensor_quality_warning(self):
        engine = RecommendationEngine()
        result = engine.generate("LOW", 10, 7.5, 7.5, sensor_quality="bad")
        assert any("sensor" in a["text"].lower() for a in result["actions"])


# ── Alert Engine Tests (extended) ──
from alerts.ph_alert_engine import PHAlertEngine, AlertStatus


class TestAlertEngineExtended:
    def test_process_full_early_warning(self):
        engine = PHAlertEngine(consecutive_count=3)
        ts = datetime.now()
        status, msg = engine.process_full(
            ts, 8.3, predicted_ph=8.8,
            risk_total=60, risk_level="HIGH",
        )
        assert status in (AlertStatus.EARLY_WARNING, AlertStatus.HIGH_RISK)

    def test_process_full_critical(self):
        engine = PHAlertEngine(consecutive_count=1)
        ts = datetime.now()
        status, msg = engine.process_full(
            ts, 9.0, predicted_ph=9.5,
            risk_total=95, risk_level="CRITICAL",
        )
        assert status == AlertStatus.CRITICAL

    def test_sensor_warning(self):
        engine = PHAlertEngine(consecutive_count=3)
        ts = datetime.now()
        status, msg = engine.process_full(
            ts, 7.5, sensor_quality="bad",
        )
        assert status == AlertStatus.SENSOR_WARNING

    def test_predicted_vs_actual_distinction(self):
        """System must NOT say pH has exceeded when it's only predicted."""
        engine = PHAlertEngine(consecutive_count=3)
        ts = datetime.now()
        status, msg = engine.process_full(
            ts, 8.3, predicted_ph=8.8,
            risk_total=50, risk_level="ELEVATED",
        )
        assert "has breached" not in msg.lower() or status in (AlertStatus.ALERT_HIGH_PH,)
        # pH 8.3 is within range, so shouldn't say it breached
        assert status != AlertStatus.ALERT_HIGH_PH


# ── Simulator Scenario Tests ──
from simulator.ph_simulator import PHSimulator, Scenario


class TestSimulatorScenarios:
    def test_available_scenarios(self):
        scenarios = PHSimulator.available_scenarios()
        assert "normal" in scenarios
        assert "competition_demo" in scenarios
        assert "rapid_ph_rise" in scenarios

    def test_deterministic_scenario(self):
        s1 = PHSimulator(scenario="normal", seed=42)
        s2 = PHSimulator(scenario="normal", seed=42)
        v1 = [s1.generate_reading()[1] for _ in range(10)]
        v2 = [s2.generate_reading()[1] for _ in range(10)]
        assert v1 == v2  # Must be deterministic with same seed

    def test_rapid_rise_reaches_high(self):
        sim = PHSimulator(scenario="rapid_ph_rise", seed=42)
        values = [sim.generate_reading()[1] for _ in range(100)]
        assert max(values) > 8.5  # Should exceed upper threshold

    def test_competition_demo_has_variation(self):
        sim = PHSimulator(scenario="competition_demo", seed=42)
        values = [sim.generate_reading()[1] for _ in range(100)]
        assert max(values) - min(values) > 0.5  # Should have meaningful variation

    def test_sensor_anomaly_has_stuck(self):
        sim = PHSimulator(scenario="sensor_anomaly", seed=42)
        values = [sim.generate_reading()[1] for _ in range(50)]
        # Should have some constant segments
        diffs = [abs(values[i] - values[i-1]) for i in range(1, len(values))]
        zero_diffs = sum(1 for d in diffs if d < 0.001)
        assert zero_diffs > 5  # At least some stuck readings


# ── Edge Inference Engine Tests ──
from edge.inference_engine import (
    SklearnInferenceEngine, create_inference_engine,
    OPENVINO_AVAILABLE, SKL2ONNX_AVAILABLE,
)
from sklearn.ensemble import RandomForestRegressor


class TestEdgeInference:
    def _train_simple_model(self):
        rng = np.random.RandomState(42)
        X = rng.rand(50, 11)
        y = rng.rand(50)
        model = RandomForestRegressor(n_estimators=10, random_state=42)
        model.fit(X, y)
        return model

    def test_sklearn_engine(self):
        model = self._train_simple_model()
        engine = SklearnInferenceEngine()
        assert engine.load_model(model, 11)
        X = np.random.rand(1, 11)
        pred = engine.predict(X)
        assert len(pred) == 1

    def test_sklearn_benchmark(self):
        model = self._train_simple_model()
        engine = SklearnInferenceEngine()
        engine.load_model(model, 11)
        X = np.random.rand(1, 11)
        result = engine.benchmark(X, n_iterations=10)
        assert "p50_ms" in result
        assert "throughput_per_sec" in result

    def test_factory_function(self):
        engine = create_inference_engine(prefer_openvino=False)
        assert isinstance(engine, SklearnInferenceEngine)

    @pytest.mark.skipif(
        not (OPENVINO_AVAILABLE and SKL2ONNX_AVAILABLE),
        reason="OpenVINO or skl2onnx not available"
    )
    def test_openvino_engine(self):
        from edge.inference_engine import OpenVINOInferenceEngine
        model = self._train_simple_model()
        engine = OpenVINOInferenceEngine(device="CPU")
        success = engine.load_model(model, 11)
        if success:
            X = np.random.rand(1, 11).astype(np.float32)
            pred = engine.predict(X)
            assert len(pred) == 1
            info = engine.get_info()
            assert info["backend"] == "openvino"


# ── Edge Cases ──
class TestEdgeCases:
    def test_ph_zero(self):
        r = SensorReading(
            timestamp=datetime.now(), sensor_id="S1", pond_id="P1",
            parameter="pH", value=0.0, unit="pH",
        )
        result = validate_reading(r)
        assert result.is_valid  # 0 is physically valid

    def test_ph_14(self):
        r = SensorReading(
            timestamp=datetime.now(), sensor_id="S1", pond_id="P1",
            parameter="pH", value=14.0, unit="pH",
        )
        result = validate_reading(r)
        assert result.is_valid

    def test_forecast_with_constant_values(self):
        engine = ForecastingEngine(window_size=5, min_train_samples=15)
        for _ in range(30):
            engine.add_reading(7.5)
        pred, trained = engine.predict_single()
        assert isinstance(pred, float)

    def test_risk_with_extreme_values(self):
        engine = AquacultureRiskEngine()
        r = engine.compute(current_ph=0.0, predicted_ph=14.0, rate_of_change=5.0, anomaly_score=1.0)
        assert 0 <= r["total"] <= 100

    def test_anomaly_sudden_spike(self):
        det = AnomalyDetector(z_score_window=20, z_score_threshold=2.0)
        for _ in range(25):
            det.add_reading(7.5)
        det.add_reading(12.0)
        result = det.detect(12.0)
        assert result["is_anomaly"]
