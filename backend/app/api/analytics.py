import pandas as pd

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from app.schemas.analytics import (
    EnergyTrendResponse,
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

from app.models.device import Device
from app.models.facility import Facility
from app.models.user import User

from app.schemas.analytics import (
    AnalyticsOverview,
    FacilityAnalytics,
    DeviceAnalytics,
)

from app.services.analytics_service import (
    AnalyticsService,
)


router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


# ============================================================
# ORGANIZATION DATAFRAME
# ============================================================

def get_organization_dataframe(
    current_user: User,
    db: Session,
):

    records = db.scalars(
        select(OperationalRecord)
        .where(
            OperationalRecord.organization_id
            == current_user.organization_id
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
                "for your organization."
            ),
        )

    return pd.DataFrame(
        [
            {
                "timestamp":
                    record.timestamp,

                "device_id":
                    record.device_id,

                "facility_id":
                    record.facility_id,

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


# ==========================================================
# Helper: Organization Data
# ==========================================================

def get_organization_records(
    current_user: User,
    db: Session,
):

    records = db.scalars(
        select(OperationalRecord)
        .where(
            OperationalRecord.organization_id
            == current_user.organization_id
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
                "for your organization."
            ),
        )

    return records


# ==========================================================
# Helper: DataFrame
# ==========================================================

def records_to_dataframe(
    records,
) -> pd.DataFrame:

    return pd.DataFrame(
        [
            {
                "timestamp":
                    record.timestamp,

                "device_id":
                    record.device_id,

                "facility_id":
                    record.facility_id,

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


# ==========================================================
# OVERVIEW
# ==========================================================

@router.get(
    "/overview",
    response_model=AnalyticsOverview,
)
def analytics_overview(

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(
        get_database
    ),
):

    records = get_organization_records(
        current_user,
        db,
    )

    dataframe = records_to_dataframe(
        records
    )

    service = AnalyticsService()

    try:

        return service.analyze(
            dataframe
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


# ==========================================================
# FACILITY ANALYTICS
# ==========================================================

@router.get(
    "/facility/{facility_id}",
    response_model=FacilityAnalytics,
)
def facility_analytics(

    facility_id: int,

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(
        get_database
    ),
):

    facility = db.scalar(
        select(Facility)
        .where(
            Facility.id
            == facility_id,

            Facility.organization_id
            == current_user.organization_id,
        )
    )

    if not facility:

        raise HTTPException(
            status_code=404,
            detail="Facility not found.",
        )

    records = db.scalars(
        select(OperationalRecord)
        .where(
            OperationalRecord.organization_id
            == current_user.organization_id,

            OperationalRecord.facility_id
            == facility_id,
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
                "for this facility."
            ),
        )

    dataframe = records_to_dataframe(
        records
    )

    total_energy = float(
        dataframe[
            "energy_kwh"
        ].sum()
    )

    average_energy = float(
        dataframe[
            "energy_kwh"
        ].mean()
    )

    peak_energy = float(
        dataframe[
            "energy_kwh"
        ].max()
    )

    device_count = int(
        dataframe[
            "device_id"
        ].nunique()
    )

    record_count = len(
        dataframe
    )

    return {
        "facility_id":
            facility.id,

        "facility_name":
            facility.name,

        "total_energy_kwh":
            round(
                total_energy,
                2,
            ),

        "average_energy_kwh":
            round(
                average_energy,
                2,
            ),

        "peak_energy_kwh":
            round(
                peak_energy,
                2,
            ),

        "device_count":
            device_count,

        "record_count":
            record_count,
    }


# ==========================================================
# DEVICE ANALYTICS
# ==========================================================

@router.get(
    "/device/{device_id}",
    response_model=DeviceAnalytics,
)
def device_analytics(

    device_id: int,

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(
        get_database
    ),
):

    device = db.scalar(
        select(Device)
        .join(
            Facility,
            Device.facility_id
            == Facility.id,
        )
        .where(
            Device.id
            == device_id,

            Facility.organization_id
            == current_user.organization_id,
        )
    )

    if not device:

        raise HTTPException(
            status_code=404,
            detail="Device not found.",
        )

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

    dataframe = records_to_dataframe(
        records
    )

    total_energy = float(
        dataframe[
            "energy_kwh"
        ].sum()
    )

    average_energy = float(
        dataframe[
            "energy_kwh"
        ].mean()
    )

    peak_energy = float(
        dataframe[
            "energy_kwh"
        ].max()
    )

    return {

        "device_id":
            device.id,

        "device_name":
            device.name,

        "facility_id":
            device.facility_id,

        "total_energy_kwh":
            round(
                total_energy,
                2,
            ),

        "average_energy_kwh":
            round(
                average_energy,
                2,
            ),

        "peak_energy_kwh":
            round(
                peak_energy,
                2,
            ),

        "record_count":
            len(dataframe),
    }


# ==========================================================
# COMPARISON
# ==========================================================

@router.get(
    "/comparison",
)
def analytics_comparison(

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(
        get_database
    ),
):

    records = get_organization_records(
        current_user,
        db,
    )

    dataframe = records_to_dataframe(
        records
    )

    # ======================================================
    # Facilities
    # ======================================================

    facility_ids = (
        dataframe[
            "facility_id"
        ]
        .dropna()
        .unique()
        .tolist()
    )

    facilities = db.scalars(
        select(Facility)
        .where(
            Facility.organization_id
            == current_user.organization_id,

            Facility.id.in_(
                facility_ids
            ),
        )
    ).all()

    facility_names = {
        facility.id:
            facility.name

        for facility in facilities
    }

    facility_group = (
        dataframe
        .groupby(
            "facility_id"
        )
        .agg(
            total_energy_kwh=(
                "energy_kwh",
                "sum",
            ),

            average_energy_kwh=(
                "energy_kwh",
                "mean",
            ),

            device_count=(
                "device_id",
                "nunique",
            ),

            record_count=(
                "energy_kwh",
                "count",
            ),
        )
        .reset_index()
    )

    facility_comparison = []

    for row in facility_group.itertuples():

        facility_comparison.append(
            {
                "facility_id":
                    int(
                        row.facility_id
                    ),

                "facility_name":
                    facility_names.get(
                        int(
                            row.facility_id
                        ),
                        "Unknown Facility",
                    ),

                "total_energy_kwh":
                    round(
                        float(
                            row.total_energy_kwh
                        ),
                        2,
                    ),

                "average_energy_kwh":
                    round(
                        float(
                            row.average_energy_kwh
                        ),
                        2,
                    ),

                "device_count":
                    int(
                        row.device_count
                    ),

                "record_count":
                    int(
                        row.record_count
                    ),
            }
        )

    facility_comparison.sort(
        key=lambda item:
            item[
                "total_energy_kwh"
            ],

        reverse=True,
    )

    # ======================================================
    # Devices
    # ======================================================

    device_ids = (
        dataframe[
            "device_id"
        ]
        .dropna()
        .unique()
        .tolist()
    )

    devices = db.scalars(
        select(Device)
        .join(
            Facility,
            Device.facility_id
            == Facility.id,
        )
        .where(
            Facility.organization_id
            == current_user.organization_id,

            Device.id.in_(
                device_ids
            ),
        )
    ).all()

    device_info = {

        device.id: {
            "name":
                device.name,

            "facility_id":
                device.facility_id,
        }

        for device in devices
    }

    device_group = (
        dataframe
        .groupby(
            "device_id"
        )
        .agg(
            total_energy_kwh=(
                "energy_kwh",
                "sum",
            ),

            average_energy_kwh=(
                "energy_kwh",
                "mean",
            ),

            record_count=(
                "energy_kwh",
                "count",
            ),
        )
        .reset_index()
    )

    device_comparison = []

    for row in device_group.itertuples():

        current_device_id = int(
            row.device_id
        )

        info = device_info.get(
            current_device_id,
            {},
        )

        device_comparison.append(
            {
                "device_id":
                    current_device_id,

                "device_name":
                    info.get(
                        "name",
                        "Unknown Device",
                    ),

                "facility_id":
                    info.get(
                        "facility_id"
                    ),

                "total_energy_kwh":
                    round(
                        float(
                            row.total_energy_kwh
                        ),
                        2,
                    ),

                "average_energy_kwh":
                    round(
                        float(
                            row.average_energy_kwh
                        ),
                        2,
                    ),

                "record_count":
                    int(
                        row.record_count
                    ),
            }
        )

    device_comparison.sort(
        key=lambda item:
            item[
                "total_energy_kwh"
            ],

        reverse=True,
    )

    return {
        "facilities":
            facility_comparison,

        "devices":
            device_comparison,
    }


# ==========================================================
# ENERGY TREND
# ==========================================================

@router.get(
    "/trend",
)
def analytics_trend(

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(
        get_database
    ),
):

    records = get_organization_records(
        current_user,
        db,
    )

    dataframe = records_to_dataframe(
        records
    )

    if dataframe.empty:
        raise HTTPException(
            status_code=404,
            detail="No operational data found.",
        )

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

    dataframe = dataframe.sort_values(
        "timestamp"
    )

    return [
        {
            "timestamp":
                row.timestamp.isoformat(),

            "energy_kwh":
                round(
                    float(row.energy_kwh),
                    2,
                ),
        }

        for row in dataframe.itertuples()
    ]

# ==========================================================
# RISK DISTRIBUTION
# ==========================================================

@router.get(
    "/risk-distribution",
)
def analytics_risk_distribution(

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(
        get_database
    ),
):

    records = get_organization_records(
        current_user,
        db,
    )

    dataframe = records_to_dataframe(
        records
    )

    service = AnalyticsService()

    try:

        anomaly_analysis = (
            service._get_anomaly_analysis(
                dataframe
            )
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    distribution = (
        anomaly_analysis[
            "severity_distribution"
        ]
    )

    return {
        "low":
            int(
                distribution["low"]
            ),

        "medium":
            int(
                distribution["medium"]
            ),

        "high":
            int(
                distribution["high"]
            ),

        "critical":
            int(
                distribution["critical"]
            ),
    }

@router.get(
    "/trend",
    response_model=EnergyTrendResponse,
)
def analytics_trend(
    granularity: str = "hour",

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(
        get_database
    ),
):

    dataframe = get_organization_dataframe(
        current_user,
        db,
    )

    service = AnalyticsService()

    try:

        return service.energy_trend(
            dataframe=dataframe,
            granularity=granularity,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

@router.get(
"/device/{device_id}/trend",
response_model=EnergyTrendResponse,
)

def device_energy_trend(
    device_id: int,

    granularity: str = "hour",

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
            }
            for record in records
        ]
    )

    service = AnalyticsService()

    try:

        return service.energy_trend(
            dataframe=dataframe,
            granularity=granularity,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )