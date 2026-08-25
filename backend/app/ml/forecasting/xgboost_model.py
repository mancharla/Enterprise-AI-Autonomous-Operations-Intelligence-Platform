import pandas as pd
from xgboost import XGBRegressor


class XGBoostForecastModel:

    def __init__(self):
        self.model = XGBRegressor(
            n_estimators=300,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            objective="reg:squarederror",
            random_state=42,
        )

    @staticmethod
    def create_features(
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:

        data = dataframe.copy()

        data["timestamp"] = pd.to_datetime(
            data["timestamp"]
        )

        data = data.sort_values(
            "timestamp"
        )

        data["hour"] = data["timestamp"].dt.hour
        data["day_of_week"] = (
            data["timestamp"].dt.dayofweek
        )
        data["day_of_month"] = (
            data["timestamp"].dt.day
        )
        data["month"] = (
            data["timestamp"].dt.month
        )
        data["week_of_year"] = (
            data["timestamp"].dt.isocalendar().week
            .astype(int)
        )

        data["lag_1"] = (
            data["energy_kwh"]
            .shift(1)
        )

        data["lag_24"] = (
            data["energy_kwh"]
            .shift(24)
        )

        data["lag_168"] = (
            data["energy_kwh"]
            .shift(168)
        )

        data["rolling_24"] = (
            data["energy_kwh"]
            .shift(1)
            .rolling(24)
            .mean()
        )

        data["rolling_168"] = (
            data["energy_kwh"]
            .shift(1)
            .rolling(168)
            .mean()
        )

        data = data.dropna()

        return data

    def train(
        self,
        dataframe: pd.DataFrame,
    ):

        data = self.create_features(
            dataframe
        )

        if len(data) < 200:
            raise ValueError(
                "At least 200 usable records "
                "are required for XGBoost forecasting."
            )

        feature_columns = [
            "hour",
            "day_of_week",
            "day_of_month",
            "month",
            "week_of_year",
            "lag_1",
            "lag_24",
            "lag_168",
            "rolling_24",
            "rolling_168",
        ]

        X = data[feature_columns]
        y = data["energy_kwh"]

        self.model.fit(
            X,
            y,
        )

        return feature_columns

    def predict(
        self,
        dataframe: pd.DataFrame,
        periods: int,
    ):

        feature_columns = self.train(
            dataframe
        )

        history = dataframe.copy()

        history["timestamp"] = pd.to_datetime(
            history["timestamp"]
        )

        history = history.sort_values(
            "timestamp"
        )

        predictions = []

        for _ in range(periods):

            next_timestamp = (
                history["timestamp"].iloc[-1]
                + pd.Timedelta(hours=1)
            )

            temp = history.copy()

            temp["hour"] = (
                temp["timestamp"].dt.hour
            )

            temp["day_of_week"] = (
                temp["timestamp"].dt.dayofweek
            )

            temp["day_of_month"] = (
                temp["timestamp"].dt.day
            )

            temp["month"] = (
                temp["timestamp"].dt.month
            )

            temp["week_of_year"] = (
                temp["timestamp"]
                .dt.isocalendar()
                .week
                .astype(int)
            )

            temp["lag_1"] = (
                temp["energy_kwh"]
                .shift(1)
            )

            temp["lag_24"] = (
                temp["energy_kwh"]
                .shift(24)
            )

            temp["lag_168"] = (
                temp["energy_kwh"]
                .shift(168)
            )

            temp["rolling_24"] = (
                temp["energy_kwh"]
                .shift(1)
                .rolling(24)
                .mean()
            )

            temp["rolling_168"] = (
                temp["energy_kwh"]
                .shift(1)
                .rolling(168)
                .mean()
            )

            latest = temp.iloc[-1:]

            prediction = float(
                self.model.predict(
                    latest[feature_columns]
                )[0]
            )

            prediction = max(
                prediction,
                0,
            )

            new_row = {
                "timestamp": next_timestamp,
                "energy_kwh": prediction,
            }

            history = pd.concat(
                [
                    history,
                    pd.DataFrame([new_row]),
                ],
                ignore_index=True,
            )

            predictions.append(
                {
                    "timestamp": next_timestamp,
                    "predicted_value": round(
                        prediction,
                        2,
                    ),
                }
            )

        return predictions