import numpy as np

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
)


def evaluate_predictions(
    actual,
    predicted,
):
    actual = np.asarray(actual, dtype=float)
    predicted = np.asarray(predicted, dtype=float)

    if len(actual) != len(predicted):
        raise ValueError(
            "Actual and predicted values must have "
            "the same length."
        )

    if len(actual) == 0:
        raise ValueError(
            "At least one prediction is required."
        )

    mae = mean_absolute_error(
        actual,
        predicted,
    )

    rmse = np.sqrt(
        mean_squared_error(
            actual,
            predicted,
        )
    )

    non_zero_mask = actual != 0

    if np.any(non_zero_mask):
        mape = np.mean(
            np.abs(
                (
                    actual[non_zero_mask]
                    - predicted[non_zero_mask]
                )
                / actual[non_zero_mask]
            )
        ) * 100
    else:
        mape = 0.0

    accuracy = max(
        0.0,
        100.0 - mape,
    )

    return {
        "mae": round(float(mae), 4),
        "rmse": round(float(rmse), 4),
        "mape": round(float(mape), 4),
        "accuracy_percent": round(
            float(accuracy),
            4,
        ),
    }