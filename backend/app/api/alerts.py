from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.alert import Alert
from app.schemas.alert import (
    AlertResponse,
    AlertSummary,
)
from app.services.alert_service import AlertService


router = APIRouter(
    prefix="/alerts",
    tags=["Operational Alerts"],
)


# ============================================================
# LIST ALL ALERTS
# ============================================================

@router.get(
    "",
    response_model=list[AlertResponse],
)
def list_alerts(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):

    organization_id = current_user.organization_id

    alerts = (
        db.query(Alert)
        .filter(
            Alert.organization_id == organization_id
        )
        .order_by(
            Alert.created_at.desc()
        )
        .all()
    )

    return alerts


# ============================================================
# ALERT SUMMARY
# ============================================================

@router.get(
    "/summary",
    response_model=AlertSummary,
)
def alert_summary(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):

    organization_id = current_user.organization_id

    return AlertService.get_summary(
        db=db,
        organization_id=organization_id,
    )


# ============================================================
# DEVICE ALERTS
# ============================================================

@router.get(
    "/device/{device_id}",
    response_model=list[AlertResponse],
)
def get_device_alerts(
    device_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):

    organization_id = current_user.organization_id

    alerts = (
        db.query(Alert)
        .filter(
            Alert.device_id == device_id,
            Alert.organization_id == organization_id,
        )
        .order_by(
            Alert.created_at.desc()
        )
        .all()
    )

    return alerts


# ============================================================
# GET SINGLE ALERT
# ============================================================

@router.get(
    "/{alert_id}",
    response_model=AlertResponse,
)
def get_alert(
    alert_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):

    organization_id = current_user.organization_id

    alert = (
        db.query(Alert)
        .filter(
            Alert.id == alert_id,
            Alert.organization_id == organization_id,
        )
        .first()
    )

    if not alert:
        raise HTTPException(
            status_code=404,
            detail="Alert not found",
        )

    return alert


# ============================================================
# ACKNOWLEDGE ALERT
# ============================================================

@router.put(
    "/{alert_id}/acknowledge",
    response_model=AlertResponse,
)
def acknowledge_alert(
    alert_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):

    organization_id = current_user.organization_id

    alert = (
        db.query(Alert)
        .filter(
            Alert.id == alert_id,
            Alert.organization_id == organization_id,
        )
        .first()
    )

    if not alert:
        raise HTTPException(
            status_code=404,
            detail="Alert not found",
        )

    if alert.status == "RESOLVED":
        raise HTTPException(
            status_code=400,
            detail="Resolved alert cannot be acknowledged",
        )

    return AlertService.acknowledge_alert(
        db,
        alert,
    )


# ============================================================
# RESOLVE ALERT
# ============================================================

@router.put(
    "/{alert_id}/resolve",
    response_model=AlertResponse,
)
def resolve_alert(
    alert_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):

    organization_id = current_user.organization_id

    alert = (
        db.query(Alert)
        .filter(
            Alert.id == alert_id,
            Alert.organization_id == organization_id,
        )
        .first()
    )

    if not alert:
        raise HTTPException(
            status_code=404,
            detail="Alert not found",
        )

    if alert.status == "RESOLVED":
        raise HTTPException(
            status_code=400,
            detail="Alert is already resolved",
        )

    return AlertService.resolve_alert(
        db,
        alert,
    )