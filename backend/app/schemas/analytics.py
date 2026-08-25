from pydantic import BaseModel


class AnalyticsOverview(BaseModel):
    total_energy_kwh: float
    average_energy_kwh: float
    peak_energy_kwh: float
    minimum_energy_kwh: float

    total_facilities: int
    total_devices: int

    active_devices: int

    total_records: int

    anomaly_count: int
    anomaly_rate_percent: float

    estimated_savings_percent: float
    estimated_energy_savings_kwh: float

    overall_risk: str


class FacilityAnalytics(BaseModel):
    facility_id: int
    facility_name: str

    total_energy_kwh: float
    average_energy_kwh: float
    peak_energy_kwh: float

    device_count: int
    record_count: int


class DeviceAnalytics(BaseModel):
    device_id: int
    device_name: str

    facility_id: int

    total_energy_kwh: float
    average_energy_kwh: float
    peak_energy_kwh: float

    record_count: int


class EnergyTrendPoint(BaseModel):
    timestamp: str
    energy_kwh: float


class RiskDistribution(BaseModel):
    low: int
    medium: int
    high: int
    critical: int



class EnergyTrendPoint(BaseModel):
    timestamp: str
    energy_kwh: float


class EnergyTrendResponse(BaseModel):
    granularity: str
    total_points: int
    average_energy_kwh: float
    peak_energy_kwh: float
    trend: list[EnergyTrendPoint]