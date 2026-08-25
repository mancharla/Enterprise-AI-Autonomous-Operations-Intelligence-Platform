import pandas as pd

from app.ml.anomaly.anomaly_detector import (
    AnomalyDetector,
)


class AnalyticsService:

    def __init__(self):
        self.anomaly_detector = AnomalyDetector()

    # ==========================================================
    # Prepare Data
    # ==========================================================

    @staticmethod
    def _prepare_data(
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:

        if dataframe.empty:
            raise ValueError(
                "No operational data available."
            )

        data = dataframe.copy()

        numeric_columns = [
            "energy_kwh",
            "operational_load",
            "temperature_c",
            "utilization_percent",
        ]

        for column in numeric_columns:

            if column not in data.columns:
                data[column] = 0.0

            data[column] = pd.to_numeric(
                data[column],
                errors="coerce",
            )

            data[column] = (
                data[column]
                .interpolate(
                    limit_direction="both"
                )
                .ffill()
                .bfill()
                .fillna(0.0)
            )

        if "timestamp" in data.columns:

            data["timestamp"] = pd.to_datetime(
                data["timestamp"],
                errors="coerce",
            )

            data = data.dropna(
                subset=["timestamp"]
            )

            data = data.sort_values(
                "timestamp"
            )

        return data

    # ==========================================================
    # Anomaly Analysis
    # ==========================================================

    def _get_anomaly_analysis(
        self,
        data: pd.DataFrame,
    ):

        try:

            if len(data) < 30:

                return {
                    "anomaly_count": 0,
                    "anomaly_rate_percent": 0.0,
                    "severity_distribution": {
                        "low": 0,
                        "medium": 0,
                        "high": 0,
                        "critical": 0,
                    },
                }

            anomaly_data = (
                self.anomaly_detector.detect(
                    data
                )
            )

            anomaly_count = int(
                anomaly_data[
                    "is_anomaly"
                ].sum()
            )

            total_records = len(
                anomaly_data
            )

            anomaly_rate = 0.0

            if total_records > 0:

                anomaly_rate = (
                    anomaly_count
                    / total_records
                ) * 100

            severity_distribution = {
                "low": int(
                    (
                        anomaly_data[
                            "severity"
                        ] == "low"
                    ).sum()
                ),
                "medium": int(
                    (
                        anomaly_data[
                            "severity"
                        ] == "medium"
                    ).sum()
                ),
                "high": int(
                    (
                        anomaly_data[
                            "severity"
                        ] == "high"
                    ).sum()
                ),
                "critical": int(
                    (
                        anomaly_data[
                            "severity"
                        ] == "critical"
                    ).sum()
                ),
            }

            return {
                "anomaly_count":
                    anomaly_count,

                "anomaly_rate_percent":
                    round(
                        anomaly_rate,
                        2,
                    ),

                "severity_distribution":
                    severity_distribution,
            }

        except ValueError:

            return {
                "anomaly_count": 0,
                "anomaly_rate_percent": 0.0,
                "severity_distribution": {
                    "low": 0,
                    "medium": 0,
                    "high": 0,
                    "critical": 0,
                },
            }

    # ==========================================================
    # Risk Analysis
    # ==========================================================

    @staticmethod
    def _calculate_risk(
        data: pd.DataFrame,
        anomaly_rate: float,
    ) -> str:

        average_utilization = float(
            data[
                "utilization_percent"
            ].mean()
        )

        average_load = float(
            data[
                "operational_load"
            ].mean()
        )

        average_temperature = float(
            data[
                "temperature_c"
            ].mean()
        )

        risk_score = 0.0

        # Anomaly contribution
        if anomaly_rate >= 10:

            risk_score += 35

        elif anomaly_rate >= 5:

            risk_score += 25

        elif anomaly_rate >= 2:

            risk_score += 15

        elif anomaly_rate > 0:

            risk_score += 5

        # Utilization
        if average_utilization >= 90:

            risk_score += 25

        elif average_utilization >= 80:

            risk_score += 15

        elif average_utilization >= 70:

            risk_score += 8

        # Operational load
        if average_load >= 90:

            risk_score += 20

        elif average_load >= 80:

            risk_score += 15

        elif average_load >= 65:

            risk_score += 8

        # Temperature
        if average_temperature >= 40:

            risk_score += 20

        elif average_temperature >= 35:

            risk_score += 15

        elif average_temperature >= 30:

            risk_score += 7

        risk_score = min(
            risk_score,
            100,
        )

        if risk_score >= 70:

            return "CRITICAL"

        if risk_score >= 45:

            return "HIGH"

        if risk_score >= 25:

            return "MEDIUM"

        return "LOW"

    # ==========================================================
    # Estimated Savings
    # ==========================================================

    @staticmethod
    def _calculate_savings(
        data: pd.DataFrame,
        anomaly_rate: float,
    ):

        average_utilization = float(
            data[
                "utilization_percent"
            ].mean()
        )

        average_load = float(
            data[
                "operational_load"
            ].mean()
        )

        savings_percent = 0.0

        # Anomaly based opportunity
        savings_percent += min(
            anomaly_rate * 0.5,
            5.0,
        )

        # High utilization opportunity
        if average_utilization > 85:

            savings_percent += 4.0

        elif average_utilization > 70:

            savings_percent += 2.0

        # High load opportunity
        if average_load > 85:

            savings_percent += 3.0

        elif average_load > 70:

            savings_percent += 1.5

        savings_percent = min(
            savings_percent,
            15.0,
        )

        total_energy = float(
            data["energy_kwh"].sum()
        )

        estimated_energy_savings = (
            total_energy
            * savings_percent
            / 100
        )

        return (
            round(
                savings_percent,
                2,
            ),
            round(
                estimated_energy_savings,
                2,
            ),
        )

    # ==========================================================
    # Main Analysis
    # ==========================================================

    def analyze(
        self,
        dataframe: pd.DataFrame,
    ) -> dict:

        data = self._prepare_data(
            dataframe
        )

        # ------------------------------------------------------
        # Basic Energy Metrics
        # ------------------------------------------------------

        total_energy = float(
            data["energy_kwh"].sum()
        )

        average_energy = float(
            data["energy_kwh"].mean()
        )

        peak_energy = float(
            data["energy_kwh"].max()
        )

        minimum_energy = float(
            data["energy_kwh"].min()
        )

        # ------------------------------------------------------
        # Entity Counts
        # ------------------------------------------------------

        unique_devices = 0

        if "device_id" in data.columns:

            unique_devices = int(
                data["device_id"].nunique()
            )

        unique_facilities = 0

        if "facility_id" in data.columns:

            unique_facilities = int(
                data["facility_id"].nunique()
            )

        # ------------------------------------------------------
        # Active Devices
        #
        # A device is considered active when it has
        # at least one operational record.
        # ------------------------------------------------------

        active_devices = unique_devices

        # ------------------------------------------------------
        # Anomaly Analysis
        # ------------------------------------------------------

        anomaly_analysis = (
            self._get_anomaly_analysis(
                data
            )
        )

        anomaly_count = (
            anomaly_analysis[
                "anomaly_count"
            ]
        )

        anomaly_rate = (
            anomaly_analysis[
                "anomaly_rate_percent"
            ]
        )

        # ------------------------------------------------------
        # Savings
        # ------------------------------------------------------

        (
            estimated_savings_percent,
            estimated_energy_savings_kwh,
        ) = self._calculate_savings(
            data,
            anomaly_rate,
        )

        # ------------------------------------------------------
        # Risk
        # ------------------------------------------------------

        overall_risk = (
            self._calculate_risk(
                data,
                anomaly_rate,
            )
        )

        # ------------------------------------------------------
        # Return
        # ------------------------------------------------------

        return {

            "total_energy_kwh":
                round(
                    total_energy,
                    2,
                ),

            "average_energy_kwh":
                round(
                    average_energy,
                    2,
                ),

            "peak_energy_kwh":
                round(
                    peak_energy,
                    2,
                ),

            "minimum_energy_kwh":
                round(
                    minimum_energy,
                    2,
                ),

            "total_facilities":
                unique_facilities,

            "total_devices":
                unique_devices,

            "active_devices":
                active_devices,

            "total_records":
                int(len(data)),

            "anomaly_count":
                anomaly_count,

            "anomaly_rate_percent":
                anomaly_rate,

            "estimated_savings_percent":
                estimated_savings_percent,

            "estimated_energy_savings_kwh":
                estimated_energy_savings_kwh,

            "overall_risk":
                overall_risk,
        }

    def energy_trend(
        self,
        dataframe: pd.DataFrame,
        granularity: str = "hour",
    ) -> dict:

        if dataframe.empty:
            raise ValueError(
                "No operational data available."
            )

        data = dataframe.copy()

        # -----------------------------------------
        # Validate timestamp
        # -----------------------------------------

        if "timestamp" not in data.columns:
            raise ValueError(
                "Timestamp column is required."
            )

        data["timestamp"] = pd.to_datetime(
            data["timestamp"],
            errors="coerce",
        )

        # -----------------------------------------
        # Validate energy
        # -----------------------------------------

        if "energy_kwh" not in data.columns:
            raise ValueError(
                "Energy column is required."
            )

        data["energy_kwh"] = pd.to_numeric(
            data["energy_kwh"],
            errors="coerce",
        )

        data = data.dropna(
            subset=[
                "timestamp",
                "energy_kwh",
            ]
        )

        if data.empty:
            raise ValueError(
                "No valid timestamp or energy data available."
            )

        data = data.sort_values(
            "timestamp"
        )

        # -----------------------------------------
        # Group by time
        # -----------------------------------------

        if granularity == "hour":

            data["period"] = (
                data["timestamp"]
                .dt.floor("h")
            )

        elif granularity == "day":

            data["period"] = (
                data["timestamp"]
                .dt.floor("D")
            )

        else:

            raise ValueError(
                "Granularity must be 'hour' or 'day'."
            )

        # -----------------------------------------
        # Aggregate energy
        # -----------------------------------------

        grouped = (
            data
            .groupby("period")["energy_kwh"]
            .sum()
            .reset_index()
        )

        if grouped.empty:
            raise ValueError(
                "Unable to generate energy trend."
            )

        # -----------------------------------------
        # Build trend response
        # -----------------------------------------

        trend = []

        for row in grouped.itertuples():

            trend.append(
                {
                    "timestamp":
                        row.period.isoformat(),

                    "energy_kwh":
                        round(
                            float(
                                row.energy_kwh
                            ),
                            2,
                        ),
                }
            )

        # -----------------------------------------
        # Statistics
        # -----------------------------------------

        average_energy = float(
            grouped["energy_kwh"].mean()
        )

        peak_energy = float(
            grouped["energy_kwh"].max()
        )

        return {
            "granularity": granularity,

            "total_points": len(
                trend
            ),

            "average_energy_kwh":
                round(
                    average_energy,
                    2,
                ),

            "peak_energy_kwh":
                round(
                    peak_energy,
                    2,
                ),

            "trend": trend,
        }