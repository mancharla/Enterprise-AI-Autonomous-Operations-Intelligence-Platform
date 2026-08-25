import pandas as pd

from app.ml.forecasting.evaluation import (
    evaluate_predictions,
)
from app.ml.forecasting.model_selector import (
    select_best_model,
)
from app.ml.forecasting.prophet_model import (
    ProphetForecastModel,
)
from app.ml.forecasting.xgboost_model import (
    XGBoostForecastModel,
)


def compare_models(
    dataframe: pd.DataFrame,
):
    dataframe = dataframe.copy()

    dataframe["timestamp"] = pd.to_datetime(
        dataframe["timestamp"]
    )

    dataframe["energy_kwh"] = pd.to_numeric(
        dataframe["energy_kwh"],
        errors="coerce",
    )

    dataframe = dataframe.dropna(
        subset=[
            "timestamp",
            "energy_kwh",
        ]
    )

    dataframe = (
        dataframe
        .sort_values("timestamp")
        .groupby(
            "timestamp",
            as_index=False,
        )["energy_kwh"]
        .mean()
    )

    dataframe = dataframe.set_index(
        "timestamp"
    )

    dataframe = dataframe.resample(
        "h"
    ).mean()

    dataframe["energy_kwh"] = (
        dataframe["energy_kwh"]
        .interpolate(
            method="time"
        )
        .ffill()
        .bfill()
    )

    dataframe = dataframe.reset_index()

    if len(dataframe) < 300:
        raise ValueError(
            "At least 300 hourly observations "
            "are required for model comparison."
        )

    validation_size = min(
        168,
        len(dataframe) // 5,
    )

    train = dataframe.iloc[
        :-validation_size
    ].copy()

    validation = dataframe.iloc[
        -validation_size:
    ].copy()

    # --------------------------------
    # Prophet
    # --------------------------------

    prophet = ProphetForecastModel()

    prophet_historical, prophet_prediction = (
        prophet.predict(
            dataframe=train,
            periods=validation_size,
            frequency="h",
        )
    )

    actual_values = validation[
        "energy_kwh"
    ].tolist()

    prophet_predicted = prophet_prediction[
        "predicted_value"
    ].tolist()

    prophet_metrics = evaluate_predictions(
        actual=actual_values,
        predicted=prophet_predicted,
    )

    # --------------------------------
    # XGBoost
    # --------------------------------

    xgboost = XGBoostForecastModel()

    xgboost_prediction = xgboost.predict(
        dataframe=train,
        periods=validation_size,
    )

    xgboost_predicted = [
        item["predicted_value"]
        for item in xgboost_prediction
    ]

    xgboost_metrics = evaluate_predictions(
        actual=actual_values,
        predicted=xgboost_predicted,
    )

    # --------------------------------
    # Select best model
    # --------------------------------

    selection = select_best_model(
        prophet_metrics=prophet_metrics,
        xgboost_metrics=xgboost_metrics,
    )

    return {
        "validation_points": validation_size,
        "prophet": prophet_metrics,
        "xgboost": xgboost_metrics,
        "selected_model": selection[
            "selected_model"
        ],
    }