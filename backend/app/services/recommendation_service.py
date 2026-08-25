from app.ml.recommendation.recommendation_engine import (
    RecommendationEngine,
)


class RecommendationService:

    def __init__(self):

        self.engine = (
            RecommendationEngine()
        )

    def generate(
        self,
        device_id: int,
        forecast_result: dict,
        anomaly_result: dict,
        root_cause_result: dict,
        optimization_result: dict,
        simulation_result: dict | None = None,
    ):

        forecast_risk = (
            forecast_result
            .get("forecast_risk", {})
        )

        recommendation = (
            self.engine.generate(

                forecast_risk_level=
                    forecast_risk.get(
                        "risk_level",
                        "LOW",
                    ),

                forecast_increase_percent=
                    forecast_risk.get(
                        "forecast_increase_percent",
                        0,
                    ),

                anomaly_count=
                    anomaly_result.get(
                        "anomaly_count",
                        0,
                    ),

                anomaly_rate_percent=
                    anomaly_result.get(
                        "anomaly_rate_percent",
                        0,
                    ),

                root_cause=
                    root_cause_result.get(
                        "root_cause",
                    ),

                primary_factor=
                    root_cause_result.get(
                        "primary_factor",
                    ),

                optimization_strategy=
                    optimization_result.get(
                        "recommended_strategy",
                    ),

                optimization_savings_percent=
                    optimization_result.get(
                        "expected_savings_percent",
                        0,
                    ),

                simulation_risk_level=(
                    simulation_result.get(
                        "risk_level"
                    )
                    if simulation_result
                    else None
                ),

                simulation_energy_change_percent=(
                    simulation_result.get(
                        "energy_change_percent"
                    )
                    if simulation_result
                    else None
                ),
            )
        )

        return {
            "device_id": device_id,

            "priority":
                recommendation.priority,

            "risk_level":
                recommendation.risk_level,

            "action":
                recommendation.action,

            "reason":
                recommendation.reason,

            "expected_benefit":
                recommendation.expected_benefit,

            "confidence":
                recommendation.confidence,

            "estimated_savings_percent":
                recommendation.estimated_savings_percent,

            "signals": {
                "forecast":
                    forecast_result,

                "anomalies":
                    anomaly_result,

                "root_cause":
                    root_cause_result,

                "optimization":
                    optimization_result,

                "simulation":
                    simulation_result,
            },
        }