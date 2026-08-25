from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DatasetResponse(BaseModel):
    id: int
    organization_id: int
    name: str
    original_filename: str
    status: str
    total_rows: int
    valid_rows: int
    invalid_rows: int
    quality_score: float
    error_message: str | None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )