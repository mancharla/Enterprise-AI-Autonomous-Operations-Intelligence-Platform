import numpy as np
import pandas as pd

from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


class AnomalyDetector:

    MIN_RECORDS = 30

    def __init__(
        self,
        contamination: float = 0.02,
    ):
        if not 0 < contamination < 0.5:
            raise ValueError(
                "Contamination must be between 0 and 0.5."
            )

        self.contamination = contamination

        self.scaler = StandardScaler()

        self.model = IsolationForest(
            n_estimators=200,
            contamination=contamination,
            random_state=42,
            n_jobs=-1,
        )

    @staticmethod
    def create_features(
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:

        if dataframe.empty:
            raise ValueError(
                "No data available for anomaly detection."
            )

        data = dataframe.copy()

        # -----------------------------------------
        # Timestamp
        # -----------------------------------------

        data["timestamp"] = pd.to_datetime(
            data["timestamp"],
            errors="coerce",
        )

        data = data.dropna(
            subset=["timestamp"]
        )

        if data.empty:
            raise ValueError(
                "No valid timestamps found."
            )

        data = data.sort_values(
            "timestamp"
        ).reset_index(drop=True)

        # -----------------------------------------
        # Required numeric columns
        # -----------------------------------------

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
                    method="linear",
                    limit_direction="both",
                )
                .ffill()
                .bfill()
            )

            data[column] = (
                data[column]
                .replace(
                    [np.inf, -np.inf],
                    np.nan,
                )
                .fillna(0.0)
            )

        # -----------------------------------------
        # Time features
        # -----------------------------------------

        data["hour"] = (
            data["timestamp"].dt.hour
        )

        data["day_of_week"] = (
            data["timestamp"].dt.dayofweek
        )

        # -----------------------------------------
        # Rolling energy statistics
        # -----------------------------------------

        data["rolling_mean_24"] = (
            data["energy_kwh"]
            .rolling(
                window=24,
                min_periods=1,
            )
            .mean()
        )

        data["rolling_std_24"] = (
            data["energy_kwh"]
            .rolling(
                window=24,
                min_periods=2,
            )
            .std()
            .fillna(0.0)
        )

        # -----------------------------------------
        # Energy deviation
        # -----------------------------------------

        data["energy_deviation"] = (
            data["energy_kwh"]
            - data["rolling_mean_24"]
        )

        # -----------------------------------------
        # Energy z-score
        # -----------------------------------------

        data["energy_zscore"] = np.where(
            data["rolling_std_24"] > 0,
            data["energy_deviation"]
            / data["rolling_std_24"],
            0.0,
        )

        data["energy_zscore"] = (
            pd.Series(
                data["energy_zscore"]
            )
            .replace(
                [np.inf, -np.inf],
                np.nan,
            )
            .fillna(0.0)
        )

        return data

    def detect(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:

        data = self.create_features(
            dataframe
        )

        if len(data) < self.MIN_RECORDS:
            raise ValueError(
                f"At least {self.MIN_RECORDS} "
                "records are required for anomaly "
                "detection."
            )

        feature_columns = [
            "energy_kwh",
            "operational_load",
            "temperature_c",
            "utilization_percent",
            "energy_deviation",
            "energy_zscore",
        ]

        X = data[
            feature_columns
        ].astype(float)

        X = X.replace(
            [np.inf, -np.inf],
            np.nan,
        )

        X = X.fillna(0.0)

        # -----------------------------------------
        # Scaling
        # -----------------------------------------

        X_scaled = (
            self.scaler.fit_transform(X)
        )

        # -----------------------------------------
        # Isolation Forest
        # -----------------------------------------

        predictions = (
            self.model.fit_predict(
                X_scaled
            )
        )

        raw_scores = (
            self.model.decision_function(
                X_scaled
            )
        )

        data["is_anomaly"] = (
            predictions == -1
        )

        data["raw_score"] = raw_scores

        # -----------------------------------------
        # Normalize anomaly score
        # -----------------------------------------

        min_score = float(
            np.min(raw_scores)
        )

        max_score = float(
            np.max(raw_scores)
        )

        if np.isclose(
            max_score,
            min_score,
        ):
            data["anomaly_score"] = 0.0

        else:
            data["anomaly_score"] = (
                1.0
                - (
                    raw_scores
                    - min_score
                )
                / (
                    max_score
                    - min_score
                )
            )

        data["anomaly_score"] = (
            data["anomaly_score"]
            .clip(0.0, 1.0)
            .round(4)
        )

        # -----------------------------------------
        # Severity
        # -----------------------------------------

        data["severity"] = data.apply(
            self._severity,
            axis=1,
        )

        # -----------------------------------------
        # Anomaly type
        # -----------------------------------------

        data["anomaly_type"] = data.apply(
            self._classify_anomaly,
            axis=1,
        )

        return data

    @staticmethod
    def _severity(row) -> str:

        if not row["is_anomaly"]:
            return "normal"

        score = float(
            row["anomaly_score"]
        )

        if score >= 0.85:
            return "critical"

        if score >= 0.65:
            return "high"

        if score >= 0.45:
            return "medium"

        return "low"

    @staticmethod
    def _classify_anomaly(row) -> str:

        if not row["is_anomaly"]:
            return "normal"

        zscore = abs(
            float(
                row["energy_zscore"]
            )
        )

        energy = float(
            row["energy_kwh"]
        )

        rolling_mean = float(
            row["rolling_mean_24"]
        )

        temperature = float(
            row["temperature_c"]
        )

        utilization = float(
            row["utilization_percent"]
        )

        # -----------------------------------------
        # Extreme consumption
        # -----------------------------------------

        if zscore >= 4:
            return "extreme_usage"

        # -----------------------------------------
        # Temperature related
        # -----------------------------------------

        if (
            temperature > 35
            and energy
            > rolling_mean * 1.25
        ):
            return "temperature_related"

        # -----------------------------------------
        # Inefficient usage
        # -----------------------------------------

        if (
            utilization < 20
            and energy
            > rolling_mean * 1.25
        ):
            return "inefficient_usage"

        # -----------------------------------------
        # General anomaly
        # -----------------------------------------

        return "unusual_behavior"