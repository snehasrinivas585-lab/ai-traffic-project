"""
Data Preprocessing Pipeline for Traffic Prediction
- Load CSV with Pandas
- Forward-fill missing time-series values
- Remove outliers using IQR method
- Feature engineering (cyclical encoding, rolling averages)
- Export cleaned dataset
"""

import pandas as pd
import numpy as np
import os

# ─── Paths ───
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
RAW_DATA = os.path.join(BASE_DIR, "data", "traffic_data.csv")
CLEAN_DATA = os.path.join(BASE_DIR, "data", "traffic_data_cleaned.csv")


def load_data():
    """Step 1: Load the Traffic Prediction Dataset."""
    print("=" * 60)
    print("STEP 1: Loading Dataset")
    print("=" * 60)

    df = pd.read_csv(RAW_DATA, parse_dates=["timestamp"])
    print(f"  Shape: {df.shape}")
    print(f"  Columns: {list(df.columns)}")
    print(f"\n  First 5 rows:")
    print(df.head().to_string(index=False))
    print(f"\n  Data types:\n{df.dtypes}")
    return df


def handle_missing_values(df):
    """Step 2a: Handle missing values using forward-fill for time-series."""
    print("\n" + "=" * 60)
    print("STEP 2a: Handling Missing Values")
    print("=" * 60)

    missing_before = df.isnull().sum()
    print(f"  Missing values BEFORE cleaning:\n{missing_before[missing_before > 0]}")

    # Convert to numeric (some might be strings after CSV read)
    df["vehicle_count"] = pd.to_numeric(df["vehicle_count"], errors="coerce")
    df["avg_speed"] = pd.to_numeric(df["avg_speed"], errors="coerce")

    # Forward-fill within each junction (time-series aware)
    df = df.sort_values(["junction_id", "timestamp"])
    df["vehicle_count"] = df.groupby("junction_id")["vehicle_count"].transform(
        lambda x: x.ffill().bfill()
    )
    df["avg_speed"] = df.groupby("junction_id")["avg_speed"].transform(
        lambda x: x.ffill().bfill()
    )

    missing_after = df.isnull().sum()
    print(f"\n  Missing values AFTER forward-fill:\n{missing_after[missing_after > 0]}")
    if missing_after.sum() == 0:
        print("  ✅ No missing values remain!")

    return df


def remove_outliers(df):
    """Step 2b: Remove outliers using the IQR method."""
    print("\n" + "=" * 60)
    print("STEP 2b: Removing Outliers (IQR Method)")
    print("=" * 60)

    rows_before = len(df)

    for col in ["vehicle_count", "avg_speed"]:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR

        outliers = ((df[col] < lower) | (df[col] > upper)).sum()
        print(f"  {col}: Q1={Q1:.1f}, Q3={Q3:.1f}, IQR={IQR:.1f}")
        print(f"    Bounds: [{lower:.1f}, {upper:.1f}]")
        print(f"    Outliers found: {outliers}")

        df = df[(df[col] >= lower) & (df[col] <= upper)]

    rows_after = len(df)
    print(f"\n  Rows removed: {rows_before - rows_after} ({(rows_before - rows_after) / rows_before * 100:.2f}%)")
    print(f"  Rows remaining: {rows_after}")

    return df


def feature_engineering(df):
    """Step 2c: Feature engineering for ML models."""
    print("\n" + "=" * 60)
    print("STEP 2c: Feature Engineering")
    print("=" * 60)

    # Cyclical encoding for hour (captures that hour 23 is close to hour 0)
    df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24)
    df["hour_cos"] = np.cos(2 * np.pi * df["hour"] / 24)
    print("  ✅ Added cyclical hour encoding (hour_sin, hour_cos)")

    # Cyclical encoding for day_of_week
    df["dow_sin"] = np.sin(2 * np.pi * df["day_of_week"] / 7)
    df["dow_cos"] = np.cos(2 * np.pi * df["day_of_week"] / 7)
    print("  ✅ Added cyclical day-of-week encoding (dow_sin, dow_cos)")

    # Is_rush_hour flag
    df["is_rush_hour"] = ((df["hour"].between(8, 10)) | (df["hour"].between(17, 19))).astype(int)
    print("  ✅ Added is_rush_hour flag")

    # Is_weekend flag
    df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)
    print("  ✅ Added is_weekend flag")

    # Weather one-hot encoding
    weather_dummies = pd.get_dummies(df["weather"], prefix="weather", dtype=int)
    df = pd.concat([df, weather_dummies], axis=1)
    print(f"  ✅ One-hot encoded weather ({list(weather_dummies.columns)})")

    print(f"\n  Final shape: {df.shape}")
    print(f"  Final columns: {list(df.columns)}")

    return df


def summary_statistics(df):
    """Print summary statistics of cleaned data."""
    print("\n" + "=" * 60)
    print("SUMMARY STATISTICS (Cleaned Data)")
    print("=" * 60)

    print(f"\n  Numeric columns:")
    print(df[["vehicle_count", "avg_speed"]].describe().to_string())

    print(f"\n  Traffic by junction:")
    junction_stats = df.groupby("junction_id")["vehicle_count"].agg(["mean", "std", "min", "max"])
    print(junction_stats.to_string())

    print(f"\n  Traffic by weather:")
    weather_stats = df.groupby("weather")["vehicle_count"].agg(["mean", "count"])
    print(weather_stats.to_string())

    print(f"\n  Rush hour vs. non-rush hour:")
    rush_stats = df.groupby("is_rush_hour")["vehicle_count"].mean()
    print(f"    Non-rush hour avg: {rush_stats.get(0, 'N/A'):.1f}")
    print(f"    Rush hour avg:     {rush_stats.get(1, 'N/A'):.1f}")


def main():
    print("🚦 Traffic Data Preprocessing Pipeline")
    print("=" * 60 + "\n")

    # Step 1: Load
    df = load_data()

    # Step 2a: Missing values
    df = handle_missing_values(df)

    # Step 2b: Outliers
    df = remove_outliers(df)

    # Step 2c: Feature engineering
    df = feature_engineering(df)

    # Summary
    summary_statistics(df)

    # Export
    df.to_csv(CLEAN_DATA, index=False)
    print(f"\n✅ Cleaned dataset saved to: {CLEAN_DATA}")
    print(f"   Final shape: {df.shape}")


if __name__ == "__main__":
    main()
