import pandas as pd

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_database
from app.core.dependencies import (
    get_current_user,
)

from app.models.operational_record import (
    OperationalRecord,
)

from app.models.user import User

from app.schemas.anomalies import (
    AnomalyItem,
    AnomalySummary,
)

from app.services.anomaly_service import (
    AnomalyService,
)


router = APIRouter(
    prefix="/anomalies",
    tags=["Anomalies"],
)


def get_device_dataframe(
    device_id: int,
    current_user: User,
    db: Session,
) -> pd.DataFrame:

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
            detail=(
                "No operational data found "
                "for this device."
            ),
        )

    dataframe = pd.DataFrame(
        [
            {
                "timestamp":
                    record.timestamp,

                "energy_kwh":
                    record.energy_kwh,

                "operational_load":
                    record.operational_load,

                "temperature_c":
                    record.temperature_c,

                "utilization_percent":
                    record.utilization_percent,
            }
            for record in records
        ]
    )

    # -----------------------------------------
    # Clean numeric values
    # -----------------------------------------

    numeric_columns = [
        "energy_kwh",
        "operational_load",
        "temperature_c",
        "utilization_percent",
    ]

    for column in numeric_columns:

        dataframe[column] = pd.to_numeric(
            dataframe[column],
            errors="coerce",
        )

    dataframe = (
        dataframe
        .replace(
            [float("inf"), float("-inf")],
            pd.NA,
        )
        .dropna(
            subset=["timestamp"]
        )
        .sort_values(
            "timestamp"
        )
        .reset_index(drop=True)
    )

    return dataframe


@router.get(
    "/device/{device_id}",
    response_model=list[AnomalyItem],
)
def detect_device_anomalies(
    device_id: int,

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(
        get_database
    ),
):

    dataframe = get_device_dataframe(
        device_id,
        current_user,
        db,
    )

    service = AnomalyService()

    try:

        anomalies = service.analyze(
            dataframe
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    # -----------------------------------------
    # Return anomalies only
    # -----------------------------------------

    anomalies = anomalies[
        anomalies["is_anomaly"] == True
    ].copy()

    return [
        {
            "timestamp":
                row.timestamp,

            "energy_kwh":
                float(row.energy_kwh),

            "operational_load":
                float(row.operational_load),

            "temperature_c":
                float(row.temperature_c),

            "utilization_percent":
                float(row.utilization_percent),

            "anomaly_score":
                round(
                    float(
                        row.anomaly_score
                    ),
                    4,
                ),

            "severity":
                row.severity,

            "anomaly_type":
                row.anomaly_type,
        }

        for row in anomalies.itertuples()
    ]


@router.get(
    "/device/{device_id}/summary",
    response_model=AnomalySummary,
)
def anomaly_summary(
    device_id: int,

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(
        get_database
    ),
):

    dataframe = get_device_dataframe(
        device_id,
        current_user,
        db,
    )

    service = AnomalyService()

    try:

        return service.summary(
            dataframe
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )