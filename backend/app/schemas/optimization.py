from datetime import datetime

from pydantic import BaseModel


class OptimizationStrategyResponse(
    BaseModel
):

    strategy: str

    description: str

    decision_score: float
    
    estimated_savings_percent: float

    estimated_energy_savings_kwh: float

    operational_impact_percent: float

    implementation_cost: float

    risk_percent: float

    applicability_score: float


class ForecastOptimizationResponse(
    BaseModel
):

    model: str

    horizon_hours: int

    forecast_points: int

    average_predicted_energy_kwh: float

    peak_predicted_energy_kwh: float

    peak_time: datetime

    forecast_increase_percent: float

    lower_bound: float

    upper_bound: float


class CurrentConditionsResponse(
    BaseModel
):

    current_energy_kwh: float

    operational_load: float

    utilization_percent: float

    temperature_c: float


class ForecastRiskResponse(BaseModel):

    risk_level: str

    risk_score: float

    forecast_increase_percent: float

    uncertainty_percent: float

    reason: str


class OptimizationResponse(BaseModel):

    recommended_strategy: str

    recommendation: str

    ranking: list[
        OptimizationStrategyResponse
    ]

    expected_savings_percent: float

    expected_energy_savings_kwh: float

    confidence: float

    forecast: ForecastOptimizationResponse

    current_conditions: (
        CurrentConditionsResponse
    )

    forecast_risk: ForecastRiskResponse