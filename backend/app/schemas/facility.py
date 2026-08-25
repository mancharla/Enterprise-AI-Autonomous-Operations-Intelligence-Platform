from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class FacilityCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    code: str = Field(min_length=2, max_length=50)
    region: str = Field(min_length=2, max_length=100)
    capacity_kw: float = Field(default=0.0, ge=0)


class FacilityUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=150)
    region: str | None = Field(default=None, min_length=2, max_length=100)
    capacity_kw: float | None = Field(default=None, ge=0)


class FacilityResponse(BaseModel):
    id: int
    organization_id: int
    name: str
    code: str
    region: str
    capacity_kw: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)