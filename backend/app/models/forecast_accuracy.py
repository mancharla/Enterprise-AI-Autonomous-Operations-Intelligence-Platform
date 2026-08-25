from datetime import datetime

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.core.database import Base


class ForecastAccuracy(Base):

    __tablename__ = "forecast_accuracy"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )

    device_id: Mapped[int] = mapped_column(
        ForeignKey("devices.id"),
        nullable=False,
        index=True,
    )

    model_name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    validation_points: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    mae: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    rmse: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    mape: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    accuracy_percent: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    evaluated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True,
    )