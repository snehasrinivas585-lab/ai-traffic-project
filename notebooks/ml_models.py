"""
Machine Learning Models for Traffic Pattern Discovery
========================================================
Step 1: K-Means Clustering (Unsupervised) — discover hidden traffic patterns
Step 2: Linear Regression (Supervised) — predict vehicle counts
Step 3: Decision Tree Classifier — categorize congestion levels
Step 4: Random Forest & Gradient Boosting — ensemble methods
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import os
import warnings
warnings.filterwarnings('ignore')

from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    r2_score, mean_absolute_error, mean_squared_error,
    accuracy_score, classification_report, confusion_matrix
)

# ─── Paths ───
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data", "traffic_data_cleaned.csv")
PLOTS_DIR = os.path.join(BASE_DIR, "plots")
os.makedirs(PLOTS_DIR, exist_ok=True)


def load_clean_data():
    """Load the preprocessed dataset."""
    df = pd.read_csv(DATA_FILE, parse_dates=["timestamp"])
    # Fill any remaining NaN in numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df[numeric_cols] = df[numeric_cols].fillna(0)
    # Drop rows with any remaining NaN
    df = df.dropna(subset=["vehicle_count", "avg_speed"]).reset_index(drop=True)
    print(f"📊 Loaded cleaned dataset: {df.shape[0]} rows, {df.shape[1]} columns")
    return df


# ============================================================
# STEP 1: K-MEANS CLUSTERING (Unsupervised)
# ============================================================

def step1_kmeans_clustering(df):
    """Discover hidden traffic patterns using K-Means."""
    print("\n" + "=" * 65)
    print("STEP 1: K-MEANS CLUSTERING (Unsupervised Learning)")
    print("=" * 65)

    # Features for clustering
    features = ["hour", "day_of_week", "vehicle_count", "avg_speed", "is_holiday"]
    X = df[features].copy()

    # Standardize
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Elbow Method to find optimal K
    inertias = []
    K_range = range(2, 9)
    for k in K_range:
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        km.fit(X_scaled)
        inertias.append(km.inertia_)

    # Plot elbow curve
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    fig.patch.set_facecolor('#0f172a')

    ax1 = axes[0]
    ax1.set_facecolor('#1e293b')
    ax1.plot(list(K_range), inertias, 'o-', color='#38bdf8', linewidth=2, markersize=8)
    ax1.set_xlabel('Number of Clusters (K)', color='#94a3b8', fontsize=12)
    ax1.set_ylabel('Inertia', color='#94a3b8', fontsize=12)
    ax1.set_title('Elbow Method for Optimal K', color='white', fontsize=14, fontweight='bold')
    ax1.tick_params(colors='#94a3b8')
    for spine in ax1.spines.values():
        spine.set_color('#334155')

    # Train with K=4
    optimal_k = 4
    kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
    df["cluster"] = kmeans.fit_predict(X_scaled)

    # Cluster analysis
    print(f"\n  Optimal K chosen: {optimal_k}")
    print(f"\n  Cluster Profiles:")
    cluster_profiles = df.groupby("cluster")[features].mean()
    print(cluster_profiles.to_string())

    # Name the clusters based on profiles
    cluster_names = {}
    for c in range(optimal_k):
        profile = cluster_profiles.loc[c]
        hour = profile["hour"]
        dow = profile["day_of_week"]
        count = profile["vehicle_count"]

        if count > cluster_profiles["vehicle_count"].quantile(0.75):
            if hour < 12:
                name = "Morning Rush Hour"
            else:
                name = "Evening Rush Hour"
        elif dow >= 4.5:
            name = "Weekend Leisure"
        elif count < cluster_profiles["vehicle_count"].quantile(0.25):
            name = "Night / Off-Peak"
        else:
            name = "Midday Normal"

        cluster_names[c] = name
        print(f"    Cluster {c}: {name}")
        print(f"      Avg Hour={hour:.1f}, Avg DoW={dow:.1f}, Avg Count={count:.1f}, Avg Speed={profile['avg_speed']:.1f}")

    # Scatter plot
    ax2 = axes[1]
    ax2.set_facecolor('#1e293b')
    colors = ['#38bdf8', '#f59e0b', '#10b981', '#f43f5e', '#8b5cf6']
    for c in range(optimal_k):
        mask = df["cluster"] == c
        ax2.scatter(df.loc[mask, "hour"], df.loc[mask, "vehicle_count"],
                   c=colors[c], label=cluster_names[c], alpha=0.4, s=10)
    ax2.set_xlabel('Hour of Day', color='#94a3b8', fontsize=12)
    ax2.set_ylabel('Vehicle Count', color='#94a3b8', fontsize=12)
    ax2.set_title('Traffic Clusters by Hour', color='white', fontsize=14, fontweight='bold')
    ax2.legend(fontsize=9, facecolor='#1e293b', edgecolor='#334155',
              labelcolor='#e2e8f0')
    ax2.tick_params(colors='#94a3b8')
    for spine in ax2.spines.values():
        spine.set_color('#334155')

    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "step1_kmeans_clusters.png"), dpi=150,
                facecolor='#0f172a', bbox_inches='tight')
    plt.close()
    print(f"\n  ✅ Plot saved: plots/step1_kmeans_clusters.png")

    return df


# ============================================================
# STEP 2: LINEAR REGRESSION (Supervised)
# ============================================================

def step2_linear_regression(df):
    """Build Linear Regression to predict vehicle counts."""
    print("\n" + "=" * 65)
    print("STEP 2: LINEAR REGRESSION (Supervised Learning)")
    print("=" * 65)

    # Features & target
    feature_cols = ["hour_sin", "hour_cos", "dow_sin", "dow_cos",
                    "is_holiday", "is_rush_hour", "is_weekend", "avg_speed"]
    # Add weather dummies if present
    weather_cols = [c for c in df.columns if c.startswith("weather_")]
    feature_cols.extend(weather_cols)

    X = df[feature_cols]
    y = df["vehicle_count"]

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Train
    lr = LinearRegression()
    lr.fit(X_train, y_train)

    # Predict
    y_pred = lr.predict(X_test)

    # Metrics
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))

    print(f"\n  📈 Linear Regression Results:")
    print(f"    R² Score:  {r2:.4f}")
    print(f"    MAE:       {mae:.2f} vehicles")
    print(f"    RMSE:      {rmse:.2f} vehicles")

    # Feature importance (coefficients)
    print(f"\n  Feature Coefficients:")
    coef_df = pd.DataFrame({
        'Feature': feature_cols,
        'Coefficient': lr.coef_
    }).sort_values('Coefficient', key=abs, ascending=False)
    for _, row in coef_df.iterrows():
        print(f"    {row['Feature']:25s} {row['Coefficient']:+.4f}")

    # Plot actual vs predicted
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    fig.patch.set_facecolor('#0f172a')

    ax1 = axes[0]
    ax1.set_facecolor('#1e293b')
    sample_idx = np.random.choice(len(y_test), min(500, len(y_test)), replace=False)
    ax1.scatter(y_test.iloc[sample_idx], y_pred[sample_idx],
               alpha=0.5, s=15, c='#38bdf8')
    ax1.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()],
            'r--', linewidth=2, label='Perfect Prediction')
    ax1.set_xlabel('Actual Vehicle Count', color='#94a3b8', fontsize=12)
    ax1.set_ylabel('Predicted Vehicle Count', color='#94a3b8', fontsize=12)
    ax1.set_title(f'Actual vs Predicted (R² = {r2:.4f})', color='white',
                 fontsize=14, fontweight='bold')
    ax1.legend(fontsize=10, facecolor='#1e293b', edgecolor='#334155', labelcolor='#e2e8f0')
    ax1.tick_params(colors='#94a3b8')
    for spine in ax1.spines.values():
        spine.set_color('#334155')

    # Residuals
    ax2 = axes[1]
    ax2.set_facecolor('#1e293b')
    residuals = y_test.values - y_pred
    ax2.hist(residuals, bins=40, color='#8b5cf6', alpha=0.7, edgecolor='#6d28d9')
    ax2.axvline(x=0, color='#f43f5e', linewidth=2, linestyle='--')
    ax2.set_xlabel('Residual (Actual - Predicted)', color='#94a3b8', fontsize=12)
    ax2.set_ylabel('Frequency', color='#94a3b8', fontsize=12)
    ax2.set_title('Residual Distribution', color='white', fontsize=14, fontweight='bold')
    ax2.tick_params(colors='#94a3b8')
    for spine in ax2.spines.values():
        spine.set_color('#334155')

    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "step2_linear_regression.png"), dpi=150,
                facecolor='#0f172a', bbox_inches='tight')
    plt.close()
    print(f"\n  ✅ Plot saved: plots/step2_linear_regression.png")

    return lr


# ============================================================
# STEP 3: DECISION TREE CLASSIFIER
# ============================================================

def step3_decision_tree(df):
    print("\n" + "=" * 65)
    print("STEP 3: DECISION TREE CLASSIFIER")
    print("=" * 65)

    # Create congestion labels
    q33 = df["vehicle_count"].quantile(0.33)
    q66 = df["vehicle_count"].quantile(0.66)

    df["congestion"] = pd.cut(
        df["vehicle_count"],
        bins=[-np.inf, q33, q66, np.inf],
        labels=["Low", "Medium", "High"]
    )

    # Remove NaN rows
    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.dropna()

    print(f"\nCongestion thresholds: Low < {q33:.0f} < Medium < {q66:.0f} < High")
    print(df["congestion"].value_counts())

    # Features
    feature_cols = [
        "hour_sin", "hour_cos", "dow_sin", "dow_cos",
        "is_holiday", "is_rush_hour", "is_weekend", "avg_speed"
    ]

    weather_cols = [c for c in df.columns if c.startswith("weather_")]
    feature_cols.extend(weather_cols)

    X = df[feature_cols]
    y = df["congestion"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    dt = DecisionTreeClassifier(
        max_depth=6,
        random_state=42,
        min_samples_leaf=20
    )

    dt.fit(X_train, y_train)

    y_pred = dt.predict(X_test)

    acc = accuracy_score(y_test, y_pred)

    print("\nDecision Tree Accuracy:", acc)
    print(classification_report(y_test, y_pred))

    return dt, df


# ============================================================
# STEP 4: RANDOM FOREST & GRADIENT BOOSTING (Ensemble)
# ============================================================

def step4_ensemble_methods(df):
    """Implement Random Forest and Gradient Boosting for improved accuracy."""
    print("\n" + "=" * 65)
    print("STEP 4: ENSEMBLE METHODS (Random Forest & Gradient Boosting)")
    print("=" * 65)

    # Features
    feature_cols = ["hour_sin", "hour_cos", "dow_sin", "dow_cos",
                    "is_holiday", "is_rush_hour", "is_weekend", "avg_speed"]
    weather_cols = [c for c in df.columns if c.startswith("weather_")]
    feature_cols.extend(weather_cols)

    X = df[feature_cols].fillna(0)
    y = df["congestion"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # ─── Random Forest ───
    print("\n  🌲 Random Forest Classifier:")
    rf = RandomForestClassifier(
        n_estimators=100, max_depth=10, random_state=42,
        min_samples_leaf=10, n_jobs=-1
    )
    rf.fit(X_train, y_train)
    rf_pred = rf.predict(X_test)
    rf_acc = accuracy_score(y_test, rf_pred)
    print(f"    Accuracy: {rf_acc:.4f} ({rf_acc*100:.1f}%)")
    print(classification_report(y_test, rf_pred, target_names=["Low", "Medium", "High"]))

    # ─── Gradient Boosting ───
    print("  🚀 Gradient Boosting Classifier:")
    gb = GradientBoostingClassifier(
        n_estimators=150, max_depth=5, learning_rate=0.1,
        random_state=42, min_samples_leaf=10
    )
    gb.fit(X_train, y_train)
    gb_pred = gb.predict(X_test)
    gb_acc = accuracy_score(y_test, gb_pred)
    print(f"    Accuracy: {gb_acc:.4f} ({gb_acc*100:.1f}%)")
    print(classification_report(y_test, gb_pred, target_names=["Low", "Medium", "High"]))

    # ─── Comparison Chart ───
    fig, axes = plt.subplots(1, 3, figsize=(20, 6))
    fig.patch.set_facecolor('#0f172a')

    # Bar chart comparison
    ax1 = axes[0]
    ax1.set_facecolor('#1e293b')
    dt_acc = accuracy_score(y_test, DecisionTreeClassifier(
        max_depth=6, random_state=42, min_samples_leaf=20
    ).fit(X_train, y_train).predict(X_test))

    models = ['Decision Tree', 'Random Forest', 'Gradient\nBoosting']
    accuracies = [dt_acc, rf_acc, gb_acc]
    bars = ax1.bar(models, accuracies,
                   color=['#f59e0b', '#10b981', '#8b5cf6'],
                   alpha=0.85, edgecolor='white', linewidth=0.5)

    for bar, acc in zip(bars, accuracies):
        ax1.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.005,
                f'{acc:.1%}', ha='center', va='bottom', color='white',
                fontsize=13, fontweight='bold')

    ax1.set_ylim(0, 1.05)
    ax1.set_ylabel('Accuracy', color='#94a3b8', fontsize=12)
    ax1.set_title('Model Accuracy Comparison', color='white',
                 fontsize=14, fontweight='bold')
    ax1.tick_params(colors='#94a3b8')
    for spine in ax1.spines.values():
        spine.set_color('#334155')

    # RF Feature Importance
    ax2 = axes[1]
    ax2.set_facecolor('#1e293b')
    rf_imp = rf.feature_importances_
    sorted_idx = np.argsort(rf_imp)
    ax2.barh(range(len(sorted_idx)), rf_imp[sorted_idx],
            color='#10b981', alpha=0.8)
    ax2.set_yticks(range(len(sorted_idx)))
    ax2.set_yticklabels([feature_cols[i] for i in sorted_idx], color='#94a3b8', fontsize=9)
    ax2.set_title('Random Forest\nFeature Importance', color='white',
                 fontsize=13, fontweight='bold')
    ax2.tick_params(colors='#94a3b8')
    for spine in ax2.spines.values():
        spine.set_color('#334155')

    # GB Feature Importance
    ax3 = axes[2]
    ax3.set_facecolor('#1e293b')
    gb_imp = gb.feature_importances_
    sorted_idx = np.argsort(gb_imp)
    ax3.barh(range(len(sorted_idx)), gb_imp[sorted_idx],
            color='#8b5cf6', alpha=0.8)
    ax3.set_yticks(range(len(sorted_idx)))
    ax3.set_yticklabels([feature_cols[i] for i in sorted_idx], color='#94a3b8', fontsize=9)
    ax3.set_title('Gradient Boosting\nFeature Importance', color='white',
                 fontsize=13, fontweight='bold')
    ax3.tick_params(colors='#94a3b8')
    for spine in ax3.spines.values():
        spine.set_color('#334155')

    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "step4_ensemble_comparison.png"), dpi=150,
                facecolor='#0f172a', bbox_inches='tight')
    plt.close()

    print(f"\n  📊 MODEL COMPARISON SUMMARY:")
    print(f"    {'Model':<25s} {'Accuracy':>10s}")
    print(f"    {'-'*35}")
    print(f"    {'Decision Tree':<25s} {dt_acc:>10.4f}")
    print(f"    {'Random Forest':<25s} {rf_acc:>10.4f}")
    print(f"    {'Gradient Boosting':<25s} {gb_acc:>10.4f}")
    print(f"    {'Best Model':<25s} {max(zip(accuracies, models))[1]:>10s}")
    print(f"\n  ✅ Plot saved: plots/step4_ensemble_comparison.png")

    return rf, gb


# ============================================================
# MAIN
# ============================================================

def main():
    print("🧠 Machine Learning Pipeline for Traffic Pattern Discovery")
    print("=" * 65 + "\n")

    df = load_clean_data()

    # Step 1: Unsupervised — K-Means
    df = step1_kmeans_clustering(df)

    # Step 2: Supervised — Linear Regression
    lr = step2_linear_regression(df)

    # Step 3: Classification — Decision Tree
    dt, df = step3_decision_tree(df)

    # Step 4: Ensemble — Random Forest & Gradient Boosting
    rf, gb = step4_ensemble_methods(df)

    print("\n" + "=" * 65)
    print("✅ ALL ML MODELS COMPLETE")
    print("=" * 65)
    print(f"  Plots saved in: plots/")
    print(f"  Models trained: K-Means, Linear Regression, Decision Tree, Random Forest, Gradient Boosting")


if __name__ == "__main__":
    main()
