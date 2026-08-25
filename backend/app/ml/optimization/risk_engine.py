class ForecastRiskEngine:

    @staticmethod
    def classify(
        current_energy: float,
        peak_energy: float,
        upper_bound: float,
    ):

        if current_energy <= 0:
            return {
                "risk_level": "UNKNOWN",
                "risk_score": 0.0,
                "reason": "Current energy baseline is unavailable."
            }

        increase_percent = (
            (peak_energy - current_energy)
            / current_energy
        ) * 100

        uncertainty_percent = (
            (upper_bound - peak_energy)
            / peak_energy
        ) * 100 if peak_energy > 0 else 0

        risk_score = (
            increase_percent * 0.7
            + uncertainty_percent * 0.3
        )

        if risk_score >= 40:
            level = "CRITICAL"

        elif risk_score >= 25:
            level = "HIGH"

        elif risk_score >= 10:
            level = "MEDIUM"

        else:
            level = "LOW"

        return {
            "risk_level": level,
            "risk_score": round(
                min(risk_score, 100),
                2,
            ),
            "forecast_increase_percent": round(
                increase_percent,
                2,
            ),
            "uncertainty_percent": round(
                uncertainty_percent,
                2,
            ),
            "reason": (
                f"Forecast peak is "
                f"{increase_percent:.2f}% above "
                f"the current energy level."
            ),
        }