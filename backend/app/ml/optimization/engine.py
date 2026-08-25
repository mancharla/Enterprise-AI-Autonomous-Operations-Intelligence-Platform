import pandas as pd


class OptimizationEngine:

    STRATEGIES = {
        "workload_redistribution": {
            "description": (
                "Redistribute workload from highly utilized "
                "devices to devices with available capacity."
            ),
            "base_savings": 8.0,
            "base_cost": 12.0,
            "base_risk": 15.0,
        },
        "cooling_optimization": {
            "description": (
                "Optimize cooling systems and reduce "
                "non-critical cooling consumption."
            ),
            "base_savings": 10.0,
            "base_cost": 18.0,
            "base_risk": 12.0,
        },
        "peak_shifting": {
            "description": (
                "Shift flexible workloads away from "
                "predicted peak consumption periods."
            ),
            "base_savings": 12.0,
            "base_cost": 10.0,
            "base_risk": 10.0,
        },
        "predictive_maintenance": {
            "description": (
                "Schedule predictive maintenance for "
                "devices showing abnormal behavior."
            ),
            "base_savings": 7.0,
            "base_cost": 20.0,
            "base_risk": 18.0,
        },
        "capacity_optimization": {
            "description": (
                "Increase available capacity or redistribute "
                "operations before demand exceeds safe limits."
            ),
            "base_savings": 5.0,
            "base_cost": 30.0,
            "base_risk": 20.0,
        },
        "energy_reduction": {
            "description": (
                "Reduce non-critical energy consumption "
                "during periods of high utilization."
            ),
            "base_savings": 9.0,
            "base_cost": 8.0,
            "base_risk": 8.0,
        },
    }

    def optimize(
        self,
        dataframe: pd.DataFrame,
        forecast: list[dict],
        forecast_model: str,
        forecast_horizon: int,
    ) -> dict:

        if dataframe is None or dataframe.empty:
            raise ValueError(
                "No operational data available."
            )

        if not forecast:
            raise ValueError(
                "No forecast data available."
            )

        data = self._prepare_operational_data(
            dataframe
        )

        latest = data.iloc[-1]

        current_energy = float(
            latest["energy_kwh"]
        )

        operational_load = float(
            latest["operational_load"]
        )

        utilization = float(
            latest["utilization_percent"]
        )

        temperature = float(
            latest["temperature_c"]
        )

        forecast_df = self._prepare_forecast(
            forecast
        )

        if forecast_df.empty:
            raise ValueError(
                "Forecast contains no valid values."
            )

        # ==================================================
        # FORECAST METRICS
        # ==================================================

        average_predicted = float(
            forecast_df["predicted_value"].mean()
        )

        peak_index = forecast_df[
            "predicted_value"
        ].idxmax()

        peak_row = forecast_df.loc[
            peak_index
        ]

        peak_predicted = float(
            peak_row["predicted_value"]
        )

        lower_bound = float(
            forecast_df["lower_bound"].min()
        )

        upper_bound = float(
            forecast_df["upper_bound"].max()
        )

        peak_time = pd.to_datetime(
            peak_row["timestamp"]
        ).to_pydatetime()

        total_forecast_energy = float(
            forecast_df["predicted_value"].sum()
        )

        # ==================================================
        # FORECAST CHANGE
        # ==================================================

        if current_energy > 0:

            forecast_increase = (
                (
                    average_predicted
                    - current_energy
                )
                / current_energy
            ) * 100

        else:

            forecast_increase = 0.0

        # ==================================================
        # UNCERTAINTY
        # ==================================================

        if average_predicted > 0:

            uncertainty = (
                (
                    upper_bound
                    - lower_bound
                )
                / average_predicted
            ) * 100

        else:

            uncertainty = 0.0

        uncertainty = max(
            uncertainty,
            0.0,
        )

        # ==================================================
        # RISK
        # ==================================================

        risk_score = self._calculate_risk(
            forecast_increase=forecast_increase,
            utilization=utilization,
            operational_load=operational_load,
            temperature=temperature,
            uncertainty=uncertainty,
        )

        risk_level = self._risk_level(
            risk_score
        )

        risk_reason = self._risk_reason(
            risk_level,
            forecast_increase,
            utilization,
            temperature,
            uncertainty,
        )

        # ==================================================
        # STRATEGY EVALUATION
        # ==================================================

        ranking = []

        for strategy, config in self.STRATEGIES.items():

            evaluation = self._evaluate_strategy(
                strategy=strategy,
                config=config,
                forecast_increase=forecast_increase,
                utilization=utilization,
                operational_load=operational_load,
                temperature=temperature,
                uncertainty=uncertainty,
                forecast_df=forecast_df,
                total_forecast_energy=total_forecast_energy,
                forecast_horizon=forecast_horizon,
            )

            ranking.append(evaluation)

        # ==================================================
        # RANK STRATEGIES
        # ==================================================

        ranking.sort(
            key=lambda item: item["decision_score"],
            reverse=True,
        )

        recommended = ranking[0]

        # ==================================================
        # CONFIDENCE
        # ==================================================

        confidence = self._calculate_confidence(
            uncertainty=uncertainty,
            forecast_model=forecast_model,
            forecast_horizon=forecast_horizon,
            strategy_score=recommended[
                "decision_score"
            ],
        )

        # ==================================================
        # EXPLANATION
        # ==================================================

        explanation = self._build_explanation(
            strategy=recommended["strategy"],
            forecast_increase=forecast_increase,
            peak_predicted=peak_predicted,
            peak_time=peak_time,
            utilization=utilization,
            operational_load=operational_load,
            temperature=temperature,
            risk_level=risk_level,
        )

        # ==================================================
        # DECISION
        # ==================================================

        decision = {
            "action": recommended["strategy"],
            "priority": self._priority(
                risk_level
            ),
            "reason": explanation,
            "expected_savings_percent": (
                recommended[
                    "estimated_savings_percent"
                ]
            ),
            "expected_energy_savings_kwh": (
                recommended[
                    "estimated_energy_savings_kwh"
                ]
            ),
            "implementation_cost": (
                recommended[
                    "implementation_cost"
                ]
            ),
            "risk_percent": (
                recommended["risk_percent"]
            ),
            "confidence": round(
                confidence,
                2,
            ),
        }

        # ==================================================
        # FINAL RESPONSE
        # ==================================================

        return {
            "recommended_strategy":
                recommended["strategy"],

            "recommendation":
                (
                    f"Recommended strategy: "
                    f"{recommended['strategy']}. "
                    f"{recommended['description']}"
                ),

            "decision":
                decision,

            "ranking":
                ranking,

            "expected_savings_percent":
                recommended[
                    "estimated_savings_percent"
                ],

            "expected_energy_savings_kwh":
                recommended[
                    "estimated_energy_savings_kwh"
                ],

            "confidence":
                round(
                    confidence,
                    2,
                ),

            "forecast": {
                "model":
                    forecast_model,

                "horizon_hours":
                    forecast_horizon,

                "forecast_points":
                    len(forecast_df),

                "total_forecast_energy_kwh":
                    round(
                        total_forecast_energy,
                        2,
                    ),

                "average_predicted_energy_kwh":
                    round(
                        average_predicted,
                        2,
                    ),

                "peak_predicted_energy_kwh":
                    round(
                        peak_predicted,
                        2,
                    ),

                "peak_time":
                    peak_time,

                "forecast_increase_percent":
                    round(
                        forecast_increase,
                        2,
                    ),

                "lower_bound":
                    round(
                        lower_bound,
                        2,
                    ),

                "upper_bound":
                    round(
                        upper_bound,
                        2,
                    ),
            },

            "current_conditions": {
                "current_energy_kwh":
                    round(
                        current_energy,
                        2,
                    ),

                "operational_load":
                    round(
                        operational_load,
                        2,
                    ),

                "utilization_percent":
                    round(
                        utilization,
                        2,
                    ),

                "temperature_c":
                    round(
                        temperature,
                        2,
                    ),
            },

            "forecast_risk": {
                "risk_level":
                    risk_level,

                "risk_score":
                    risk_score,

                "forecast_increase_percent":
                    round(
                        forecast_increase,
                        2,
                    ),

                "uncertainty_percent":
                    round(
                        uncertainty,
                        2,
                    ),

                "reason":
                    risk_reason,
            },
        }

    # ======================================================
    # DATA PREPARATION
    # ======================================================

    @staticmethod
    def _prepare_operational_data(
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:

        data = dataframe.copy()

        columns = [
            "energy_kwh",
            "operational_load",
            "temperature_c",
            "utilization_percent",
        ]

        for column in columns:

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

        return data

    @staticmethod
    def _prepare_forecast(
        forecast: list[dict],
    ) -> pd.DataFrame:

        dataframe = pd.DataFrame(
            forecast
        )

        required = [
            "timestamp",
            "predicted_value",
            "lower_bound",
            "upper_bound",
        ]

        for column in required:

            if column not in dataframe.columns:
                raise ValueError(
                    f"Forecast missing required "
                    f"field: {column}"
                )

        dataframe["timestamp"] = pd.to_datetime(
            dataframe["timestamp"],
            errors="coerce",
        )

        for column in [
            "predicted_value",
            "lower_bound",
            "upper_bound",
        ]:

            dataframe[column] = pd.to_numeric(
                dataframe[column],
                errors="coerce",
            )

        dataframe = dataframe.dropna(
            subset=required
        )

        return dataframe

    # ======================================================
    # RISK
    # ======================================================

    @staticmethod
    def _calculate_risk(
        forecast_increase,
        utilization,
        operational_load,
        temperature,
        uncertainty,
    ):

        score = 0.0

        score += min(
            max(forecast_increase, 0) * 1.5,
            35,
        )

        if utilization > 85:
            score += 20
        elif utilization > 70:
            score += 10

        if operational_load > 80:
            score += 15
        elif operational_load > 65:
            score += 8

        if temperature > 35:
            score += 15
        elif temperature > 30:
            score += 7

        if uncertainty > 30:
            score += 15
        elif uncertainty > 20:
            score += 8

        return round(
            min(score, 100),
            2,
        )

    @staticmethod
    def _risk_level(
        risk_score,
    ):

        if risk_score >= 70:
            return "CRITICAL"

        if risk_score >= 45:
            return "HIGH"

        if risk_score >= 25:
            return "MEDIUM"

        return "LOW"

    # ======================================================
    # STRATEGY EVALUATION
    # ======================================================

    def _evaluate_strategy(
        self,
        strategy,
        config,
        forecast_increase,
        utilization,
        operational_load,
        temperature,
        uncertainty,
        forecast_df,
        total_forecast_energy,
        forecast_horizon,
    ):

        savings = config["base_savings"]
        cost = config["base_cost"]
        risk = config["base_risk"]

        applicability = 50.0

        # ----------------------------------------------
        # Utilization
        # ----------------------------------------------

        if utilization > 85:

            if strategy in {
                "workload_redistribution",
                "capacity_optimization",
                "energy_reduction",
            }:
                applicability += 25

        elif utilization > 70:

            if strategy in {
                "workload_redistribution",
                "energy_reduction",
            }:
                applicability += 15

        # ----------------------------------------------
        # Temperature
        # ----------------------------------------------

        if temperature > 35:

            if strategy == "cooling_optimization":
                applicability += 35
                savings += 5

        elif temperature > 30:

            if strategy == "cooling_optimization":
                applicability += 20
                savings += 3

        # ----------------------------------------------
        # Forecast growth
        # ----------------------------------------------

        if forecast_increase > 15:

            if strategy == "peak_shifting":
                applicability += 30
                savings += 5

            elif strategy == "capacity_optimization":
                applicability += 25

            elif strategy == "workload_redistribution":
                applicability += 20

        elif forecast_increase > 5:

            if strategy == "peak_shifting":
                applicability += 20

        # ----------------------------------------------
        # Operational load
        # ----------------------------------------------

        if operational_load > 80:

            if strategy == "workload_redistribution":
                applicability += 20

            elif strategy == "capacity_optimization":
                applicability += 15

            elif strategy == "predictive_maintenance":
                applicability += 20

        # ----------------------------------------------
        # Uncertainty
        # ----------------------------------------------

        if uncertainty > 30:

            risk += 8

            if strategy == "predictive_maintenance":
                applicability += 10

        # ----------------------------------------------
        # Peak detection
        # ----------------------------------------------

        peak_value = float(
            forecast_df[
                "predicted_value"
            ].max()
        )

        average_value = float(
            forecast_df[
                "predicted_value"
            ].mean()
        )

        if average_value > 0:

            peak_ratio = (
                peak_value
                / average_value
            )

        else:

            peak_ratio = 1.0

        if peak_ratio > 1.30:

            if strategy == "peak_shifting":
                applicability += 25
                savings += 3

        # ----------------------------------------------
        # Keep values valid
        # ----------------------------------------------

        applicability = min(
            applicability,
            100,
        )

        savings = min(
            savings,
            40,
        )

        # ----------------------------------------------
        # Forecast-based savings
        # ----------------------------------------------

        estimated_energy_savings = (
            total_forecast_energy
            * savings
            / 100
        )

        # ----------------------------------------------
        # Decision score
        # ----------------------------------------------

        score = (
            applicability * 0.45
            + savings * 2.5
            - risk * 0.20
            - cost * 0.15
        )

        score = max(
            0.0,
            min(
                score,
                100,
            ),
        )

        return {
            "strategy":
                strategy,

            "description":
                config["description"],

            "decision_score":
                round(
                    score,
                    2,
                ),

            "estimated_savings_percent":
                round(
                    savings,
                    2,
                ),

            "estimated_energy_savings_kwh":
                round(
                    estimated_energy_savings,
                    2,
                ),

            "operational_impact_percent":
                round(
                    max(
                        forecast_increase,
                        0,
                    ),
                    2,
                ),

            "implementation_cost":
                round(
                    cost,
                    2,
                ),

            "risk_percent":
                round(
                    risk,
                    2,
                ),

            "applicability_score":
                round(
                    applicability,
                    2,
                ),

            "peak_ratio":
                round(
                    peak_ratio,
                    2,
                ),
        }

    # ======================================================
    # CONFIDENCE
    # ======================================================

    @staticmethod
    def _calculate_confidence(
        uncertainty,
        forecast_model,
        forecast_horizon,
        strategy_score,
    ):

        confidence = 100.0

        confidence -= (
            uncertainty * 0.50
        )

        if forecast_model.lower() == "prophet":
            confidence += 5

        if forecast_horizon <= 24:
            confidence += 5

        elif forecast_horizon <= 168:
            confidence += 2

        # Stronger strategy separation increases
        # decision confidence slightly.
        confidence += (
            strategy_score * 0.05
        )

        return max(
            0.0,
            min(
                confidence,
                100.0,
            ),
        )

    # ======================================================
    # EXPLANATION
    # ======================================================

    @staticmethod
    def _build_explanation(
        strategy,
        forecast_increase,
        peak_predicted,
        peak_time,
        utilization,
        operational_load,
        temperature,
        risk_level,
    ):

        reasons = []

        if forecast_increase > 10:

            reasons.append(
                f"forecasted energy demand is "
                f"{forecast_increase:.1f}% above the "
                f"current baseline"
            )

        if utilization > 70:

            reasons.append(
                f"device utilization is "
                f"{utilization:.1f}%"
            )

        if operational_load > 65:

            reasons.append(
                f"operational load is "
                f"{operational_load:.1f}%"
            )

        if temperature > 30:

            reasons.append(
                f"temperature is "
                f"{temperature:.1f}°C"
            )

        reasons.append(
            f"forecast peak is "
            f"{peak_predicted:.2f} kWh at "
            f"{peak_time.strftime('%Y-%m-%d %H:%M')}"
        )

        if not reasons:

            return (
                f"{strategy} was selected based on "
                "current and forecasted operational conditions."
            )

        return (
            f"{strategy} was selected because "
            + ", ".join(reasons)
            + f". Current risk level is {risk_level}."
        )

    @staticmethod
    def _priority(
        risk_level,
    ):

        if risk_level == "CRITICAL":
            return "IMMEDIATE"

        if risk_level == "HIGH":
            return "HIGH"

        if risk_level == "MEDIUM":
            return "MEDIUM"

        return "LOW"

    @staticmethod
    def _risk_reason(
        risk_level,
        forecast_increase,
        utilization,
        temperature,
        uncertainty,
    ):

        reasons = []

        if forecast_increase > 10:
            reasons.append(
                "forecasted energy demand is increasing"
            )

        if utilization > 85:
            reasons.append(
                "device utilization is above 85%"
            )

        if temperature > 35:
            reasons.append(
                "temperature is above 35°C"
            )

        if uncertainty > 30:
            reasons.append(
                "forecast uncertainty is high"
            )

        if not reasons:

            return (
                "Current operational conditions "
                "and forecast risk remain within "
                "acceptable limits."
            )

        return (
            f"{risk_level} risk because "
            + ", ".join(reasons)
            + "."
        )