from datetime import datetime

from pydantic import BaseModel


class ReportResponse(BaseModel):
    device_id: int
    generated_at: datetime

    executive_summary: str

    current_energy_kwh: float
    average_energy_kwh: float
    peak_energy_kwh: float
    minimum_energy_kwh: float

    utilization_percent: float
    temperature_c: float

    forecast: dict
    anomalies: dict
    root_cause: dict
    optimization: dict
    recommendation: dict

    overall_risk: str
    estimated_savings_percent: float
    estimated_energy_savings_kwh: float