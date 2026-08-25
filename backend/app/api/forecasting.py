from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import pandas as pd
from sqlalchemy import select

from app.ml.forecasting.comparison_service import (
    compare_models,
)

from app.models.operational_record import (
    OperationalRecord,
)

from app.core.dependencies import (
    get_current_user,
    get_database,
)
from app.ml.forecasting.forecast_service import (
    generate_forecast,
)
from app.models.user import User

from app.schemas.forecasting import (
    ForecastResponse,
    ModelComparisonResponse,
)


router = APIRouter(
    prefix="/forecasting",
    tags=["Forecasting"],
)


@router.get(
    "/device/{device_id}",
    response_model=ForecastResponse,
)
def forecast_device(
    device_id: int,
    horizon_hours: int = 24,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(
        get_database
    ),
):

    try:

        return generate_forecast(
            db=db,
            organization_id=current_user.organization_id,
            device_id=device_id,
            horizon_hours=horizon_hours,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

@router.get(
    "/device/{device_id}/compare",
    response_model=ModelComparisonResponse,
)
def compare_device_models(
    device_id: int,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(
        get_database
    ),
):
    records = db.scalars(
        select(OperationalRecord)
        .where(
            OperationalRecord.organization_id
            == current_user.organization_id,
            OperationalRecord.device_id
            == device_id,
        )
        .order_by(
            OperationalRecord.timestamp
        )
    ).all()

    if not records:
        raise HTTPException(
            status_code=404,
            detail="No operational data found for device",
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

    try:
        result = compare_models(
            dataframe
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    return {
        "device_id": device_id,
        **result,
    }