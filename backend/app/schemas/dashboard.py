from pydantic import BaseModel


class DashboardOrganization(BaseModel):

    total_facilities: int
    total_devices: int
    total_records: int


class DashboardEnergy(BaseModel):

    total_energy_kwh: float
    average_energy_kwh: float
    peak_energy_kwh: float
    minimum_energy_kwh: float


class DashboardOperations(BaseModel):

    average_load: float
    average_utilization_percent: float
    average_temperature_c: float


class DashboardRisk(BaseModel):

    overall_risk: str
    risk_score: float


class DashboardAnomalies(BaseModel):

    total: int
    critical: int
    high: int
    medium: int
    low: int


class DashboardOptimization(BaseModel):

    recommended_strategy: str
    expected_savings_percent: float
    expected_energy_savings_kwh: float
    confidence: float


class DashboardResponse(BaseModel):

    organization: DashboardOrganization

    energy: DashboardEnergy

    operations: DashboardOperations

    risk: DashboardRisk

    anomalies: DashboardAnomalies

    optimization: DashboardOptimization

    insights: list[str]