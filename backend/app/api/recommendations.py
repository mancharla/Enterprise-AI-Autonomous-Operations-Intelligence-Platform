import pandas as pd

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_database

from app.core.dependencies import (
    get_current_user,
)

from app.models.operational_record import (
    OperationalRecord,
)

from app.models.user import User

from app.schemas.recommendations import (
    RecommendationResponse,
)

from app.services.anomaly_service import (
    AnomalyService,
)

from app.services.root_cause_service import (
    RootCauseService,
)

from app.services.optimization_service import (
    OptimizationService,
)

from app.ml.recommendation.recommendation_engine import (
    RecommendationEngine,
)


router = APIRouter(
    prefix="/recommendations",
    tags=["Recommendations"],
)


def get_device_dataframe(
    device_id: int,
    organization_id: int,
    db: Session,
):

    records = db.scalars(
        select(OperationalRecord)
        .where(
            OperationalRecord.organization_id
            == organization_id,

            OperationalRecord.device_id
            == device_id,
        )
        .order_by(
            OperationalRecord.timestamp
        )
    ).all()

    if not records:

        raise HTTPException(
            status_code=404,
            detail=(
                "No operational data found "
                "for this device."
            ),
        )

    return pd.DataFrame(
        [
            {
                "timestamp":
                    record.timestamp,

                "energy_kwh":
                    record.energy_kwh,

                "operational_load":
                    record.operational_load,

                "temperature_c":
                    record.temperature_c,

                "utilization_percent":
                    record.utilization_percent,
            }

            for record in records
        ]
    )


@router.get(
    "/device/{device_id}",
    response_model=RecommendationResponse,
)
def generate_device_recommendation(

    device_id: int,

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(
        get_database
    ),
):

    # ==========================================
    # Load device operational data
    # ==========================================

    dataframe = get_device_dataframe(
        device_id=device_id,
        organization_id=
            current_user.organization_id,
        db=db,
    )

    try:

        # ======================================
        # 1. Anomaly Intelligence
        # ======================================

        anomaly_service = AnomalyService()

        anomaly_result = (
            anomaly_service.summary(
                dataframe
            )
        )

        # ======================================
        # 2. Root Cause Intelligence
        # ======================================

        root_cause_service = (
            RootCauseService()
        )

        root_cause_result = (
            root_cause_service.analyze(
                dataframe
            )
        )

        # ======================================
        # 3. Forecast + Optimization
        # ======================================

        optimization_service = (
            OptimizationService()
        )

        optimization_result = (
            optimization_service.optimize(
                dataframe=dataframe,

                db=db,

                organization_id=
                    current_user.organization_id,

                device_id=device_id,

                forecast_horizon=24,
            )
        )

        # ======================================
        # 4. Extract forecast information
        # ======================================

        forecast_result = (
            optimization_result.get(
                "forecast",
                {}
            )
        )

        forecast_risk = (
            optimization_result.get(
                "forecast_risk",
                {}
            )
        )

        # ======================================
        # 5. Build recommendation
        # ======================================

        engine = RecommendationEngine()

        recommendation = engine.generate(

            forecast_risk_level=
                forecast_risk.get(
                    "risk_level",
                    "LOW",
                ),

            forecast_increase_percent=
                forecast_result.get(
                    "forecast_increase_percent",
                    0,
                ),

            anomaly_count=
                anomaly_result.get(
                    "anomaly_count",
                    0,
                ),

            anomaly_rate_percent=
                anomaly_result.get(
                    "anomaly_rate_percent",
                    0,
                ),

            root_cause=
                root_cause_result.get(
                    "root_cause"
                ),

            primary_factor=
                root_cause_result.get(
                    "primary_factor"
                ),

            optimization_strategy=
                optimization_result.get(
                    "recommended_strategy"
                ),

            optimization_savings_percent=
                optimization_result.get(
                    "expected_savings_percent",
                    0,
                ),

            simulation_risk_level=None,

            simulation_energy_change_percent=None,
        )

        # ======================================
        # 6. Final enterprise response
        # ======================================

        return {

            "device_id":
                device_id,

            "priority":
                recommendation.priority,

            "risk_level":
                recommendation.risk_level,

            "action":
                recommendation.action,

            "reason":
                recommendation.reason,

            "expected_benefit":
                recommendation.expected_benefit,

            "confidence":
                recommendation.confidence,

            "estimated_savings_percent":
                recommendation
                .estimated_savings_percent,

            "signals": {

                "forecast": {
                    "model":
                        forecast_result.get(
                            "model"
                        ),

                    "horizon_hours":
                        forecast_result.get(
                            "horizon_hours"
                        ),

                    "average_predicted_energy_kwh":
                        forecast_result.get(
                            "average_predicted_energy_kwh"
                        ),

                    "peak_predicted_energy_kwh":
                        forecast_result.get(
                            "peak_predicted_energy_kwh"
                        ),

                    "peak_time":
                        forecast_result.get(
                            "peak_time"
                        ),

                    "forecast_increase_percent":
                        forecast_result.get(
                            "forecast_increase_percent"
                        ),

                    "risk":
                        forecast_risk,
                },

                "anomalies":
                    anomaly_result,

                "root_cause":
                    root_cause_result,

                "optimization":
                    optimization_result,
            },
        }

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )