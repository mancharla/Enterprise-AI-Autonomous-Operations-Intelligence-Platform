from uuid import uuid4

from app.schemas.streaming import (
    StreamEventCreate,
)


class StreamingService:

    @staticmethod
    def process_event(
        event: StreamEventCreate,
    ) -> dict:

        anomaly_score = 0.0

        anomaly_reasons = []

        # =========================================
        # 1. ENERGY ANOMALY
        # =========================================

        if event.energy_kwh > 120:

            anomaly_score += 30

            anomaly_reasons.append(
                "Energy consumption is unusually high."
            )

        # =========================================
        # 2. OPERATIONAL LOAD
        # =========================================

        if event.operational_load > 85:

            anomaly_score += 25

            anomaly_reasons.append(
                "Operational load is above safe threshold."
            )

        # =========================================
        # 3. DEVICE UTILIZATION
        # =========================================

        if event.utilization_percent > 90:

            anomaly_score += 25

            anomaly_reasons.append(
                "Device utilization is critically high."
            )

        elif event.utilization_percent > 80:

            anomaly_score += 15

            anomaly_reasons.append(
                "Device utilization is high."
            )

        # =========================================
        # 4. TEMPERATURE
        # =========================================

        if event.temperature_c > 40:

            anomaly_score += 20

            anomaly_reasons.append(
                "Device temperature is critically high."
            )

        elif event.temperature_c > 35:

            anomaly_score += 10

            anomaly_reasons.append(
                "Device temperature is elevated."
            )

        # =========================================
        # 5. LIMIT SCORE
        # =========================================

        anomaly_score = min(
            anomaly_score,
            100,
        )

        # =========================================
        # 6. DETERMINE SEVERITY
        # =========================================

        if anomaly_score >= 70:

            severity = "CRITICAL"

        elif anomaly_score >= 45:

            severity = "HIGH"

        elif anomaly_score >= 20:

            severity = "MEDIUM"

        else:

            severity = "LOW"

        # =========================================
        # 7. DETERMINE RECOMMENDATION
        # =========================================

        recommendation = {
            "strategy": "none",
            "priority": "LOW",
            "reason": (
                "No immediate optimization action "
                "required."
            ),
        }

        if severity == "CRITICAL":

            recommendation = {
                "strategy": "workload_redistribution",
                "priority": "CRITICAL",
                "reason": (
                    "Immediately redistribute workload "
                    "from the affected device."
                ),
            }

        elif severity == "HIGH":

            recommendation = {
                "strategy": "peak_shifting",
                "priority": "HIGH",
                "reason": (
                    "Shift flexible workloads away "
                    "from the affected device."
                ),
            }

        elif severity == "MEDIUM":

            recommendation = {
                "strategy": "energy_reduction",
                "priority": "MEDIUM",
                "reason": (
                    "Reduce non-critical consumption "
                    "and monitor device behavior."
                ),
            }

        # =========================================
        # 8. FINAL RESULT
        # =========================================

        return {

            "event_id": str(uuid4()),

            "organization_id":
                event.organization_id,

            "device_id":
                event.device_id,

            "event_type":
                event.event_type,

            "timestamp":
                event.timestamp,

            "energy_kwh":
                event.energy_kwh,

            "operational_load":
                event.operational_load,

            "utilization_percent":
                event.utilization_percent,

            "temperature_c":
                event.temperature_c,

            "anomaly": {

                "is_anomaly":
                    anomaly_score >= 20,

                "score":
                    round(
                        anomaly_score,
                        2,
                    ),

                "severity":
                    severity,

                "reasons":
                    anomaly_reasons,
            },

            "recommendation":
                recommendation,
        }