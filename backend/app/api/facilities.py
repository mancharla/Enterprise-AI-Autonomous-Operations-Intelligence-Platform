from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_database, require_roles
from app.models.facility import Facility
from app.models.user import User
from app.schemas.facility import (
    FacilityCreate,
    FacilityResponse,
    FacilityUpdate,
)


router = APIRouter(
    prefix="/facilities",
    tags=["Facilities"],
)


@router.post(
    "",
    response_model=FacilityResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_facility(
    request: FacilityCreate,
    current_user: User = Depends(
        require_roles("super_admin", "operations_manager")
    ),
    db: Session = Depends(get_database),
):
    existing = db.scalar(
        select(Facility).where(
            Facility.organization_id == current_user.organization_id,
            Facility.code == request.code,
        )
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Facility code already exists in this organization",
        )

    facility = Facility(
        organization_id=current_user.organization_id,
        name=request.name,
        code=request.code,
        region=request.region,
        capacity_kw=request.capacity_kw,
    )

    db.add(facility)
    db.commit()
    db.refresh(facility)

    return facility


@router.get(
    "",
    response_model=list[FacilityResponse],
)
def list_facilities(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database),
):
    facilities = db.scalars(
        select(Facility)
        .where(
            Facility.organization_id == current_user.organization_id
        )
        .order_by(Facility.id)
    ).all()

    return facilities


@router.get(
    "/{facility_id}",
    response_model=FacilityResponse,
)
def get_facility(
    facility_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database),
):
    facility = db.scalar(
        select(Facility).where(
            Facility.id == facility_id,
            Facility.organization_id == current_user.organization_id,
        )
    )

    if not facility:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Facility not found",
        )

    return facility


@router.put(
    "/{facility_id}",
    response_model=FacilityResponse,
)
def update_facility(
    facility_id: int,
    request: FacilityUpdate,
    current_user: User = Depends(
        require_roles("super_admin", "operations_manager")
    ),
    db: Session = Depends(get_database),
):
    facility = db.scalar(
        select(Facility).where(
            Facility.id == facility_id,
            Facility.organization_id == current_user.organization_id,
        )
    )

    if not facility:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Facility not found",
        )

    if request.name is not None:
        facility.name = request.name

    if request.region is not None:
        facility.region = request.region

    if request.capacity_kw is not None:
        facility.capacity_kw = request.capacity_kw

    db.commit()
    db.refresh(facility)

    return facility


@router.delete(
    "/{facility_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_facility(
    facility_id: int,
    current_user: User = Depends(
        require_roles("super_admin", "operations_manager")
    ),
    db: Session = Depends(get_database),
):
    facility = db.scalar(
        select(Facility).where(
            Facility.id == facility_id,
            Facility.organization_id == current_user.organization_id,
        )
    )

    if not facility:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Facility not found",
        )

    db.delete(facility)
    db.commit()