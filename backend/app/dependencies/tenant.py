from fastapi import Depends, HTTPException, status

from app.core.dependencies import get_current_user


def get_current_organization(
    current_user=Depends(get_current_user),
):
    organization_id = getattr(
        current_user,
        "organization_id",
        None,
    )

    if organization_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not associated with an organization.",
        )

    return organization_id