import pandas as pd

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.dependencies import (
    get_current_user,
    get_database,
)

from app.models.operational_record import (
    OperationalRecord,
)

from app.models.user import User

from app.ml.forecasting.accuracy_service import (
    calculate_model_accuracy,
    compare_model_accuracy,
)


router = APIRouter(
    prefix="/forecasting/accuracy",
    tags=["Forecast Accuracy"],
)


# ============================================================
# Helper
# ============================================================

def get_device_dataframe(
    db: Session,
    organization_id: int,
    device_id: int,
) -> pd.DataFrame:

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
                "timestamp": record.timestamp,
                "energy_kwh": record.energy_kwh,
            }
            for record in records
        ]
    )

    # --------------------------------------------------------
    # Data cleaning
    # --------------------------------------------------------

    dataframe["timestamp"] = pd.to_datetime(
        dataframe["timestamp"],
        errors="coerce",
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

    # --------------------------------------------------------
    # Convert data to hourly frequency
    # --------------------------------------------------------

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

    if len(dataframe) < 10:
        raise HTTPException(
            status_code=400,
            detail=(
                "At least 10 usable hourly observations "
                "are required for accuracy analysis."
            ),
        )

    return dataframe


# ============================================================
# Individual Model Accuracy
# ============================================================

@router.get(
    "/device/{device_id}",
)
def device_accuracy(
    device_id: int,

    model: str = "Prophet",

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(
        get_database
    ),
):

    dataframe = get_device_dataframe(
        db=db,
        organization_id=current_user.organization_id,
        device_id=device_id,
    )

    # --------------------------------------------------------
    # Validate model
    # --------------------------------------------------------

    model = model.strip()

    supported_models = {
        "Prophet",
        "XGBoost",
    }

    normalized_models = {
        item.lower(): item
        for item in supported_models
    }

    normalized_model = normalized_models.get(
        model.lower()
    )

    if normalized_model is None:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported model. "
                "Supported models: Prophet, XGBoost."
            ),
        )

    try:

        # IMPORTANT:
        # Pass arguments positionally.
        #
        # This avoids the error:
        # calculate_model_accuracy()
        # got an unexpected keyword argument 'model'

        result = calculate_model_accuracy(
            dataframe,
            normalized_model,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to calculate model accuracy: "
                f"{str(exc)}"
            ),
        )

    return {
        "device_id": device_id,
        "model": normalized_model,
        **result,
    }


# ============================================================
# Compare Model Accuracy
# ============================================================

@router.get(
    "/device/{device_id}/compare",
)
def compare_accuracy(
    device_id: int,

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(
        get_database
    ),
):

    dataframe = get_device_dataframe(
        db=db,
        organization_id=current_user.organization_id,
        device_id=device_id,
    )

    try:

        result = compare_model_accuracy(
            dataframe
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to compare model accuracy: "
                f"{str(exc)}"
            ),
        )

    return {
        "device_id": device_id,
        **result,
    }