from fastapi import Depends, HTTPException, status

from app.core.dependencies import get_current_user


def require_roles(*allowed_roles):

    def role_checker(
        current_user=Depends(get_current_user),
    ):
        role = getattr(
            current_user,
            "role",
            None,
        )

        if role is None and isinstance(
            current_user,
            dict,
        ):
            role = current_user.get("role")

        if role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action.",
            )

        return current_user

    return role_checker