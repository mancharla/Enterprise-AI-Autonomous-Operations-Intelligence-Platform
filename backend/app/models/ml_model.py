from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
)

from app.core.database import Base


class MLModel(Base):
    __tablename__ = "ml_models"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    model_name = Column(
        String(150),
        nullable=False,
    )

    model_type = Column(
        String(100),
        nullable=False,
    )

    version = Column(
        String(50),
        nullable=False,
    )

    status = Column(
        String(50),
        nullable=False,
        default="trained",
    )

    accuracy = Column(
        Float,
        nullable=True,
    )

    mae = Column(
        Float,
        nullable=True,
    )

    rmse = Column(
        Float,
        nullable=True,
    )

    mape = Column(
        Float,
        nullable=True,
    )

    description = Column(
        Text,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=True,
    )