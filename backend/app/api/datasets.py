import pandas as pd

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.dependencies import (
    get_current_user,
    get_database,
)

from app.models.dataset import Dataset
from app.models.device import Device
from app.models.facility import Facility
from app.models.operational_record import OperationalRecord
from app.models.user import User

from app.schemas.dataset import DatasetResponse

from app.services.dataset_service import (
    validate_dataset,
)


router = APIRouter(
    prefix="/datasets",
    tags=["Datasets"],
)


# ============================================================
# UPLOAD DATASET
# ============================================================

@router.post(
    "/upload",
    response_model=DatasetResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_dataset(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database),
):

    # --------------------------------------------------------
    # FILE VALIDATION
    # --------------------------------------------------------

    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required",
        )

    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are supported",
        )

    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty",
        )

    # --------------------------------------------------------
    # READ + VALIDATE CSV
    # --------------------------------------------------------

    dataframe, validation_errors = validate_dataset(
        content
    )

    # --------------------------------------------------------
    # CREATE DATASET
    # --------------------------------------------------------

    dataset = Dataset(
        organization_id=current_user.organization_id,
        name=file.filename.rsplit(".", 1)[0],
        original_filename=file.filename,
        status="processing",
    )

    db.add(dataset)
    db.flush()

    dataset.total_rows = len(dataframe)

    # --------------------------------------------------------
    # COMPLETELY INVALID DATASET
    # --------------------------------------------------------

    if validation_errors and dataframe.empty:

        dataset.status = "failed"

        dataset.valid_rows = 0
        dataset.invalid_rows = 0
        dataset.quality_score = 0.0

        dataset.error_message = "; ".join(
            validation_errors
        )

        db.commit()
        db.refresh(dataset)

        return dataset

    # --------------------------------------------------------
    # INSERT OPERATIONAL RECORDS
    # --------------------------------------------------------

    valid_rows = 0
    invalid_rows = 0

    row_errors = []

    for index, row in dataframe.iterrows():

        # ----------------------------------------------------
        # FACILITY
        # ----------------------------------------------------

        facility = db.scalar(
            select(Facility).where(
                Facility.id == int(row["facility_id"]),
                Facility.organization_id
                == current_user.organization_id,
            )
        )

        if not facility:

            invalid_rows += 1

            row_errors.append(
                f"Row {index + 2}: "
                f"Facility {int(row['facility_id'])} "
                f"does not exist for your organization"
            )

            continue

        # ----------------------------------------------------
        # DEVICE
        # ----------------------------------------------------

        device = db.scalar(
            select(Device).where(
                Device.id == int(row["device_id"]),
                Device.facility_id
                == int(row["facility_id"]),
            )
        )

        if not device:

            invalid_rows += 1

            row_errors.append(
                f"Row {index + 2}: "
                f"Device {int(row['device_id'])} "
                f"does not belong to Facility "
                f"{int(row['facility_id'])}"
            )

            continue

        # ----------------------------------------------------
        # CREATE OPERATIONAL RECORD
        # ----------------------------------------------------

        record = OperationalRecord(
            dataset_id=dataset.id,

            organization_id=(
                current_user.organization_id
            ),

            facility_id=int(
                row["facility_id"]
            ),

            device_id=int(
                row["device_id"]
            ),

            timestamp=(
                row["timestamp"].to_pydatetime()
            ),

            energy_kwh=float(
                row["energy_kwh"]
            ),

            operational_load=(
                float(row["operational_load"])
                if (
                    "operational_load" in row
                    and pd.notna(
                        row["operational_load"]
                    )
                )
                else None
            ),

            temperature_c=(
                float(row["temperature_c"])
                if (
                    "temperature_c" in row
                    and pd.notna(
                        row["temperature_c"]
                    )
                )
                else None
            ),

            utilization_percent=(
                float(
                    row["utilization_percent"]
                )
                if (
                    "utilization_percent" in row
                    and pd.notna(
                        row["utilization_percent"]
                    )
                )
                else None
            ),

            status="valid",
        )

        db.add(record)

        valid_rows += 1

    # --------------------------------------------------------
    # DATASET STATISTICS
    # --------------------------------------------------------

    dataset.valid_rows = valid_rows
    dataset.invalid_rows = invalid_rows

    if dataset.total_rows > 0:

        dataset.quality_score = round(
            (
                valid_rows
                / dataset.total_rows
            ) * 100,
            2,
        )

    # --------------------------------------------------------
    # DATASET STATUS
    # --------------------------------------------------------

    if valid_rows == 0:

        dataset.status = "failed"

        dataset.error_message = (
            "; ".join(
                validation_errors
                + row_errors[:20]
            )
        )

    elif (
        invalid_rows > 0
        or validation_errors
    ):

        dataset.status = (
            "completed_with_warnings"
        )

        dataset.error_message = (
            "; ".join(
                validation_errors
                + row_errors[:20]
            )
        )

    else:

        dataset.status = "completed"

        dataset.error_message = None

    # --------------------------------------------------------
    # COMMIT
    # --------------------------------------------------------

    try:

        db.commit()

    except Exception:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to save operational "
                "records."
            ),
        )

    db.refresh(dataset)

    return dataset


# ============================================================
# LIST DATASETS
# ============================================================

@router.get(
    "",
    response_model=list[DatasetResponse],
)
def list_datasets(
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(
        get_database
    ),
):

    datasets = db.scalars(
        select(Dataset)
        .where(
            Dataset.organization_id
            == current_user.organization_id
        )
        .order_by(
            Dataset.id.desc()
        )
    ).all()

    return datasets


# ============================================================
# DELETE DATASET
# ============================================================

@router.delete(
    "/{dataset_id}",
)
def delete_dataset(
    dataset_id: int,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(
        get_database
    ),
):

    dataset = db.scalar(
        select(Dataset).where(
            Dataset.id == dataset_id,
            Dataset.organization_id
            == current_user.organization_id,
        )
    )

    if not dataset:

        raise HTTPException(
            status_code=404,
            detail="Dataset not found",
        )

    db.delete(dataset)

    db.commit()

    return {
        "message": (
            "Dataset deleted successfully"
        ),
        "dataset_id": dataset_id,
    }