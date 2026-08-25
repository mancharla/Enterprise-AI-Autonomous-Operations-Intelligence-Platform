from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import (
    get_current_user,
)

from app.services.ml_service import (
    ml_service,
)


router = APIRouter(
    prefix="/ml",
    tags=["ML Pipeline"],
)


@router.post("/pipeline/run")
def run_ml_pipeline(
    db: Session = Depends(get_db),
    current_user=Depends(
        get_current_user
    ),
):

    try:

        return ml_service.run_pipeline(
            db
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@router.get("/models")
def get_models(
    db: Session = Depends(get_db),
    current_user=Depends(
        get_current_user
    ),
):

    models = ml_service.get_models(
        db
    )

    return {
        "total_models": len(models),
        "models": models,
    }


@router.get("/models/{model_id}")
def get_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        get_current_user
    ),
):

    model = ml_service.get_model(
        db,
        model_id,
    )

    if not model:

        raise HTTPException(
            status_code=404,
            detail="Model not found",
        )

    return model


@router.post(
    "/models/{model_id}/retrain"
)
def retrain_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        get_current_user
    ),
):

    model = ml_service.retrain_model(
        db,
        model_id,
    )

    if not model:

        raise HTTPException(
            status_code=404,
            detail="Model not found",
        )

    return {
        "message":
            "Model retrained successfully",

        "model": model,
    }