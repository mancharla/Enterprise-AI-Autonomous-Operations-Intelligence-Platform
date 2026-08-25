from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class OperationalRecord(Base):
    __tablename__ = "operational_records"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    dataset_id: Mapped[int] = mapped_column(
        ForeignKey("datasets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    facility_id: Mapped[int] = mapped_column(
        ForeignKey("facilities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    device_id: Mapped[int] = mapped_column(
        ForeignKey("devices.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        index=True,
    )

    energy_kwh: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    operational_load: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    temperature_c: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    utilization_percent: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="valid",
    )

    dataset = relationship(
        "Dataset",
        back_populates="records",
    )


Index(
    "ix_operational_records_device_timestamp",
    OperationalRecord.device_id,
    OperationalRecord.timestamp,
)