import pandas as pd

from app.ml.anomaly.anomaly_detector import (
    AnomalyDetector,
)


class AnomalyService:

    def __init__(self):

        self.detector = AnomalyDetector()

    # -----------------------------------------
    # Analyze anomalies
    # -----------------------------------------

    def analyze(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:

        return self.detector.detect(
            dataframe
        )

    # -----------------------------------------
    # Generate summary
    # -----------------------------------------

    def summary(
        self,
        dataframe: pd.DataFrame,
    ) -> dict:

        result = self.detector.detect(
            dataframe
        )

        total_records = len(result)

        anomalies = result[
            result["is_anomaly"] == True
        ].copy()

        anomaly_count = len(anomalies)

        # -----------------------------------------
        # Anomaly percentage
        # -----------------------------------------

        if total_records > 0:

            anomaly_rate = (
                anomaly_count
                / total_records
                * 100
            )

        else:

            anomaly_rate = 0.0

        # -----------------------------------------
        # Severity distribution
        # -----------------------------------------

        severity_distribution = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
        }

        if not anomalies.empty:

            severity_counts = (
                anomalies["severity"]
                .value_counts()
                .to_dict()
            )

            for severity, count in (
                severity_counts.items()
            ):

                severity_distribution[
                    severity
                ] = int(count)

        # -----------------------------------------
        # Anomaly type distribution
        # -----------------------------------------

        anomaly_type_distribution = {}

        if not anomalies.empty:

            type_counts = (
                anomalies["anomaly_type"]
                .value_counts()
                .to_dict()
            )

            anomaly_type_distribution = {
                str(anomaly_type): int(count)

                for anomaly_type, count
                in type_counts.items()
            }

        # -----------------------------------------
        # Final response
        # -----------------------------------------

        return {
            "total_records": total_records,

            "anomaly_count": anomaly_count,

            "anomaly_rate_percent": round(
                anomaly_rate,
                2,
            ),

            "severity_distribution":
                severity_distribution,

            "anomaly_type_distribution":
                anomaly_type_distribution,
        }