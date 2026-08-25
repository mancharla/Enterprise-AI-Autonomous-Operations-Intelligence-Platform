import pandas as pd


class DatasetValidator:

    REQUIRED_COLUMNS = {
        "timestamp",
        "energy_kwh",
    }

    @classmethod
    def validate(
        cls,
        dataframe: pd.DataFrame,
    ) -> dict:

        errors = []
        warnings = []

        if dataframe.empty:
            errors.append(
                "Dataset is empty."
            )

            return {
                "valid": False,
                "errors": errors,
                "warnings": warnings,
                "rows": 0,
                "columns": [],
            }

        columns = set(
            dataframe.columns
        )

        missing_columns = (
            cls.REQUIRED_COLUMNS
            - columns
        )

        if missing_columns:
            errors.append(
                "Missing required columns: "
                + ", ".join(
                    sorted(missing_columns)
                )
            )

        # -----------------------------------------
        # Timestamp validation
        # -----------------------------------------

        if "timestamp" in dataframe.columns:

            timestamps = pd.to_datetime(
                dataframe["timestamp"],
                errors="coerce",
            )

            invalid_timestamps = int(
                timestamps.isna().sum()
            )

            if invalid_timestamps > 0:

                errors.append(
                    f"{invalid_timestamps} invalid "
                    "timestamp values found."
                )

        # -----------------------------------------
        # Energy validation
        # -----------------------------------------

        if "energy_kwh" in dataframe.columns:

            energy = pd.to_numeric(
                dataframe["energy_kwh"],
                errors="coerce",
            )

            invalid_energy = int(
                energy.isna().sum()
            )

            if invalid_energy > 0:

                warnings.append(
                    f"{invalid_energy} invalid "
                    "energy values found."
                )

            negative_energy = int(
                (energy < 0).sum()
            )

            if negative_energy > 0:

                errors.append(
                    f"{negative_energy} negative "
                    "energy values found."
                )

        # -----------------------------------------
        # Duplicate timestamps
        # -----------------------------------------

        if "timestamp" in dataframe.columns:

            duplicate_count = int(
                dataframe["timestamp"]
                .duplicated()
                .sum()
            )

            if duplicate_count > 0:

                warnings.append(
                    f"{duplicate_count} duplicate "
                    "timestamps found."
                )

        # -----------------------------------------
        # Missing values
        # -----------------------------------------

        missing_values = int(
            dataframe.isna()
            .sum()
            .sum()
        )

        if missing_values > 0:

            warnings.append(
                f"{missing_values} missing "
                "values detected."
            )

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "rows": len(dataframe),
            "columns": list(
                dataframe.columns
            ),
        }