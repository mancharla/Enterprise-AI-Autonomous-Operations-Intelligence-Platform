from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_database, require_roles
from app.models.device import Device
from app.models.facility import Facility
from app.models.user import User
from app.schemas.device import (
    DeviceCreate,
    DeviceResponse,
    DeviceUpdate,
)


router = APIRouter(
    prefix="/devices",
    tags=["Devices"],
)


@router.post(
    "",
    response_model=DeviceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_device(
    request: DeviceCreate,
    current_user: User = Depends(
        require_roles("super_admin", "operations_manager")
    ),
    db: Session = Depends(get_database),
):
    facility = db.scalar(
        select(Facility).where(
            Facility.id == request.facility_id,
            Facility.organization_id == current_user.organization_id,
        )
    )

    if not facility:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Facility not found in your organization",
        )

    device = Device(
        facility_id=request.facility_id,
        name=request.name,
        device_type=request.device_type,
        rated_capacity_kw=request.rated_capacity_kw,
        status=request.status,
    )

    db.add(device)
    db.commit()
    db.refresh(device)

    return device


@router.get(
    "",
    response_model=list[DeviceResponse],
)
def list_devices(
    facility_id: int | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database),
):
    query = (
        select(Device)
        .join(Facility)
        .where(
            Facility.organization_id == current_user.organization_id
        )
    )

    if facility_id is not None:
        query = query.where(
            Device.facility_id == facility_id
        )

    devices = db.scalars(
        query.order_by(Device.id)
    ).all()

    return devices


@router.get(
    "/{device_id}",
    response_model=DeviceResponse,
)
def get_device(
    device_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database),
):
    device = db.scalar(
        select(Device)
        .join(Facility)
        .where(
            Device.id == device_id,
            Facility.organization_id == current_user.organization_id,
        )
    )

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found",
        )

    return device


@router.put(
    "/{device_id}",
    response_model=DeviceResponse,
)
def update_device(
    device_id: int,
    request: DeviceUpdate,
    current_user: User = Depends(
        require_roles("super_admin", "operations_manager")
    ),
    db: Session = Depends(get_database),
):
    device = db.scalar(
        select(Device)
        .join(Facility)
        .where(
            Device.id == device_id,
            Facility.organization_id == current_user.organization_id,
        )
    )

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found",
        )

    if request.name is not None:
        device.name = request.name

    if request.device_type is not None:
        device.device_type = request.device_type

    if request.rated_capacity_kw is not None:
        device.rated_capacity_kw = request.rated_capacity_kw

    if request.status is not None:
        device.status = request.status

    db.commit()
    db.refresh(device)

    return device


@router.delete(
    "/{device_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_device(
    device_id: int,
    current_user: User = Depends(
        require_roles("super_admin", "operations_manager")
    ),
    db: Session = Depends(get_database),
):
    device = db.scalar(
        select(Device)
        .join(Facility)
        .where(
            Device.id == device_id,
            Facility.organization_id == current_user.organization_id,
        )
    )

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found",
        )

    db.delete(device)
    db.commit()