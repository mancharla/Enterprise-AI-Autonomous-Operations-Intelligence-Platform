from dataclasses import dataclass


@dataclass
class Recommendation:
    priority: str
    action: str
    reason: str
    expected_benefit: str
    confidence: float
    risk_level: str
    estimated_savings_percent: float


class RecommendationEngine:

    def generate(
        self,
        forecast_risk_level: str,
        forecast_increase_percent: float,
        anomaly_count: int,
        anomaly_rate_percent: float,
        root_cause: str | None,
        primary_factor: str | None,
        optimization_strategy: str | None,
        optimization_savings_percent: float,
        simulation_risk_level: str | None,
        simulation_energy_change_percent: float | None,
    ) -> Recommendation:

        signals = []

        risk_scores = {
            "LOW": 1,
            "MEDIUM": 2,
            "HIGH": 3,
            "CRITICAL": 4,
        }

        forecast_score = risk_scores.get(
            forecast_risk_level.upper(),
            0,
        )

        simulation_score = risk_scores.get(
            (simulation_risk_level or "LOW").upper(),
            0,
        )

        # ------------------------------------------
        # Forecast signal
        # ------------------------------------------

        if forecast_score >= 4:

            signals.append({
                "score": 4,
                "reason":
                    "Forecast indicates critical "
                    "future operational demand.",
            })

        elif forecast_score >= 3:

            signals.append({
                "score": 3,
                "reason":
                    "Forecast indicates elevated "
                    "future operational demand.",
            })

        elif forecast_score >= 2:

            signals.append({
                "score": 2,
                "reason":
                    "Forecast indicates moderate "
                    "future operational demand.",
            })

        # ------------------------------------------
        # Anomaly signal
        # ------------------------------------------

        if anomaly_rate_percent >= 5:

            signals.append({
                "score": 4,
                "reason":
                    "High anomaly frequency detected "
                    "in operational data.",
            })

        elif anomaly_rate_percent >= 2:

            signals.append({
                "score": 3,
                "reason":
                    "Operational anomalies require "
                    "attention.",
            })

        elif anomaly_count > 0:

            signals.append({
                "score": 2,
                "reason":
                    "Operational anomalies have been "
                    "detected.",
            })

        # ------------------------------------------
        # Simulation signal
        # ------------------------------------------

        if simulation_score >= 4:

            signals.append({
                "score": 4,
                "reason":
                    "Scenario simulation predicts "
                    "critical operational impact.",
            })

        elif simulation_score >= 3:

            signals.append({
                "score": 3,
                "reason":
                    "Scenario simulation predicts "
                    "significant operational impact.",
            })

        # ------------------------------------------
        # Determine priority
        # ------------------------------------------

        highest_signal = max(
            [item["score"] for item in signals],
            default=1,
        )

        if highest_signal >= 4:
            priority = "CRITICAL"

        elif highest_signal >= 3:
            priority = "HIGH"

        elif highest_signal >= 2:
            priority = "MEDIUM"

        else:
            priority = "LOW"

        # ------------------------------------------
        # Action generation
        # ------------------------------------------

        if (
            forecast_score >= 3
            and optimization_strategy
        ):

            action = (
                f"Execute {optimization_strategy} "
                "before the predicted demand peak."
            )

        elif (
            primary_factor
            and forecast_score >= 2
        ):

            action = (
                f"Investigate {primary_factor} "
                "and apply corrective operational "
                "controls."
            )

        elif anomaly_count > 0:

            action = (
                "Investigate detected anomalies "
                "and monitor affected devices."
            )

        else:

            action = (
                "Continue monitoring operational "
                "conditions."
            )

        # ------------------------------------------
        # Explainable reason
        # ------------------------------------------

        reason_parts = []

        if forecast_increase_percent > 0:

            reason_parts.append(
                f"Forecast demand may increase "
                f"by {forecast_increase_percent:.2f}%."
            )

        if anomaly_count > 0:

            reason_parts.append(
                f"{anomaly_count} anomalies detected."
            )

        if root_cause:

            reason_parts.append(
                f"Root-cause analysis: {root_cause}"
            )

        if simulation_energy_change_percent:

            reason_parts.append(
                "Simulation indicates a "
                f"{simulation_energy_change_percent:.2f}% "
                "energy change under the selected scenario."
            )

        if not reason_parts:

            reason_parts.append(
                "No significant operational risk "
                "signals were detected."
            )

        reason = " ".join(
            reason_parts
        )

        # ------------------------------------------
        # Confidence
        # ------------------------------------------

        confidence = 0.50

        if forecast_score:
            confidence += 0.10

        if anomaly_count > 0:
            confidence += 0.10

        if root_cause:
            confidence += 0.10

        if optimization_strategy:
            confidence += 0.05

        if simulation_risk_level:
            confidence += 0.05

        confidence = min(
            confidence,
            0.95,
        )

        # ------------------------------------------
        # Expected benefit
        # ------------------------------------------

        if optimization_savings_percent > 0:

            expected_benefit = (
                f"Estimated optimization savings "
                f"of {optimization_savings_percent:.2f}%."
            )

        else:

            expected_benefit = (
                "Reduced operational risk and "
                "improved resource utilization."
            )

        return Recommendation(
            priority=priority,
            action=action,
            reason=reason,
            expected_benefit=expected_benefit,
            confidence=round(
                confidence,
                2,
            ),
            risk_level=(
                forecast_risk_level.upper()
                if forecast_risk_level
                else "LOW"
            ),
            estimated_savings_percent=round(
                optimization_savings_percent,
                2,
            ),
        )