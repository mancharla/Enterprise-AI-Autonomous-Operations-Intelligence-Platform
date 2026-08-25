from datetime import datetime

from pydantic import BaseModel


class AlertResponse(BaseModel):

    id: int

    organization_id: int

    facility_id: int

    device_id: int

    alert_type: str

    severity: str

    message: str

    value: float | None = None

    threshold: float | None = None

    status: str

    created_at: datetime

    acknowledged_at: datetime | None = None

    resolved_at: datetime | None = None

    class Config:
        from_attributes = True


class AlertSummary(BaseModel):

    total_alerts: int

    open_alerts: int

    acknowledged_alerts: int

    resolved_alerts: int

    critical_alerts: int

    high_alerts: int