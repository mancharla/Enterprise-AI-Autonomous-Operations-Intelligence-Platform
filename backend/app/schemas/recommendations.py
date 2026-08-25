from pydantic import BaseModel


class RecommendationResponse(BaseModel):

    device_id: int

    priority: str

    risk_level: str

    action: str

    reason: str

    expected_benefit: str

    confidence: float

    estimated_savings_percent: float

    signals: dict