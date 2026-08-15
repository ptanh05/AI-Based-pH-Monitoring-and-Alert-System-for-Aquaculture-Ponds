"""
Sensor Data Schema and Validation for AI Aquaculture Guardian.

Provides typed sensor reading models, physical validation,
and sensor quality monitoring.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict
import math


class SensorParameter(str, Enum):
    """Supported sensor parameters."""
    PH = "pH"
    TEMPERATURE = "temperature"
    DISSOLVED_OXYGEN = "dissolved_oxygen"
    TURBIDITY = "turbidity"
    SALINITY = "salinity"
    AMMONIA = "ammonia"


class SensorQuality(str, Enum):
    """Sensor reading quality classification."""
    GOOD = "good"
    SUSPECT = "suspect"
    BAD = "bad"
    MISSING = "missing"
    STALE = "stale"


class DataSource(str, Enum):
    """Origin of the sensor data."""
    SIMULATOR = "simulator"
    REAL_SENSOR = "real_sensor"
    MANUAL_INPUT = "manual_input"
    CSV_IMPORT = "csv_import"


# Physical ranges for sensor parameters (not safety thresholds)
PHYSICAL_RANGES = {
    SensorParameter.PH: (0.0, 14.0),
    SensorParameter.TEMPERATURE: (-5.0, 50.0),
    SensorParameter.DISSOLVED_OXYGEN: (0.0, 25.0),
    SensorParameter.TURBIDITY: (0.0, 4000.0),
    SensorParameter.SALINITY: (0.0, 50.0),
    SensorParameter.AMMONIA: (0.0, 100.0),
}

# Maximum physically realistic change per reading
MAX_JUMP = {
    SensorParameter.PH: 2.0,
    SensorParameter.TEMPERATURE: 5.0,
    SensorParameter.DISSOLVED_OXYGEN: 5.0,
    SensorParameter.TURBIDITY: 500.0,
    SensorParameter.SALINITY: 10.0,
    SensorParameter.AMMONIA: 10.0,
}


@dataclass
class SensorReading:
    """A single sensor measurement with optional multi-sensor context."""
    timestamp: datetime
    sensor_id: str
    pond_id: str
    parameter: str
    value: float
    unit: str
    source: str = "simulator"
    quality: str = "good"
    temperature: Optional[float] = None
    dissolved_oxygen: Optional[float] = None
    turbidity: Optional[float] = None
    salinity: Optional[float] = None

    def to_dict(self) -> dict:
        d = {
            "timestamp": self.timestamp.isoformat(),
            "sensor_id": self.sensor_id,
            "pond_id": self.pond_id,
            "parameter": self.parameter,
            "value": self.value,
            "unit": self.unit,
            "source": self.source,
            "quality": self.quality,
        }
        if self.temperature is not None:
            d["temperature"] = self.temperature
        if self.dissolved_oxygen is not None:
            d["dissolved_oxygen"] = self.dissolved_oxygen
        if self.turbidity is not None:
            d["turbidity"] = self.turbidity
        if self.salinity is not None:
            d["salinity"] = self.salinity
        return d


class ValidationResult:
    """Result of validating a sensor reading."""
    def __init__(self, is_valid: bool, quality: SensorQuality, issues: List[str]):
        self.is_valid = is_valid
        self.quality = quality
        self.issues = issues

    def to_dict(self) -> dict:
        return {
            "is_valid": self.is_valid,
            "quality": self.quality.value,
            "issues": self.issues,
        }


def validate_reading(
    reading: SensorReading,
    previous_reading: Optional[SensorReading] = None,
    stale_threshold_seconds: float = 120.0,
) -> ValidationResult:
    """
    Validate a sensor reading against physical constraints.

    This checks physical plausibility, NOT aquaculture safety thresholds.
    Safety thresholds belong to the risk/alert modules.

    Args:
        reading: The sensor reading to validate.
        previous_reading: The previous reading for jump detection.
        stale_threshold_seconds: Seconds after which a reading is stale.

    Returns:
        ValidationResult with quality assessment and issues list.
    """
    issues: List[str] = []

    # Check for NaN or infinity
    if reading.value is None or math.isnan(reading.value) or math.isinf(reading.value):
        return ValidationResult(False, SensorQuality.BAD, ["Value is NaN or infinity"])

    # Check physical range
    param_key = None
    for p in SensorParameter:
        if p.value == reading.parameter:
            param_key = p
            break

    if param_key and param_key in PHYSICAL_RANGES:
        low, high = PHYSICAL_RANGES[param_key]
        if reading.value < low or reading.value > high:
            return ValidationResult(
                False, SensorQuality.BAD,
                [f"Value {reading.value} outside physical range [{low}, {high}]"]
            )

    # Check for unrealistic jump from previous reading
    if previous_reading is not None and param_key:
        jump = abs(reading.value - previous_reading.value)
        max_allowed = MAX_JUMP.get(param_key, 5.0)
        if jump > max_allowed:
            issues.append(
                f"Unrealistic jump: {jump:.2f} (max {max_allowed:.2f})"
            )

        # Check for stale reading (duplicate timestamp)
        if reading.timestamp == previous_reading.timestamp:
            issues.append("Duplicate timestamp with previous reading")

        # Check for stale data
        time_diff = (reading.timestamp - previous_reading.timestamp).total_seconds()
        if time_diff > stale_threshold_seconds:
            issues.append(
                f"Stale reading: {time_diff:.0f}s since last reading "
                f"(threshold: {stale_threshold_seconds:.0f}s)"
            )

    if issues:
        return ValidationResult(True, SensorQuality.SUSPECT, issues)

    return ValidationResult(True, SensorQuality.GOOD, [])


class SensorQualityMonitor:
    """
    Monitors sensor health over time.

    Tracks stuck sensors, data gaps, and quality trends.
    Distinguishes SENSOR PROBLEMS from WATER QUALITY RISKS.
    """
    def __init__(
        self,
        stuck_threshold: int = 10,
        stuck_tolerance: float = 0.001,
        stale_threshold_seconds: float = 120.0,
    ):
        self.stuck_threshold = stuck_threshold
        self.stuck_tolerance = stuck_tolerance
        self.stale_threshold_seconds = stale_threshold_seconds

        self._recent_values: List[float] = []
        self._last_reading: Optional[SensorReading] = None
        self._total_readings: int = 0
        self._bad_readings: int = 0
        self._suspect_readings: int = 0

    def process(self, reading: SensorReading) -> ValidationResult:
        """Process a reading and return quality assessment."""
        result = validate_reading(
            reading, self._last_reading, self.stale_threshold_seconds
        )

        self._total_readings += 1
        if result.quality == SensorQuality.BAD:
            self._bad_readings += 1
        elif result.quality == SensorQuality.SUSPECT:
            self._suspect_readings += 1

        # Stuck sensor detection
        self._recent_values.append(reading.value)
        if len(self._recent_values) > self.stuck_threshold:
            self._recent_values.pop(0)

        if len(self._recent_values) >= self.stuck_threshold:
            val_range = max(self._recent_values) - min(self._recent_values)
            if val_range < self.stuck_tolerance:
                result.issues.append(
                    f"Sensor may be stuck: {self.stuck_threshold} readings "
                    f"with range {val_range:.4f}"
                )
                if result.quality == SensorQuality.GOOD:
                    result.quality = SensorQuality.SUSPECT

        self._last_reading = reading
        return result

    def get_health_summary(self) -> dict:
        """Get sensor health statistics."""
        total = max(self._total_readings, 1)
        return {
            "total_readings": self._total_readings,
            "bad_readings": self._bad_readings,
            "suspect_readings": self._suspect_readings,
            "good_rate": round((total - self._bad_readings - self._suspect_readings) / total, 4),
            "status": self._overall_status(),
        }

    def _overall_status(self) -> str:
        if self._total_readings == 0:
            return "no_data"
        total = self._total_readings
        bad_rate = self._bad_readings / total
        suspect_rate = self._suspect_readings / total
        if bad_rate > 0.1:
            return "degraded"
        if suspect_rate > 0.2:
            return "suspect"
        return "good"
