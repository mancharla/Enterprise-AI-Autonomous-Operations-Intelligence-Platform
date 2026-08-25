import pandas as pd

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import (
    get_database,
)

from app.core.dependencies import (
    get_current_user,
)

from app.models.operational_record import (
    OperationalRecord,
)

from app.models.user import User

from app.schemas.root_cause import (
    RootCauseResponse,
)

from app.services.root_cause_service import (
    RootCauseService,
)


router = APIRouter(
    prefix="/root-cause",
    tags=["Root Cause Analysis"],
)


@router.get(
    "/device/{device_id}",
    response_model=RootCauseResponse,
)
def analyze_root_cause(
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
            detail=(
                "No operational data found "
                "for this device"
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

    service = RootCauseService()

    try:

        return service.analyze(
            dataframe
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )