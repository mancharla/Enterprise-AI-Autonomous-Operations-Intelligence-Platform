from typing import Optional

import pandas as pd

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
)

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_database
from app.core.dependencies import get_current_user

from app.models.operational_record import OperationalRecord
from app.models.autonomous_action import AutonomousAction
from app.models.user import User

from app.pipelines.autonomous_engine import (
    AutonomousOperationsEngine,
)


router = APIRouter(
    prefix="/autonomous",
    tags=["Autonomous Operations"],
)


# =========================================================
# 1. ANALYZE DEVICE
# =========================================================

@router.get(
    "/device/{device_id}"
)
def analyze_device(
    device_id: int,
    forecast_horizon: int = 24,

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
                "timestamp": record.timestamp,
                "energy_kwh": record.energy_kwh,
                "operational_load": record.operational_load,
                "temperature_c": record.temperature_c,
                "utilization_percent":
                    record.utilization_percent,
            }

            for record in records
        ]
    )

    try:

        engine = AutonomousOperationsEngine()

        return engine.analyze(
            dataframe=dataframe,
            db=db,
            organization_id=
                current_user.organization_id,
            device_id=device_id,
            forecast_horizon=
                forecast_horizon,
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
                "Autonomous operations analysis "
                f"failed: {str(exc)}"
            ),
        )


# =========================================================
# 2. GET ALL AUTONOMOUS ACTIONS
# =========================================================

@router.get(
    "/actions"
)
def get_autonomous_actions(

    device_id: Optional[int] = Query(
        default=None
    ),

    status: Optional[str] = Query(
        default=None
    ),

    priority: Optional[str] = Query(
        default=None
    ),

    limit: int = Query(
        default=50,
        ge=1,
        le=200,
    ),

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(
        get_database
    ),
):

    query = (
        select(AutonomousAction)
        .where(
            AutonomousAction.organization_id
            == current_user.organization_id
        )
        .order_by(
            AutonomousAction.created_at.desc()
        )
    )

    # Optional device filter
    if device_id is not None:

        query = query.where(
            AutonomousAction.device_id
            == device_id
        )

    # Optional status filter
    if status is not None:

        query = query.where(
            AutonomousAction.status
            == status
        )

    # Optional priority filter
    if priority is not None:

        query = query.where(
            AutonomousAction.priority
            == priority
        )

    query = query.limit(limit)

    actions = db.scalars(query).all()

    return {
        "status": "success",
        "count": len(actions),

        "actions": [
            {
                "id": action.id,

                "organization_id":
                    action.organization_id,

                "device_id":
                    action.device_id,

                "action":
                    action.action,

                "priority":
                    action.priority,

                "risk_level":
                    action.risk_level,

                "reason":
                    action.reason,

                "expected_benefit":
                    action.expected_benefit,

                "confidence":
                    action.confidence,

                "estimated_savings_percent":
                    action.estimated_savings_percent,

                "status":
                    action.status,

                "signals":
                    action.signals,

                "created_at":
                    action.created_at.isoformat()
                    if action.created_at
                    else None,
            }

            for action in actions
        ],
    }


# =========================================================
# 3. GET SINGLE AUTONOMOUS ACTION
# =========================================================

@router.get(
    "/actions/{action_id}"
)
def get_autonomous_action(

    action_id: int,

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(
        get_database
    ),
):

    action = db.scalar(
        select(AutonomousAction)
        .where(
            AutonomousAction.id
            == action_id,

            AutonomousAction.organization_id
            == current_user.organization_id,
        )
    )

    if not action:

        raise HTTPException(
            status_code=404,
            detail="Autonomous action not found.",
        )

    return {
        "id": action.id,

        "organization_id":
            action.organization_id,

        "device_id":
            action.device_id,

        "action":
            action.action,

        "priority":
            action.priority,

        "risk_level":
            action.risk_level,

        "reason":
            action.reason,

        "expected_benefit":
            action.expected_benefit,

        "confidence":
            action.confidence,

        "estimated_savings_percent":
            action.estimated_savings_percent,

        "status":
            action.status,

        "signals":
            action.signals,

        "created_at":
            action.created_at.isoformat()
            if action.created_at
            else None,
    }


# =========================================================
# 4. UPDATE ACTION STATUS
# =========================================================

@router.patch(
    "/actions/{action_id}/status"
)
def update_autonomous_action_status(

    action_id: int,

    status: str,

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(
        get_database
    ),
):

    allowed_statuses = {
        "RECOMMENDED",
        "APPROVED",
        "EXECUTING",
        "COMPLETED",
        "REJECTED",
        "CANCELLED",
    }

    status = status.upper()

    if status not in allowed_statuses:

        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid status. Allowed values: "
                + ", ".join(
                    sorted(allowed_statuses)
                )
            ),
        )

    action = db.scalar(
        select(AutonomousAction)
        .where(
            AutonomousAction.id
            == action_id,

            AutonomousAction.organization_id
            == current_user.organization_id,
        )
    )

    if not action:

        raise HTTPException(
            status_code=404,
            detail="Autonomous action not found.",
        )

    action.status = status

    db.commit()
    db.refresh(action)

    return {
        "status": "success",
        "message": "Autonomous action status updated.",

        "action": {
            "id": action.id,
            "device_id": action.device_id,
            "action": action.action,
            "priority": action.priority,
            "risk_level": action.risk_level,
            "status": action.status,
            "created_at":
                action.created_at.isoformat()
                if action.created_at
                else None,
        },
    }