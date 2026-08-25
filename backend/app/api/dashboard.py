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

from app.schemas.dashboard import (
    DashboardResponse,
)

from app.services.analytics_service import (
    AnalyticsService,
)

from app.services.anomaly_service import (
    AnomalyService,
)

from app.services.optimization_service import (
    OptimizationService,
)

from app.services.dashboard_service import (
    DashboardService,
)


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)

@router.get(
    "/",
    response_model=DashboardResponse,
)
def dashboard(
    forecast_horizon: int = 24,

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(
        get_database
    ),
):

    records = db.scalars(
        select(OperationalRecord)
        .where(
            OperationalRecord.organization_id
            == current_user.organization_id
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
                "for your organization."
            ),
        )

    dataframe = pd.DataFrame(
        [
            {
                "timestamp":
                    record.timestamp,

                "device_id":
                    record.device_id,

                "facility_id":
                    record.facility_id,

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

    try:

        # ==========================================
        # Analytics
        # ==========================================

        analytics_service = (
            AnalyticsService()
        )

        analytics = (
            analytics_service.analyze(
                dataframe
            )
        )

        # ==========================================
        # Anomaly detection
        # ==========================================

        anomaly_service = (
            AnomalyService()
        )

        anomaly_summary = (
            anomaly_service.summary(
                dataframe
            )
        )

        # ==========================================
        # Optimization
        # ==========================================

        optimization_service = (
            OptimizationService()
        )

        optimization = (
            optimization_service.optimize(
                dataframe=dataframe,
                db=db,
                organization_id=
                    current_user.organization_id,
                device_id=int(
                    dataframe[
                        "device_id"
                    ].iloc[-1]
                ),
                forecast_horizon=
                    forecast_horizon,
            )
        )

        # ==========================================
        # Risk
        # ==========================================

        risk_level = "LOW"
        risk_score = 0.0

        # Calculate utilization directly from dataframe
        average_utilization = float(
            pd.to_numeric(
                dataframe["utilization_percent"],
                errors="coerce",
            )
            .fillna(0)
            .mean()
        )

        # Utilization risk
        if average_utilization > 85:

            risk_score += 30

        elif average_utilization > 70:

            risk_score += 15


        # Anomaly risk
        anomaly_rate = float(
            anomaly_summary.get(
                "anomaly_rate_percent",
                0.0,
            )
        )

        if anomaly_rate > 5:

            risk_score += 30

        elif anomaly_rate > 2:

            risk_score += 15


        # Limit score
        risk_score = min(
            risk_score,
            100,
        )


        # Risk level
        if risk_score >= 60:

            risk_level = "CRITICAL"

        elif risk_score >= 40:

            risk_level = "HIGH"

        elif risk_score >= 20:

            risk_level = "MEDIUM"

        else:

            risk_level = "LOW"


        risk = {
            "overall_risk": risk_level,

            "risk_score": round(
                risk_score,
                2,
            ),
        }

        # ==========================================
        # Dashboard
        # ==========================================

        service = DashboardService()

        return service.build(
            dataframe=dataframe,
            analytics=analytics,
            anomaly_summary=anomaly_summary,
            optimization=optimization,
            risk=risk,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )