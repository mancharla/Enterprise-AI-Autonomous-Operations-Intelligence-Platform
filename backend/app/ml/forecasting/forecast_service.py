import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ml.forecasting.prophet_model import (
    ProphetForecastModel,
)
from app.models.device import Device
from app.models.facility import Facility
from app.models.operational_record import (
    OperationalRecord,
)


ALLOWED_HORIZONS = {
    24,
    24 * 7,
    24 * 30,
    24 * 90,
}


def generate_forecast(
    db: Session,
    organization_id: int,
    device_id: int,
    horizon_hours: int,
):

    if horizon_hours not in ALLOWED_HORIZONS:
        raise ValueError(
            "Horizon must be one of: "
            "24, 168, 720, 2160 hours."
        )

    device = db.scalar(
        select(Device)
        .join(Facility)
        .where(
            Device.id == device_id,
            Facility.organization_id == organization_id,
        )
    )

    if not device:
        raise ValueError(
            "Device not found in your organization."
        )

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

    if len(records) < 10:
        raise ValueError(
            "At least 10 historical records "
            "are required for forecasting."
        )

    dataframe = pd.DataFrame(
        [
            {
                "timestamp": record.timestamp,
                "energy_kwh": record.energy_kwh,
            }
            for record in records
        ]
    )

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

    dataframe = dataframe.sort_values(
        "timestamp"
    )

    # Remove duplicate timestamps.
    dataframe = (
        dataframe
        .groupby(
            "timestamp",
            as_index=False,
        )["energy_kwh"]
        .mean()
    )

    # Reindex to hourly frequency.
    dataframe = dataframe.set_index(
        "timestamp"
    )

    dataframe = dataframe.resample(
        "h"
    ).mean()

    # Fill missing observations using interpolation.
    dataframe["energy_kwh"] = (
        dataframe["energy_kwh"]
        .interpolate(
            method="time"
        )
        .ffill()
        .bfill()
    )

    dataframe = dataframe.reset_index()

    if len(dataframe) < 10:
        raise ValueError(
            "Not enough usable historical data "
            "after preprocessing."
        )

    model = ProphetForecastModel()

    historical, forecast = model.predict(
        dataframe=dataframe,
        periods=horizon_hours,
        frequency="h",
    )

    forecast_points = []

    for row in forecast.itertuples():

        forecast_points.append(
            {
                "timestamp": row.timestamp,
                "predicted_value": round(
                    max(float(row.predicted_value), 0),
                    2,
                ),
                "lower_bound": round(
                    max(float(row.lower_bound), 0),
                    2,
                ),
                "upper_bound": round(
                    max(float(row.upper_bound), 0),
                    2,
                ),
            }
        )

    return {
        "device_id": device_id,
        "horizon_hours": horizon_hours,
        "model": "Prophet",
        "historical_points": len(historical),
        "forecast_points": len(forecast_points),
        "forecast": forecast_points,
    }