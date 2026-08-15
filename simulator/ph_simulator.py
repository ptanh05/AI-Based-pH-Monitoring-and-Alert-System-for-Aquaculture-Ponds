"""
pH Data Simulator for AI Aquaculture Guardian.

Supports both stochastic simulation and deterministic competition
scenarios for reproducible demos.

Scenarios:
- NORMAL: Stable pH around 7.5
- RAPID_PH_RISE: pH climbs toward/above upper threshold
- RAPID_PH_DROP: pH drops toward/below lower threshold
- HEAVY_RAIN: Simulates acidic rain event
- HEAT_EVENT: Algal bloom pH increase
- SENSOR_ANOMALY: Stuck sensor + glitch readings
- RECOVERY: pH returns to normal after a stress event
- COMPETITION_DEMO: Full end-to-end scenario for video recording
"""

import numpy as np
import time
from datetime import datetime
from typing import Generator, Tuple, Optional, List
from enum import Enum


class Scenario(str, Enum):
    NORMAL = "normal"
    RAPID_PH_RISE = "rapid_ph_rise"
    RAPID_PH_DROP = "rapid_ph_drop"
    HEAVY_RAIN = "heavy_rain"
    HEAT_EVENT = "heat_event"
    SENSOR_ANOMALY = "sensor_anomaly"
    RECOVERY = "recovery"
    COMPETITION_DEMO = "competition_demo"


# Pre-defined scenario value sequences (deterministic)
def _build_scenario_values(scenario: Scenario, length: int = 120, seed: int = 42) -> List[float]:
    """Build a deterministic pH sequence for a given scenario."""
    rng = np.random.RandomState(seed)
    noise = lambda scale=0.04: rng.normal(0, scale)

    values = []

    if scenario == Scenario.NORMAL:
        for i in range(length):
            base = 7.5 + 0.15 * np.sin(2 * np.pi * i / 60)
            values.append(round(base + noise(), 2))

    elif scenario == Scenario.RAPID_PH_RISE:
        for i in range(length):
            if i < 30:
                base = 7.5 + noise()
            elif i < 80:
                base = 7.5 + (i - 30) * 0.03 + noise(0.03)
            else:
                base = 9.0 + noise(0.05)
            values.append(round(np.clip(base, 4.0, 10.0), 2))

    elif scenario == Scenario.RAPID_PH_DROP:
        for i in range(length):
            if i < 30:
                base = 7.5 + noise()
            elif i < 80:
                base = 7.5 - (i - 30) * 0.025 + noise(0.03)
            else:
                base = 6.2 + noise(0.05)
            values.append(round(np.clip(base, 4.0, 10.0), 2))

    elif scenario == Scenario.HEAVY_RAIN:
        for i in range(length):
            if i < 25:
                base = 7.6 + noise()
            elif i < 40:
                base = 7.6 - (i - 25) * 0.06 + noise(0.05)
            elif i < 70:
                base = 6.7 + noise(0.06)
            else:
                base = 6.7 + (i - 70) * 0.018 + noise(0.04)
            values.append(round(np.clip(base, 4.0, 10.0), 2))

    elif scenario == Scenario.HEAT_EVENT:
        for i in range(length):
            if i < 25:
                base = 7.8 + noise()
            elif i < 60:
                base = 7.8 + (i - 25) * 0.03 + noise(0.04)
            elif i < 90:
                base = 8.85 + noise(0.05)
            else:
                base = 8.85 - (i - 90) * 0.02 + noise(0.04)
            values.append(round(np.clip(base, 4.0, 10.0), 2))

    elif scenario == Scenario.SENSOR_ANOMALY:
        for i in range(length):
            if i < 20:
                base = 7.5 + noise()
            elif i < 40:
                base = 7.5  # stuck sensor — constant
            elif i < 50:
                # glitch: random jumps
                base = 7.5 + rng.uniform(-2.0, 2.0)
            elif i < 70:
                base = 7.5  # stuck again
            else:
                base = 7.5 + noise()  # recovery
            values.append(round(np.clip(base, 4.0, 10.0), 2))

    elif scenario == Scenario.RECOVERY:
        for i in range(length):
            if i < 20:
                base = 6.3 + noise(0.05)  # start stressed
            elif i < 80:
                base = 6.3 + (i - 20) * 0.02 + noise(0.04)
            else:
                base = 7.5 + noise()
            values.append(round(np.clip(base, 4.0, 10.0), 2))

    elif scenario == Scenario.COMPETITION_DEMO:
        # Full arc: normal → rise → warning → critical → recovery
        phases = [
            (25, lambda i: 7.5 + noise()),                           # normal
            (20, lambda i: 7.5 + i * 0.015 + noise(0.03)),          # gentle rise
            (15, lambda i: 7.8 + i * 0.035 + noise(0.03)),          # faster rise
            (15, lambda i: 8.3 + i * 0.04 + noise(0.04)),           # approaching threshold
            (15, lambda i: 8.9 + noise(0.05)),                      # above threshold
            (15, lambda i: 8.9 - i * 0.025 + noise(0.04)),          # recovery begins
            (15, lambda i: 7.5 + noise()),                           # recovered
        ]
        for phase_len, fn in phases:
            for i in range(phase_len):
                values.append(round(np.clip(fn(i), 4.0, 10.0), 2))

    return values[:length]


