import pandas as pd
from prophet import Prophet


class ProphetForecastModel:

    def __init__(self):
        self.model = None

    def prepare_data(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:

        data = dataframe.copy()

        data = data.rename(
            columns={
                "timestamp": "ds",
                "energy_kwh": "y",
            }
        )

        data["ds"] = pd.to_datetime(
            data["ds"],
            errors="coerce",
        )

        data["y"] = pd.to_numeric(
            data["y"],
            errors="coerce",
        )

        data = data.dropna(
            subset=["ds", "y"]
        )

        data = (
            data.groupby("ds", as_index=False)["y"]
            .mean()
            .sort_values("ds")
        )

        return data

    def train(
        self,
        dataframe: pd.DataFrame,
    ):

        data = self.prepare_data(dataframe)

        if len(data) < 10:
            raise ValueError(
                "At least 10 valid historical records "
                "are required for forecasting."
            )

        self.model = Prophet(
            interval_width=0.90,
            daily_seasonality=True,
            weekly_seasonality=True,
            yearly_seasonality=False,
        )

        self.model.fit(data)

        return data

    def predict(
        self,
        dataframe: pd.DataFrame,
        periods: int,
        frequency: str = "h",
    ):

        historical_data = self.train(dataframe)

        future = self.model.make_future_dataframe(
            periods=periods,
            freq=frequency,
            include_history=False,
        )

        forecast = self.model.predict(future)

        result = forecast[
            [
                "ds",
                "yhat",
                "yhat_lower",
                "yhat_upper",
            ]
        ].copy()

        result = result.rename(
            columns={
                "ds": "timestamp",
                "yhat": "predicted_value",
                "yhat_lower": "lower_bound",
                "yhat_upper": "upper_bound",
            }
        )

        return historical_data, result