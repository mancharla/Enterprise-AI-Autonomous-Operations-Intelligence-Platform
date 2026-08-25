import pandas as pd


class DashboardService:

    def build(
        self,
        dataframe: pd.DataFrame,
        analytics: dict,
        anomaly_summary: dict,
        optimization: dict,
        risk: dict,
    ) -> dict:

        if dataframe.empty:
            raise ValueError(
                "No operational data available."
            )

        data = dataframe.copy()

        # ==========================================
        # Normalize numeric columns
        # ==========================================

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

        # ==========================================
        # Organization
        # ==========================================

        total_facilities = int(
            data["facility_id"].nunique()
            if "facility_id" in data.columns
            else 0
        )

        total_devices = int(
            data["device_id"].nunique()
            if "device_id" in data.columns
            else 0
        )

        total_records = int(
            len(data)
        )

        # ==========================================
        # Energy
        # ==========================================

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

        energy = {
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
        }

        # ==========================================
        # Operations
        # ==========================================

        average_load = float(
            data["operational_load"].mean()
        )

        average_utilization = float(
            data["utilization_percent"].mean()
        )

        average_temperature = float(
            data["temperature_c"].mean()
        )

        operations = {
            "average_load":
                round(
                    average_load,
                    2,
                ),

            "average_utilization_percent":
                round(
                    average_utilization,
                    2,
                ),

            "average_temperature_c":
                round(
                    average_temperature,
                    2,
                ),
        }

        # ==========================================
        # Risk
        # ==========================================

        risk_data = {
            "overall_risk":
                risk.get(
                    "overall_risk",
                    "LOW",
                ),

            "risk_score":
                round(
                    float(
                        risk.get(
                            "risk_score",
                            0,
                        )
                    ),
                    2,
                ),
        }

        # ==========================================
        # Anomalies
        # ==========================================

        anomalies = {
            "total":
                int(
                    anomaly_summary.get(
                        "anomaly_count",
                        0,
                    )
                ),

            "critical":
                int(
                    anomaly_summary.get(
                        "critical_count",
                        0,
                    )
                ),

            "high":
                int(
                    anomaly_summary.get(
                        "high_count",
                        0,
                    )
                ),

            "medium":
                int(
                    anomaly_summary.get(
                        "medium_count",
                        0,
                    )
                ),

            "low":
                int(
                    anomaly_summary.get(
                        "low_count",
                        0,
                    )
                ),
        }

        # ==========================================
        # Optimization
        # ==========================================

        optimization_data = {
            "recommended_strategy":
                optimization.get(
                    "recommended_strategy",
                    "energy_reduction",
                ),

            "expected_savings_percent":
                round(
                    float(
                        optimization.get(
                            "expected_savings_percent",
                            0,
                        )
                    ),
                    2,
                ),

            "expected_energy_savings_kwh":
                round(
                    float(
                        optimization.get(
                            "expected_energy_savings_kwh",
                            0,
                        )
                    ),
                    2,
                ),

            "confidence":
                round(
                    float(
                        optimization.get(
                            "confidence",
                            0,
                        )
                    ),
                    2,
                ),
        }

        # ==========================================
        # Intelligence
        # ==========================================

        insights = []

        utilization = operations[
            "average_utilization_percent"
        ]

        anomaly_count = anomalies[
            "total"
        ]

        risk_level = risk_data[
            "overall_risk"
        ]

        savings = optimization_data[
            "expected_savings_percent"
        ]

        # ------------------------------------------
        # Utilization insight
        # ------------------------------------------

        if utilization >= 85:

            insights.append(
                "Average device utilization is high. "
                "Workload redistribution should be considered."
            )

        elif utilization >= 70:

            insights.append(
                "Device utilization is moderately high. "
                "Monitor capacity and workload distribution."
            )

        else:

            insights.append(
                "Device utilization is currently within "
                "normal operating levels."
            )

        # ------------------------------------------
        # Load insight
        # ------------------------------------------

        if average_load >= 80:

            insights.append(
                "Operational load is high and may increase "
                "future energy consumption."
            )

        elif average_load >= 65:

            insights.append(
                "Operational load is moderately high. "
                "Consider monitoring workload distribution."
            )

        # ------------------------------------------
        # Temperature insight
        # ------------------------------------------

        if average_temperature >= 35:

            insights.append(
                "Average operating temperature is high. "
                "Cooling optimization should be considered."
            )

        # ------------------------------------------
        # Anomaly insight
        # ------------------------------------------

        if anomaly_count > 0:

            insights.append(
                f"{anomaly_count} anomalous operational "
                "records require attention."
            )

        else:

            insights.append(
                "No significant operational anomalies "
                "were detected."
            )

        # ------------------------------------------
        # Risk insight
        # ------------------------------------------

        insights.append(
            f"Overall operational risk is "
            f"{risk_level}."
        )

        # ------------------------------------------
        # Optimization insight
        # ------------------------------------------

        if savings > 0:

            insights.append(
                f"The recommended optimization strategy "
                f"could reduce energy consumption by "
                f"approximately {savings}%."
            )

        # ==========================================
        # Final response
        # ==========================================

        return {
            "organization": {
                "total_facilities":
                    total_facilities,

                "total_devices":
                    total_devices,

                "total_records":
                    total_records,
            },

            "energy":
                energy,

            "operations":
                operations,

            "risk":
                risk_data,

            "anomalies":
                anomalies,

            "optimization":
                optimization_data,

            "insights":
                insights,
        }