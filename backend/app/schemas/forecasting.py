from datetime import datetime

from pydantic import BaseModel


class ForecastPoint(BaseModel):
    timestamp: datetime
    predicted_value: float
    lower_bound: float
    upper_bound: float


class ForecastResponse(BaseModel):
    device_id: int
    horizon_hours: int
    model: str
    historical_points: int
    forecast_points: int
    forecast: list[ForecastPoint]

class ModelMetrics(BaseModel):
    mae: float
    rmse: float


class ModelComparisonResponse(BaseModel):
    device_id: int
    validation_points: int
    prophet: ModelMetrics
    xgboost: ModelMetrics
    selected_model: str