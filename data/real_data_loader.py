"""
Real-World Aquaculture Data Loader for AI Aquaculture Guardian.

Loads and normalizes the Mendeley Data aquaculture dataset (DOI: 10.17632/8s73jfvgr5.2).
Converts records into canonical pandas DataFrames and existing SensorReading objects.

Handles:
- Primary continuous IoT stream ('Data IoTMLCQ.xlsx')
- Pre-IoT historical water quality ('Pre_IoT_Historical_Water_Quality_2023.xlsx')
- Fish health & intervention events ('IoT_Intervention_Events.xlsx', 'Fish_Health_Intervention_Comparison_2024_Corrected.xlsx')
- Climate conditions ('Monteria_Climate_Conditions_2023.xlsx')
"""

from __future__ import annotations

import os
import math
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Generator, Any

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    class _DummyPandas:
        class DataFrame:
            pass
        class Series:
            pass
    pd = _DummyPandas()

from ai.sensor_schema import SensorReading, SensorParameter, DataSource, SensorQuality


class RealDataLoader:
    """
    Loader and normalizer for real-world aquaculture datasets.
    """

    def __init__(self, data_dir: Optional[str] = None):
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "real")
        self.data_dir = data_dir

    def load_iot_stream(
        self,
        physical_scale: bool = True,
        max_rows: Optional[int] = None,
    ) -> Any:
        """
        Load the primary continuous IoT stream ('Data IoTMLCQ.xlsx').

        Args:
            physical_scale: If True, maps normalized pH (0-1) and turbidity (0-1)
                            to physical aquaculture scales (pH ~ 7.0-8.5, turbidity ~ 2.5-7.5 NTU).
                            Temperature and DO already use physical units.
            max_rows: Optional limit on number of rows.

        Returns:
            Cleaned, sorted DataFrame with canonical columns:
            ['timestamp', 'ph', 'temperature', 'dissolved_oxygen', 'turbidity',
             'month', 'day', 'hour', 'reading_id']
        """
        if not PANDAS_AVAILABLE:
            raise ImportError("pandas is required for loading real dataset files.")

        fpath = os.path.join(self.data_dir, "Data IoTMLCQ.xlsx")
        if not os.path.exists(fpath):
            raise FileNotFoundError(
                f"Real dataset file not found: {fpath}. "
                f"Please run 'python scripts/download_real_dataset.py' first."
            )

        df = pd.read_excel(fpath, nrows=max_rows)

        # Sort chronologically by month, day, hour, id
        df = df.sort_values(["month", "day", "hour", "id"]).reset_index(drop=True)

        # Construct synthetic/interpolated timestamp from month/day/hour (Year 2024)
        # Multiple readings per hour are spaced evenly within that hour
        timestamps = []
        for (m, d, h), group in df.groupby(["month", "day", "hour"], sort=False):
            n_readings = len(group)
            base_dt = datetime(2024, int(m), int(d), int(h), 0, 0)
            if n_readings == 1:
                timestamps.append(base_dt)
            else:
                step_seconds = max(1, int(3600 / n_readings))
                for i in range(n_readings):
                    timestamps.append(base_dt + timedelta(seconds=min(3599, i * step_seconds)))

        df["timestamp"] = timestamps

        # Canonical column mapping
        # In Data IoTMLCQ.xlsx:
        # - 'temperatura_scaled': °C (mean ~26.95, range 20.0-27.5)
        # - 'oxigeno_scaled': mg/L DO (mean ~8.17, range 7.3-9.0)
        # - 'ph': normalized 0.0 - 1.04
        # - 'turbidez': normalized 0.0 - 1.02
        temp_col = "temperatura_scaled" if "temperatura_scaled" in df.columns else "temperatura"
        do_col = "oxigeno_scaled" if "oxigeno_scaled" in df.columns else "oxigeno"

        if physical_scale:
            # Map normalized pH to physical aquaculture range [7.0, 8.5]
            # When normalized ph is 0.43 (mean), physical pH is ~7.65 (optimal)
            ph_series = 7.0 + df["ph"] * 1.5
            # Map normalized turbidity to physical NTU [2.5, 7.5]
            turb_series = 2.5 + df["turbidez"] * 5.0
        else:
            ph_series = df["ph"]
            turb_series = df["turbidez"]

        clean_df = pd.DataFrame({
            "timestamp": df["timestamp"],
            "ph": ph_series.astype(float),
            "temperature": df[temp_col].astype(float),
            "dissolved_oxygen": df[do_col].astype(float),
            "turbidity": turb_series.astype(float),
            "month": df["month"].astype(int),
            "day": df["day"].astype(int),
            "hour": df["hour"].astype(int),
            "reading_id": df["id"].astype(int),
            "is_interpolated_timestamp": True,  # Monotonic minutes within hour are regularized
        })

        return clean_df

    def load_historical_baseline(self) -> Any:
        """
        Load the 2023 pre-IoT monthly baseline with alkalinity and nitrates.
        """
        if not PANDAS_AVAILABLE:
            raise ImportError("pandas is required for loading real dataset files.")

        fpath = os.path.join(self.data_dir, "Pre_IoT_Historical_Water_Quality_2023.xlsx")
        if not os.path.exists(fpath):
            raise FileNotFoundError(f"Baseline file not found: {fpath}")

        df = pd.read_excel(fpath)
        # Normalize columns
        df = df.rename(columns={
            "Month": "month_name",
            "Dissolved Oxygen (mg/L)": "dissolved_oxygen",
            "Temperature (C)": "temperature",
            "Temperature (°C)": "temperature",
            "pH": "ph",
            "Turbidity (NTU)": "turbidity",
            "Alkalinity (mg/L)": "alkalinity",
            "Nitrates (mg/L)": "nitrates",
        })
        return df

    def load_fish_health_data(self) -> Any:
        """
        Load fish health metrics (Weight, Survival Rate, Disease Cases).
        """
        if not PANDAS_AVAILABLE:
            raise ImportError("pandas is required for loading real dataset files.")

        fpath = os.path.join(self.data_dir, "Validated_IoT_Fish_Health_Data 2024.xlsx")
        if not os.path.exists(fpath):
            raise FileNotFoundError(f"Fish health file not found: {fpath}")

        df = pd.read_excel(fpath)
        df = df.rename(columns={
            "Month": "month_name",
            "Average Fish Weight (g)": "avg_fish_weight_g",
            "Survival Rate (%)": "survival_rate_pct",
            "Disease Occurrence (Cases)": "disease_cases",
            "Temperature (C)": "temperature",
            "Temperature (°C)": "temperature",
            "Dissolved Oxygen (mg/L)": "dissolved_oxygen",
            "pH": "ph",
            "Turbidity (NTU)": "turbidity",
        })
        return df

    def to_sensor_readings(
        self,
        parameter: str = "pH",
        pond_id: str = "MONTERIA-POND-01",
        max_readings: Optional[int] = None,
    ) -> List[SensorReading]:
        """
        Convert real dataset records into SensorReading objects.

        Args:
            parameter: 'pH', 'temperature', 'dissolved_oxygen', or 'turbidity'
            pond_id: Identifier for the physical aquaculture pond
            max_readings: Optional reading limit

        Returns:
            List of typed SensorReading instances.
        """
        df = self.load_iot_stream(max_rows=max_readings)
        readings = []

        param_map = {
            "pH": ("ph", "pH"),
            "temperature": ("temperature", "°C"),
            "dissolved_oxygen": ("dissolved_oxygen", "mg/L"),
            "turbidity": ("turbidity", "NTU"),
        }

        col_name, unit = param_map.get(parameter, ("ph", "pH"))

        for idx, row in df.iterrows():
            val = float(row[col_name])
            reading = SensorReading(
                timestamp=row["timestamp"],
                sensor_id=f"{pond_id}-{parameter.upper()}",
                pond_id=pond_id,
                parameter=parameter,
                value=val,
                unit=unit,
                source=DataSource.CSV_IMPORT,
                quality=SensorQuality.GOOD if not math.isnan(val) else SensorQuality.BAD,
            )
            readings.append(reading)

        return readings

    def stream_real_readings(
        self,
        parameter: str = "pH",
        start_idx: int = 0,
    ) -> Generator[Tuple[datetime, float, Dict], None, None]:
        """
        Generator yielding (timestamp, value, context_dict) from real dataset.
        Enables streaming playback of real-world data in the dashboard.
        """
        df = self.load_iot_stream()
        for idx in range(start_idx, len(df)):
            row = df.iloc[idx]
            val = float(row["ph"]) if parameter == "pH" else float(row.get(parameter, 7.5))
            context = {
                "temperature": float(row["temperature"]),
                "dissolved_oxygen": float(row["dissolved_oxygen"]),
                "turbidity": float(row["turbidity"]),
                "reading_id": int(row["reading_id"]),
                "month": int(row["month"]),
                "day": int(row["day"]),
                "hour": int(row["hour"]),
                "data_source": "mendeley_real_data",
            }
            yield row["timestamp"], val, context
