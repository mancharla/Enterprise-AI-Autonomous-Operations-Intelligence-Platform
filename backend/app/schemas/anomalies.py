from datetime import datetime

from pydantic import BaseModel


class AnomalyItem(BaseModel):

    timestamp: datetime

    energy_kwh: float

    operational_load: float

    temperature_c: float

    utilization_percent: float

    anomaly_score: float

    severity: str

    anomaly_type: str


class AnomalySummary(BaseModel):

    total_records: int

    anomaly_count: int

    anomaly_rate_percent: float

    severity_distribution: dict[str, int]

    anomaly_type_distribution: dict[str, int]