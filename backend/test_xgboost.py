import pandas as pd

from app.ml.forecasting.xgboost_model import (
    XGBoostForecastModel,
)


df = pd.read_csv(
    "../data/operational_data.csv"
)

df = df[
    df["device_id"] == 1
].copy()

model = XGBoostForecastModel()

forecast = model.predict(
    dataframe=df[
        [
            "timestamp",
            "energy_kwh",
        ]
    ],
    periods=24,
)

print(
    "\nXGBoost Forecast\n"
)

for item in forecast[:5]:
    print(item)