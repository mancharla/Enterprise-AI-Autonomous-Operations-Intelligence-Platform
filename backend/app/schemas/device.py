from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DeviceCreate(BaseModel):
    facility_id: int
    name: str = Field(min_length=2, max_length=150)
    device_type: str = Field(min_length=2, max_length=100)
    rated_capacity_kw: float = Field(ge=0)
    status: str = Field(default="active", max_length=50)


class DeviceUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=150)
    device_type: str | None = Field(default=None, min_length=2, max_length=100)
    rated_capacity_kw: float | None = Field(default=None, ge=0)
    status: str | None = Field(default=None, max_length=50)


class DeviceResponse(BaseModel):
    id: int
    facility_id: int
    name: str
    device_type: str
    rated_capacity_kw: float
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)