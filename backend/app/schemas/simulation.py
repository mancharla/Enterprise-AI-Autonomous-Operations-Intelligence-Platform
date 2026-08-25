from datetime import datetime

from pydantic import BaseModel, Field


class SimulationRequest(BaseModel):
    scenario: str = Field(
        ...,
        description=(
            "Scenario to simulate. "
            "Examples: demand_surge, device_failure, "
            "facility_shutdown, temperature_increase, "
            "workforce_reduction, resource_shortage."
        ),
    )

    impact_percent: float = Field(
        default=20.0,
        ge=0,
        le=100,
        description="Expected scenario impact percentage.",
    )

    duration_hours: int = Field(
        default=24,
        ge=1,
        le=2160,
        description="Duration of the simulated scenario.",
    )


class SimulationResponse(BaseModel):
    device_id: int
    scenario: str

    baseline_energy_kwh: float
    simulated_energy_kwh: float
    energy_change_percent: float

    operational_impact_percent: float
    failure_probability_percent: float

    estimated_cost_impact_percent: float
    estimated_savings_percent: float

    risk_level: str

    duration_hours: int
    simulated_until: datetime

    recommendation: str


class ScenarioComparisonRequest(BaseModel):
    scenarios: list[str] = Field(
        ...,
        min_length=1,
        max_length=10,
        description=(
            "Scenarios to compare. "
            "Example: demand_surge, device_failure."
        ),
    )

    impact_percent: float = Field(
        default=20.0,
        ge=0,
        le=100,
    )

    duration_hours: int = Field(
        default=24,
        ge=1,
        le=2160,
    )


class ScenarioComparisonResponse(BaseModel):
    device_id: int

    scenario_count: int

    best_scenario: str
    lowest_risk_scenario: str
    lowest_cost_scenario: str
    highest_savings_scenario: str

    scenarios: list[dict]