from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user

from app.schemas.streaming import (
    StreamEventCreate,
    StreamEventResponse,
)

from app.services.streaming_service import (
    StreamingService,
)

from app.services.alert_service import (
    AlertService,
)

from app.services.websocket_manager import (
    websocket_manager,
)

from app.models.device import Device


router = APIRouter(
    prefix="/stream",
    tags=["Real-Time Streaming"],
)


@router.post(
    "/events",
    response_model=StreamEventResponse,
)
async def ingest_event(
    event: StreamEventCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):

    # ======================================================
    # 1. ORGANIZATION SECURITY
    # ======================================================

    organization_id = (
        current_user.organization_id
    )

    # JWT organization is authoritative.
    event.organization_id = organization_id

    # ======================================================
    # 2. PROCESS STREAMING EVENT
    # ======================================================

    result = StreamingService.process_event(
        event
    )

    # ======================================================
    # 3. CHECK ANOMALY
    # ======================================================

    anomaly = result.get(
        "anomaly",
        {},
    )

    is_anomaly = anomaly.get(
        "is_anomaly",
        False,
    )

    severity = anomaly.get(
        "severity",
        "LOW",
    )

    alert_data = None

    # ======================================================
    # 4. CREATE DATABASE ALERT
    # ======================================================

    if is_anomaly and severity in {
        "CRITICAL",
        "HIGH",
    }:

        device = (
            db.query(Device)
            .filter(
                Device.id
                == event.device_id,
            )
            .first()
        )

        if device:

            reasons = anomaly.get(
                "reasons",
                [],
            )

            message = (
                "Real-time operational anomaly detected."
            )

            if reasons:

                message += (
                    " "
                    + " ".join(reasons)
                )

            alert = AlertService.create_alert(
                db=db,
                organization_id=organization_id,
                facility_id=device.facility_id,
                device_id=event.device_id,
                alert_type="REAL_TIME_ANOMALY",
                severity=severity,
                message=message,
                value=event.energy_kwh,
                threshold=120.0,
            )

            alert_data = {
                "id": alert.id,

                "organization_id":
                    alert.organization_id,

                "facility_id":
                    alert.facility_id,

                "device_id":
                    alert.device_id,

                "alert_type":
                    alert.alert_type,

                "severity":
                    alert.severity,

                "message":
                    alert.message,

                "value":
                    alert.value,

                "threshold":
                    alert.threshold,

                "status":
                    alert.status,

                "created_at":
                    alert.created_at.isoformat(),
            }

    # ======================================================
    # 5. ADD ALERT TO RESPONSE
    # ======================================================

    result["alert"] = alert_data

    # ======================================================
    # 6. BROADCAST OPERATIONAL EVENT
    # ======================================================

    await websocket_manager.broadcast(
        message={
            "event":
                "operational_event",

            "data":
                result,
        },

        organization_id=
            organization_id,
    )

    # ======================================================
    # 7. BROADCAST ALERT
    # ======================================================

    if alert_data:

        await websocket_manager.broadcast(
            message={
                "event":
                    "operational_alert",

                "data":
                    alert_data,
            },

            organization_id=
                organization_id,
        )

    # ======================================================
    # 8. RETURN
    # ======================================================

    return result