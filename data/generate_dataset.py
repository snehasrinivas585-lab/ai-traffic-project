"""
Traffic Prediction Dataset Generator
Generates realistic synthetic traffic data for Indian city intersections.
"""

import csv
import random
import math
import os
from datetime import datetime, timedelta

random.seed(42)

# Configuration
NUM_JUNCTIONS = 4
DAYS = 90  # 3 months of data
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "traffic_data.csv")

JUNCTION_NAMES = {
    1: "Silk Board Junction",
    2: "Hebbal Flyover",
    3: "KR Puram Bridge",
    4: "Marathahalli Bridge"
}

WEATHER_CONDITIONS = ["Clear", "Cloudy", "Light Rain", "Heavy Rain", "Fog"]
WEATHER_WEIGHTS = [0.45, 0.25, 0.15, 0.10, 0.05]

HOLIDAYS = {
    "2025-01-26", "2025-03-14", "2025-04-14", "2025-08-15",
    "2025-10-02", "2025-10-24", "2025-11-01", "2025-12-25"
}


def get_base_traffic(hour, day_of_week):
    """Generate base vehicle count based on hour and day patterns."""
    is_weekend = day_of_week >= 5

    if is_weekend:
        # Weekend: gradual rise, peak around noon, lower overall
        base = 40 + 30 * math.sin(math.pi * (hour - 6) / 12) if 6 <= hour <= 22 else 15
    else:
        # Weekday: dual peak (morning rush 8-10, evening rush 17-19)
        morning_peak = 80 * math.exp(-0.5 * ((hour - 9) / 1.2) ** 2)
        evening_peak = 90 * math.exp(-0.5 * ((hour - 18) / 1.5) ** 2)
        lunch_dip = 45 * math.exp(-0.5 * ((hour - 13) / 1.0) ** 2)
        night_low = 10 if (hour < 6 or hour > 22) else 0
        base = 25 + morning_peak + evening_peak + lunch_dip - night_low

    return max(5, base)


def get_weather_effect(weather):
    """Weather multiplier on traffic count and speed."""
    effects = {
        "Clear": (1.0, 1.0),
        "Cloudy": (1.05, 0.95),
        "Light Rain": (0.85, 0.80),
        "Heavy Rain": (0.60, 0.55),
        "Fog": (0.75, 0.65)
    }
    return effects.get(weather, (1.0, 1.0))


def get_junction_multiplier(junction_id):
    """Each junction has different traffic intensity."""
    multipliers = {1: 1.3, 2: 1.0, 3: 0.9, 4: 1.15}
    return multipliers.get(junction_id, 1.0)


def generate_dataset():
    """Main generation function."""
    start_date = datetime(2025, 1, 1, 0, 0, 0)
    rows = []
    missing_injection_rate = 0.02  # 2% missing values

    for day in range(DAYS):
        current_date = start_date + timedelta(days=day)
        day_of_week = current_date.weekday()
        date_str = current_date.strftime("%Y-%m-%d")
        is_holiday = 1 if date_str in HOLIDAYS else 0

        # Weather for the day (with some intra-day variation)
        day_weather = random.choices(WEATHER_CONDITIONS, weights=WEATHER_WEIGHTS, k=1)[0]

        for hour in range(24):
            # Slight weather variation within the day
            if random.random() < 0.15:
                weather = random.choices(WEATHER_CONDITIONS, weights=WEATHER_WEIGHTS, k=1)[0]
            else:
                weather = day_weather

            for junction_id in range(1, NUM_JUNCTIONS + 1):
                # Base traffic
                base = get_base_traffic(hour, day_of_week)

                # Apply junction multiplier
                base *= get_junction_multiplier(junction_id)

                # Weather effect
                count_mult, speed_mult = get_weather_effect(weather)
                base *= count_mult

                # Holiday effect
                if is_holiday:
                    base *= 0.6

                # Add noise
                vehicle_count = max(0, int(base + random.gauss(0, base * 0.15)))

                # Speed inversely related to count
                if vehicle_count > 0:
                    avg_speed = max(5, 60 - 0.4 * vehicle_count + random.gauss(0, 5))
                    avg_speed *= speed_mult
                    avg_speed = round(max(5, min(80, avg_speed)), 1)
                else:
                    avg_speed = round(60 + random.gauss(0, 3), 1)

                # Inject occasional missing values
                if random.random() < missing_injection_rate:
                    vehicle_count = ""
                if random.random() < missing_injection_rate:
                    avg_speed = ""

                # Inject occasional outliers (sensor glitches)
                if random.random() < 0.005:
                    vehicle_count = random.choice([500, 600, -10, 999])
                if random.random() < 0.005:
                    avg_speed = random.choice([200, -5, 150])

                timestamp = current_date.replace(hour=hour).strftime("%Y-%m-%d %H:%M:%S")

                rows.append([
                    timestamp,
                    junction_id,
                    vehicle_count,
                    avg_speed,
                    weather,
                    day_of_week,
                    is_holiday,
                    hour
                ])

    # Write to CSV
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "timestamp", "junction_id", "vehicle_count", "avg_speed",
            "weather", "day_of_week", "is_holiday", "hour"
        ])
        writer.writerows(rows)

    print(f"✅ Dataset generated: {OUTPUT_FILE}")
    print(f"   Total rows: {len(rows):,}")
    print(f"   Junctions: {NUM_JUNCTIONS}")
    print(f"   Date range: {start_date.strftime('%Y-%m-%d')} to {(start_date + timedelta(days=DAYS-1)).strftime('%Y-%m-%d')}")
    print(f"   Missing values injected: ~{missing_injection_rate*100}%")
    print(f"   Outliers injected: ~0.5%")


if __name__ == "__main__":
    generate_dataset()
