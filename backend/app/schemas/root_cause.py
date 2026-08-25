from pydantic import BaseModel


class RankedFactor(BaseModel):
    factor: str
    score: float


class RootCauseResponse(BaseModel):

    current_energy_kwh: float

    baseline_energy_kwh: float

    energy_deviation_percent: float

    correlations: dict[str, float]

    contribution_scores: dict[str, float]

    ranked_factors: list[RankedFactor]

    primary_factor: str | None

    confidence: float

    root_cause: str

    recommended_action: str