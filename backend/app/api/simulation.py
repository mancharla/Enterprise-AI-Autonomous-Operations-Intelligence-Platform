import pandas as pd

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_database
from app.core.dependencies import get_current_user

from app.ml.simulation.simulation_engine import (
    SimulationEngine,
)

from app.models.operational_record import (
    OperationalRecord,
)

from app.models.user import User

from app.schemas.simulation import (
    SimulationRequest,
    SimulationResponse,
    ScenarioComparisonRequest,
    ScenarioComparisonResponse,
)


router = APIRouter(
    prefix="/simulation",
    tags=["Simulation"],
)


@router.post(
    "/device/{device_id}",
    response_model=SimulationResponse,
)
def simulate_device(
    device_id: int,
    request: SimulationRequest,
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
            == current_user.organization_id,

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

    dataframe = pd.DataFrame(
        [
            {
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

    numeric_columns = [
        "energy_kwh",
        "operational_load",
        "temperature_c",
        "utilization_percent",
    ]

    for column in numeric_columns:

        dataframe[column] = pd.to_numeric(
            dataframe[column],
            errors="coerce",
        )

        dataframe[column] = (
            dataframe[column]
            .interpolate()
            .ffill()
            .bfill()
        )

    latest = dataframe.iloc[-1]

    engine = SimulationEngine()

    try:

        result = engine.simulate(
            scenario=request.scenario,

            baseline_energy=float(
                latest["energy_kwh"]
            ),

            operational_load=float(
                latest["operational_load"]
            ),

            utilization_percent=float(
                latest["utilization_percent"]
            ),

            temperature_c=float(
                latest["temperature_c"]
            ),

            impact_percent=request.impact_percent,

            duration_hours=request.duration_hours,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    return {
        "device_id": device_id,
        **result,
    }

@router.post(
    "/device/{device_id}/compare",
    response_model=ScenarioComparisonResponse,
)
def compare_device_scenarios(
    device_id: int,
    request: ScenarioComparisonRequest,
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
            == current_user.organization_id,

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

    dataframe = pd.DataFrame(
        [
            {
                "energy_kwh": record.energy_kwh,
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

    numeric_columns = [
        "energy_kwh",
        "operational_load",
        "temperature_c",
        "utilization_percent",
    ]

    for column in numeric_columns:

        dataframe[column] = pd.to_numeric(
            dataframe[column],
            errors="coerce",
        )

        dataframe[column] = (
            dataframe[column]
            .interpolate()
            .ffill()
            .bfill()
        )

    latest = dataframe.iloc[-1]

    engine = SimulationEngine()

    results = []

    try:

        for scenario in request.scenarios:

            result = engine.simulate(
                scenario=scenario,

                baseline_energy=float(
                    latest["energy_kwh"]
                ),

                operational_load=float(
                    latest["operational_load"]
                ),

                utilization_percent=float(
                    latest["utilization_percent"]
                ),

                temperature_c=float(
                    latest["temperature_c"]
                ),

                impact_percent=request.impact_percent,

                duration_hours=request.duration_hours,
            )

            results.append(result)

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    if not results:

        raise HTTPException(
            status_code=400,
            detail="No scenarios were provided.",
        )

    # -----------------------------------------
    # Rank scenarios
    # -----------------------------------------

    # Best scenario:
    # lowest risk + lowest cost impact
    best = min(
        results,
        key=lambda item: (
            item["failure_probability_percent"]
            + item["estimated_cost_impact_percent"]
        ),
    )

    lowest_risk = min(
        results,
        key=lambda item:
            item["failure_probability_percent"],
    )

    lowest_cost = min(
        results,
        key=lambda item:
            item["estimated_cost_impact_percent"],
    )

    highest_savings = max(
        results,
        key=lambda item:
            item["estimated_savings_percent"],
    )

    # -----------------------------------------
    # Add ranking
    # -----------------------------------------

    for index, result in enumerate(
        sorted(
            results,
            key=lambda item: (
                item["failure_probability_percent"]
                + item["estimated_cost_impact_percent"]
            ),
        ),
        start=1,
    ):

        result["rank"] = index

    return {
        "device_id": device_id,

        "scenario_count": len(results),

        "best_scenario": best[
            "scenario"
        ],

        "lowest_risk_scenario":
            lowest_risk[
                "scenario"
            ],

        "lowest_cost_scenario":
            lowest_cost[
                "scenario"
            ],

        "highest_savings_scenario":
            highest_savings[
                "scenario"
            ],

        "scenarios": results,
    }