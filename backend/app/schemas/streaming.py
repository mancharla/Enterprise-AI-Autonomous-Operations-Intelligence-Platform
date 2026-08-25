from datetime import datetime

from pydantic import BaseModel, Field


class StreamEventCreate(BaseModel):

    organization_id: int

    device_id: int

    event_type: str = Field(
        default="energy_reading",
        max_length=50,
    )

    energy_kwh: float = Field(
        ge=0,
    )

    operational_load: float = Field(
        default=0,
        ge=0,
    )

    utilization_percent: float = Field(
        default=0,
        ge=0,
        le=100,
    )

    temperature_c: float = Field(
        default=0,
    )

    timestamp: datetime


class StreamEventResponse(BaseModel):

    event_id: str

    organization_id: int

    device_id: int

    event_type: str

    timestamp: datetime

    energy_kwh: float

    operational_load: float

    utilization_percent: float

    temperature_c: float

    anomaly: dict

    recommendation: dict

    alert: dict | None = None