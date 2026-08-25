from datetime import datetime

import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.operational_record import OperationalRecord

from app.ml.forecasting.forecast_service import (
    generate_forecast,
)

from app.services.anomaly_service import (
    AnomalyService,
)

from app.services.root_cause_service import (
    RootCauseService,
)

from app.services.optimization_service import (
    OptimizationService,
)


class ReportService:

    def generate_device_report(
        self,
        db: Session,
        organization_id: int,
        device_id: int,
    ):

        records = db.scalars(
            select(OperationalRecord)
            .where(
                OperationalRecord.organization_id
                == organization_id,

                OperationalRecord.device_id
                == device_id,
            )
            .order_by(
                OperationalRecord.timestamp
            )
        ).all()

        if not records:
            raise ValueError(
                "No operational data found for this device."
            )

        dataframe = pd.DataFrame(
            [
                {
                    "timestamp": record.timestamp,
                    "energy_kwh": record.energy_kwh,
                    "operational_load":
                        record.operational_load,
                    "temperature_c":
                        record.temperature_c,
                    "utilization_percent":
                        record.utilization_percent,
                }
                for record in records
            ]
        )

        numeric_columns = [
            "energy_kwh",
            "operational_load",
            "temperature_c",
            "utilization_percent",
        ]

        for column in numeric_columns:

            dataframe[column] = pd.to_numeric(
                dataframe[column],
                errors="coerce",
            )

            dataframe[column] = (
                dataframe[column]
                .interpolate()
                .ffill()
                .bfill()
            )

        # ==========================================
        # Historical statistics
        # ==========================================

        current_energy = float(
            dataframe.iloc[-1]["energy_kwh"]
        )

        average_energy = float(
            dataframe["energy_kwh"].mean()
        )

        peak_energy = float(
            dataframe["energy_kwh"].max()
        )

        minimum_energy = float(
            dataframe["energy_kwh"].min()
        )

        utilization = float(
            dataframe.iloc[-1][
                "utilization_percent"
            ]
        )

        temperature = float(
            dataframe.iloc[-1][
                "temperature_c"
            ]
        )

        # ==========================================
        # Forecast
        # ==========================================

        forecast_result = generate_forecast(
            db=db,
            organization_id=organization_id,
            device_id=device_id,
            horizon_hours=24,
        )

        forecast_points = forecast_result[
            "forecast"
        ]

        predicted_values = [
            point["predicted_value"]
            for point in forecast_points
        ]

        peak_forecast = max(
            predicted_values
        )

        average_forecast = (
            sum(predicted_values)
            / len(predicted_values)
        )

        forecast_increase = 0.0

        if current_energy > 0:
            forecast_increase = (
                (
                    peak_forecast
                    - current_energy
                )
                / current_energy
            ) * 100

        forecast = {
            "model":
                forecast_result["model"],

            "horizon_hours": 24,

            "average_predicted_energy_kwh":
                round(
                    average_forecast,
                    2,
                ),

            "peak_predicted_energy_kwh":
                round(
                    peak_forecast,
                    2,
                ),

            "forecast_increase_percent":
                round(
                    forecast_increase,
                    2,
                ),

            "peak_time":
                forecast_points[
                    predicted_values.index(
                        peak_forecast
                    )
                ]["timestamp"],
        }

        # ==========================================
        # Anomaly analysis
        # ==========================================

        anomaly_service = AnomalyService()

        anomalies = anomaly_service.summary(
            dataframe
        )

        # ==========================================
        # Root cause analysis
        # ==========================================

        root_cause_service = RootCauseService()

        root_cause = root_cause_service.analyze(
            dataframe
        )

        # ==========================================
        # Optimization
        # ==========================================

        optimization_service = (
            OptimizationService()
        )

        optimization = (
            optimization_service.optimize(
                dataframe=dataframe,
                db=db,
                organization_id=organization_id,
                device_id=device_id,
                forecast_horizon=24,
            )
        )

        # ==========================================
        # Overall risk
        # ==========================================

        anomaly_count = anomalies[
            "anomaly_count"
        ]

        anomaly_rate = anomalies[
            "anomaly_rate_percent"
        ]

        if (
            forecast_increase >= 50
            or anomaly_count >= 40
        ):
            overall_risk = "CRITICAL"

        elif (
            forecast_increase >= 25
            or anomaly_rate >= 5
        ):
            overall_risk = "HIGH"

        elif (
            forecast_increase >= 10
            or anomaly_rate >= 2
        ):
            overall_risk = "MEDIUM"

        else:
            overall_risk = "LOW"

        # ==========================================
        # Recommendation
        # ==========================================

        estimated_savings = float(
            optimization.get(
                "expected_savings_percent",
                0,
            )
        )

        estimated_energy_savings = float(
            optimization.get(
                "expected_energy_savings_kwh",
                0,
            )
        )

        recommendation = {
            "strategy":
                optimization.get(
                    "recommended_strategy"
                ),

            "recommendation":
                optimization.get(
                    "recommendation"
                ),

            "estimated_savings_percent":
                estimated_savings,

            "estimated_energy_savings_kwh":
                estimated_energy_savings,
        }

        # ==========================================
        # Executive summary
        # ==========================================

        executive_summary = (
            f"Device {device_id} is currently "
            f"classified as {overall_risk} risk. "
            f"Current energy consumption is "
            f"{current_energy:.2f} kWh, while the "
            f"next 24-hour forecast predicts a "
            f"peak of {peak_forecast:.2f} kWh. "
            f"{anomaly_count} anomalies were detected. "
            f"The primary root cause is "
            f"{root_cause.get('primary_factor', 'unknown')}. "
            f"The recommended optimization strategy "
            f"is {optimization.get('recommended_strategy', 'monitoring')}."
        )

        return {
            "device_id": device_id,

            "generated_at":
                datetime.utcnow(),

            "executive_summary":
                executive_summary,

            "current_energy_kwh":
                round(
                    current_energy,
                    2,
                ),

            "average_energy_kwh":
                round(
                    average_energy,
                    2,
                ),

            "peak_energy_kwh":
                round(
                    peak_energy,
                    2,
                ),

            "minimum_energy_kwh":
                round(
                    minimum_energy,
                    2,
                ),

            "utilization_percent":
                round(
                    utilization,
                    2,
                ),

            "temperature_c":
                round(
                    temperature,
                    2,
                ),

            "forecast":
                forecast,

            "anomalies":
                anomalies,

            "root_cause":
                root_cause,

            "optimization":
                optimization,

            "recommendation":
                recommendation,

            "overall_risk":
                overall_risk,

            "estimated_savings_percent":
                estimated_savings,

            "estimated_energy_savings_kwh":
                estimated_energy_savings,
        }