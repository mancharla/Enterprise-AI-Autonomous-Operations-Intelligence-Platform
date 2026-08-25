from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.forecast_accuracy import (
    ForecastAccuracy,
)


class ForecastAccuracyService:

    @staticmethod
    def save_accuracy(
        db: Session,
        organization_id: int,
        device_id: int,
        result: dict,
    ):

        record = ForecastAccuracy(
            organization_id=organization_id,
            device_id=device_id,
            model_name=result["model"],
            validation_points=result[
                "validation_points"
            ],
            mae=result["mae"],
            rmse=result["rmse"],
            mape=result["mape"],
            accuracy_percent=result[
                "accuracy_percent"
            ],
        )

        db.add(record)
        db.commit()
        db.refresh(record)

        return record

    @staticmethod
    def get_history(
        db: Session,
        organization_id: int,
        device_id: int,
        model_name: str | None = None,
        limit: int = 50,
    ):

        query = (
            select(ForecastAccuracy)
            .where(
                ForecastAccuracy.organization_id
                == organization_id,

                ForecastAccuracy.device_id
                == device_id,
            )
            .order_by(
                ForecastAccuracy.evaluated_at.desc()
            )
            .limit(limit)
        )

        if model_name:

            query = query.where(
                ForecastAccuracy.model_name
                == model_name
            )

        return db.scalars(
            query
        ).all()