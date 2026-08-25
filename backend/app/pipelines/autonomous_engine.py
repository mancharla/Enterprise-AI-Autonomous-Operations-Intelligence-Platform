from typing import Any
import json

import pandas as pd

from app.services.anomaly_service import AnomalyService
from app.services.root_cause_service import RootCauseService
from app.services.optimization_service import OptimizationService
from app.services.simulation_service import SimulationService
from app.services.recommendation_service import RecommendationService

from app.models.autonomous_action import AutonomousAction


class AutonomousOperationsEngine:

    def __init__(self):

        self.anomaly_service = (
            AnomalyService()
        )

        self.root_cause_service = (
            RootCauseService()
        )

        self.optimization_service = (
            OptimizationService()
        )

        self.simulation_service = (
            SimulationService()
        )

        self.recommendation_service = (
            RecommendationService()
        )

    # ========================================================
    # MAIN AUTONOMOUS PIPELINE
    # ========================================================

    def analyze(
        self,
        dataframe: pd.DataFrame,
        db,
        organization_id: int,
        device_id: int,
        forecast_horizon: int = 24,
    ) -> dict[str, Any]:

        if (
            dataframe is None
            or dataframe.empty
        ):

            raise ValueError(
                "No operational data available."
            )

        # ====================================================
        # 1. ANOMALY INTELLIGENCE
        # ====================================================

        anomaly_result = (
            self.anomaly_service.summary(
                dataframe
            )
        )

        # ====================================================
        # 2. ROOT CAUSE INTELLIGENCE
        # ====================================================

        root_cause_result = (
            self.root_cause_service.analyze(
                dataframe
            )
        )

        # ====================================================
        # 3. FORECAST + OPTIMIZATION
        # ====================================================

        optimization_result = (
            self.optimization_service.optimize(
                dataframe=dataframe,

                db=db,

                organization_id=
                    organization_id,

                device_id=
                    device_id,

                forecast_horizon=
                    forecast_horizon,
            )
        )

        # ====================================================
        # 4. RECOMMENDATION
        # ====================================================

        recommendation_result = (
            self.recommendation_service.generate(

                device_id=device_id,

                forecast_result={
                    "forecast":
                        optimization_result.get(
                            "forecast",
                            {},
                        ),

                    "forecast_risk":
                        optimization_result.get(
                            "forecast_risk",
                            {},
                        ),
                },

                anomaly_result=
                    anomaly_result,

                root_cause_result=
                    root_cause_result,

                optimization_result=
                    optimization_result,
            )
        )

        # ====================================================
        # 5. AUTONOMOUS DECISION
        # ====================================================

        risk_level = (
            optimization_result
            .get(
                "forecast_risk",
                {},
            )
            .get(
                "risk_level",
                "LOW",
            )
        )

        autonomous_action = (
            self._determine_action(
                risk_level=
                    risk_level,

                anomaly_result=
                    anomaly_result,
            )
        )

        # ====================================================
        # 6. PREPARE JSON-SAFE SIGNALS
        # ====================================================

        signals = self._make_json_safe(
            {
                "anomaly":
                    anomaly_result,

                "root_cause":
                    root_cause_result,

                "optimization":
                    optimization_result,

                "recommendation":
                    recommendation_result,
            }
        )

        # ====================================================
        # 7. PERSIST AUTONOMOUS ACTION
        # ====================================================

        autonomous_record = AutonomousAction(

            organization_id=
                organization_id,

            device_id=
                device_id,

            action=
                autonomous_action[
                    "action"
                ],

            priority=
                autonomous_action[
                    "priority"
                ],

            risk_level=
                risk_level,

            reason=
                autonomous_action[
                    "reason"
                ],

            expected_benefit=
                recommendation_result.get(
                    "expected_benefit"
                ),

            confidence=
                recommendation_result.get(
                    "confidence"
                ),

            estimated_savings_percent=
                recommendation_result.get(
                    "estimated_savings_percent"
                ),

            status=
                "RECOMMENDED",

            signals=
                signals,
        )

        try:

            db.add(
                autonomous_record
            )

            db.commit()

            db.refresh(
                autonomous_record
            )

        except Exception:

            db.rollback()

            raise

        # ====================================================
        # 8. FINAL RESPONSE
        # ====================================================

        return {

            "device_id":
                device_id,

            "status":
                "completed",

            "autonomous_action": {

                **autonomous_action,

                "action_id":
                    autonomous_record.id,

                "status":
                    autonomous_record.status,

                "created_at":
                    autonomous_record.created_at,
            },

            "anomaly":
                anomaly_result,

            "root_cause":
                root_cause_result,

            "optimization":
                optimization_result,

            "recommendation":
                recommendation_result,
        }

    # ========================================================
    # AUTONOMOUS DECISION ENGINE
    # ========================================================

    @staticmethod
    def _determine_action(
        risk_level: str,
        anomaly_result: dict,
    ) -> dict:

        anomaly_count = (
            anomaly_result.get(
                "anomaly_count",
                0,
            )
        )

        risk_level = (
            str(risk_level)
            .upper()
        )

        # ----------------------------------------------------
        # CRITICAL
        # ----------------------------------------------------

        if risk_level == "CRITICAL":

            return {
                "action":
                    "IMMEDIATE_INTERVENTION",

                "priority":
                    "CRITICAL",

                "reason":
                    (
                        "Critical operational risk "
                        "detected. Immediate intervention "
                        "is required."
                    ),
            }

        # ----------------------------------------------------
        # HIGH
        # ----------------------------------------------------

        if risk_level == "HIGH":

            return {
                "action":
                    "PROACTIVE_INTERVENTION",

                "priority":
                    "HIGH",

                "reason":
                    (
                        "High operational risk detected. "
                        "Proactive intervention is "
                        "recommended."
                    ),
            }

        # ----------------------------------------------------
        # MEDIUM / ANOMALIES
        # ----------------------------------------------------

        if anomaly_count > 0:

            return {
                "action":
                    "MONITOR_AND_REVIEW",

                "priority":
                    "MEDIUM",

                "reason":
                    (
                        "Operational anomalies detected. "
                        "Continue monitoring and review."
                    ),
            }

        # ----------------------------------------------------
        # LOW
        # ----------------------------------------------------

        return {
            "action":
                "NO_ACTION_REQUIRED",

            "priority":
                "LOW",

            "reason":
                (
                    "No significant operational risk "
                    "requires immediate intervention."
                ),
        }

    # ========================================================
    # JSON SERIALIZATION
    # ========================================================

    @staticmethod
    def _make_json_safe(
        data: Any,
    ) -> Any:

        return json.loads(
            json.dumps(
                data,
                default=str,
            )
        )