from datetime import datetime, timedelta


class SimulationEngine:

    SCENARIOS = {
        "demand_surge",
        "device_failure",
        "facility_shutdown",
        "temperature_increase",
        "workforce_reduction",
        "resource_shortage",
    }

    def simulate(
        self,
        scenario: str,
        baseline_energy: float,
        operational_load: float,
        utilization_percent: float,
        temperature_c: float,
        impact_percent: float,
        duration_hours: int,
    ):

        scenario = scenario.lower().strip()

        if scenario not in self.SCENARIOS:
            raise ValueError(
                "Unsupported scenario. "
                "Supported scenarios: "
                + ", ".join(sorted(self.SCENARIOS))
            )

        if baseline_energy < 0:
            raise ValueError(
                "Baseline energy cannot be negative."
            )

        # -----------------------------------------
        # Scenario parameters
        # -----------------------------------------

        energy_multiplier = 1.0
        operational_impact = 0.0
        failure_probability = 0.0
        cost_impact = 0.0
        savings = 0.0
        recommendation = ""

        if scenario == "demand_surge":

            energy_multiplier = (
                1 + impact_percent / 100
            )

            operational_impact = min(
                impact_percent * 0.75,
                100,
            )

            failure_probability = min(
                5 + impact_percent * 0.35,
                100,
            )

            cost_impact = impact_percent * 0.8

            recommendation = (
                "Redistribute workload and prepare "
                "additional capacity before the demand surge."
            )

        elif scenario == "device_failure":

            energy_multiplier = max(
                0.65,
                1 - impact_percent / 200,
            )

            operational_impact = min(
                30 + impact_percent * 0.5,
                100,
            )

            failure_probability = min(
                40 + impact_percent * 0.6,
                100,
            )

            cost_impact = 15 + impact_percent * 0.7

            recommendation = (
                "Redistribute workloads to healthy devices "
                "and initiate predictive maintenance."
            )

        elif scenario == "facility_shutdown":

            energy_multiplier = max(
                0.30,
                1 - impact_percent / 100,
            )

            operational_impact = min(
                50 + impact_percent * 0.4,
                100,
            )

            failure_probability = min(
                20 + impact_percent * 0.4,
                100,
            )

            cost_impact = 20 + impact_percent * 0.8

            recommendation = (
                "Redirect operations to available facilities "
                "and activate business continuity procedures."
            )

        elif scenario == "temperature_increase":

            temperature_factor = (
                impact_percent / 100
            )

            energy_multiplier = (
                1 + temperature_factor * 0.60
            )

            operational_impact = min(
                impact_percent * 0.50,
                100,
            )

            failure_probability = min(
                5 + impact_percent * 0.30,
                100,
            )

            cost_impact = impact_percent * 0.65

            savings = min(
                impact_percent * 0.25,
                30,
            )

            recommendation = (
                "Optimize cooling systems and reduce "
                "non-critical cooling load."
            )

        elif scenario == "workforce_reduction":

            energy_multiplier = max(
                0.60,
                1 - impact_percent * 0.004,
            )

            operational_impact = min(
                impact_percent * 0.70,
                100,
            )

            failure_probability = min(
                5 + impact_percent * 0.20,
                100,
            )

            cost_impact = impact_percent * 0.40

            savings = min(
                impact_percent * 0.50,
                40,
            )

            recommendation = (
                "Automate repetitive operations and "
                "redistribute workforce responsibilities."
            )

        elif scenario == "resource_shortage":

            energy_multiplier = (
                1 + impact_percent * 0.003
            )

            operational_impact = min(
                20 + impact_percent * 0.65,
                100,
            )

            failure_probability = min(
                10 + impact_percent * 0.55,
                100,
            )

            cost_impact = 10 + impact_percent * 0.75

            recommendation = (
                "Prioritize critical workloads and "
                "redistribute available resources."
            )

        # -----------------------------------------
        # Environmental / utilization adjustments
        # -----------------------------------------

        if temperature_c > 30:

            energy_multiplier *= 1.05

            failure_probability += 5

        if utilization_percent > 85:

            failure_probability += 8

            operational_impact += 5

        if operational_load > 80:

            failure_probability += 5

            operational_impact += 5

        failure_probability = min(
            failure_probability,
            100,
        )

        operational_impact = min(
            operational_impact,
            100,
        )

        # -----------------------------------------
        # Calculate simulation
        # -----------------------------------------

        simulated_energy = (
            baseline_energy
            * energy_multiplier
        )

        energy_change_percent = 0.0

        if baseline_energy > 0:

            energy_change_percent = (
                (
                    simulated_energy
                    - baseline_energy
                )
                / baseline_energy
            ) * 100

        # -----------------------------------------
        # Risk classification
        # -----------------------------------------

        risk_score = (
            failure_probability * 0.45
            + operational_impact * 0.35
            + max(cost_impact, 0) * 0.20
        )

        if risk_score >= 70:

            risk_level = "CRITICAL"

        elif risk_score >= 45:

            risk_level = "HIGH"

        elif risk_score >= 25:

            risk_level = "MEDIUM"

        else:

            risk_level = "LOW"

        simulated_until = (
            datetime.utcnow()
            + timedelta(hours=duration_hours)
        )

        return {
            "scenario": scenario,
            "baseline_energy_kwh": round(
                baseline_energy,
                2,
            ),
            "simulated_energy_kwh": round(
                simulated_energy,
                2,
            ),
            "energy_change_percent": round(
                energy_change_percent,
                2,
            ),
            "operational_impact_percent": round(
                operational_impact,
                2,
            ),
            "failure_probability_percent": round(
                failure_probability,
                2,
            ),
            "estimated_cost_impact_percent": round(
                cost_impact,
                2,
            ),
            "estimated_savings_percent": round(
                savings,
                2,
            ),
            "risk_level": risk_level,
            "duration_hours": duration_hours,
            "simulated_until": simulated_until,
            "recommendation": recommendation,
        }