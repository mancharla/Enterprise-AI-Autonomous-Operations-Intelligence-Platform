import pandas as pd

from app.ml.simulation.simulation_engine import (
    SimulationEngine,
)


class SimulationService:

    def __init__(self):
        self.engine = SimulationEngine()

    def simulate(
        self,
        dataframe: pd.DataFrame,
        scenario: str,
        magnitude_percent: float,
        duration_hours: int,
    ):

        if dataframe.empty:
            raise ValueError(
                "No operational data available."
            )

        latest = dataframe.iloc[-1]

        baseline_energy = float(
            latest["energy_kwh"]
        )

        operational_load = float(
            latest.get(
                "operational_load",
                0,
            )
        )

        utilization_percent = float(
            latest.get(
                "utilization_percent",
                0,
            )
        )

        temperature_c = float(
            latest.get(
                "temperature_c",
                0,
            )
        )

        result = self.engine.simulate(
            scenario=scenario,
            baseline_energy_kwh=baseline_energy,
            operational_load=operational_load,
            utilization_percent=utilization_percent,
            temperature_c=temperature_c,
            magnitude_percent=magnitude_percent,
            duration_hours=duration_hours,
        )

        recommendation = self._generate_recommendation(
            scenario=scenario,
            risk_level=result.risk_level,
            energy_change_percent=result.energy_change_percent,
        )

        return {
            "baseline_energy_kwh":
                result.baseline_energy_kwh,

            "simulated_energy_kwh":
                result.simulated_energy_kwh,

            "energy_change_percent":
                result.energy_change_percent,

            "estimated_cost_impact":
                result.estimated_cost_impact,

            "failure_probability_percent":
                result.failure_probability_percent,

            "performance_impact_percent":
                result.performance_impact_percent,

            "risk_level":
                result.risk_level,

            "recommendation":
                recommendation,
        }

    @staticmethod
    def _generate_recommendation(
        scenario: str,
        risk_level: str,
        energy_change_percent: float,
    ):

        recommendations = {
            "DEMAND_SURGE":
                "Redistribute non-critical workloads "
                "and increase available capacity "
                "before the demand surge.",

            "DEVICE_FAILURE":
                "Activate backup equipment and "
                "schedule immediate maintenance "
                "for the affected device.",

            "FACILITY_SHUTDOWN":
                "Redirect workloads to available "
                "facilities and activate the "
                "business continuity plan.",

            "TEMPERATURE_SPIKE":
                "Optimize cooling systems and "
                "reduce non-critical thermal loads.",

            "WORKFORCE_REDUCTION":
                "Prioritize critical operations and "
                "automate or reschedule non-critical "
                "workloads.",

            "RESOURCE_SHORTAGE":
                "Prioritize high-value operations "
                "and redistribute constrained resources.",
        }

        recommendation = recommendations.get(
            scenario.upper(),
            "Review operational conditions "
            "and apply the recommended mitigation plan.",
        )

        if risk_level == "CRITICAL":

            recommendation += (
                " Immediate intervention is recommended."
            )

        elif risk_level == "HIGH":

            recommendation += (
                " Proactive intervention is recommended."
            )

        return recommendation