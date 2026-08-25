from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_database
from app.models.organization import Organization
from app.models.user import User
from app.schemas.organization import OrganizationResponse
from app.schemas.user import UserResponse


router = APIRouter(
    prefix="/organizations",
    tags=["Organizations"],
)


@router.get(
    "/me",
    response_model=OrganizationResponse,
)
def get_my_organization(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database),
):
    organization = db.get(
        Organization,
        current_user.organization_id,
    )

    return organization


@router.get(
    "/users",
    response_model=list[UserResponse],
)
def get_organization_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database),
):
    users = db.scalars(
        select(User)
        .where(
            User.organization_id == current_user.organization_id
        )
        .order_by(User.id)
    ).all()

    return users