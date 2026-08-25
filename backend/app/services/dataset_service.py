from io import BytesIO

import pandas as pd


REQUIRED_COLUMNS = {
    "timestamp",
    "facility_id",
    "device_id",
    "energy_kwh",
}

OPTIONAL_COLUMNS = {
    "operational_load",
    "temperature_c",
    "utilization_percent",
}


def validate_dataset(file_content: bytes) -> tuple[pd.DataFrame, list[str]]:

    errors: list[str] = []

    try:
        dataframe = pd.read_csv(
            BytesIO(file_content)
        )
    except Exception as exc:
        return pd.DataFrame(), [
            f"Unable to read CSV file: {exc}"
        ]

    if dataframe.empty:
        return pd.DataFrame(), [
            "CSV file is empty"
        ]

    dataframe.columns = (
        dataframe.columns
        .str.strip()
        .str.lower()
    )

    missing_columns = REQUIRED_COLUMNS - set(
        dataframe.columns
    )

    if missing_columns:
        errors.append(
            "Missing required columns: "
            + ", ".join(sorted(missing_columns))
        )

    if errors:
        return dataframe, errors

    dataframe["timestamp"] = pd.to_datetime(
        dataframe["timestamp"],
        errors="coerce",
    )

    invalid_timestamps = dataframe["timestamp"].isna()

    if invalid_timestamps.any():
        errors.append(
            f"{invalid_timestamps.sum()} invalid timestamp rows"
        )

    dataframe["energy_kwh"] = pd.to_numeric(
        dataframe["energy_kwh"],
        errors="coerce",
    )

    invalid_energy = dataframe["energy_kwh"].isna()

    if invalid_energy.any():
        errors.append(
            f"{invalid_energy.sum()} invalid energy_kwh rows"
        )

    dataframe["facility_id"] = pd.to_numeric(
        dataframe["facility_id"],
        errors="coerce",
    )

    dataframe["device_id"] = pd.to_numeric(
        dataframe["device_id"],
        errors="coerce",
    )

    invalid_facility = dataframe["facility_id"].isna()
    invalid_device = dataframe["device_id"].isna()

    if invalid_facility.any():
        errors.append(
            f"{invalid_facility.sum()} invalid facility_id rows"
        )

    if invalid_device.any():
        errors.append(
            f"{invalid_device.sum()} invalid device_id rows"
        )

    dataframe = dataframe.dropna(
        subset=[
            "timestamp",
            "facility_id",
            "device_id",
            "energy_kwh",
        ]
    )

    dataframe = dataframe.drop_duplicates(
        subset=[
            "timestamp",
            "facility_id",
            "device_id",
        ]
    )

    dataframe = dataframe.sort_values(
        "timestamp"
    )

    return dataframe, errors