class PHSimulator:
    """
    Simulates pH sensor readings for aquaculture ponds.

    Supports both stochastic and deterministic scenario modes.
    """

    def __init__(
        self,
        base_ph: float = 7.5,
        noise_level: float = 0.1,
        trend_factor: float = 0.0,
        enable_events: bool = True,
        scenario: Optional[str] = None,
        seed: Optional[int] = None,
    ):
        self.base_ph = base_ph
        self.noise_level = noise_level
        self.trend_factor = trend_factor
        self.enable_events = enable_events
        self.scenario = scenario
        self.seed = seed

        self.current_ph = base_ph
        self.time_counter = 0
        self.event_counter = 0

        # Event probabilities
        self.rain_event_prob = 0.02
        self.heat_event_prob = 0.015

        # Scenario pre-generated values
        self._scenario_values: Optional[List[float]] = None
        self._scenario_index = 0

        if scenario:
            try:
                sc = Scenario(scenario.lower())
                self._scenario_values = _build_scenario_values(
                    sc, length=200, seed=seed or 42
                )
            except ValueError:
                pass  # Fall back to stochastic

        # Set seed for stochastic mode
        if seed is not None:
            np.random.seed(seed)

    def _calculate_daily_cycle(self, time_hour: float) -> float:
        cycle = 0.2 * np.sin(2 * np.pi * (time_hour - 6) / 24)
        return cycle

    def _simulate_rain_event(self) -> float:
        drop = np.random.uniform(-0.8, -0.3)
        return drop

    def _simulate_heat_event(self) -> float:
        increase = np.random.uniform(0.2, 0.6)
        return increase

    def generate_reading(self) -> Tuple[datetime, float]:
        """Generate a single pH reading."""
        self.time_counter += 1

        # Scenario mode: return pre-generated deterministic values
        if self._scenario_values is not None:
            if self._scenario_index < len(self._scenario_values):
                val = self._scenario_values[self._scenario_index]
                self._scenario_index += 1
                self.current_ph = val
                return datetime.now(), val
            else:
                # Loop scenario
                self._scenario_index = 0
                val = self._scenario_values[0]
                self._scenario_index += 1
                self.current_ph = val
                return datetime.now(), val

        # Stochastic mode (original logic, preserved)
        current_hour = datetime.now().hour + datetime.now().minute / 60.0
        daily_adjustment = self._calculate_daily_cycle(current_hour)
        base_value = self.base_ph + daily_adjustment

        trend_adjustment = self.trend_factor * (self.time_counter / 1000.0)

        event_adjustment = 0.0
        if self.enable_events:
            if np.random.random() < self.rain_event_prob:
                event_adjustment = self._simulate_rain_event()
                self.event_counter += 1
            elif np.random.random() < self.heat_event_prob:
                event_adjustment = self._simulate_heat_event()
                self.event_counter += 1

        if abs(event_adjustment) > 0.01:
            decay_factor = 0.95
            event_adjustment *= (decay_factor ** (self.time_counter - self.event_counter))

        noise = np.random.normal(0, self.noise_level)
        self.current_ph = base_value + trend_adjustment + event_adjustment + noise
        self.current_ph = np.clip(self.current_ph, 4.0, 10.0)

        return datetime.now(), round(self.current_ph, 2)

    def stream_readings(
        self,
        interval_seconds: float = 5.0,
        max_readings: int = None
    ) -> Generator[Tuple[datetime, float], None, None]:
        """Stream pH readings at regular intervals."""
        reading_count = 0

        while True:
            if max_readings and reading_count >= max_readings:
                break

            timestamp, ph_value = self.generate_reading()
            yield timestamp, ph_value

            reading_count += 1
            time.sleep(interval_seconds)

    @staticmethod
    def available_scenarios() -> List[str]:
        return [s.value for s in Scenario]


if __name__ == "__main__":
    print("pH Simulator Demo")
    print("=" * 50)
    print(f"Available scenarios: {PHSimulator.available_scenarios()}")

    simulator = PHSimulator(base_ph=7.5, enable_events=True)

    print("\nGenerating 10 sample readings...\n")
    for i, (timestamp, ph_value) in enumerate(simulator.stream_readings(interval_seconds=0.1, max_readings=10)):
        status = "!" if ph_value < 7.0 or ph_value > 8.5 else "ok"
        print(f"[{i+1:2d}] {timestamp.strftime('%H:%M:%S')} | pH: {ph_value:5.2f} {status}")
