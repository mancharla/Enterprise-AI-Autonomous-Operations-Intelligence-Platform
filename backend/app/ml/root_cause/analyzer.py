import pandas as pd
import numpy as np


class RootCauseAnalyzer:

    FACTORS = [
        "operational_load",
        "temperature_c",
        "utilization_percent",
    ]

    def analyze(
        self,
        dataframe: pd.DataFrame,
    ) -> dict:

        data = dataframe.copy()

        data["timestamp"] = pd.to_datetime(
            data["timestamp"]
        )

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
                .interpolate()
                .ffill()
                .bfill()
                .fillna(0)
            )

        if len(data) < 30:
            raise ValueError(
                "At least 30 records are required "
                "for root cause analysis."
            )

        # --------------------------------
        # Historical baselines
        # --------------------------------

        baseline = data[
            "energy_kwh"
        ].mean()

        latest = data.iloc[-1]

        current_energy = float(
            latest["energy_kwh"]
        )

        energy_deviation = (
            (
                current_energy
                - baseline
            )
            / baseline
            * 100
            if baseline
            else 0
        )

        # --------------------------------
        # Correlation analysis
        # --------------------------------

        correlation_columns = [
            "energy_kwh",
            *self.FACTORS,
        ]

        correlation_matrix = (
            data[
                correlation_columns
            ]
            .corr()
        )

        correlations = {}

        for factor in self.FACTORS:

            value = correlation_matrix.loc[
                "energy_kwh",
                factor,
            ]

            if pd.isna(value):
                value = 0

            correlations[factor] = round(
                float(value),
                4,
            )

        # --------------------------------
        # Contribution scores
        # --------------------------------

        contribution_scores = {}

        for factor in self.FACTORS:

            correlation = abs(
                correlations[factor]
            )

            latest_value = float(
                latest[factor]
            )

            factor_mean = float(
                data[factor].mean()
            )

            factor_std = float(
                data[factor].std()
            )

            if factor_std > 0:

                deviation = abs(
                    (
                        latest_value
                        - factor_mean
                    )
                    / factor_std
                )

            else:
                deviation = 0

            score = (
                correlation * 0.6
                + min(
                    deviation / 3,
                    1,
                ) * 0.4
            )

            contribution_scores[factor] = round(
                float(score),
                4,
            )

        # --------------------------------
        # Rank contributing factors
        # --------------------------------

        ranked_factors = sorted(
            contribution_scores.items(),
            key=lambda item: item[1],
            reverse=True,
        )

        top_factor = (
            ranked_factors[0][0]
            if ranked_factors
            else None
        )

        top_score = (
            ranked_factors[0][1]
            if ranked_factors
            else 0
        )

        # --------------------------------
        # Determine root cause
        # --------------------------------

        if top_factor == "temperature_c":

            root_cause = (
                "Elevated temperature is strongly "
                "associated with increased energy "
                "consumption."
            )

            recommended_action = (
                "Inspect cooling systems and "
                "consider reducing cooling load "
                "during non-critical periods."
            )

        elif top_factor == "operational_load":

            root_cause = (
                "Increased operational load is "
                "the strongest contributor to the "
                "energy anomaly."
            )

            recommended_action = (
                "Redistribute operational workload "
                "to available facilities or devices."
            )

        elif top_factor == "utilization_percent":

            root_cause = (
                "High utilization is strongly "
                "associated with abnormal energy "
                "consumption."
            )

            recommended_action = (
                "Review workload scheduling and "
                "device utilization patterns."
            )

        else:

            root_cause = (
                "No dominant contributing factor "
                "was identified."
            )

            recommended_action = (
                "Continue monitoring the device "
                "for recurring anomalous behavior."
            )

        # --------------------------------
        # Confidence
        # --------------------------------

        confidence = min(
            1.0,
            top_score
            + min(
                abs(energy_deviation) / 100,
                0.3,
            ),
        )

        return {
            "current_energy_kwh": round(
                current_energy,
                2,
            ),
            "baseline_energy_kwh": round(
                float(baseline),
                2,
            ),
            "energy_deviation_percent": round(
                float(energy_deviation),
                2,
            ),
            "correlations": correlations,
            "contribution_scores":
                contribution_scores,
            "ranked_factors": [
                {
                    "factor": factor,
                    "score": score,
                }
                for factor, score
                in ranked_factors
            ],
            "primary_factor": top_factor,
            "confidence": round(
                float(confidence),
                4,
            ),
            "root_cause": root_cause,
            "recommended_action":
                recommended_action,
        }