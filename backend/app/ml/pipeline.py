import pandas as pd

from app.ml.validator import (
    DatasetValidator,
)


class MLPipeline:

    @staticmethod
    def preprocess(
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:

        data = dataframe.copy()

        # Timestamp
        data["timestamp"] = pd.to_datetime(
            data["timestamp"],
            errors="coerce",
        )

        data = data.dropna(
            subset=["timestamp"]
        )

        # Energy
        data["energy_kwh"] = pd.to_numeric(
            data["energy_kwh"],
            errors="coerce",
        )

        data["energy_kwh"] = (
            data["energy_kwh"]
            .interpolate(
                limit_direction="both"
            )
            .ffill()
            .bfill()
        )

        # Remove invalid negative values
        data = data[
            data["energy_kwh"] >= 0
        ]

        # Sort chronologically
        data = data.sort_values(
            "timestamp"
        )

        # Remove duplicate timestamps
        data = data.drop_duplicates(
            subset=["timestamp"],
            keep="last",
        )

        data = data.reset_index(
            drop=True
        )

        return data

    @classmethod
    def run(
        cls,
        dataframe: pd.DataFrame,
    ) -> dict:

        validation = (
            DatasetValidator.validate(
                dataframe
            )
        )

        if not validation["valid"]:

            raise ValueError(
                "Dataset validation failed: "
                + "; ".join(
                    validation["errors"]
                )
            )

        processed = cls.preprocess(
            dataframe
        )

        return {
            "validation": validation,
            "processed_data": processed,
            "rows_before": len(dataframe),
            "rows_after": len(processed),
        }