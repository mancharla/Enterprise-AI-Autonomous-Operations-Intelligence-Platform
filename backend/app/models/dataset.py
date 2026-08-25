from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Dataset(Base):
    __tablename__ = "datasets"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    original_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="processing",
    )

    total_rows: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    valid_rows: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    invalid_rows: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    quality_score: Mapped[float] = mapped_column(
        default=0.0,
        nullable=False,
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    records = relationship(
        "OperationalRecord",
        back_populates="dataset",
        cascade="all, delete-orphan",
    )