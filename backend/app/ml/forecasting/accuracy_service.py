import pandas as pd

from app.ml.forecasting.evaluation import (
    evaluate_predictions,
)
from app.ml.forecasting.prophet_model import (
    ProphetForecastModel,
)
from app.ml.forecasting.xgboost_model import (
    XGBoostForecastModel,
)


def prepare_dataframe(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:

    data = dataframe.copy()

    data["timestamp"] = pd.to_datetime(
        data["timestamp"],
        errors="coerce",
    )

    data["energy_kwh"] = pd.to_numeric(
        data["energy_kwh"],
        errors="coerce",
    )

    data = data.dropna(
        subset=[
            "timestamp",
            "energy_kwh",
        ]
    )

    data = (
        data
        .sort_values("timestamp")
        .groupby(
            "timestamp",
            as_index=False,
        )["energy_kwh"]
        .mean()
    )

    data = data.set_index(
        "timestamp"
    )

    data = data.resample(
        "h"
    ).mean()

    data["energy_kwh"] = (
        data["energy_kwh"]
        .interpolate(
            method="time"
        )
        .ffill()
        .bfill()
    )

    return data.reset_index()


def calculate_model_accuracy(
    dataframe: pd.DataFrame,
    model_name: str,
):
    data = prepare_dataframe(
        dataframe
    )

    if len(data) < 300:
        raise ValueError(
            "At least 300 hourly observations "
            "are required for accuracy tracking."
        )

    validation_size = min(
        168,
        len(data) // 5,
    )

    train = data.iloc[
        :-validation_size
    ].copy()

    validation = data.iloc[
        -validation_size:
    ].copy()

    actual = validation[
        "energy_kwh"
    ].tolist()

    if model_name.lower() == "prophet":

        model = ProphetForecastModel()

        _, forecast = model.predict(
            dataframe=train,
            periods=validation_size,
            frequency="h",
        )

        predicted = forecast[
            "predicted_value"
        ].tolist()

    elif model_name.lower() == "xgboost":

        model = XGBoostForecastModel()

        forecast = model.predict(
            dataframe=train,
            periods=validation_size,
        )

        predicted = [
            item["predicted_value"]
            for item in forecast
        ]

    else:

        raise ValueError(
            "Unsupported model. "
            "Use Prophet or XGBoost."
        )

    metrics = evaluate_predictions(
        actual=actual,
        predicted=predicted,
    )

    return {
        "model": model_name,
        "validation_points": validation_size,
        **metrics,
    }


def compare_model_accuracy(
    dataframe: pd.DataFrame,
):

    prophet_result = calculate_model_accuracy(
        dataframe,
        "Prophet",
    )

    xgboost_result = calculate_model_accuracy(
        dataframe,
        "XGBoost",
    )

    best_model = min(
        [
            prophet_result,
            xgboost_result,
        ],
        key=lambda item: item["rmse"],
    )

    return {
        "prophet": prophet_result,
        "xgboost": xgboost_result,
        "best_model": best_model["model"],
    }