import csv
import math
import random
from datetime import datetime, timedelta
from pathlib import Path


random.seed(42)


OUTPUT_FILE = Path(__file__).parent / "operational_data.csv"


FACILITIES = [
    {
        "id": 1,
        "name": "Hyderabad Operations Center",
    },
    {
        "id": 2,
        "name": "Bengaluru Technology Center",
    },
    {
        "id": 3,
        "name": "Chennai Manufacturing Hub",
    },
    {
        "id": 4,
        "name": "Pune Distribution Center",
    },
]


DEVICES = [
    # Facility 1
    {"id": 1, "facility_id": 1, "type": "HVAC", "base": 70},
    {"id": 2, "facility_id": 1, "type": "SERVER", "base": 55},
    {"id": 3, "facility_id": 1, "type": "LIGHTING", "base": 30},

    # Facility 2
    {"id": 4, "facility_id": 2, "type": "HVAC", "base": 80},
    {"id": 5, "facility_id": 2, "type": "SERVER", "base": 65},
    {"id": 6, "facility_id": 2, "type": "LIGHTING", "base": 35},

    # Facility 3
    {"id": 7, "facility_id": 3, "type": "HVAC", "base": 90},
    {"id": 8, "facility_id": 3, "type": "MOTOR", "base": 75},
    {"id": 9, "facility_id": 3, "type": "LIGHTING", "base": 40},

    # Facility 4
    {"id": 10, "facility_id": 4, "type": "HVAC", "base": 60},
    {"id": 11, "facility_id": 4, "type": "SERVER", "base": 50},
    {"id": 12, "facility_id": 4, "type": "MOTOR", "base": 70},
]


START_DATE = datetime(2026, 5, 1)
DAYS = 90


def temperature(hour: int, day: int) -> float:
    daily = 5 * math.sin(
        (hour - 8) * math.pi / 12
    )

    seasonal = 2 * math.sin(
        day * math.pi / 45
    )

    return round(
        29 + daily + seasonal + random.gauss(0, 1),
        2,
    )


def daily_factor(hour: int) -> float:

    if 0 <= hour < 6:
        return 0.55

    if 6 <= hour < 9:
        return 0.75

    if 9 <= hour < 13:
        return 1.05

    if 13 <= hour < 17:
        return 1.15

    if 17 <= hour < 21:
        return 1.30

    return 0.85


def weekly_factor(day_of_week: int) -> float:

    if day_of_week >= 5:
        return 0.70

    return 1.0


def calculate_energy(
    device: dict,
    hour: int,
    day: int,
    temperature_c: float,
) -> tuple[float, float, float]:

    base = device["base"]

    daily = daily_factor(hour)

    weekly = weekly_factor(
        (START_DATE + timedelta(days=day)).weekday()
    )

    temperature_effect = 1.0

    if device["type"] == "HVAC":
        temperature_effect += max(
            temperature_c - 25,
            0,
        ) * 0.035

    if device["type"] == "SERVER":
        temperature_effect += max(
            temperature_c - 27,
            0,
        ) * 0.015

    load = (
        base
        * daily
        * weekly
        * temperature_effect
    )

    noise = random.gauss(
        0,
        base * 0.04,
    )

    energy = max(
        load + noise,
        5,
    )

    # Introduce occasional operational spikes.
    if random.random() < 0.008:
        energy *= random.uniform(
            1.5,
            2.2,
        )

    utilization = min(
        100,
        max(
            10,
            daily * weekly * 75
            + random.gauss(0, 5),
        ),
    )

    operational_load = min(
        100,
        max(
            5,
            utilization
            + random.gauss(0, 4),
        ),
    )

    return (
        round(energy, 2),
        round(operational_load, 2),
        round(utilization, 2),
    )


def generate():

    rows = []

    for day in range(DAYS):

        for hour in range(24):

            timestamp = (
                START_DATE
                + timedelta(
                    days=day,
                    hours=hour,
                )
            )

            temperature_c = temperature(
                hour,
                day,
            )

            for device in DEVICES:

                energy, operational_load, utilization = (
                    calculate_energy(
                        device=device,
                        hour=hour,
                        day=day,
                        temperature_c=temperature_c,
                    )
                )

                rows.append(
                    {
                        "timestamp": timestamp.strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        "facility_id": device[
                            "facility_id"
                        ],
                        "device_id": device["id"],
                        "energy_kwh": energy,
                        "operational_load": operational_load,
                        "temperature_c": temperature_c,
                        "utilization_percent": utilization,
                    }
                )

    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "timestamp",
                "facility_id",
                "device_id",
                "energy_kwh",
                "operational_load",
                "temperature_c",
                "utilization_percent",
            ],
        )

        writer.writeheader()
        writer.writerows(rows)

    print(
        f"Generated {len(rows):,} operational records."
    )

    print(
        f"Output: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    generate()