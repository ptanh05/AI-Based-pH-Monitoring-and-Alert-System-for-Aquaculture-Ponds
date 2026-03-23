"""
pH Data Simulator for Aquaculture Monitoring System

This module simulates realistic pH sensor data for aquaculture ponds.
It mimics real-world conditions including:
- Normal fluctuations
- Sudden drops (rain events)
- Gradual increases (hot weather)
- Daily cycles
"""

import numpy as np
import time
from datetime import datetime
from typing import Generator, Tuple


class PHSimulator:
    """
    Simulates pH sensor readings for aquaculture ponds.
    
    Generates realistic time-series data that mimics:
    - Normal pH fluctuations around 7.5-8.0
    - Sudden drops during rain events
    - Gradual increases during hot weather
    - Daily circadian rhythms
    """
    
    def __init__(
        self,
        base_ph: float = 7.5,
        noise_level: float = 0.1,
        trend_factor: float = 0.0,
        enable_events: bool = True
    ):
        """
        Initialize the pH simulator.
        
        Args:
            base_ph: Base pH value around which to fluctuate (default: 7.5)
            noise_level: Standard deviation of random noise (default: 0.1)
            trend_factor: Long-term trend factor (default: 0.0 = no trend)
            enable_events: Whether to simulate sudden events (default: True)
        """
        self.base_ph = base_ph
        self.noise_level = noise_level
        self.trend_factor = trend_factor
        self.enable_events = enable_events
        
        self.current_ph = base_ph
        self.time_counter = 0
        self.event_counter = 0
        
        # Event probabilities (chance per reading)
        self.rain_event_prob = 0.02  # 2% chance of rain event
        self.heat_event_prob = 0.015  # 1.5% chance of heat event
        
    def _calculate_daily_cycle(self, time_hour: float) -> float:
        """
        Calculate daily pH cycle (lower in morning, higher in afternoon).
        
        Args:
            time_hour: Hour of day (0-24)
            
        Returns:
            Adjustment factor for pH based on time of day
        """
        # pH tends to be slightly lower in early morning, higher in afternoon
        cycle = 0.2 * np.sin(2 * np.pi * (time_hour - 6) / 24)
        return cycle
    
    def _simulate_rain_event(self) -> float:
        """
        Simulate a sudden pH drop due to rain (acidic rain).
        
        Returns:
            pH drop amount
        """
        # Rain can drop pH by 0.3-0.8
        drop = np.random.uniform(-0.8, -0.3)
        return drop
    
    def _simulate_heat_event(self) -> float:
        """
        Simulate gradual pH increase due to hot weather (algal bloom).
        
        Returns:
            pH increase amount
        """
        # Heat can increase pH by 0.2-0.6
        increase = np.random.uniform(0.2, 0.6)
        return increase
    
    def generate_reading(self) -> Tuple[datetime, float]:
        """
        Generate a single pH reading.
        
        Returns:
            Tuple of (timestamp, pH_value)
        """
        self.time_counter += 1
        
        # Get current hour for daily cycle
        current_hour = datetime.now().hour + datetime.now().minute / 60.0
        
        # Base pH with daily cycle
        daily_adjustment = self._calculate_daily_cycle(current_hour)
        base_value = self.base_ph + daily_adjustment
        
        # Add long-term trend
        trend_adjustment = self.trend_factor * (self.time_counter / 1000.0)
        
        # Simulate events
        event_adjustment = 0.0
        if self.enable_events:
            # Check for rain event
            if np.random.random() < self.rain_event_prob:
                event_adjustment = self._simulate_rain_event()
                self.event_counter += 1
            # Check for heat event
            elif np.random.random() < self.heat_event_prob:
                event_adjustment = self._simulate_heat_event()
                self.event_counter += 1
        
        # Apply event with decay (events fade over time)
        if abs(event_adjustment) > 0.01:
            decay_factor = 0.95  # Events decay by 5% per reading
            event_adjustment *= (decay_factor ** (self.time_counter - self.event_counter))
        
        # Add random noise
        noise = np.random.normal(0, self.noise_level)
        
        # Calculate final pH
        self.current_ph = base_value + trend_adjustment + event_adjustment + noise
        
        # Ensure pH stays in realistic range (4.0 - 10.0)
        self.current_ph = np.clip(self.current_ph, 4.0, 10.0)
        
        return datetime.now(), round(self.current_ph, 2)
    
    def stream_readings(
        self,
        interval_seconds: float = 5.0,
        max_readings: int = None
    ) -> Generator[Tuple[datetime, float], None, None]:
        """
        Stream pH readings at regular intervals.
        
        Args:
            interval_seconds: Time between readings in seconds (default: 5.0)
            max_readings: Maximum number of readings (None = infinite)
            
        Yields:
            Tuple of (timestamp, pH_value)
        """
        reading_count = 0
        
        while True:
            if max_readings and reading_count >= max_readings:
                break
                
            timestamp, ph_value = self.generate_reading()
            yield timestamp, ph_value
            
            reading_count += 1
            time.sleep(interval_seconds)


if __name__ == "__main__":
    # Demo: Generate some sample readings
    print("pH Simulator Demo")
    print("=" * 50)
    
    simulator = PHSimulator(base_ph=7.5, enable_events=True)
    
    print("Generating 10 sample readings...\n")
    for i, (timestamp, ph_value) in enumerate(simulator.stream_readings(interval_seconds=1, max_readings=10)):
        status = "⚠️" if ph_value < 7.0 or ph_value > 8.5 else "✓"
        print(f"[{i+1:2d}] {timestamp.strftime('%H:%M:%S')} | pH: {ph_value:5.2f} {status}")

