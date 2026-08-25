import pandas as pd

from app.ml.forecasting.forecast_service import (
    generate_forecast,
)

from app.ml.optimization.engine import (
    OptimizationEngine,
)


class OptimizationService:

    def __init__(self):
        self.engine = OptimizationEngine()

    def optimize(
        self,
        dataframe: pd.DataFrame,
        db,
        organization_id: int,
        device_id: int,
        forecast_horizon: int = 24,
    ) -> dict:

        # ==========================================
        # Validate input
        # ==========================================

        if dataframe is None or dataframe.empty:
            raise ValueError(
                "No operational data available."
            )

        if forecast_horizon < 1:
            raise ValueError(
                "Forecast horizon must be at least 1 hour."
            )

        if forecast_horizon > 168:
            raise ValueError(
                "Forecast horizon cannot exceed 168 hours."
            )

        # ==========================================
        # Prepare dataframe
        # ==========================================

        data = dataframe.copy()

        required_columns = [
            "timestamp",
            "energy_kwh",
            "operational_load",
            "temperature_c",
            "utilization_percent",
        ]

        # Create missing columns safely
        for column in required_columns:

            if column not in data.columns:

                if column == "timestamp":
                    raise ValueError(
                        "Operational data must contain "
                        "a timestamp column."
                    )

                data[column] = 0.0

        # ==========================================
        # Timestamp validation
        # ==========================================

        data["timestamp"] = pd.to_datetime(
            data["timestamp"],
            errors="coerce",
        )

        data = data.dropna(
            subset=["timestamp"]
        )

        if data.empty:
            raise ValueError(
                "No valid timestamps found in "
                "operational data."
            )

        data = data.sort_values(
            "timestamp"
        ).reset_index(drop=True)

        # ==========================================
        # Numeric data preparation
        # ==========================================

        numeric_columns = [
            "energy_kwh",
            "operational_load",
            "temperature_c",
            "utilization_percent",
        ]

        for column in numeric_columns:

            data[column] = pd.to_numeric(
                data[column],
                errors="coerce",
            )

            data[column] = (
                data[column]
                .interpolate(
                    limit_direction="both"
                )
                .ffill()
                .bfill()
                .fillna(0.0)
            )

        # ==========================================
        # Basic data validation
        # ==========================================

        if len(data) < 2:
            raise ValueError(
                "At least 2 operational records "
                "are required for optimization."
            )

        if (
            data["energy_kwh"] < 0
        ).any():

            raise ValueError(
                "Energy consumption cannot contain "
                "negative values."
            )

        # ==========================================
        # Generate ML forecast
        # ==========================================

        forecast_result = generate_forecast(
            db=db,
            organization_id=organization_id,
            device_id=device_id,
            horizon_hours=forecast_horizon,
        )

        if not forecast_result:
            raise ValueError(
                "Forecast generation returned no result."
            )

        forecast = forecast_result.get(
            "forecast",
            []
        )

        if not forecast:
            raise ValueError(
                "Forecast generation returned no data."
            )

        forecast_model = forecast_result.get(
            "model",
            "Prophet",
        )

        # ==========================================
        # Validate forecast points
        # ==========================================

        valid_forecast = []

        for point in forecast:

            if not isinstance(
                point,
                dict,
            ):
                continue

            required_forecast_fields = [
                "timestamp",
                "predicted_value",
                "lower_bound",
                "upper_bound",
            ]

            if not all(
                field in point
                for field
                in required_forecast_fields
            ):
                continue

            try:

                timestamp = pd.to_datetime(
                    point["timestamp"]
                )

                predicted_value = float(
                    point["predicted_value"]
                )

                lower_bound = float(
                    point["lower_bound"]
                )

                upper_bound = float(
                    point["upper_bound"]
                )

            except (
                TypeError,
                ValueError,
            ):
                continue

            valid_forecast.append(
                {
                    **point,
                    "timestamp":
                        timestamp,
                    "predicted_value":
                        predicted_value,
                    "lower_bound":
                        lower_bound,
                    "upper_bound":
                        upper_bound,
                }
            )

        if not valid_forecast:
            raise ValueError(
                "Forecast contains no valid "
                "forecast points."
            )

        # ==========================================
        # Call optimization engine
        # ==========================================

        try:

            result = self.engine.optimize(
                dataframe=data,
                forecast=valid_forecast,
                forecast_model=forecast_model,
                forecast_horizon=forecast_horizon,
            )

        except ValueError:
            raise

        except Exception as exc:

            raise ValueError(
                f"Optimization calculation failed: "
                f"{str(exc)}"
            )

        # ==========================================
        # Return result
        # ==========================================

        return result