"""
Digital Twin "What-If" Simulation Engine for Aquaculture Ponds.

Simulates future pond dynamics under varying environmental stressors
(rain, heat) and management interventions (lime, aeration, water exchange).
"""

import math
from typing import Dict, Any, List

class DigitalTwinSimulator:
    def __init__(self, default_volume_m3: float = 1000.0):
        self.default_volume_m3 = default_volume_m3

    def simulate(
        self,
        current_ph: float,
        current_do: float = 7.5,
        current_temp: float = 28.0,
        pond_volume_m3: float = 1000.0,
        rainfall_mm: float = 0.0,
        heat_multiplier: float = 1.0,
        lime_kg: float = 0.0,
        aerator_hours: float = 0.0,
        water_exchange_pct: float = 0.0,
        n_steps: int = 24,
    ) -> Dict[str, Any]:
        """Run parallel simulation of baseline (no action) vs counterfactual (with intervention)."""
        vol = max(100.0, pond_volume_m3 or self.default_volume_m3)
        vol_factor = 1000.0 / vol

        # Calculate impacts
        # 1. Rainfall: Acidifies pond by up to 0.015 pH drop per mm of rain
        rain_ph_drop = (rainfall_mm * 0.012) * min(1.5, vol_factor)
        # 2. Heat: Increases algal respiration causing night pH/DO drop and afternoon peak
        heat_effect = (heat_multiplier - 1.0) * 0.4
        
        # 3. Lime dosage: Increases alkalinity & pH. ~25kg/1000m3 raises pH by ~0.35
        lime_ph_boost = (lime_kg * 0.014) * vol_factor
        
        # 4. Aeration: Increases DO by ~0.6 mg/L per hour, stabilizes pH fluctuations
        aeration_do_boost = min(3.5, aerator_hours * 0.65)
        aeration_ph_stability = min(0.3, aerator_hours * 0.05)

        # 5. Water exchange: Buffers toward neutral 7.5
        exchange_fraction = min(0.5, water_exchange_pct / 100.0)

        baseline_ph_traj: List[float] = []
        counterfactual_ph_traj: List[float] = []
        baseline_do_traj: List[float] = []
        counterfactual_do_traj: List[float] = []
        time_labels: List[str] = []

        curr_base_ph = current_ph
        curr_twin_ph = current_ph
        curr_base_do = current_do
        curr_twin_do = current_do

        for t in range(1, n_steps + 1):
            time_labels.append(f"+{t}h")
            
            # Diurnal sine wave cycle for natural photosynthesis
            cycle = math.sin((t / 24.0) * 2 * math.pi) * 0.15

            # ── Baseline Dynamics ──
            step_rain_decay = (rain_ph_drop / n_steps) * (1.2 if t <= 6 else 0.4)
            step_heat_decay = (heat_effect / n_steps) * cycle
            curr_base_ph = curr_base_ph - step_rain_decay + step_heat_decay + (cycle * 0.05)
            curr_base_do = max(2.0, curr_base_do - (rainfall_mm * 0.02 / n_steps) + (cycle * 0.3) - (heat_effect * 0.2))

            # Clamp baseline
            curr_base_ph = max(5.0, min(10.0, curr_base_ph))
            baseline_ph_traj.append(round(curr_base_ph, 2))
            baseline_do_traj.append(round(curr_base_do, 2))

            # ── Counterfactual (What-If) Dynamics ──
            # Lime effect ramps up over the first 4-8 hours
            step_lime_gain = (lime_ph_boost / min(8, n_steps)) if t <= 8 else 0.0
            step_aerator_gain = (aeration_do_boost / min(6, n_steps)) if t <= 6 else 0.0
            
            curr_twin_ph = curr_twin_ph - (step_rain_decay * (1.0 - aeration_ph_stability)) + step_lime_gain + (cycle * 0.03)
            if exchange_fraction > 0:
                curr_twin_ph += (7.5 - curr_twin_ph) * (exchange_fraction / n_steps)

            curr_twin_do = min(12.0, curr_twin_do + step_aerator_gain + (cycle * 0.2))

            # Clamp twin
            curr_twin_ph = max(5.0, min(10.0, curr_twin_ph))
            counterfactual_ph_traj.append(round(curr_twin_ph, 2))
            counterfactual_do_traj.append(round(curr_twin_do, 2))

        # Compute risk scores (0-100)
        def compute_risk(ph_list: List[float], do_list: List[float]) -> float:
            risk = 0.0
            for p, d in zip(ph_list, do_list):
                if p < 7.0:
                    risk += (7.0 - p) * 35.0
                elif p > 8.5:
                    risk += (p - 8.5) * 35.0
                if d < 5.0:
                    risk += (5.0 - d) * 15.0
            return min(100.0, round(risk / len(ph_list) * 2.0, 1))

        base_risk = compute_risk(baseline_ph_traj, baseline_do_traj)
        twin_risk = compute_risk(counterfactual_ph_traj, counterfactual_do_traj)
        risk_reduction_pct = round(max(0.0, (base_risk - twin_risk) / max(1.0, base_risk) * 100.0), 1)

        summary_message = (
            f"Kịch bản can thiệp giảm {risk_reduction_pct}% rủi ro. "
            f"pH dự kiến ổn định ở mức {counterfactual_ph_traj[-1]} (so với {baseline_ph_traj[-1]} nếu không can thiệp)."
        )

        return {
            "time_labels": time_labels,
            "baseline": {
                "ph_trajectory": baseline_ph_traj,
                "do_trajectory": baseline_do_traj,
                "final_ph": baseline_ph_traj[-1],
                "min_ph": min(baseline_ph_traj),
                "max_ph": max(baseline_ph_traj),
                "risk_score": base_risk
            },
            "what_if": {
                "ph_trajectory": counterfactual_ph_traj,
                "do_trajectory": counterfactual_do_traj,
                "final_ph": counterfactual_ph_traj[-1],
                "min_ph": min(counterfactual_ph_traj),
                "max_ph": max(counterfactual_ph_traj),
                "risk_score": twin_risk
            },
            "risk_reduction_pct": risk_reduction_pct,
            "summary_message": summary_message,
            "parameters": {
                "rainfall_mm": rainfall_mm,
                "heat_multiplier": heat_multiplier,
                "lime_kg": lime_kg,
                "aerator_hours": aerator_hours,
                "water_exchange_pct": water_exchange_pct,
                "pond_volume_m3": vol
            }
        }

# Global digital twin simulator instance
digital_twin_simulator = DigitalTwinSimulator()
