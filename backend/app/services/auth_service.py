from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.organization import Organization
from app.models.user import User

from app.core.security import hash_password


def register_user(
    db: Session,
    organization_name: str,
    organization_code: str,
    full_name: str,
    email: str,
    password: str,
) -> User:

    existing_user = db.scalar(
        select(User).where(User.email == email)
    )

    if existing_user:
        raise ValueError("Email already registered")

    existing_organization = db.scalar(
        select(Organization).where(
            Organization.code == organization_code
        )
    )

    if existing_organization:
        organization = existing_organization
    else:
        organization = Organization(
            name=organization_name,
            code=organization_code,
        )

        db.add(organization)
        db.flush()

    user = User(
        organization_id=organization.id,
        full_name=full_name,
        email=email,
        hashed_password = hash_password(password),
        role="operations_manager",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def authenticate_user(
    db: Session,
    email: str,
    password: str,
) -> User | None:

    user = db.scalar(
        select(User).where(User.email == email)
    )

    if not user:
        return None

    if not verify_password(
        password,
        user.hashed_password,
    ):
        return None

    if not user.is_active:
        return None

    return user

def reset_password(
    db: Session,
    email: str,
    new_password: str,
    confirm_password: str,
):
    if new_password != confirm_password:
        raise ValueError("Passwords do not match")

    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if not user:
        raise ValueError("User not found")

    user.hashed_password = hash_password(new_password)

    db.commit()
    db.refresh(user)

    return user