def select_best_model(
    prophet_metrics: dict,
    xgboost_metrics: dict,
):

    candidates = [
        {
            "model": "Prophet",
            **prophet_metrics,
        },
        {
            "model": "XGBoost",
            **xgboost_metrics,
        },
    ]

    best = min(
        candidates,
        key=lambda item: (
            item["rmse"],
            item["mae"],
        ),
    )

    return {
        "selected_model": best["model"],
        "selection_metric": "RMSE",
        "models": candidates,
    }